"""Synthetic CUDA workloads embedded verbatim in the two provider notebooks."""
import csv, hashlib, json, math, os, platform, random, resource, statistics, sys, time, traceback, uuid
from datetime import datetime, timezone
from pathlib import Path
os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
import torch


def json_write(path, value):
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False)+'\n')


def file_sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
    return h.hexdigest()


def tensor_sha(x):
    return hashlib.sha256(x.detach().cpu().contiguous().numpy().tobytes()).hexdigest()


def sync(device):
    if device.type=='cuda':torch.cuda.synchronize(device)


def seed_all(seed):
    random.seed(seed);torch.manual_seed(seed)
    if torch.cuda.is_available():torch.cuda.manual_seed_all(seed)
    torch.use_deterministic_algorithms(True)
    if torch.cuda.is_available():
        torch.backends.cudnn.benchmark=False
        torch.backends.cuda.matmul.allow_tf32=False
        torch.backends.cudnn.allow_tf32=False


def train_ds(cfg, device, out, deadline):
    seed_all(cfg['seed']);g=torch.Generator().manual_seed(cfg['seed']);t=time.perf_counter()
    x=torch.randn((cfg['rows'],24),generator=g);y=(2*x[:,0]+x[:,1]-1.5*x[:,2]>.0).long()
    input_sha=tensor_sha(x);split=int(len(x)*.8);cpu_test=x[split:].clone();labels=y[split:].clone()
    x,y=x.to(device),y.to(device);model=torch.nn.Sequential(torch.nn.Linear(24,64),torch.nn.ReLU(),torch.nn.Linear(64,2)).to(device)
    optimizer=torch.optim.Adam(model.parameters(),lr=.01);sync(device);setup=time.perf_counter()-t;t=time.perf_counter()
    for epoch in range(cfg['epochs']):
        for begin in range(0,split,cfg['batch_size']):
            if time.perf_counter()>deadline:raise TimeoutError('Total notebook run bound exceeded')
            end=min(begin+cfg['batch_size'],split);optimizer.zero_grad(set_to_none=True)
            loss=torch.nn.functional.cross_entropy(model(x[begin:end]),y[begin:end]);loss.backward();optimizer.step()
    with torch.no_grad():logits=model(x[split:]);accuracy=float((logits.argmax(1)==y[split:]).float().mean().cpu())
    sync(device);compute=time.perf_counter()-t
    assert accuracy>=.8,f'Synthetic accuracy {accuracy} below 0.8'
    checkpoint=out/'checkpoint.pt';torch.save(dict(model=model.state_dict(),optimizer=optimizer.state_dict(),epoch=cfg['epochs'],configuration=cfg),checkpoint)
    loaded=torch.load(checkpoint,map_location='cpu',weights_only=True)
    replay=torch.nn.Sequential(torch.nn.Linear(24,64),torch.nn.ReLU(),torch.nn.Linear(64,2));replay.load_state_dict(loaded['model'])
    with torch.no_grad():cpu_logits=replay(cpu_test)
    assert torch.allclose(cpu_logits,logits.detach().cpu(),rtol=1e-4,atol=1e-4),'CPU checkpoint replay differs'
    # Verify a resumed optimizer step from the export (not merely that saving succeeded).
    restored=torch.nn.Sequential(torch.nn.Linear(24,64),torch.nn.ReLU(),torch.nn.Linear(64,2)).to(device);restored.load_state_dict(loaded['model'])
    resumed=torch.optim.Adam(restored.parameters(),lr=.01);resumed.load_state_dict(loaded['optimizer'])
    t=time.perf_counter();resumed.zero_grad(set_to_none=True);loss=torch.nn.functional.cross_entropy(restored(x[:cfg['batch_size']]),y[:cfg['batch_size']]);loss.backward();resumed.step();sync(device)
    assert math.isfinite(float(loss.detach().cpu()))
    json_write(out/'predictions.json',dict(actual=labels.tolist(),predicted=cpu_logits.argmax(1).tolist()))
    return dict(input_sha256=input_sha,rows=cfg['rows'],features=24,epochs=cfg['epochs'],batch_size=cfg['batch_size'],holdout_accuracy=accuracy,setup_seconds=setup,compute_seconds=compute,resume_seconds=time.perf_counter()-t,checkpoint_resume=True,export_reopen=True)


