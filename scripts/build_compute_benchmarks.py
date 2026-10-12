#!/usr/bin/env python3
"""Package executable component tests and self-contained provider notebooks."""
import hashlib,json,shutil,zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'benchmarks/education-compute';DEST=ROOT/'docs/education-compute/benchmarks'
def build():
 DEST.mkdir(parents=True,exist_ok=True)
 for name in ['cpu_benchmarks.py','gpu_workloads.py','size_access.py','requirements-cpu.txt','README.txt','demand-example.json']:
  shutil.copy2(SOURCE/name,DEST/name)
 raw=(SOURCE/'gpu_workloads.py').read_text()
 code="BENCHMARK_SOURCE_SHA256 = '"+hashlib.sha256(raw.encode()).hexdigest()+"'\n"+raw.split("\n\nif __name__=='__main__':")[0]
 for task,title in [('ds','Data science: small-model training'),('mlis','MLIS: catalog-feature projection and retrieval')]:
  intro=f'# {title}\n\nStaff component benchmark for Kaggle or free Colab. Select a GPU accelerator, then run cells in order. No downloads of datasets/models, paid calls or Drive mounts. CPU fallback is disabled. Defaults: 10,000 synthetic rows, one warm-up + three measured runs, 10-minute total guard. Export the ZIP before deleting the runtime. A kernel timeout or disconnect can still terminate a run; retain partial files if available.\n\nThese are component proxies, not full-course demand or semantic quality results. Actual ACCESS architecture must be replayed. Inspect versions and account quotas; do not use multiple accounts to bypass limits.\n'
  config="CFG = dict(rows=10000, epochs=3, batch_size=256, repeats=3, seed=521671, max_total_seconds=600, platform='ENTER kaggle / free-colab / access', quota_before='ENTER signed-in remaining quota and GPU type')\nOUTPUT = '/kaggle/working/benchmark-results' if Path('/kaggle/working').exists() else 'benchmark-results'\n"
  run=f"result_folder, summary = run_benchmark('{task}', CFG, OUTPUT, allow_cpu=False)\nprint(json.dumps(summary, indent=2))\n"
  cells=[]
  for kind,text in [('markdown',intro),('code',code),('markdown','## Configuration\nUse the default smoke-sized workload first. Enter the actual provider and remaining quota; run each notebook separately. Increasing sizes changes the workload manifest. Record quota after the run in the exported environment file or your provider notes.'),('code',config),('code',run),('markdown','## Export and stop\nUse the Kaggle Output panel or Colab Files panel to download the generated ZIP. Capture remaining quota and session start/end; the script cannot know billed units. Disconnect/delete the runtime after saving. Run target ACCESS replay with this same notebook and configuration. A missing GPU must remain a blocked result, never a CPU-as-GPU success.')]:
   cell=dict(cell_type=kind,metadata={},source=text.splitlines(True))
   if kind=='code':cell.update(execution_count=None,outputs=[])
   cells.append(cell)
  notebook=dict(cells=cells,metadata={'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python'},'colab':{'name':f'{task}-gpu-benchmark.ipynb','provenance':[]}},nbformat=4,nbformat_minor=5)
  for i,c in enumerate(cells):c['id']=f'{task}-cell-{i}'
  (DEST/f'{task}-gpu-benchmark.ipynb').write_text(json.dumps(notebook,indent=2)+'\n')
 manifest={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(DEST.iterdir()) if p.is_file() and p.name!='manifest.json'}
 (DEST/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
 with zipfile.ZipFile(ROOT/'docs/education-compute/classroom-benchmarks.zip','w',zipfile.ZIP_DEFLATED) as archive:
  for p in sorted(DEST.iterdir()):archive.write(p,'classroom-benchmarks/'+p.name)
 print('Packaged CPU runner, DS/MLIS GPU notebooks and ACCESS sizing tool')
if __name__=='__main__':build()
