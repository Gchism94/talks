#!/usr/bin/env python3
"""Render the evidence-backed classroom route assessment and illustrative sizing model."""
import csv
import html
import json
from pathlib import Path
from build_compute_resources import standalone

ROOT=Path(__file__).resolve().parent.parent
DEST=ROOT/'docs/education-compute'
OUT=ROOT/'output/education-compute'
esc=html.escape
MARKER='\n\nCLASSROOM ROUTE ASSESSMENT | October 12, 2026\n'


def summary_content(data):
    a=data['classroom_assessment']
    return '<p><strong>Next assessment:</strong> '+esc(a['decision'])+'</p><p><a href="classroom-assessment.html">Open the pilot assessment and interactive capacity model ↗</a></p><p>Two representative courses, 80 seats: 36,600 CPU SUs with effective shutdown controls; 516,600 for always-on student VMs; 617,400 for an always-on shared hub. An optional grouped GPU module adds 1,920 GPU-resource SUs. These Jetstream2 estimates do not establish CloudBank pricing, an award, reserved capacity or a tested classroom service.</p>'


CSS='''
*{box-sizing:border-box}
.assess-hero{background:#202938;color:#fff;border-radius:14px;padding:28px;margin:26px 0}.assess-hero h2{font-size:30px;line-height:1.2;margin:6px 0 14px}.assess-hero p{max-width:80ch}.assess-hero a{color:#bdd6ff}.assess-tag{font-size:12px;letter-spacing:.08em;text-transform:uppercase;color:#f0c86b}.assess-nav{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}.assess-flow{display:grid;grid-template-columns:1fr 1fr 1fr;gap:18px;margin:26px 0}.assess-flow article{border-top:4px solid #315fa7;background:#fffcf5;padding:18px;min-width:0}.assess-flow h3{font-size:22px;margin:8px 0}.assess-flow p{font-size:15px}.assess-callout{padding:18px 20px;border-left:4px solid #a76928;background:#fff8df;font-size:16px}.assess-section{margin:44px 0}.assess-section h2{font-size:30px;line-height:1.2}.assess-section h3{font-size:22px;line-height:1.3}.assess-grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.assess-card{background:#fffcf5;border:1px solid #c5c3ba;border-radius:10px;padding:22px;min-width:0}.assess-card p{font-size:15px}.assess-card .assess-tag{color:#315fa7;font-weight:700}.assess-ref{font-size:12px!important;overflow-wrap:anywhere}.assess-table{overflow:auto;border:1px solid #c5c3ba;background:#fffcf5}.assess-table th,.assess-table td{min-width:135px}.assess-form{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;background:#e6e9e8;padding:22px;border-radius:10px}.assess-form label{font-size:15px;font-weight:650;display:block}.assess-form input[type=number],.assess-form select{font:inherit;display:block;width:100%;padding:9px;border:1px solid #87919c;border-radius:5px;margin-top:6px;background:#fffcf5;color:#292b36}.assess-form .wide{grid-column:1/-1}.assess-metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;margin:24px 0}.assess-metrics article{border-top:3px solid #315fa7;padding:12px;background:#fffcf5;min-width:0}.assess-metrics b{display:block;font-size:28px;line-height:1.2;overflow-wrap:anywhere}.assess-metrics span{display:block;font-size:13px;margin-top:8px}.assess-bars{padding:22px;border:1px solid #c5c3ba;border-radius:10px;background:#fffcf5}.assess-bar{margin:16px 0}.assess-bar-label{display:flex;justify-content:space-between;gap:10px;font-size:14px}.assess-track{height:18px;background:#e1e2df;border-radius:4px;margin-top:6px;overflow:hidden}.assess-fill{background:#315fa7;height:100%;min-width:2px}.assess-bar[data-kind=burst] .assess-fill{background:#427d72}.assess-small{font-size:14px}.assess-gates{counter-reset:gate;list-style:none;padding:0}.assess-gates li{counter-increment:gate;position:relative;padding:20px 22px 20px 65px;margin:16px 0;background:#fffcf5;border:1px solid #c5c3ba;border-radius:10px}.assess-gates li:before{content:counter(gate);position:absolute;left:20px;top:24px;background:#202938;color:white;border-radius:50%;width:30px;height:30px;text-align:center;line-height:30px}.assess-gates h3{margin:0 0 6px}.assess-gates p{font-size:15px}.assess-questions details{border-top:1px solid #aaa;padding:16px 0}.assess-questions summary{font-size:20px;font-weight:650;cursor:pointer}.assess-questions li{margin:12px 0}button{font:inherit;border:1px solid #8f949d;border-radius:5px;background:#fffcf5;color:#292b36;padding:8px 14px;cursor:pointer}:focus-visible{outline:3px solid #b26722;outline-offset:4px}.assess-error{color:#932b21;font-weight:650}.assess-links{display:flex;flex-wrap:wrap;gap:12px}.assess-section{scroll-margin-top:20px}@media(max-width:700px){main{padding:22px 16px 45px}.assess-hero{padding:22px}.assess-flow,.assess-grid{grid-template-columns:1fr}.assess-form{grid-template-columns:1fr 1fr;padding:18px}.assess-form select{font-size:15px}.assess-metrics{grid-template-columns:1fr 1fr}.assess-metrics b{font-size:25px}.assess-card{padding:20px}.assess-gates li{padding-left:60px}.assess-hero h2{font-size:27px}}@media print{.assess-form,.assess-nav,button{display:none}.assess-hero{background:white;color:black;padding:0}.assess-tag{color:black}.assess-grid,.assess-flow{display:block}.assess-card,.assess-flow article,.assess-gates li{break-inside:avoid;margin-bottom:12px}.assess-metrics{grid-template-columns:1fr 1fr}.assess-section{margin:24px 0}}
'''

