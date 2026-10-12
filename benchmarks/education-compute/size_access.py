#!/usr/bin/env python3
"""Translate measured component runs to demand; does not submit or infer ACCESS exchange rates."""
import argparse,json,math,statistics
from pathlib import Path


def size(plan, base, allow_local=False):
    output=[];submission_eligible=True
    for task in plan['workloads']:
        file=(base/task['results_file']).resolve();rows=json.loads(file.read_text())
        if not isinstance(rows,list):raise ValueError('results_file must contain the results.json list, not summary.json')
        failed_runs=sum(r.get('workload')==task['workload'] and r.get('status')!='passed' for r in rows)
        rows=[r for r in rows if r.get('workload')==task['workload'] and not r.get('warmup') and r.get('status')=='passed']
        if not rows:raise ValueError(f"No passed measured runs for {task['id']}")
        if task['resource'] not in ['cpu','gpu']:raise ValueError('resource must be cpu or gpu')
        qualified=all((r.get('platform') in ['campus-aws','access'] if task['resource']=='cpu' else r.get('sizing_eligible') is True and str(r.get('device','')).startswith('cuda') and r.get('platform') in ['kaggle','free-colab','access']) for r in rows)
        if not qualified and not allow_local:raise ValueError(f"{task['id']}: local/CPU control cannot qualify as provider/GPU measurement; --allow-local produces a non-submission illustration only")
        submission_eligible &= qualified
        params={k:float(task[k]) for k in ['participants_or_groups','jobs_each','repetitions_per_job','allowance_fraction']}
        if any(not math.isfinite(v) or v<0 for v in params.values()) or params['allowance_fraction']>1:raise ValueError('Finite nonnegative demand; allowance fraction 0–1 required')
        times=[float(r['wall_seconds']) for r in rows]
        if any(not math.isfinite(v) or v<=0 for v in times):raise ValueError('Measured wall_seconds must be finite and positive')
        seconds=max(times);jobs=params['participants_or_groups']*params['jobs_each']*params['repetitions_per_job'];hours=seconds/3600*jobs*(1+params['allowance_fraction'])
        threads={r.get('configured_threads') for r in rows} if task['resource']=='cpu' else set()
        if task['resource']=='cpu' and (len(threads)!=1 or None in threads):raise ValueError('CPU runs need one common configured_threads value')
        row=dict(id=task['id'],resource=task['resource'],measured_runs=len(rows),excluded_failed_runs=failed_runs,measured_max_wall_seconds=seconds,median_wall_seconds=statistics.median(times),jobs=jobs,allowance_fraction=params['allowance_fraction'],component_residency_hours=hours,measurement_qualified=qualified,results_file=str(file),boundary='Conservative maximum from bounded runs, not a statistical tail/concurrency guarantee; demand multipliers require course approval.')
        if task['resource']=='cpu':row['configured_core_hour_envelope']=hours*next(iter(threads));row['cpu_memory_mib']=max(r.get('peak_process_rss_mib',r.get('host_peak_process_rss_mib',0)) for r in rows) or None
        else:
            row['visible_device_hours']=hours;row['full_physical_gpu_hours']=None;row['peak_torch_reserved_bytes']=max(r.get('peak_torch_reserved_bytes',0) for r in rows) or None
            row['gpu_boundary']='Single visible device; physical fraction and resource billing must be confirmed. Allocator bytes omit driver/context headroom.'
        conversion=task.get('provider_conversion')
        row['provider_units']=None
        if conversion and conversion.get('units_per_instance_hour') is not None:
            rate=float(conversion['units_per_instance_hour'])
            if not math.isfinite(rate) or rate<=0 or not conversion.get('provider') or not conversion.get('unit') or not conversion.get('verified_date'):raise ValueError('Conversion needs a positive verified provider rate, name, unit and date')
            row['provider_units']=hours*rate;row['provider_conversion']=conversion;row['conversion_boundary']='Operator-supplied rate per allocated instance-hour; not automatically ACCESS credits. Do not multiply configured cores twice.'
        output.append(row)
    return dict(status='provider-labeled measurements; review demand and target replay' if submission_eligible else 'local illustration only',eligible_for_submission=False,measurement_qualified=submission_eligible,workloads=output,scope=plan.get('scope','unconfirmed'),remaining=['Review every retained failure and confirm approved courses/groups/jobs and larger cohorts','Replay on intended ACCESS CPU/GPU architectures','Add idle workspace/session, provisioning, staff, retry, concurrency and storage demand without double counting','Confirm provider units/exchange/quota and educational project structure'],boundary='No submission-ready total is produced until the remaining resource plan is completed. Component runtimes omit user thinking and always-on classroom services.')


def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('plan',type=Path);ap.add_argument('--output',type=Path,default=Path('access-sizing.json'));ap.add_argument('--allow-local',action='store_true');args=ap.parse_args()
    result=size(json.loads(args.plan.read_text()),args.plan.resolve().parent,args.allow_local)
    args.output.write_text(json.dumps(result,indent=2,allow_nan=False)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
