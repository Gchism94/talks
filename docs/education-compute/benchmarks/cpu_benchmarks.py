#!/usr/bin/env python3
"""Bounded synthetic DS/MLIS component benchmarks. Creates local files only; no AWS API calls."""
import argparse, csv, hashlib, json, os, platform, resource, statistics, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''): h.update(chunk)
    return h.hexdigest()


def write_json(path, data):
    Path(path).write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')


def ds(rows, seed, out):
    import numpy as np
    t = time.perf_counter(); rng = np.random.default_rng(seed)
    x = rng.normal(size=(rows, 24)); latent = x[:, 0] * 2 + x[:, 1] - x[:, 2] * 1.5
    y = (latent + rng.normal(scale=.25, size=rows) > 0).astype(float)
    x[rng.random(x.shape) < .02] = np.nan
    source = out / 'synthetic-services.csv'
    with source.open('w', newline='') as f:
        w = csv.writer(f); w.writerow([f'feature_{i}' for i in range(24)] + ['label'])
        for a, b in zip(x, y): w.writerow(['' if np.isnan(v) else f'{v:.7f}' for v in a] + [int(b)])
    # Exercise the actual portable input, not an in-memory generation-only proxy.
    data = np.genfromtxt(source, delimiter=',', skip_header=1)
    x, y = data[:, :-1], data[:, -1]; split = int(rows * .8)
    means = np.nanmean(x[:split], axis=0); x = np.where(np.isnan(x), means, x)
    scale = np.std(x[:split], axis=0); scale = np.where(scale == 0, 1, scale)
    x = (x - means) / scale; train, test = x[:split], x[split:]
    generation = time.perf_counter() - t; t = time.perf_counter()
    weights = np.zeros(24); bias = 0.
    for _ in range(80):
        probs = 1 / (1 + np.exp(-np.clip(train @ weights + bias, -30, 30)))
        error = probs - y[:split]; weights -= .3 * (train.T @ error / split + .001 * weights)
        bias -= .3 * float(error.mean())
    predictions = (test @ weights + bias > 0).astype(int)
    accuracy = float(np.mean(predictions == y[split:])); fit = time.perf_counter() - t
    model = out / 'model.json'; write_json(model, dict(weights=weights.tolist(), bias=bias, means=means.tolist(), scale=scale.tolist()))
    restored = json.loads(model.read_text())
    fresh = np.genfromtxt(source, delimiter=',', skip_header=1)[split:, :-1]
    fresh = (np.where(np.isnan(fresh), np.array(restored['means']), fresh)-np.array(restored['means']))/np.array(restored['scale'])
    replay = (fresh @ np.array(restored['weights']) + restored['bias'] > 0).astype(int)
    assert accuracy >= .8, f'Synthetic holdout accuracy {accuracy} below 0.8'
    assert np.array_equal(replay, predictions), 'Model export/reload changed predictions'
    np.savetxt(out / 'holdout-predictions.csv', np.column_stack((y[split:], predictions)), delimiter=',', fmt='%d', header='actual,predicted', comments='')
    return dict(input_sha256=sha(source), rows=rows, features=24, holdout_accuracy=accuracy,
                generation_io_seconds=generation, compute_seconds=fit, export_reopen=True,
                checkpoint_resume='not applicable: fixed-iteration CPU fit; exported model reload verified')


def mlis(rows, seed, out):
    import sqlite3, unicodedata
    t = time.perf_counter(); source = out / 'synthetic-catalog.csv'
    fields = ['identifier', 'title', 'creator', 'date', 'subject', 'rights']
    with source.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields); w.writeheader()
        for i in range(rows):
            w.writerow(dict(identifier=f'item-{i:08}', title=f'  Synthetic collection {i}  ', creator=f' Synthetic Creator {i%25} ', date=str(1900+i%126), subject=f' SUBJECT-{(i+seed)%32} ', rights='CC0 synthetic fixture'))
    generation = time.perf_counter() - t; t = time.perf_counter()
    db = out / 'catalog.sqlite'; con = sqlite3.connect(db)
    con.execute('CREATE TABLE records (identifier TEXT PRIMARY KEY, title TEXT, creator TEXT, year INTEGER, subject TEXT, rights TEXT)')
    with source.open(newline='') as f:
        for row in csv.DictReader(f):
            norm = lambda s: ' '.join(unicodedata.normalize('NFC', s).split())
            con.execute('INSERT INTO records VALUES (?,?,?,?,?,?)', (row['identifier'], norm(row['title']), norm(row['creator']), int(row['date']), norm(row['subject']).lower(), row['rights']))
    con.execute('CREATE INDEX subject_idx ON records(subject)'); con.commit()
    count = con.execute('SELECT COUNT(*) FROM records').fetchone()[0]
    grouped = con.execute('SELECT subject, COUNT(*) FROM records GROUP BY subject ORDER BY subject').fetchall()
    assert count == rows and sum(n for _, n in grouped) == rows
    assert con.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    export = out / 'normalized-catalog.csv'
    with export.open('w', newline='') as f:
        w = csv.writer(f); w.writerow(['identifier','title','creator','year','subject','rights']); w.writerows(con.execute('SELECT * FROM records ORDER BY identifier'))
    con.close(); compute = time.perf_counter() - t
    reopened = sqlite3.connect(db); assert reopened.execute('SELECT COUNT(*) FROM records').fetchone()[0] == rows; reopened.close()
    with export.open(newline='') as f:
        reader = csv.DictReader(f); assert sum(1 for _ in reader) == rows
    write_json(out / 'schema-and-provenance.json', dict(source='Synthetic; no patron/donor/circulation data', seed=seed, crosswalk=dict(date='year', title='trim/collapse whitespace + NFC', subject='normalized lowercase'), source_sha256=sha(source), export_sha256=sha(export), grouped_counts=grouped))
    return dict(input_sha256=sha(source), rows=rows, normalized_rows=count, subject_groups=len(grouped),
                generation_io_seconds=generation, compute_seconds=compute, export_reopen=True,
                checkpoint_resume='SQLite commit/reopen and portable CSV count verified; not an archive service')


