#!/usr/bin/env python3
"""Publish the concise compute guide with pinned Zensical; retain evidence and legacy URLs.
Run after the canonical compute builders. No provider calls or private input data.
"""
import argparse,html,json,shutil,subprocess,sys,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent
SOURCE=ROOT/'site/compute-guide';PUBLIC=ROOT/'docs/education-compute'
GENERATED=ROOT/'output/education-compute/guide-source';BUILD=GENERATED/'_site'
E=html.escape

def write(name,title,body,exclude=False):
    front='---\nsearch:\n  exclude: true\n---\n\n' if exclude else ''
    (GENERATED/'pages'/name).write_text(front+'# '+title+'\n\n'+body+'\n')

def check_engine(executable):
    version=subprocess.check_output([executable,'--version'],text=True).strip()
    if version!='0.0.71':raise RuntimeError('Expected Zensical 0.0.71; install site/compute-guide/requirements.txt before building.')


def build(executable):
    check_engine(executable)
    d=json.loads((PUBLIC/'evidence.json').read_text());p=json.loads((ROOT/'site/education-compute-pilot.json').read_text())
    # The optional backend receives only public dated facts; never copy credential files.
    group=json.loads((SOURCE/'working-group.json').read_text())
    facts_path=ROOT/'services/compute-drafter/data/inventory.json'
    facts_path.parent.mkdir(parents=True,exist_ok=True)
    fact_keys=['id','name','access','cost','limits','contact','source','checked']
    facts_path.write_text(json.dumps([{k:r[k] for k in fact_keys} for r in group['inventory']],indent=2,ensure_ascii=False)+'\n')
    if GENERATED.exists():shutil.rmtree(GENERATED)
    shutil.copytree(SOURCE,GENERATED)
    # Resolve paths explicitly: the generated source is local-only and never published.
    config=(SOURCE/'zensical.toml').read_text()
    (GENERATED/'zensical.toml').write_text(config)
    assets=GENERATED/'pages/guide-assets';shutil.copytree(SOURCE/'assets',assets)
    def refs(keys):return ' · '.join('<a href="evidence.html#'+E(k)+'">'+E(d['evidence'][k]['title'])+'</a>' for k in keys)
    def details(title,body):return '<details><summary>'+E(title)+'</summary>'+body+'</details>'
    def directory(rows,kind):
        cats=sorted({r.get('category',r.get('kind','Other')) for r in rows})
        options='<option value="all">All types</option>'+''.join('<option>'+E(c)+'</option>' for c in cats)
        result='<div data-directory><div class="guide-filter"><label>Search resources<input type="search" placeholder="Try GPU, notebooks, metadata, preservation…"></label><label>Resource type<select>'+options+'</select></label><p role="status" aria-live="polite">'+str(len(rows))+' resources</p></div><div class="guide-directory">'
        for r in rows:
            name=r['name'];category=r.get('category',r.get('kind','Other'))
            access=r.get('access',r.get('route',r.get('allowance','')))
            fit=r.get('fit',r.get('work',''));limits=r.get('limits',r.get('boundary',''))
            legacy='<span id="platform-'+E(r['id'])+'"></span>' if kind=='federal' else ''
            extra=('<p><strong>Funding:</strong> '+E(r['funding'])+'</p>') if 'funding' in r else ''
            result+='<article class="guide-resource" data-resource data-category="'+E(category,quote=True)+'" id="'+E(r['id'])+'">'+legacy+'<span class="guide-tag">'+E(category)+'</span><h3>'+E(name)+'</h3><p>'+E(fit)+'</p><p><strong>Access:</strong> '+E(access)+'</p>'+details('Limits and sources','<p>'+E(limits)+'</p>'+extra+'<p>'+refs(r.get('sources',[]))+'</p>')+'</article>'
        return result+'</div><noscript><p>Search needs JavaScript; all resources are shown.</p></noscript></div>'
    write('resource-library.md','Find a resource','''Start with the work you need to do. Availability does not establish eligibility, capacity or classroom readiness.

| Need | Start here | Main limit |
| --- | --- | --- |
| Small CPU notebooks and code | [Codespaces / Binder / classroom options](classroom-resources.html) | Monthly caps, temporary sessions and no class reservation |
| Preliminary GPU benchmarks | [Kaggle or free Colab](gpu-benchmark.html) | Variable hardware, quotas and queues |
| Planned CPU + GPU classroom baseline | [ACCESS request](access-request.html) | Award, provider match and classroom checks pending |
| Research batches, notebooks or data services | [Federal platforms](federal-compute.html) | Project eligibility and operating model differ |
| Serverless jobs or hosted inference | [Modal and alternatives](serverless-compute.html) | Credits, card requirements and paid conversion |
| Assignments and evaluation | [Classroom 50](classroom50.html) / [Codabench](classroom-resources.html#codabench) | Workflow tools do not supply an unrestricted compute allocation |
| Repositories, apps and databases | [Continuity options](repository-plan.html) | Preservation, always-on hosting and compute are different needs |

[Not sure how much? Scope your needs →](needs.html)

## How to choose

1. Define the smallest useful workload, software and outputs.
2. Match CPU, memory, GPU/VRAM, storage and interactive or batch use.
3. Check eligibility, permitted data, payment requirements and the whole-term access window.
4. Measure, test recovery and name support before making it required.

**Evidence:** the directory reflects dated primary-source reviews, mostly October 8–19, 2026. Check the linked sources before adoption. No signed-in entitlement or provider capacity was tested.''')
    write('classroom-resources.md','Classroom platforms','''Compare bounded options for development, notebooks, scoring and demonstrations. Open each resource’s limits before choosing it. GPU access is variable; competition hosting is not a GPU notebook.

[Benchmark first](gpu-benchmark.html) · [Options by degree](degree-options.html) · [Cloud credits](serverless-compute.html)

'''+directory(d['classroom_resource_options'],'classroom'))
    write('federal-compute.md','Federal platforms','''Federal support can fund machines, data systems, workflow services or operator teams. It does not automatically give every instructor an account or reserved GPUs. These 32 selected families overlap; this is not a machine census.

**Start with ACCESS** for the proposed CPU + GPU classroom allocation. For research, match the work to batch pools, interactive services, data fabrics and mission-specific routes. OSPool’s opportunistic jobs differ from a live notebook service; PATh Facility credit eligibility differs from OSPool access.

**IDSS/MESA:** an operator/service grant is not a generic teaching entitlement. Confirm the actual service, present support, eligible users and underlying provider policy. MESA funding alone does not establish PATh credit eligibility.

[Scope demand](needs.html) · [Download map JSON](federal-compute.json) · [Full evidence](evidence.html)

'''+directory(d['federal_platform_map'],'federal'))
    degrees='| Degree | Suitable small-work starting point | When to move / change activity |\n| --- | --- | --- |\n'
    for r in d['degree_options']:degrees+='| ['+r['name']+']('+r['url']+') | '+r['good']+' | '+r['limit']+' '+r['handoff']+' |\n'
    write('degree-options.md','Options by degree','''Nine Information Science degrees are in scope; cyber programs are excluded. These are activity fits, not confirmed course adoptions. Free resources suit small, bounded work; larger workloads need a measured and approved route.

'''+degrees+'\n\nUse the [platform directory](classroom-resources.html) for quotas and the [needs tool](needs.html) for a planning scenario. Course-specific software, accessibility and assessment requirements still need course-lead review.')
    write('classroom50.md','Classroom 50','''**Workable successor for GitHub Classroom’s assignment workflow; evaluate it before adoption.**

| What it can help with | What it does not solve |
| --- | --- |
| Assignment distribution, course repositories, submissions, feedback and grading workflows | Reserved compute, Codespaces limits, institutional service ownership or an automatic ACCESS integration |

## Ownership and limits

- The Fifty Foundation maintains Classroom 50 and its hosted app. We do not own or operate that service.
- A college-controlled GitHub organization can own course repositories and configuration. That is different from owning the application service.
- Check the required Team/Enterprise organization and its education eligibility.
- **Codespaces’ limited free compute allocation is unchanged.** Actions-based grading has separate quotas/billing.
- GPL-3.0 self-hosting is possible in principle; no local deployment or funded operator is established here.

## Before adoption

Test with a synthetic course: app permissions, roster handling, assignment creation, feedback, Actions quotas, export and access after the term. Keep authoritative grades in the approved LMS and a portable assignment/export path.

'''+refs(['classroom50','classroom50requirements','classroom50actions','codespaces']))
    s=d['serverless_assessment']
    write('serverless-compute.md','Cloud credits & GPUs','''**Modal is a conditional instructor experiment, not the classroom baseline.** Its documented $30/workspace/month credit requires a payment method and the Starter workspace has three seats. CPU, GPU and memory share the allowance. No card, credit redemption, grant or workload has been tested here.

With $0 cash, do not depend on paid conversion. Use Kaggle/free Colab for preliminary GPU benchmarks, then replay on awarded ACCESS CPU + GPU resources. Confirm eligible grant funding before any paid use.

Provider documentation reviewed October 16, 2026. Pricing and credits can change; follow the dated sources.

'''+directory(s['platforms'],'commercial'))
    write('repository-plan.md','Repositories, hosting & databases','''Store the right thing in the right place. A Git repository, research deposit, object store, database and running web app have different jobs.

| Need | Routes to assess | Continuity requirement |
| --- | --- | --- |
| Code and assignments | GitHub; eligible GitLab education routes | Institution-controlled organization, mirrored code and exported configuration |
| Research outputs and metadata | Campus Repository / ReDATA, Zenodo, Figshare, discipline repositories | Rights, deposit policy, limits, persistent identifiers and versioned exports |
| Library collections and exhibits | Omeka and institutional repositories | Original files, metadata/schema export, rights and a tested replacement host |
| Static sites | GitHub Pages / Cloudflare Pages | Local build, portable assets, domain control and an alternate host |
| Databases and app services | Neon, Supabase, MongoDB Atlas; eligible hosting routes | Current quotas, inactivity/expiry, permitted use, export and restore |
| Active data and delivery | Approved provider storage, OSN/OSDF where eligible | Independent backup; active storage/cache is not archival preservation |

## What changed?

GitLab private Free group limits, Bitbucket aggregate storage caps and Google source-hosting onboarding restrictions constrain specific use. **GitHub Free still offers unlimited repository counts.** Heroku’s free tiers ended; Glitch hosting ended; several free database products closed or shortened their lifetime. These are distinct policies, not evidence that all repository accounts disappeared.

[See dated changes and sources →](report.html)

## A practical repair plan

1. Inventory code, files, metadata, app runtimes, databases and ownership separately.
2. Choose a bounded route with an approved fallback; do not assume allocated compute is durable managed hosting.
3. Keep portable environments, schemas, database dumps and rights-cleared file exports.
4. Test restore on a second environment. Proposed targets: a 24-hour recovery point and one-business-day recovery; neither is achieved yet.
5. Export student work, close permissions and use appropriate library archival routes for lasting outputs.

[Full findings](research-report.html) · [All source evidence](evidence.html)''')
    stages=''
    for i,(stage,phase) in enumerate(zip(p['site_flow']['stages'],p['phases']),1):
        stages+='<section class="guide-step" id="stage-'+E(stage['id'])+'"><div class="guide-step-num">'+str(i).zfill(2)+'</div><div><span class="guide-tag">'+E(phase['when'])+'</span><h2>'+E(phase['title'])+'</h2><p>'+E(stage['summary'])+'</p>'+details('Events and gate','<ul>'+''.join('<li>'+E(x)+'</li>' for x in stage['events'])+'</ul><p><strong>Advance when:</strong> '+E(stage['gate'])+'</p>')+'</div></section>'
    write('timeline.md','Stages & milestones','''**Next: scope the ORAI AI-native classroom proposal.** The stages below show the proposed two-course sequence; course scope and support commitments remain to confirm. Dates are relative to an approved future term. Six active preparation weeks do not include unpredictable allocation-review waiting time.

'''+stages+'''

All milestones after preparation are proposed. No award, resource reservation, course term or classroom admission is confirmed. [Review the 13 checks →](readiness.html)''')
    courses=''
    for c in p['courses']:
        courses+='\n## '+c['candidate']+'\n\n'+c['assignment']+'\n\n**Inputs:** '+c['data']+'\n\n**Environment:** '+c['tools']+'\n\n'+details('Outputs and acceptance','<ul>'+''.join('<li>'+E(x)+'</li>' for x in c['outcomes'])+'</ul><p>'+E(c['acceptance'])+'</p>')+'\n'
    write('pilot-plan.md','Two-course pilot','''**Proposed candidates: INFO 521 and LIS 671.** Model 40 students each over 15 weeks. Term, offering, instructor agreement and actual enrollment remain unconfirmed.

Test components → size ACCESS CPU + GPU → replay on the target → ten-person canary → full-class rehearsal → teach → export and review.

'''+courses+'''

## People and support

Greg plans to coordinate the ACCESS request, representative benchmarks and an ORAI AI-native classroom proposal. Confirm technical support responsibilities with the relevant teams. Two course support TAs and course leads have separate potential hours; course leads need no salary. A distinct independent backup is still unfilled. Do not promise a support window until commitments exist.

Use small-data CPU alternatives and assignment accommodations if GPU access fails. Keep rosters/grades in approved institutional systems. Test backups and exports before required use.

[Hours and grant dependencies](budget.html) · [Admission checks](readiness.html) · [Full plan text](pilot-plan.txt) · [Existing pilot brief PDF](pilot-brief.pdf)

Downloadable drafts describe proposed work and support needs. They do not appoint staff or establish classroom readiness.''')
    write('gpu-benchmark.md','Run benchmarks','''**Measure before piloting.** Runnable DS and MLIS components exist; provider runs remain pending. Local synthetic controls are not AWS or CUDA evidence.

| Component | Run on | Record |
| --- | --- | --- |
| CPU data-science and MLIS tests | Already-authorized campus UITS/AWS, component testing only | Wall time, configured threads, memory, input/output sizes and failures |
| GPU DS and MLIS notebooks | Kaggle or free Colab before piloting | Actual device/VRAM, runtime, allocated memory, quota/session limits, failures and exports |
| Target replay | Awarded ACCESS CPU/GPU resource | Equivalent outputs, actual architecture, provider accounting and concurrent behavior |

[Download runnable benchmark bundle](classroom-benchmarks.zip) · [Benchmark result template](gpu-benchmark-results.csv)

## Use the results

1. Agree on inputs, configuration and correctness checks with each course lead.
2. Run warm-up and retained repetitions. Preserve failed runs and platform labels.
3. Export results, environment and hardware details.
4. Use the included `size_access.py` and plan template for component demand. Add interactive idle time, provisioning, staff, storage, retries and concurrency without double counting.
5. Confirm target-provider billing units. CPU core-hours and GPU device-hours are not automatically ACCESS credits.

The MLIS GPU component is a projection/retrieval proxy; it does not establish pretrained semantic-retrieval or OCR quality. Validate those tasks separately if required.

[Explore a planning scenario](needs.html) · [Prepare the ACCESS draft](access-request.html)''')
    write('access-request.md','ACCESS CPU + GPU request','''**Draft only; not submitted or awarded.** ACCESS is the intended large classroom CPU + GPU allocation. Campus AWS is only for CPU component tests. Free GPUs support benchmarking before the pilot.

## Complete before submission

- Eligible PI, actual course leads, term, enrollment and resource match.
- Measured CPU/GPU components, concurrency, memory, storage and software needs.
- Provider exchange/billing units, access window, class/project account structure and permitted data.
- Named operators, independent backup, support commitments and any confirmed eligible grant needs.

[Download editable ACCESS request text](access-allocation-request.txt) · [Existing ACCESS draft PDF](access-allocation-request.pdf)

## Conditional alternatives

**CloudBank:** ask whether an eligible ACCESS/CloudBank route can provide the managed service required. Do not assume approval, credits or an award. [Optional concept text](cloudbank-access-request.txt).

**NAIRR Classroom:** pursue eligible instructor AI pilots in parallel where useful. Verify course/instructor criteria and reporting; this is not an assumed award or a substitute for the whole baseline.

[Needs tool](needs.html) · [Readiness checks](readiness.html) · [Full request context](research-report.html)''')
    b=p['budget'];hours='| Function | Support estimate |\n| --- | ---: |\n'
    for r in b['roles']:hours+='| '+r['role']+' | To scope |\n'
    separate='\n'.join('- **'+r['role']+':** '+str(r['hours'])+' potential hours over the modeled period; not committed.' for r in b['separate_roles'])
    write('budget.md','Time & funding','''**Plan support around the work. Cash budget: $0.** Identify owners for the functions below, confirm course support and a distinct backup, and match any paid needs to eligible funding. No staffing or grant is assumed.

'''+hours+'\n'+separate+'''

Course leads need no salary. No college sponsor or finance role is included. Regular teaching/grading is outside these added pilot hours. No appointment, funding or backup commitment is established by this plan.

## Grant dependencies

Any paid need must be covered by confirmed eligible grant funding under the EduCloud plan. Separate development, training, evaluation and recurring operations; avoid double counting hours or assuming that an application is an award. An allocation supplies resources, not automatically staffing or durable managed hosting.

[Detailed hours CSV](pilot-hours.csv) · [Grant work packages](grant-work-packages.txt) · [Scope support demand](needs.html)

**If the hours do not fit:** reduce the pilot scope or secure actual additional support before class. The independent backup remains unfilled.''')
    gates=''
    for i,g in enumerate(p['checks'],1):gates+='\n'+details(str(i)+'. '+g['category']+' · '+g['id'],'<p><strong>Status:</strong> Planned — not run</p><p>'+E(g['criterion'])+'</p><p><strong>Owner / timing:</strong> '+E(g['owner']+' / '+g['when'])+'</p><p><strong>Evidence:</strong> '+E(g['evidence'])+'</p><p><strong>Stop if:</strong> '+E(g['stop'])+'</p>')+'\n'
    write('readiness.md','Before required classroom use','''**All 13 admission checks are planned, not run.** A working notebook or award alone does not establish classroom readiness. Open a check to see the evidence and stop condition.

'''+gates+'''

[Download readiness CSV](pilot-readiness.csv) · [Return to stages](timeline.html)

This page records the plan. Selecting or opening a check does not approve it or update readiness.''')
    write('classroom-assessment.md','Route assessment','''Choose the service model before choosing a machine.

| Work | Route to assess | Verify first |
| --- | --- | --- |
| Required interactive CPU + GPU teaching | ACCESS resource/provider; conditional managed cloud option | Accounts, scheduling, simultaneous sessions, persistent homes, support and full term |
| Short independent research batches | OSPool; eligible PATh Facility or ACCESS | Interruptions, checkpointing, data policy and project eligibility |
| Instructor-led AI pilot | NAIRR Classroom; eligible notebook/model services | Instructor eligibility, course scope, quota, reporting and permitted data |
| Bounded experiments | Codespaces, Kaggle, Colab, conditional credits | Limits, queues, card requirements, output export and fallback |
| Durable apps, databases and archives | Separate hosting/storage/preservation service | Funding, uptime, backups, ownership, retention and restore |

**Proposed pilot:** two 40-student courses, a ten-person canary and a whole-class rehearsal. Every number is provisional until course leads and measurements confirm it.

[Scope needs](needs.html) · [Federal map](federal-compute.html) · [Admission checks](readiness.html) · [Full assessment evidence](research-report.html)''')
    guide_marker='\n\nCONCISE COMPUTE GUIDE AND PUBLISHING ASSESSMENT | October 19, 2026\n'
    report=(PUBLIC/'research-and-sources.txt').read_text().split(guide_marker)[0]+guide_marker+'''The guide now uses pinned Zensical 0.0.71 on the existing GitHub Pages host. Short task-based pages, client-side search, resource/evidence filters and collapsed audit detail preserve the original URLs, five-slide talk and downloads. MESA's public landing page informed direct headings, spacing and simple actions; its code/private content was not copied.

Publishing alternatives: Zensical fits the Python/static documentation workflow with search and custom CSS/JavaScript. Astro Starlight is a strong component-oriented alternative but adds a Node/Astro workflow. Quarto is useful when notebook/report authoring becomes central. Custom HTML retains maximum control but requires maintaining navigation/search. These are authoring engines, not compute resources. Version pinning and upgrade compatibility checks remain necessary.

needs.html provides local classroom/research planning examples: runs x wall hours x configured cores or GPU devices x allowance. Peak resources and logical storage/copies are separate. It exports all assumptions to text/JSON, flags sensitive-data permissions, scope-specific support needs and missing backups, and does not infer provider credits or approve readiness. Different groups/courses require separate scenarios; continuous-service uptime needs separate sizing. Input evidence is self-reported. Every export remains ineligible for submission. Use actual benchmark results and target replay next.

All 13 classroom checks remain planned. No provider job, award, account, purchase, grant submission or classroom deployment is established. ACCESS remains the intended CPU/GPU classroom route; campus AWS is only component testing; free GPUs support preliminary benchmarks. No cash budget or staffing commitment is assumed.

Publishing/design primary references reviewed October 19, separate from the 181-record compute ledger:
https://idss-mesa.github.io/
https://zensical.org/docs/
https://zensical.org/docs/customization/
https://zensical.org/docs/setup/search/
https://zensical.org/docs/publish-your-site/
https://zensical.org/docs/compatibility/mkdocs/migration/
https://zensical.org/docs/compatibility/mkdocs/plugins/
https://starlight.astro.build/
https://quarto.org/docs/websites/
https://pypi.org/pypi/zensical/json
'''
    (PUBLIC/'research-and-sources.txt').write_text(report)
    (ROOT/'output/education-compute/research-and-sources.txt').write_text(report)

    evidence='''<span id="options"></span><span id="resources"></span><span id="hosting"></span><span id="library"></span><span id="federal"></span><span id="plan"></span><span id="ledger"></span><span id="serverless"></span><span id="classroom50-assessment"></span>

181 primary-source and verification records. Search by provider or topic; open a record for its claim, scope and date. This ledger includes unavailable/historical sources with their stated limitations. A source listing does not mean its current account entitlement was tested.

[Short findings](report.html) · [Full report](research-report.html) · [Download JSON](evidence.json)

<div data-directory><div class="guide-filter"><label>Search evidence<input type="search" placeholder="Provider, policy or topic"></label><p role="status" aria-live="polite">181 records</p></div>'''
    for key,r in d['evidence'].items():
        date=r.get('date','Date basis in source record');recheck=' · Rechecked '+r['rechecked_at'] if r.get('rechecked_at') else ''
        evidence+='<article data-resource id="'+E(key)+'">'+details(r['title'],'<p><a href="'+E(r['url'],quote=True)+'">Primary/source link ↗</a></p><p>'+E(date+recheck)+'</p><p><strong>Claim:</strong> '+E(r.get('claim',''))+'</p><p><strong>Scope:</strong> '+E(r.get('scope',''))+'</p><p>'+E(r.get('quality',''))+'</p>')+'</article>'
    write('evidence.md','Source evidence',evidence+'</div>',True)
    # Needs form: arithmetic is independently testable in needs.js and uses the benchmark
    # helper's wall-time × workload × resource × allowance convention.
    number_groups=[('2. Workload per run',[('people','People or independent groups','Each gets the per-week runs below.',1,1),('weeks','Active weeks','Course or research working period.',1,1),('runs','Runs per person / week','Use the busiest representative workload.',1,1),('cpuHours','CPU-only wall hours / run','Exclude GPU-only work; include interactive idle time if allocated.',0,.01),('cores','CPU cores / run','Configured/allocated, not assumed full utilization.',1,1),('ram','RAM GiB / run','Include the whole process/container.',.1,.1),('gpuHours','GPU wall hours / run','Set 0 for CPU-only work.',0,.01),('gpus','GPU devices / GPU run','A visible/shared device is not automatically a full physical GPU.',0,1),('vram','VRAM GiB / device','A fit requirement, not GPU-hour conversion.',0,.1),('peak','Simultaneous CPU jobs/sessions','Up to the participant/group count.',1,1),('gpuPeak','Simultaneous GPU jobs','Cannot exceed the overall peak.',0,1),('allowance','Retry / variation allowance %','Applied to runtime totals only; 0–100.',0,.1)]),('3. Storage and support',[('shared','Shared input data GiB','One shared copy; avoid per-person duplication here.',0,.1),('personal','Working files GiB / person','Home/workspace allowance.',0,.1),('output','Total output data GiB','Across this whole scenario.',0,.1),('copies','Independent backup copies','Beyond active data; 0 requires a recovery decision.',0,1),('retention','Retention weeks','How long files need to remain available.',1,1),('operator','Potential technical-support hours / week','Scope-specific estimate; confirm the responsible team.',0,.5),('ta','Separate TA hours / week','Potential support; not a staffing commitment.',0,.5)])]
    form='''<form class="needs-form" id="needsForm"><fieldset><legend>1. Purpose and permissions</legend><div class="needs-grid"><label>Purpose<select name="scope"><option value="classroom">Classroom</option><option value="research">Research</option></select></label><label>Work pattern<select name="pattern"><option value="interactive">Interactive notebooks / sessions</option><option value="batch">Independent batch jobs</option><option value="service">Continuous service / API</option></select></label><label>Data class<select name="data"><option value="public">Public / synthetic, rights-cleared</option><option value="internal">Institutional / student records</option><option value="restricted">Sensitive / regulated / restricted</option></select></label><label>Input basis<select name="basis"><option value="assumed">Unmeasured assumptions</option><option value="component">Component measurements available</option><option value="target">Target-resource replay available</option></select><small>A selection is self-reported, not verified evidence.</small></label></div></fieldset>'''
    defaults={'people':40,'weeks':15,'runs':1,'cpuHours':2,'cores':4,'ram':8,'gpuHours':.25,'gpus':1,'vram':16,'peak':40,'gpuPeak':4,'shared':20,'personal':5,'output':20,'copies':1,'retention':19,'allowance':25,'operator':4,'ta':6}
    for title,fields in number_groups:
        form+=('<details><summary>3. Storage and support · editable defaults</summary>' if title.startswith('3.') else '')
        form+='<fieldset><legend>'+title+'</legend><div class="needs-grid">'
        for key,label,hint,minimum,step in fields:form+='<label>'+E(label)+'<input required type="number" name="'+key+'" min="'+str(minimum)+'" '+('max="100" ' if key=='allowance' else '')+'step="'+str(step)+'" value="'+str(defaults[key])+'"><small>'+E(hint)+'</small></label>'
        form+='</div></fieldset>'+('</details>' if title.startswith('3.') else '')
    form+='''<div class="needs-controls"><button class="guide-button" id="updateScenario" type="submit" disabled>Update scenario</button></div></form><p id="needsError" class="needs-error" role="alert"></p><section id="needsResults" class="needs-results" hidden><p class="guide-tag" id="needsScope"></p><h2>Your planning envelope</h2><div class="needs-metrics"><div class="needs-metric"><strong id="cpuTotal"></strong><span>CPU core-hours</span></div><div class="needs-metric"><strong id="gpuTotal"></strong><span>GPU device-hours</span></div><div class="needs-metric"><strong id="storageTotal"></strong><span>GiB active + independent copies</span></div></div><p id="peakSummary"></p><p id="storageSummary"></p><p id="needsFormula"></p><h3>Route to assess</h3><p id="needsRoute"></p><h3>Checks still required</h3><ul id="needsChecks"></ul><div class="guide-actions needs-controls"><button type="button" class="guide-button" data-needs-export="text" disabled>Download brief</button><button type="button" class="needs-secondary" data-needs-export="json" disabled>Download JSON</button><button type="button" class="needs-secondary" id="printNeeds">Print results</button></div></section>'''
    write('needs.md','Scope your computing needs','''Estimate a research project or classroom workload before asking for resources. Numbers are editable examples, not measured demand, provider credits or an award. **No data is uploaded or saved by this tool.** Enter counts and requirements only, never private records.

<div class="guide-actions needs-controls"><button class="needs-secondary" type="button" data-preset="classroom">Load 40-student example</button><button class="needs-secondary" type="button" data-preset="research">Load research example</button></div><p id="presetStatus" role="status">40-student example loaded; edit the assumptions below.</p><p id="needsQuick" class="guide-note" role="status"></p>

'''+form+'''

<noscript><p class="guide-note">Enable JavaScript to calculate and export, or use these formulas: runs = people × weeks × runs/week; CPU core-hours = runs × CPU wall hours × cores × (1 + allowance/100); GPU device-hours = runs × GPU wall hours × devices × the same allowance. Peak demand is separate. Storage = shared inputs + people × working files + outputs; independent copies multiply that storage.</p></noscript>

## How to use the estimate

This is one representative workload envelope. For different CPU/GPU groups or multiple courses, export separate scenarios and review overlap before adding totals. Continuous services need uptime-based sizing beyond this per-run model. Storage capacity does not establish throughput, preservation or a backup service.

The tool follows the benchmark helper’s runtime × workload × resource × allowance arithmetic. Use [measured component results](gpu-benchmark.html) and `size_access.py` for the next sizing step, then confirm provider units, target replay and [classroom checks](readiness.html). Neither the tool nor a selected evidence basis makes a request submission-ready.''')
    from compute_working_group import build as build_working_group
    build_working_group(ROOT,GENERATED,PUBLIC,write)
    from compute_site_focus import build as build_focused_site
    build_focused_site(ROOT,GENERATED,PUBLIC,d,group,write)
    # The overview owns the directory entry; the original presentation is supplemental.
    overview=(GENERATED/'pages/program.md').read_text()
    (GENERATED/'pages/index.md').write_text(overview)
    (GENERATED/'pages/program.md').write_text(overview.replace('---\n','---\nsearch:\n  exclude: true\n',1))
    from build_site import public_deck
    catalog=json.loads((ROOT/'catalog.json').read_text())
    (PUBLIC/'talk.html').write_text(public_deck((ROOT/'education-compute.html').read_text(),catalog.get('publish_notes',False)))
    subprocess.run([executable,'build','--clean','-f',str(GENERATED/'zensical.toml')],check=True,cwd=GENERATED)
    # Overlay only this talk's generated HTML/assets; preserve deck, downloads and ledger.
    for src in BUILD.rglob('*'):
        if src.is_file():
            dest=PUBLIC/src.relative_to(BUILD);dest.parent.mkdir(parents=True,exist_ok=True)
            if src.suffix=='.html':
                text=src.read_text().replace('href="/talks/education-compute/','href="').replace('src="/talks/education-compute/','src="')
                text=text.replace('https://unpkg.com/iframe-worker/shim','guide-assets/vendor/iframe-worker-1.0.4.js')
                # Version custom assets so returning visitors receive matching controls.
                for name in ['guide.css','guide.js','needs.js','working-needs.js','luna-drafting.js','request-submission.js']:
                    revision=hashlib.sha256((SOURCE/'assets'/name).read_bytes()).hexdigest()[:12]
                    text=text.replace('guide-assets/'+name+'\"','guide-assets/'+name+'?v='+revision+'\"')
                text=text.replace('href=""', 'href="index.html"').replace('href="program.html"','href="index.html"')
                band='<div class="guide-college-band"><a href="https://infosci.arizona.edu/">College of Information Science</a><span><a href="index.html">Computing Resources Working Group</a> · Point people: <a href="mailto:maccabe@arizona.edu">Barney Maccabe</a> and <a href="mailto:gchism@arizona.edu">Greg Chism</a></span></div>'
                text=text.replace('<article class="md-content__inner md-typeset">','<article id="program-content" class="md-content__inner md-typeset">'+band)
                icons='<link rel="icon" href="../assets/favicons/talk.svg" type="image/svg+xml"><link rel="icon" href="../assets/favicons/talk-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="../assets/favicons/talk-180.png" sizes="180x180">'
                text=text.replace('</head>',icons+'</head>')
                if src.name in {'index.html','program.html'}:
                    text=text.replace('https://gchism94.github.io/talks/education-compute/'+src.name,'https://gchism94.github.io/talks/education-compute/')
                dest.write_text('\n'.join(line.rstrip() for line in text.splitlines())+'\n')
            else:shutil.copy2(src,dest)
    # Strong source links: anchor navigation must open the enclosing evidence detail.
    script=PUBLIC/'guide-assets/guide.js'
    script.write_text(script.read_text()+"\nfunction revealSource(){if(location.hash){const el=document.getElementById(decodeURIComponent(location.hash.slice(1)));if(el){const d=el.querySelector('details');if(d)d.open=true;el.scrollIntoView();}}}addEventListener('hashchange',revealSource);revealSource();\n")
    print('Built concise Zensical guide, research/classroom needs tool, 181-record appendix; retained talk and downloads.')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--zensical',default='zensical');args=ap.parse_args();build(args.zensical)