JS='''<script>
const model=MODEL;
const nf=new Intl.NumberFormat('en-US',{maximumFractionDigits:1});
const form=document.getElementById('capacityForm');
function calculate(){
 const seats=Number(form.elements.seats.value),weeks=Number(form.elements.weeks.value),active=Number(form.elements.active.value),kind=form.elements.scenario.value;
 if(!form.checkValidity()){document.getElementById('modelError').textContent='Use 1–400 seats, 1–52 weeks and 1–168 active hours per week.';return}
 document.getElementById('modelError').textContent='';
 const a=model.assumptions, mult=1+a.allowance_percent/100,term=weeks*168;
 const controller=a.controller_vcpu*term*mult;
 const workerCount=Math.max(Math.ceil(seats*a.cpu_per_student/a.shared_worker_vcpu),Math.ceil(seats*a.ram_gb_per_student/a.shared_worker_ram_gb));
 const totals={burst:seats*a.cpu_per_student*active*weeks*mult+controller,dedicated:(seats*a.cpu_per_student+a.controller_vcpu)*term*mult,shared:(workerCount*a.shared_worker_vcpu+a.controller_vcpu)*term*mult};
 const peak=(kind==='shared'?workerCount*a.shared_worker_vcpu:seats*a.cpu_per_student)+a.controller_vcpu;
 const ram=(kind==='shared'?workerCount*a.shared_worker_ram_gb:seats*a.ram_gb_per_student)+a.controller_ram_gb;
 const gpu=form.elements.gpu.checked?model.gpu_model.su:0;
 const courses=Math.ceil(seats/a.students_per_course),working=seats*a.home_gb_per_student+courses*a.shared_gb_per_course;
 const backup=working*(1+a.backup_daily_change_percent/100*a.backup_history_days);
 const sum=totals[kind]+gpu;
 document.getElementById('cpuValue').textContent=nf.format(totals[kind]);
 document.getElementById('gpuValue').textContent=nf.format(gpu);
 document.getElementById('peakValue').textContent=nf.format(peak)+' vCPU';
 document.getElementById('storageValue').textContent=nf.format(working/1000)+' TB';
 const max=Math.max(...Object.values(totals));
 document.querySelectorAll('.assess-bar').forEach(bar=>{const value=totals[bar.dataset.kind];bar.querySelector('.assess-bar-number').textContent=nf.format(value)+' CPU SUs';bar.querySelector('.assess-fill').style.width=(value/max*100)+'%'});
 document.getElementById('modelSummary').textContent=nf.format(seats)+' seats for '+nf.format(weeks)+' weeks: '+nf.format(sum)+' modeled Jetstream2 credits ('+nf.format(totals[kind])+' CPU + '+nf.format(gpu)+' separate GPU-resource SUs). Peak CPU RAM '+nf.format(ram)+' GB; independent backup estimate '+nf.format(backup/1000)+' TB. Shared data assumes '+courses+' groups of up to 40 seats. Optional GPU module stays fixed at 40 DS students; it does not scale with the seat control.';
 let tier=sum<=200000?'Within the Explore initial credit ceiling on paper.':sum<=750000?'Above the Explore initial ceiling; within Discover’s initial ceiling on paper.':sum<=1500000?'Above Discover’s initial ceiling; within Accelerate’s initial ceiling on paper.':'Above Accelerate’s initial ceiling; redesign or consult ACCESS about a larger project.';
 document.getElementById('modelGate').textContent=tier+' Provider approval, separate exchanges and actual quota still govern. '+(peak>150?'Peak exceeds the default 150-vCPU CPU quota. ':'Peak is within the documented default CPU core quota; actual quota/availability still needs confirmation. ')+(working>1000?'Working data exceeds default 1 TB storage. ':'Storage remains within the documented default 1 TB before root/image/log overhead. ')+(kind==='burst'?'Burst is an ideal lower bound, requiring effective stopping/autoscaling and measured shared-worker overhead.':kind==='shared'?'Uses '+workerCount+' always-on m3.2xl workers plus a controller; placement and performance are untested.':'Student VMs run for the whole term, even when idle.');
}
form.addEventListener('input',calculate);form.addEventListener('submit',event=>event.preventDefault());document.getElementById('resetModel').onclick=()=>{form.reset();calculate()};calculate();
let printState;const details=[...document.querySelectorAll('details')];addEventListener('beforeprint',()=>{printState=details.map(d=>d.open);details.forEach(d=>d.open=true)});addEventListener('afterprint',()=>details.forEach((d,i)=>d.open=printState?.[i]??false));
</script>'''


