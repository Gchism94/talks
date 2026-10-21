/* Local planning arithmetic only. No submission, account access or data upload. */
(function(root){
'use strict';
const defaults={classroom:{people:40,weeks:15,runs:1,cpuHours:2,cores:4,ram:8,gpuHours:.25,gpus:1,vram:16,peak:40,gpuPeak:4,shared:20,personal:5,output:20,copies:1,retention:19,allowance:25,operator:4,ta:6},research:{people:4,weeks:26,runs:2,cpuHours:1,cores:8,ram:16,gpuHours:.5,gpus:1,vram:24,peak:4,gpuPeak:1,shared:200,personal:20,output:200,copies:1,retention:52,allowance:25,operator:4,ta:0}};
const integerFields=['people','weeks','runs','cores','gpus','peak','gpuPeak','copies','retention'];
function calculate(a){
 for(const key of Object.keys(defaults.classroom)){if(typeof a[key]!=='number'||!Number.isFinite(a[key])||a[key]<0)throw Error('Enter finite, nonnegative values for every numeric field.');if(integerFields.includes(key)&&!Number.isInteger(a[key]))throw Error('People, weeks, runs, devices, copies and peak jobs must be whole numbers.');}
 if(a.people<1||a.weeks<1||a.runs<1||a.cores<1||a.ram<=0||a.peak<1||a.retention<1||a.allowance>100||a.peak>a.people||a.gpuPeak>a.peak)throw Error('Check participants, weeks, runs and CPU size; peak jobs must fit the participant count, GPU peak cannot exceed total peak, and allowance must be 0–100%.');
 if(a.gpuHours>0&&(a.gpus<1||a.vram<=0||a.gpuPeak<1))throw Error('GPU work needs at least one device per job, VRAM and one simultaneous GPU job.');
 const pilot=a.context!=='working-group';
 const jobs=a.people*a.weeks*a.runs,multiplier=1+a.allowance/100;
 const cpuWall=jobs*a.cpuHours*multiplier,gpuWall=jobs*a.gpuHours*multiplier;
 const active=a.shared+a.people*a.personal+a.output;
 const result={status:'Planning scenario — not measured sizing or an award',eligible_for_submission:false,scope:a.scope||'classroom',pattern:a.pattern||'interactive',data:a.data||'public',basis:a.basis||'assumed',assumptions:{...a},totalJobs:jobs,cpuCoreHours:cpuWall*a.cores,cpuJobHours:cpuWall,gpuDeviceHours:gpuWall*a.gpus,peakCpuCores:a.peak*a.cores,peakRamGiB:a.peak*a.ram,peakGpus:a.gpuHours>0?a.gpuPeak*a.gpus:0,vramGiBPerDevice:a.gpuHours>0?a.vram:0,activeStorageGiB:active,independentBackupGiB:active*a.copies,logicalStorageGiB:active*(1+a.copies),retentionWeeks:a.retention,weeklyOperatorHours:a.operator,weeklyTAHours:a.ta,remainingGregHours:pilot?4-a.operator:null};
 if(!Object.values(result).filter(x=>typeof x==='number').every(Number.isFinite))throw Error('The scenario is too large to calculate. Reduce the inputs.');
 result.checks=['Confirm software, eligibility, provider billing units and allocation term.',pilot?'Measure DS/MLIS components; retain failures and replay on the target ACCESS resource.':'Measure the actual workload; retain failures and replay on the intended resource.','Validate concurrent sessions/jobs, queue wait, persistence, accessibility, recovery and staffed support.'];
 if(a.copies===0)result.checks.unshift('No independent backup is sized. Confirm an export/restore plan or add a backup copy before required use.');
 if(a.retention<a.weeks)result.checks.push('Retention is shorter than the active work period; confirm when files are removed and how outputs are retained.');
 if(result.data!=='public')result.checks.unshift('Obtain institutional approval for this data class and the named provider before uploading any real records.');
 if(!pilot)result.checks.push('Confirm who can supply the estimated support hours, existing commitments and any recurring funding. No college-wide staffing ceiling is assumed.');
 else if(result.remainingGregHours<0)result.checks.unshift('Support exceeds Greg’s entire 4-hour weekly envelope. Reduce scope or confirm additional support.');
 else if(result.remainingGregHours===0)result.checks.unshift('This scope uses Greg’s entire four-hour weekly capacity and leaves no time for other duties. Reduce scope or confirm distinct support.');
 else result.checks.push('Reserve the remaining '+result.remainingGregHours+' Greg hours/week for all other duties, including EduCloud; TA hours are separate and unconfirmed.');
 result.route=!pilot&&result.data==='public'&&result.scope==='classroom'?'Compare Puma class groups and appropriate allocated resources. The PI pool is shared; validate remaining hours, queue waits and instructor-led support.':result.data!=='public'?'Review data permissions first; no provider is preapproved by this tool.':result.scope==='classroom'?'Plan an ACCESS CPU + GPU classroom request. Free notebook services are for bounded benchmarks before piloting.':result.pattern==='batch'?'Assess ACCESS and OSPool for independent, checkpointed research jobs; verify GPU availability and eligibility separately.':'Assess ACCESS/provider cloud or an eligible institutional notebook service for interactive research. Confirm session and persistence terms.';
 if(!pilot&&result.scope==='classroom')result.checks.push('Puma publishes 150,000 CPU core-hours/PI/month shared by research and classes; CPU/GPU/high-memory jobs debit the same CPU-based pool and unused hours expire monthly. This is not 150,000 GPU-hours or reserved class capacity.');
 if(a.gpuHours>0)result.checks.push('Kaggle/free Colab may support preliminary GPU measurements; neither reserves GPUs. Match device model, VRAM and physical/shared-device accounting before conversion.');
 if(result.pattern==='service')result.checks.push('Continuous services need a separate instance-uptime/storage/billing model. These per-run totals do not size always-on hosting or databases.');
 return result;
}
root.ComputeNeeds={calculate,defaults};
if(typeof document==='undefined')return;
const form=document.getElementById('needsForm');if(!form)return;const submit=form.querySelector('button[type=submit]');if(submit)submit.disabled=false;
let result;
const fmt=n=>new Intl.NumberFormat('en-US',{maximumFractionDigits:2}).format(n);
const fields=Object.keys(defaults.classroom);
function text(id,value){document.getElementById(id).textContent=value;}
function read(){const a={};for(const k of fields)a[k]=form.elements[k].value.trim()===''?NaN:Number(form.elements[k].value);a.context=form.elements.context?.value||'pilot';for(const k of ['scope','pattern','data','basis'])a[k]=form.elements[k].value;return a;}
function update(){
 result=undefined;document.querySelectorAll('[data-needs-export]').forEach(b=>b.disabled=true);
 try{
 if(!form.checkValidity())throw Error('Complete the highlighted fields with valid, nonnegative numbers.');
 result=calculate(read());text('needsError','');document.getElementById('needsResults').hidden=false;
 for(const [id,k] of [['cpuTotal','cpuCoreHours'],['gpuTotal','gpuDeviceHours'],['storageTotal','logicalStorageGiB']])text(id,fmt(result[k]));
 text('needsQuick',fmt(result.cpuCoreHours)+' CPU core-hours · '+fmt(result.gpuDeviceHours)+' GPU device-hours · '+fmt(result.logicalStorageGiB)+' GiB active + copies. Planning only.');
 text('needsScope',result.scope==='research'?'Research planning scenario':'Classroom planning scenario');text('needsRoute',result.route);
 text('peakSummary',fmt(result.peakCpuCores)+' CPU cores and '+fmt(result.peakRamGiB)+' GiB RAM across '+result.assumptions.peak+' simultaneous jobs; '+fmt(result.peakGpus)+' GPU devices at '+fmt(result.vramGiBPerDevice)+' GiB VRAM each. CPU and GPU peaks are separate planning ceilings; confirm scheduling and overlap.');
 text('storageSummary',fmt(result.activeStorageGiB)+' GiB active + '+fmt(result.independentBackupGiB)+' GiB independent copies for '+result.retentionWeeks+' weeks. Logical capacity only: replicas, versions, filesystem overhead and I/O are additional.');
 text('needsFormula',fmt(result.totalJobs)+' runs × per-run wall hours × configured cores or GPU devices × '+fmt(1+result.assumptions.allowance/100)+' allowance. CPU and GPU totals are separate demands; exclude GPU-only wall time from the CPU input to avoid double counting.');
 const checks=document.getElementById('needsChecks');checks.replaceChildren(...result.checks.map(s=>{const li=document.createElement('li');li.textContent=s;return li;}));
 document.querySelectorAll('[data-needs-export]').forEach(b=>b.disabled=false);
 }catch(e){text('needsQuick','Enter valid assumptions to calculate the scenario.');text('needsError',e.message);document.getElementById('needsResults').hidden=true;}
}
function preset(mode){form.elements.scope.value=mode;for(const [k,v]of Object.entries(defaults[mode]))form.elements[k].value=v;form.elements.pattern.value=mode==='classroom'?'interactive':'batch';form.elements.data.value='public';form.elements.basis.value='assumed';update();text('presetStatus',(mode==='research'?'Research':'Classroom')+' example loaded. All numbers are editable assumptions.');}
function brief(r){return ['COMPUTE NEEDS — PLANNING ONLY',r.scope+' / '+r.pattern+' / '+r.data+' data / '+r.basis+' inputs','CPU core-hours: '+fmt(r.cpuCoreHours),'GPU device-hours: '+fmt(r.gpuDeviceHours),'Peak: '+document.getElementById('peakSummary').textContent,'Storage: '+document.getElementById('storageSummary').textContent,'Operator hours/week: '+r.weeklyOperatorHours+'; separate TA hours/week: '+r.weeklyTAHours,'Route: '+r.route,'Checks:',...r.checks.map(s=>'- '+s),'Assumptions:',JSON.stringify(r.assumptions,null,2),'No provider credits, costs, awards or readiness inferred. Research eligibility and teaching eligibility are distinct.'].join('\n');}
form.addEventListener('submit',e=>{e.preventDefault();update();if(!result)form.reportValidity();});form.addEventListener('input',update);form.addEventListener('change',update);
for(const b of document.querySelectorAll('[data-preset]'))b.onclick=()=>preset(b.dataset.preset);
for(const b of document.querySelectorAll('[data-needs-export]'))b.onclick=()=>{if(!result)return;const json=b.dataset.needsExport==='json';const blob=new Blob([json?JSON.stringify(result,null,2)+'\n':brief(result)+'\n'],{type:json?'application/json':'text/plain'});const u=URL.createObjectURL(blob);const link=document.createElement('a');link.href=u;link.download='compute-needs-'+result.scope+(json?'.json':'.txt');link.click();setTimeout(()=>URL.revokeObjectURL(u),1000);};
const print=document.getElementById('printNeeds');if(print)print.onclick=()=>window.print();update();
})(typeof window==='undefined'?globalThis:window);