def retrieve_mlis(cfg, device, out, deadline):
    seed_all(cfg['seed']);g=torch.Generator().manual_seed(cfg['seed']);t=time.perf_counter();n=cfg['rows']
    topics=torch.arange(n)%32;raw=torch.randn((n,256),generator=g)*.025;raw[torch.arange(n),topics]+=1
    projection=torch.randn((256,64),generator=g)/16;input_sha=tensor_sha(raw);q=min(64,n)
    # Synthetic feature projection is a component-size proxy, not a semantic/pretrained language model.
    corpus=raw.to(device);proj=projection.to(device);sync(device);setup=time.perf_counter()-t;t=time.perf_counter()
    parts=[]
    for begin in range(0,n,cfg['batch_size']):
        if time.perf_counter()>deadline:raise TimeoutError('Total notebook run bound exceeded')
        parts.append(torch.nn.functional.normalize(corpus[begin:begin+cfg['batch_size']]@proj,dim=1))
    embeddings=torch.cat(parts);queries=embeddings[:q];top_values=None;top_indices=None
    for begin in range(0,n,cfg['batch_size']):
        if time.perf_counter()>deadline:raise TimeoutError('Total notebook run bound exceeded')
        scores=queries@embeddings[begin:begin+cfg['batch_size']].T
        k=min(5,scores.shape[1]);values,indices=torch.topk(scores,k,dim=1);indices+=begin
        if top_values is not None:values=torch.cat((top_values,values),1);indices=torch.cat((top_indices,indices),1)
        top_values,positions=torch.topk(values,min(5,values.shape[1]),dim=1);top_indices=torch.gather(indices,1,positions)
    sync(device);compute=time.perf_counter()-t
    assert torch.equal(top_indices[:,0].cpu(),torch.arange(q)),'Self-query exact retrieval failed'
    reference=torch.nn.functional.normalize(raw@projection,dim=1)
    reference_scores=reference[:8]@reference.T
    selected_scores=queries[:8]@embeddings.T
    assert torch.allclose(reference_scores,selected_scores.cpu(),rtol=1e-4,atol=1e-4),'CPU/CUDA score check failed'
    export=out/'embeddings.pt';torch.save(dict(embeddings=embeddings.detach().cpu(),projection=projection,configuration=cfg),export)
    loaded=torch.load(export,map_location='cpu',weights_only=True);reopened=loaded['embeddings']
    replay=(reopened[:q]@reopened.T).argmax(1)
    assert torch.equal(replay,top_indices[:,0].cpu()),'Export/reopen changed retrieval'
    json_write(out/'retrieval.json',dict(query_ids=[f'item-{i:08}' for i in range(q)],top5=top_indices.cpu().tolist(),source='Synthetic catalog features, not private records or semantic embeddings',input_sha256=input_sha))
    return dict(input_sha256=input_sha,rows=n,features=256,embedding_dimensions=64,queries=q,batch_size=cfg['batch_size'],retrieval_self_accuracy=1.,setup_seconds=setup,compute_seconds=compute,checkpoint_resume='Saved embedding index + projection reopened; training checkpoint not applicable',export_reopen=True,proxy_boundary='Projection/retrieval component proxy; no tokenization, pretrained model, OCR or semantic-quality claim')


