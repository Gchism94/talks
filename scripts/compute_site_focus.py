"""Focused report and readable archive; retain the original dated audit and URLs."""
import html
import re

E = html.escape
PRIMARY = {'index', 'program', 'inventory', 'primers', 'needs', 'report', 'supplemental'}


def inline(text):
    """Escape source text and link only literal HTTP(S) URLs."""
    parts = re.split(r'(https?://[^\s<>]+)', text)
    result=[]
    for p in parts:
        if p.startswith(('http://','https://')):
            url=p.rstrip('.,;')
            while url.endswith(')') and url.count(')')>url.count('('):url=url[:-1]
            result.append('<a href="'+E(url,quote=True)+'">'+E(p)+'</a>')
        else:result.append(E(p))
    return ''.join(result)



def archive_html(report):
    chapters = [
        ('TEACHING ON BORROWED COMPUTE', 'Original findings and method'),
        ('CURRENT FREE OPTIONS BY DEGREE |', 'Early degree and platform comparison'),
        ('REPOSITORY ACCESS UPDATE |', 'Repository changes and continuity'),
        ('LIBRARY, HOSTING AND DATABASE EVIDENCE EXTENSION |', 'Library repositories, hosting and databases'),
        ('CODABENCH CORRECTION AND CLASSROOM RESOURCE REPORT |', 'Codabench and classroom platforms'),
        ('FEDERALLY SUPPORTED COMPUTING MAP |', 'Federal platforms and products'),
        ('CLASSROOM ROUTE ASSESSMENT |', 'Classroom service assessment'),
        ('ACCESS CPU + GPU REQUEST AND TWO-COURSE PILOT |', 'ACCESS request and DS/MLIS pilot'),
        ('CLASSROOM 50 SUCCESSOR ASSESSMENT |', 'Classroom 50 assessment'),
        ('MODAL AND SIMILAR COMPUTE PLATFORMS |', 'Modal and commercial alternatives'),
        ('CONCISE COMPUTE GUIDE AND PUBLISHING ASSESSMENT |', 'Publishing and guide assessment'),
        ('COMPUTING RESOURCES WORKING GROUP |', 'Working-group packet and campus inventory'),
    ]
    lines=report.splitlines();starts=[]
    for i,line in enumerate(lines):
        for prefix,title in chapters:
            if line.startswith(prefix):starts.append((i,title));break
    if not starts or starts[0][0]!=0:raise ValueError('Archive must begin with the original research')
    sections=[]
    def render_chunk(chunk):
        result=[]
        for block in re.split(r'\n\s*\n', chunk):
            if not block.strip():continue
            rows=block.splitlines()
            # Historical all-caps/Markdown section names become readable headings.
            first=rows[0].strip()
            heading=(first.startswith('#') or (len(first)<110 and first.upper()==first and any(c.isalpha() for c in first)))
            if heading:
                result.append('<h3>'+E(first.lstrip('#').strip())+'</h3>');rows=rows[1:]
            if rows:result.append('<p>'+ '<br>'.join(inline(row) for row in rows)+'</p>')
        return ''.join(result)
    for n,(start,title) in enumerate(starts):
        end=starts[n+1][0] if n+1<len(starts) else len(lines)
        sections.append('<details class="guide-archive" id="archive-'+str(n+1)+'"><summary>'+str(n+1)+'. '+E(title)+'</summary>'+render_chunk('\n'.join(lines[start:end]))+'</details>')
    return ''.join(sections)