def build():
    data=json.loads((DEST/'evidence.json').read_text()); a=data['classroom_assessment']; evidence=data['evidence']
    def refs(keys):return ' · '.join('<a href="evidence.html#'+esc(k)+'">'+esc(evidence[k]['title'])+'</a>' for k in keys)
    cards=''.join('<article class="assess-card" id="route-'+esc(r['id'])+'"><p class="assess-tag">'+esc(r['role'])+'</p><h3>'+esc(r['name'])+'</h3><p>'+esc(r['fit'])+'</p><p><strong>Before adoption:</strong> '+esc(r['gate'])+'</p><p><strong>Boundary:</strong> '+esc(r['limits'])+'</p><p class="assess-ref">'+refs(r['sources'])+'</p></article>' for r in a['providers'])
    courses=''.join('<article class="assess-card"><h3>'+esc(c['name'])+' · '+str(c['students'])+' seats</h3><p>'+esc(c['work'])+'</p><p><strong>Fallback:</strong> '+esc(c['fallback'])+'</p></article>' for c in a['representative_courses'])
    bars=''.join('<div class="assess-bar" data-kind="'+r['id']+'"><div class="assess-bar-label"><span>'+esc(r['name'])+'</span><strong class="assess-bar-number">'+f'{r["cpu_su"]:,}'+' CPU SUs</strong></div><div class="assess-track"><div class="assess-fill" style="width:'+str(r['cpu_su']/617400*100)+'%"></div></div></div>' for r in a['scenarios'])
    table=''.join('<tr><th scope="row">'+esc(r['name'])+'</th><td>'+f'{r["cpu_su"]:,}'+'</td><td>'+str(r['peak_cpu_vcpu'])+'</td><td>'+str(r['peak_ram_gb'])+'</td><td>'+esc(r['boundary'])+'</td></tr>' for r in a['scenarios'])
    gates=''.join('<li><h3>'+esc(g['title'])+'</h3><p class="assess-small">'+esc(g['when']+' · '+g['owner'])+'</p><p>'+esc(g['evidence'])+'</p><p><strong>Stop if:</strong> '+esc(g['stop'])+'</p><p class="assess-small">Status: '+esc(g['status'])+'</p></li>' for g in a['gates'])
    questions=''.join('<details><summary>'+esc(provider)+'</summary><ul>'+''.join('<li>'+esc(q)+'</li>' for q in qs)+'</ul></details>' for provider,qs in a['provider_questions'].items())
    content='''<p class="assess-small">UArizona Information Science · October 12, 2026 · Documentation assessment; illustrative workload model</p>
<div class="assess-hero"><p class="assess-tag">Recommendation</p><h2>Build a reliable CPU classroom first.<br>Add specialized resources one component at a time.</h2><p>'''+esc(a['decision'])+'''</p><p><a href="federal-compute.html">See the 32-family federal resource map ↗</a></p></div>
<nav class="assess-nav" aria-label="Assessment sections"><a href="#routes">Route decisions</a><a href="#capacity">Capacity model</a><a href="#readiness">Readiness gates</a><a href="#questions">Provider questions</a><a href="#evidence">Evidence and exports</a></nav>
<div class="assess-flow" role="figure" aria-label="Proposed classroom service: required CPU workspace, optional specialized modules, independent continuity service"><article><p class="assess-tag" style="color:#315fa7">1 · Required coursework</p><h3>CPU workspace</h3><p>ACCESS for CPU + GPU classroom use<br>CloudBank conditional; confirm service fit</p></article><article><p class="assess-tag" style="color:#315fa7">2 · Independent modules</p><h3>GPU · batch · data</h3><p>Campus AWS: CPU component tests only<br>Free GPUs: benchmark before piloting<br>ACCESS: CPU + GPU classroom allocation</p></article><article><p class="assess-tag" style="color:#315fa7">3 · Continuity</p><h3>College + Libraries</h3><p>Operators · support · roster/grades<br>Independent backups · restore<br>Student exports · preservation</p></article></div>
<p class="assess-callout"><strong>Three findings change the plan.</strong> CloudBank has a general ACCESS teaching route, but its fall 2026 GPU pilot is full. MESA uses the learner’s existing CyVerse quota. PATh’s published affiliated-program list does not explicitly include IDSS; MESA funding is not automatic access.</p>
<section class="assess-section"><h2>Two representative course workloads</h2><p>Data science and library/information science are the planning pair, not approved courses or named instructor commitments. Start with one assignment per course before a full-term service.</p><div class="assess-grid">'''+courses+'''</div><p class="assess-small">'''+esc(a['degree_expansion'])+''' <a href="degree-options.html">Existing nine-degree comparison ↗</a></p></section>
<section class="assess-section" id="routes"><h2>Assign each platform a job</h2><p>Qualitative fit and operating requirements; no unsupported weighted ranking. The current route follows the user’s confirmed scope: campus AWS tests components only; ACCESS is the CPU/GPU classroom route, after free GPU benchmarks. Existing Jetstream2 numbers are comparison scenarios.</p><div class="assess-grid">'''+cards+'''</div><p class="assess-callout"><strong>Resolve a documentation conflict:</strong> CloudBank’s provider page describes a one-year allocation and renewal; ACCESS says educational projects align with the course and are typically not extended. Its ACCESS support page also mixes managed Classroom and commercial-cloud broker terms. Confirm the exact service, budget and next-term route before relying on either. '''+refs(['assesscloudbank','access','assesscbscope'])+'''</p></section>
<section class="assess-section" id="capacity"><h2>The hidden cost is leaving machines on</h2><p>Jetstream2-only model: two 40-seat courses, 15 weeks, eight active hours/seat/week, 2 vCPU and 6 GB RAM per seat, 20 GB homes, 200 GB shared data/course, a 4-vCPU always-on controller and 25% spending allowance. These rates do not price CloudBank or any other provider.</p>
<form class="assess-form" id="capacityForm"><label>Seats<input name="seats" type="number" min="1" max="400" step="1" value="80" required></label><label>Teaching weeks<input name="weeks" type="number" min="1" max="52" step="1" value="15" required></label><label>Active hours / seat / week<input name="active" type="number" min="1" max="168" step="1" value="8" required></label><label class="wide">Operating scenario<select name="scenario"><option value="burst">Stopped between sessions · ideal lower bound</option><option value="dedicated" selected>Student VMs always on</option><option value="shared">Shared hub workers always on</option></select></label><label class="wide"><input name="gpu" type="checkbox" checked> Include a separate, optional 40-student grouped GPU module</label><div class="wide"><button type="button" id="resetModel">Reset assumptions</button><p id="modelError" class="assess-error" role="alert"></p></div></form>
<div id="modelResults" aria-live="polite" aria-atomic="true"><div class="assess-metrics"><article><b id="cpuValue">516,600</b><span>CPU-resource SUs</span></article><article><b id="gpuValue">1,920</b><span>Separate GPU-resource SUs</span></article><article><b id="peakValue">164 vCPU</b><span>Peak CPU concurrency</span></article><article><b id="storageValue">2 TB</b><span>Working homes + shared data</span></article></div><p id="modelSummary"></p><p class="assess-callout" id="modelGate"></p></div>
<div class="assess-bars" role="figure" aria-label="Modeled CPU credit comparison for shutdown-controlled, always-on dedicated and always-on shared environments">'''+bars+'''<p class="assess-small">Bars compare modeled billed CPU SUs; they are not performance measurements. A 25% spending allowance does not automatically provide more concurrent quota.</p></div>
<details><summary>Default calculations and hardware assumptions</summary><div class="assess-table"><table><thead><tr><th>Scenario</th><th>CPU SUs</th><th>Peak vCPU</th><th>Peak RAM GB</th><th>Basis</th></tr></thead><tbody>'''+table+'''</tbody></table></div><p>Student burst: 80 × 2 × 8 × 15 × 1.25 = 24,000. Always-on controller: 4 × 168 × 15 × 1.25 = 12,600. Always-on dedicated: (80 × 2 + 4) × 168 × 15 × 1.25 = 516,600. Shared workers: (3 × 64 + 4) × 168 × 15 × 1.25 = 617,400.</p><p>Optional GPU: 40 students in groups of five → eight g3.medium slots × six labs × two hours × 16 SU/hour × 1.25 = 1,920 GPU-resource SUs. That is 120 planned fractional-instance hours, <strong>not 120 full-GPU hours</strong>. Each slot has at most 10 GB VRAM; the eight slots require 64 GPU-resource vCPU and 240 GB RAM. Confirm the separate GPU exchange, availability and private networking.</p><p>Working storage: 80 × 20 + 2 × 200 = 2,000 GB. Independent backup estimate: 2,000 + 30 × 1% × 2,000 = 2,600 GB. Decimal GB/TB; excludes root disks, images, logs and snapshots. Actual changed-data rate and retention need measurement.</p><p>Jetstream2 default CPU quota is 150 vCPU; default storage is 1 TB. Neither meets these default modeled requirements without adjusted awards/quotas. '''+refs(['assessjetflavors','assessjetcredit','assessjetquota','assessjetstoragecap'])+'''</p></details>
<p>'''+esc(a['allocation_interpretation'])+''' '''+refs(['types','access'])+'''</p><noscript><p class="assess-callout">The default table remains available without JavaScript. The interactive model requires JavaScript; use the capacity CSV for fixed assumptions.</p></noscript></section>
<section class="assess-section" id="readiness"><h2>Move from a component canary to two courses</h2><p>Proposed timing and acceptance targets. Every gate is currently untested or unconfirmed; document success before promoting a service to required coursework.</p><ol class="assess-gates">'''+gates+'''</ol><p class="assess-callout">'''+esc(a['operations_model'])+'''</p></section>
<section class="assess-section assess-questions" id="questions"><h2>Questions to resolve before a request</h2><p>Draft questions for review; none has been sent to a provider or program officer.</p>'''+questions+'''</section>
<section class="assess-section" id="evidence"><h2>Evidence and review package</h2><p>'''+esc(a['method'])+''' Existing commercial/free-platform records were not all reverified in this assessment.</p><p class="assess-links"><a href="classroom-assessment.json" download>Structured assessment</a><a href="classroom-capacity.csv" download>Capacity assumptions/results</a><a href="classroom-readiness.csv" download>Readiness register</a><a href="research-and-sources.txt">Full research report</a><a href="evidence.html">Source ledger</a></p><details><summary>Primary documentation used for this assessment</summary><p class="assess-ref">'''+refs(a['evidence_sources'])+'''</p></details></section>'''
    page=standalone(a['title'],content,CSS).replace('</body>',JS.replace('MODEL',json.dumps(a,ensure_ascii=False).replace('<','\\u003c'))+'</body>')
    (DEST/'classroom-assessment.html').write_text(page)
    (DEST/'classroom-assessment.json').write_text(json.dumps(a,indent=2,ensure_ascii=False)+'\n')
    with (DEST/'classroom-readiness.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(a['gates'][0]),lineterminator='\n');writer.writeheader();writer.writerows(a['gates'])
    capacity=[]
    for key,value in a['assumptions'].items():capacity.append(dict(category='assumption',name=key,value=value,unit='See structured assumptions',boundary='Illustrative; not a provider award or measurement'))
    for r in a['scenarios']:
        for key in ['student_su','controller_su','cpu_su','peak_cpu_vcpu','peak_ram_gb']:
            capacity.append(dict(category=r['name'],name=key,value=r[key],unit='SUs' if key.endswith('su') else 'vCPU' if 'vcpu' in key else 'GB',boundary=r['boundary']))
    for group in ['gpu_model','storage_model']:
        for key,value in a[group].items():
            if key!='boundary':capacity.append(dict(category=group,name=key,value=value,unit='See structured model',boundary=a[group]['boundary']))
    with (DEST/'classroom-capacity.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(capacity[0]),lineterminator='\n');writer.writeheader();writer.writerows(capacity)
    report=(DEST/'research-and-sources.txt').read_text().split(MARKER)[0]+MARKER+a['title']+'\n'+a['status']+'\n\nRECOMMENDATION\n'+a['decision']+'\n\nWORKLOADS\n'
    for c in a['representative_courses']:report+=f"{c['name']}: {c['students']} illustrative students. {c['work']}\nFallback: {c['fallback']}\n"
    report+='\nQUALITATIVE ROUTE DECISIONS\n'
    for r in a['providers']:report+=f"\n{r['name']} | {r['role']}\n{r['fit']}\nGate: {r['gate']}\nBoundary: {r['limits']}\nSources: {', '.join(r['sources'])}\n"
    report+='\nCAPACITY AND ALLOCATION MODEL\n'+json.dumps({k:a[k] for k in ['assumptions','scenarios','gpu_model','storage_model']},indent=2)+'\n'+a['allocation_interpretation']+'\n\nREADINESS GATES (ALL UNCONFIRMED)\n'
    for g in a['gates']:report+=f"\n{g['title']} | {g['when']} | {g['owner']}\n{g['evidence']}\nStop if: {g['stop']}\n"
    report+='\nOPERATING FUNDING\n'+a['operations_model']+'\n\nDEGREE EXPANSION\n'+a['degree_expansion']+'\n\nDRAFT PROVIDER QUESTIONS (NOT SENT)\n'
    for name,qs in a['provider_questions'].items():report+='\n'+name+'\n'+'\n'.join('- '+q for q in qs)+'\n'
    report+='\nMETHOD AND LIMITS\n'+a['method']+'\n\nPRIMARY SOURCES\n'
    for k in a['evidence_sources']:
        r=evidence[k];report+='\n'+r['title']+'\n'+r['date']+'\n'+r['claim']+'\nScope: '+r['scope']+'\n'+r['url']+'\n'
    (DEST/'research-and-sources.txt').write_text(report)
    for name in ['evidence.json','research-and-sources.txt','classroom-assessment.html','classroom-assessment.json','classroom-capacity.csv','classroom-readiness.csv']:(OUT/name).write_bytes((DEST/name).read_bytes())
    print('Built classroom assessment: seven roles, three CPU scenarios, seven unconfirmed readiness gates')


if __name__=='__main__':build()