def worker(args):
    # Each run is a fresh process. RSS includes imports, generated inputs and pipeline artifacts.
    for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']:
        os.environ[key] = str(args.threads)
    out = Path(args.output); out.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter(); cpu = time.process_time()
    row = dict(workload=args.workload, status='failed', started_utc=datetime.now(timezone.utc).isoformat(),
               platform=args.platform, evidence='local-functional' if args.platform == 'local' else 'operator-labeled-provider-run',
               warmup=args.warmup, seed=args.seed, configured_threads=args.threads,
               platform_label_boundary='Operator-entered label, not independently verified provider identity',
               python=sys.version, os=platform.platform(), logical_cpus=os.cpu_count(), source_sha256=sha(__file__))
    try:
        row.update((ds if args.workload == 'ds' else mlis)(args.rows, args.seed, out)); row['status'] = 'passed'
    except Exception as exc:
        row['error'] = f'{type(exc).__name__}: {exc}'
    row.update(wall_seconds=time.perf_counter()-started, process_cpu_seconds=time.process_time()-cpu)
    rss = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    row['peak_process_rss_mib'] = rss / (1024**2 if sys.platform == 'darwin' else 1024)
    row['rss_scope'] = 'Fresh process peak, includes imports/generation; not provider billing or disk/cache quota'
    try:
        import numpy as np
        row['numpy_version'] = np.__version__
    except ImportError: pass
    row['artifacts'] = {p.name: dict(bytes=p.stat().st_size, sha256=sha(p)) for p in out.iterdir() if p.is_file()}
    write_json(out/'result.json', row); print(json.dumps(row), flush=True)
    return 0 if row['status']=='passed' else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--workload', choices=['ds','mlis','all'], default='all'); ap.add_argument('--rows',type=int,default=10000)
    ap.add_argument('--repeats',type=int,default=3); ap.add_argument('--threads',type=int,default=2); ap.add_argument('--seed',type=int,default=521671)
    ap.add_argument('--platform',default='local',choices=['local','campus-aws','access']); ap.add_argument('--output',default='benchmark-results')
    ap.add_argument('--worker',action='store_true',help=argparse.SUPPRESS); ap.add_argument('--warmup',action='store_true',help=argparse.SUPPRESS)
    args=ap.parse_args()
    if not 100<=args.rows<=200000 or not 1<=args.repeats<=5 or not 1<=args.threads<=8: ap.error('rows 100–200000, repeats 1–5 and threads 1–8 required')
    if args.worker: return worker(args)
    base=Path(args.output); base.mkdir(parents=True,exist_ok=True)
    session=base/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'-'+uuid.uuid4().hex[:8]); session.mkdir()
    results=[]; failed=False
    for task in (['ds','mlis'] if args.workload=='all' else [args.workload]):
        for i in range(args.repeats+1):
            cmd=[sys.executable,__file__,'--worker','--workload',task,'--rows',str(args.rows),'--seed',str(args.seed),'--threads',str(args.threads),'--platform',args.platform,'--output',str(session/f'{task}-{i}')]
            if i==0: cmd.append('--warmup')
            try:
                run=subprocess.run(cmd,capture_output=True,text=True,timeout=300)
                resultfile=session/f'{task}-{i}'/'result.json'
                row=json.loads(resultfile.read_text()) if resultfile.exists() else dict(workload=task,status='failed',warmup=i==0,error=run.stderr[-2000:])
            except subprocess.TimeoutExpired:
                row=dict(workload=task,status='timeout',warmup=i==0,error='Five-minute process bound reached; retain partial files')
                write_json(session/f'{task}-{i}'/'result.json',row)
            row['run_index']=i; results.append(row); failed|=row['status']!='passed'; print(task,i,row['status'],row.get('wall_seconds',''),flush=True)
            write_json(session/'results.json',results)
    fields=['workload','run_index','warmup','status','platform','rows','configured_threads','wall_seconds','process_cpu_seconds','peak_process_rss_mib','compute_seconds','generation_io_seconds','holdout_accuracy','export_reopen','error']
    with (session/'results.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(results)
    summary={task:dict(measured_runs=len(rows),max_wall_seconds=max(r['wall_seconds'] for r in rows),median_wall_seconds=statistics.median(r['wall_seconds'] for r in rows),peak_process_rss_mib=max(r['peak_process_rss_mib'] for r in rows)) for task in ['ds','mlis'] if (rows:=[r for r in results if r['workload']==task and r['status']=='passed' and not r['warmup']])}
    write_json(session/'summary.json',dict(results=summary,complete=not failed,boundary='Synthetic component measurements on this host only; excludes idle workspace, user thinking time, class concurrency, provider provisioning and ACCESS conversion.'))
    print('Results:',session)
    return int(failed)

if __name__=='__main__': sys.exit(main())