def build(root, generated, public, data, group, write):
    overview=data['report_overview']
    counts={level:sum(r['level']==level for r in group['inventory']) for level in ['College','University','National / external']}
    inventory_summary=f"{len(group['inventory'])} entries: {counts['College']} college, {counts['University']} university and {counts['National / external']} national/external"
    def refs(keys):
        return ' · '.join('<a href="evidence.html#'+E(k)+'">'+E(data['evidence'][k]['title'])+'</a>' for k in keys)
    resource_details=[]
    for r in overview['available']:
        resource_details.append('<details><summary>'+E(r['title'])+' · '+E(r['status'])+'</summary><p><strong>'+E(r['names'])+'</strong></p><p>'+E(r['fit'])+'</p><p><strong>Boundary:</strong> '+E(r['boundary'])+'</p><p><a href="'+E(r['detail'],quote=True)+'">Detailed comparison →</a></p><p class="guide-source-links">'+refs(r['sources'])+'</p></details>')
    history=[]
    for year in overview['years']:
        events=[]
        for event in year['events']:
            events.append('<li><strong>'+E(event['date']+' · '+event['title'])+'</strong><p>'+E(event['before']+' → '+event['after'])+'</p><p class="guide-source-links">'+refs(event['sources'])+'</p></li>')
        history.append('<details class="guide-history"><summary>'+E(year['year'])+' · '+E({
            '2022':'Hosting and collaboration limits','2023':'Classroom onboarding closes','2024':'Shorter database life and service withdrawals','2025':'Storage limits, hosting losses and shorter free access','2026':'GitHub Classroom ends'}[year['year']])+'</summary><ul>'+''.join(events)+'</ul></details>')
    observation=overview['observation'];upcoming=overview['upcoming']
    write('report.md','Computing resources report','''<span id="report-overview"></span>

For the **College of Information Science Computing Resources Working Group**. This report connects available services, changes in access and a practical response. The [resource inventory](inventory.html) contains service-specific access, cost and contact details.

**Review basis:** dated provider and campus documentation, mostly checked October 8–19, 2026, with campus HPC allocation and teaching policies rechecked October 20, plus the explicitly attributed ORAI update. This is a working assessment, not a completed college-wide needs study.

## Key findings

- **Resources exist, but access and support differ.** College and campus services, national allocations and bounded free platforms serve different work.
- **Continuity is the gap illustrated by the provider history.** Closed services, narrower eligibility, shorter windows and tighter limits can break a course or research workflow.
- **The opportunity is a supported route, not only more hardware.** Match activities to existing services, identify the remaining gap, and test shared capacity, expertise and portable environments.

## Available resources

<span id="available-resources-at-a-glance"></span>

The inventory contains **'''+inventory_summary+'''**. It covers hardware, software and models, data, RSE and technical support, training and collaboration. Unknown local equipment, licenses and available support hours are recorded as unknown, rather than assumed absent.

Campus starting points include Puma CPU/GPU computing, software licensing, library data and digital-scholarship services, and research software expertise.

### Campus HPC: Puma classroom access

**Verified October 20, 2026:** the current [HPC teaching policy](https://hpcdocs.hpc.arizona.edu/policies/hpc_for_instruction/) explicitly permits Puma class groups. Earlier references to an Ocelote-only policy are superseded.

| What is available | Limitation to plan around |
| --- | --- |
| 150,000 CPU core-hours per PI group/month | Research and class groups share one pool; unused hours do not carry forward |
| CPU, GPU and high-memory jobs | CPU-based accounting uses that same pool; 150,000 is not a GPU-hour entitlement or course reservation |
| Standard concurrency: four GPUs / 3,290 CPUs per group | Shared group ceilings, not promised availability or one GPU per student |
| Standard allocation; optional windfall | Shared queues have uncertain waits and no assignment-deadline priority; windfall jobs can be interrupted |
| Instructor setup and infrastructure consulting | Instructors/team support students; HPC Consult works weekday business hours, excluding university holidays |

Check the PI's remaining allocation with **va** and actual group limits/usage with **job-limits &lt;group_name&gt;**, confirm class-group setup and device requirements, and test assignment fit before required use. No signed-in balance, peak-class rehearsal or reserved capacity is established here. [Allocation and charging policy](https://hpcdocs.hpc.arizona.edu/resources/allocations/) · [Job limits](https://hpcdocs.hpc.arizona.edu/running_jobs/job_limits/) · [HPC Consult](https://hpcdocs.hpc.arizona.edu/support_and_training/consulting_services/).

The [hardware page](https://hpcdocs.hpc.arizona.edu/resources/compute_resources/) lists **Lynx/H200 as not available yet**. Its Puma MIG memory table and narrative differ; confirm the requested device rather than assuming a memory quota. ACCESS remains the proposed large CPU/GPU allocation route for the separate instructional pilot.

**Briefing cross-check:** a Jeremy Frumkin (UITS) hardware slide in supplied October 14–15 AI AWS Days notes lists **40 GB A100 MIG slices on Puma**, marks Ocelote retired and lists Lynx for 2026. These are cluster hardware descriptions, not a PI/classroom allocation or proof of current availability. The current public policies above govern the documented access route; confirm the GPU/MIG shape before sizing a class. The private notes export is not published here.

[Browse the inventory](inventory.html) · [Campus AI transition and supplied prices](campus-ai.html)

### External routes and their limits

Open a resource group for its role, status and evidence. These are dated comparisons; availability does not establish account eligibility or reserved capacity.

'''+ '\n'.join(resource_details)+'''

Commercial offers and free credits require particular care with payment methods, account scope and paid conversion. [Full commercial comparison](serverless-compute.html).

## The growing gap

<span id="resource-trend"></span><span id="selected-losses-and-reductions-20222026"></span>

<div class="guide-thesis">What we have previously relied on can no longer be guaranteed</div>

The selected history shows losses across compute, classroom workflows, repositories, hosting and databases. It is **not a census or a measured decline in total free compute**, nor does it establish the size of the college’s unmet demand. GitHub Free repositories and base free Colab remain available.

### Documented changes by year

'''+ '\n'.join(history)+'''

<div class="guide-note"><strong>'''+E(observation['label'])+': '+E(observation['title'])+'''.</strong> '''+E(observation['body'])+''' <span class="guide-source-links">'''+refs(observation['sources'])+'''</span></div>

<details><summary>'''+E(upcoming['label'])+' · '+E(upcoming['title'])+'''</summary><p>'''+E(upcoming['body'])+'''</p><p>'''+refs(upcoming['sources'])+'''</p></details>

### What the college still needs to establish

Which activities are blocked; who is affected; whether the barrier is capacity, eligibility, awareness, affordability or support; and what existing services can realistically absorb. The [resource tool](needs.html) prepares an individual brief. An optional private pilot queue lets Barney and Greg review submitted briefs. Participation and verification are still needed before making college-wide claims.

## The opportunity

<span id="program-response"></span><span id="what-to-do-about-it"></span>

| Avenue | Practical next step | Commitment to confirm |
| --- | --- | --- |
| Better use of existing services | Map one research and one teaching workflow to a documented route | Eligibility, headroom, onboarding and support |
| Shared expertise and portable environments | Scope reusable software/data workflows and support tasks | Named capacity, task hours, ownership and recurring effort |
| Allocation-backed CPU and GPU | Benchmark representative work and justify an ACCESS request | Award, provider fit, operations, accounts and classroom use |
| Instructor pilots and partnerships | Explore eligible NAIRR Classroom and compatible campus/federal services | Scope, access, reporting, support and continuity |

**Instructional-computing case study:** the proposed DS/MLIS pilot uses ACCESS for CPU **and** GPU. Campus AWS is only for component testing; free GPU notebooks support preliminary benchmarks, followed by target-resource replay. CloudBank remains conditional. The pilot has no assigned cash budget; necessary paid support requires confirmed eligible grant funding. Confirm TA/course-lead and technical support responsibilities.

No award, capacity reservation, provider benchmark or classroom deployment is established here. All 13 pilot readiness checks remain planned. [Pilot details and request draft](supplemental.html#instructional-computing-pilot).

### Planned next step: ORAI AI Innovation Pilot

Greg Chism will draft a separate proposal to showcase ORAI tools alongside his infrastructure components in an **AI-native classroom**, through [ORAI AI Innovation Pilots](https://responsibleai.arizona.edu/tools-support/ai-innovation-pilots). The proposal will focus on approved AI use in EduCloud and a standardized, reusable AI-enabled classroom.

The ORAI program targets one working proof of concept within eight weeks of execution after assessment, with one pilot per faculty/staff member per year and essential data/access ready at entry. Fit, acceptance, staff assignments and infrastructure are unconfirmed. Drafting the proposal is next; it has not been submitted. An ORAI prototype does not provide semester-long operations or an ACCESS award.

## Key considerations

| Consideration | Evidence to seek |
| --- | --- |
| Activity and service fit | Interactive/batch needs, software, memory, concurrency and deadlines |
| Access and reliability | Eligible users, whole-term access, queues, quotas and fallback |
| People and cost | Support tasks/hours, maintainer, backup, recurring obligations and funding status |
| Data and software rights | Permitted data, licenses, retention, exports and recovery |
| Ownership and continuity | Institutional control, provider dependencies and an exit path |
| Evaluation and equity | Useful outcomes, accessibility, participation and missing perspectives |

The [working-group primers](primers.html) turn these into discussion questions. The [approaches](approaches.html) and [recommendations](recommendations.html) remain candidates for group review.

## Working-group next steps

By the **end of Fall 2026**, aim for preliminary drafts of the inventory, needs assessment, portfolio of approaches and recommendations. Refine and circulate within the college **early in Spring 2027**. Identify owner roles, a university channel for collecting needs, resource-owner checks and participation across faculty, students and technical staff.

Prioritize practical college actions while separating capacity, agreements and shared staffing questions that need university participation. [Working materials](supplemental.html#working-group-materials).

## Evidence and limitations

<span id="research-library"></span><span id="full-report-and-evidence"></span>

The historical ledger retains **181 source and verification records**, including unavailable sources and their limitations. Campus sources and review dates are attached to inventory entries. Dates of observation, policy effect and recheck are distinct; a page response does not test a signed-in account or available capacity.

The Arizona AI Assistant transition, planned $200/month Bedrock credit and supplied model prices come from **Wolfgang Jetner at ORAI, relayed by Greg Chism**. Recipient scope, renewal, overage rules, migration timing and campus API access still need confirmation. The screenshot was received October 19; its capture/effective date is unknown.

No college-wide survey totals, confirmed spare staffing, institutional endorsement or approved funding are inferred. The request tool generates a local brief; optional Luna drafting requires consent for public/synthetic information and does not submit a request to the working group.

[Source evidence](evidence.html) · [Chronological research archive](research-report.html) · [Original audit text](research-and-sources.txt) · [Grouped supplements](supplemental.html)
''')
    report=(public/'research-and-sources.txt').read_text()
    write('research-report.md','Chronological research archive','''<span id="full-research-report"></span>

The full historical research and planning record, organized into readable chapters. It includes earlier proposals and test stages that may have been superseded. Use the [current report](report.html) for the assessment and current boundaries.

[Download original audit text](research-and-sources.txt) · [Search source evidence](evidence.html) · [Supplement](supplemental.html)

Open a chapter to read it. The download preserves the original text; no historical trial is promoted to a completed deployment or college commitment.

'''+archive_html(report),True)
    # Detail pages remain addressable without crowding the main nav.
    for path in (generated/'pages').glob('*.md'):
        if path.stem in PRIMARY:continue
        text=path.read_text();lines=text.splitlines(keepends=True)
        for i,line in enumerate(lines):
            if line.startswith('# '):
                label='Historical archive' if path.stem=='research-report' else 'Supplemental reference'
                lines.insert(i+1,'\n<p class="guide-context">'+label+' · <a href="supplemental.html">Browse supplements</a> · <a href="report.html">Current report</a></p>\n')
                break
        path.write_text(''.join(lines))
