/* Independent arithmetic and rejection controls for the local planning tool. */
const assert=require('node:assert/strict');
require('../site/compute-guide/assets/needs.js');
const {calculate,defaults}=globalThis.ComputeNeeds;
const c=calculate({...defaults.classroom,scope:'classroom'});
assert.equal(c.totalJobs,600);assert.equal(c.cpuCoreHours,6000);assert.equal(c.gpuDeviceHours,187.5);
assert.equal(c.peakCpuCores,160);assert.equal(c.peakRamGiB,320);assert.equal(c.peakGpus,4);
assert.equal(c.activeStorageGiB,240);assert.equal(c.logicalStorageGiB,480);assert.equal(c.eligible_for_submission,false);
const r=calculate({...defaults.research,scope:'research',pattern:'batch'});
assert.equal(r.cpuCoreHours,2080);assert.equal(r.gpuDeviceHours,130);assert.equal(r.logicalStorageGiB,960);assert.match(r.route,/OSPool/);
const one=calculate({...defaults.classroom,people:1,weeks:1,runs:1,cpuHours:1,cores:2,gpuHours:2,gpus:2,peak:1,gpuPeak:1,allowance:0,shared:3,personal:4,output:5,copies:2});
assert.equal(one.cpuCoreHours,2);assert.equal(one.gpuDeviceHours,4);assert.equal(one.logicalStorageGiB,36);
const cpu=calculate({...defaults.classroom,gpuHours:0,gpus:0,gpuPeak:0,vram:0});assert.equal(cpu.gpuDeviceHours,0);assert.equal(cpu.peakGpus,0);
for(const patch of [{people:0},{weeks:NaN},{cpuHours:-1},{gpuHours:Infinity},{people:1.5},{cores:0},{allowance:101},{peak:41},{gpuPeak:41},{gpuHours:1,gpus:0},{gpuHours:1,vram:0}])assert.throws(()=>calculate({...defaults.classroom,...patch}));
const sensitive=calculate({...defaults.classroom,data:'restricted',operator:11});assert.match(sensitive.route,/permissions first/);assert(sensitive.checks.some(x=>x.includes('exceeds')));
const service=calculate({...defaults.research,pattern:'service'});assert(service.checks.some(x=>x.includes('uptime')));
assert.equal(calculate({...defaults.classroom,basis:'target'}).eligible_for_submission,false);
console.log('Passed classroom/research arithmetic, peak/storage accounting, CPU-only, invalid input and readiness controls.');