def run_benchmark(workload, cfg, output='benchmark-results', allow_cpu=False):
    if workload not in ['ds','mlis']:raise ValueError('workload must be ds or mlis')
    if not 100<=cfg['rows']<=50000 or not 1<=cfg['epochs']<=10 or not 32<=cfg['batch_size']<=2048 or not 1<=cfg['repeats']<=5:raise ValueError('Bound rows 100–50000, epochs 1–10, batch 32–2048, repeats 1–5')
    if not 1<=cfg.get('max_total_seconds',600)<=1800:raise ValueError('Total time bound must be 1–1800 seconds')
    torch.set_num_threads(2)
    base=Path(output);base.mkdir(parents=True,exist_ok=True);folder=base/(workload+'-'+datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]);folder.mkdir()
    cuda=torch.cuda.is_available();device=torch.device('cuda:0' if cuda else 'cpu')
    environment=dict(torch=torch.__version__,python=sys.version,os=platform.platform(),cuda_runtime=torch.version.cuda,cuda_available=cuda,configuration=cfg,device=str(device),precision='float32; TF32 disabled',cpu_threads=2,platform=cfg.get('platform','unspecified'),quota_before=cfg.get('quota_before','not entered'),quota_after='Record manually before exporting; code does not query provider account/billing APIs',evidence='actual-CUDA-run-on-operator-labeled-host' if cuda else 'local-CPU-functional-control',billing_boundary='Measurements are not provider billed units; account/platform labels are operator-entered',source_sha256=globals().get('BENCHMARK_SOURCE_SHA256') or file_sha(__file__))
    if cuda:
        props=torch.cuda.get_device_properties(0);environment.update(gpu_name=props.name,device_memory_bytes=props.total_memory,visible_devices=torch.cuda.device_count(),device_fraction='Confirm provider; one visible device is not proof of a full physical GPU')
    json_write(folder/'environment.json',environment)
    if not cuda and not allow_cpu:
        json_write(folder/'summary.json',dict(status='blocked-no-cuda',sizing_eligible=False,reason='Select a free GPU accelerator in Kaggle/Colab, or retain this unavailable run. CPU fallback is disabled for GPU sizing.'))
        import shutil
        shutil.make_archive(str(folder),'zip',root_dir=folder)
        raise RuntimeError(f'No CUDA GPU. Blocked result saved at {folder}; do not call this a GPU benchmark.')
    rows=[];deadline=time.perf_counter()+cfg.get('max_total_seconds',600)
    for index in range(cfg['repeats']+1):
        out=folder/f'run-{index}';out.mkdir();row=dict(workload=workload,run_index=index,warmup=index==0,status='failed',device=str(device),platform=cfg.get('platform','unspecified'),configured_threads=2,sizing_eligible=cuda,evidence=environment['evidence'])
        started=time.perf_counter();cpu=time.process_time()
        try:
            if time.perf_counter()>deadline:raise TimeoutError('Total run time limit reached')
            if cuda:torch.cuda.empty_cache();torch.cuda.reset_peak_memory_stats(device)
            row.update((train_ds if workload=='ds' else retrieve_mlis)(cfg,device,out,deadline));sync(device);row['status']='passed'
        except Exception as exc:
            row.update(error=f'{type(exc).__name__}: {exc}');(out/'error.txt').write_text(traceback.format_exc())
        row.update(wall_seconds=time.perf_counter()-started,process_cpu_seconds=time.process_time()-cpu,host_peak_process_rss_mib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/(1024**2 if sys.platform=='darwin' else 1024),host_rss_scope='Cumulative notebook process peak, includes previous runs; not per-run incremental RAM')
        if cuda:row.update(peak_torch_allocated_bytes=torch.cuda.max_memory_allocated(device),peak_torch_reserved_bytes=torch.cuda.max_memory_reserved(device),memory_scope='PyTorch allocator peak, excludes driver/context/other processes; reserve additional headroom')
        row['artifacts']={p.name:dict(bytes=p.stat().st_size,sha256=file_sha(p)) for p in out.iterdir() if p.is_file()};json_write(out/'result.json',row);rows.append(row);json_write(folder/'results.json',rows);print(workload,index,row['status'],round(row['wall_seconds'],3),'seconds')
        if row['status']!='passed':break  # Do not consume more quota after a failure.
    fields=['workload','run_index','warmup','status','device','sizing_eligible','rows','epochs','batch_size','wall_seconds','compute_seconds','setup_seconds','peak_torch_allocated_bytes','peak_torch_reserved_bytes','holdout_accuracy','retrieval_self_accuracy','export_reopen','error']
    with (folder/'results.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
    measured=[r for r in rows if not r['warmup'] and r['status']=='passed'];complete=len(measured)==cfg['repeats'] and all(r['status']=='passed' for r in rows)
    summary=dict(status='passed' if complete else 'incomplete-or-failed',sizing_eligible=cuda and complete,measured_runs=len(measured),configuration=cfg,boundary='Synthetic component run; not class concurrency, full assignment time, account entitlement, idle-session bill or target ACCESS performance.')
    if measured:summary.update(max_wall_seconds=max(r['wall_seconds'] for r in measured),median_wall_seconds=statistics.median(r['wall_seconds'] for r in measured),max_compute_seconds=max(r['compute_seconds'] for r in measured))
    json_write(folder/'summary.json',summary)
    # User may copy/download this zip through notebook UI; no Drive mount, billing API or paid call.
    import shutil
    archive=shutil.make_archive(str(folder), 'zip', root_dir=folder)
    print('Saved',folder,'and',archive);return folder,summary


if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--workload',choices=['ds','mlis'],required=True);ap.add_argument('--platform',choices=['local-functional-control','campus-aws','access'],default='local-functional-control');ap.add_argument('--allow-cpu',action='store_true');ap.add_argument('--smoke',action='store_true');ap.add_argument('--output',default='benchmark-results');args=ap.parse_args()
    cfg=dict(rows=2000 if args.smoke else 10000,epochs=2 if args.smoke else 3,batch_size=256,repeats=1 if args.smoke else 3,seed=521671,max_total_seconds=600,platform=args.platform,quota_before='Record actual account limits separately')
    folder,summary=run_benchmark(args.workload,cfg,args.output,args.allow_cpu)
    sys.exit(0 if summary['status']=='passed' else 1)
