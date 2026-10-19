"""Working-group deliverables and local needs discovery, separate from the compute pilot."""
import csv,html,json,shutil
from pathlib import Path
E=html.escape

def build(root,generated,public,write):
    src=root/'site/compute-guide';g=json.loads((src/'working-group.json').read_text())
    # Preserve the existing compute calculator as an optional specialist tool.
    old=generated/'pages/needs.md';text=old.read_text().replace('# Scope your computing needs','# Optional compute estimate')
    text=text.replace('Estimate a research project or classroom workload before asking for resources.','Start with the <a href="needs.html">short needs brief</a>. Use this optional calculator only when you can estimate the workload; unknown technical quantities belong in the brief, not as invented numbers.')
    text=text.replace('<form class="needs-form" id="needsForm">','<form class="needs-form" id="needsForm"><input type="hidden" name="context" value="working-group">')
    text=text.replace('Greg hours / week for this scope','Potential technical-support hours / week').replace('Inside ten total weekly hours for everything.','Scope-specific estimate; no college staffing capacity is assumed.')
    (generated/'pages/compute-estimator.md').write_text(text)
    # Keep the pilot's six-stage plan at a stable, explicit case-study address.
    shutil.copy2(generated/'pages/timeline.md',generated/'pages/pilot-stages.md')
    for name in ['pilot-plan','pilot-stages','access-request','budget','readiness','gpu-benchmark','classroom-assessment']:
        path=generated/'pages'/f'{name}.md';text=path.read_text();parts=text.split('\n',1)
        note='\n<div class="guide-note"><strong>Supporting compute pilot.</strong> These DS/MLIS proposals retain their own $0 cash and Greg’s ten-hour weekly envelope. They are not college-wide capacity findings or the working group’s selected solution. <a href="deliverables.html">Return to working-group deliverables →</a></div>\n'
        path.write_text(parts[0]+'\n'+note+parts[1])
    intro='''**Seeded draft — verify with resource owners.** This inventory includes documented routes and explicitly unverified college entries. It is not a complete college asset register or proof of signed-in access, available staff or spare capacity.

[Download CSV](ai-resource-inventory.csv) · [Download JSON](ai-working-group.json) · [Describe a missing resource or need](needs.html)

Campus sources below were reviewed October 19, 2026. National/provider entries inherit the earlier compute-ledger reviews and need rechecking before adoption. A public page is evidence of a documented route; the group still needs owner confirmation of college access, support and funding.

'''
    cards='<div data-directory><div class="guide-filter"><label>Search inventory<input type="search" placeholder="Try RSE, datasets, campus, GPU or support"></label><label>Resource type<select><option value="all">All types</option>'+''.join('<option>'+E(c)+'</option>' for c in sorted({r['category'] for r in g['inventory']}))+'</select></label><p role="status" aria-live="polite">15 entries</p></div><div class="guide-directory">'
    for r in g['inventory']:
        source=('<a href="'+E(r['source'],quote=True)+'">Source / access route ↗</a>') if r['source'] else 'Resource owner/source not yet identified.'
        cards+='<article class="guide-resource" data-resource data-category="'+E(r['category'])+'" id="'+E(r['id'])+'"><span class="guide-tag">'+E(r['level']+' · '+r['status'])+'</span><h3>'+E(r['name'])+'</h3><p><strong>Access:</strong> '+E(r['access'])+'</p><p><strong>Cost:</strong> '+E(r['cost'])+'</p><p><strong>Support:</strong> '+E(r['support'])+'</p><details><summary>Limitations, funding and evidence</summary><p>'+E(r['limits'])+'</p><p><strong>Funding:</strong> '+E(r['funding'])+'</p><p>'+source+'</p><p><strong>Review basis:</strong> '+E(r['checked'])+'</p><p>'+E(r['next_action'])+'</p></details></article>'
    write('inventory.md','Resource inventory',intro+cards+'</div><noscript><p>All entries are shown; filtering requires JavaScript.</p></noscript></div>\n\n## Keep the inventory useful\n\nConfirm access, owner, support window, funding, costs and limits before changing an entry to verified. Record missing resources as unknown, not unavailable. Use the [detailed platform directory](resource-library.html) for further comparisons.')
    phases=''
    for i,stage in enumerate(g['timeline'],1):
        phases+='<section class="guide-step"><div class="guide-step-num">'+str(i).zfill(2)+'</div><div><span class="guide-tag">'+E(stage['when'])+'</span><h2>'+E(stage['title'])+'</h2><p>'+E(stage['work'])+'</p><p><strong>Output:</strong> '+E(stage['output'])+'</p></div></section>'
    write('timeline.md','Working-group milestones','''The working group aims to draft **all four deliverables by the end of the Fall 2026 semester**, then refine and circulate them within the college **early in Spring 2027**. These are planning windows, not scheduled meetings or award dates.

'''+phases+'\n\n[Review deliverables](deliverables.html) · [Working-session guide](working-session.html)\n\n## Supporting compute-pilot sequence\n\nThe [separate CPU/GPU pilot stages](pilot-stages.html) depend on measurements, resource approval and classroom checks. Those gates do not define the working group’s semester deadlines.')
    path=generated/'pages/degree-options.md';path.write_text(path.read_text().replace('Nine Information Science degrees are in scope; cyber programs are excluded.','This earlier nine-degree comparison excludes cyber programs. The working group’s needs assessment covers the college and is not limited to this historical comparison.',1))
    # Existing history/resource pages remain valid, but no longer imply the pilot is
    # the entire college strategy.
    path=generated/'pages/resource-library.md';path.write_text(path.read_text().replace('# Find a resource','# Detailed platform directory',1).replace('Start with the work you need to do.','For college and university routes, start with the [working-group inventory](inventory.html). This detailed directory supports comparison and the compute case study. Start with the work you need to do.',1))
    fields=[('scope','Activity type',['Research','Instruction','Both research and instruction']),('stage','Current or anticipated',['Current need','Anticipated / emerging need']),('timing','When needed',['This semester','Early Spring 2027','Within 12 months','Not yet known']),('priority','Impact',['Work is blocked','Work is limited or difficult','Exploratory opportunity']),('data','Data involved',['Not yet known','Public / synthetic','Internal / student records','Restricted / regulated']),('budget','Funding position',['Not yet known','No funds identified','Existing resources identified; terms to verify','Confirmed funding; permitted use to verify'])]
    form='<form id="workingNeeds" class="needs-form"><label>What are you trying to do? <span class="guide-required">(required)</span><textarea name="activity" required maxlength="240" rows="2" placeholder="Describe an activity, not private project data or student information."></textarea></label><fieldset><legend>What resources would help? <span class="guide-required">(choose at least one)</span></legend><div class="working-checks">'
    types=['Hardware / compute','Software / models','Data / stewardship','Cloud / hosting','RSE / engineering','Technical support / training','Collaboration / shared services']
    form+=''.join('<label><input type="checkbox" name="resources" value="'+E(t)+'">'+E(t)+'</label>' for t in types)+'</div></fieldset><div class="needs-grid">'
    for key,label,choices in fields:form+='<label>'+label+'<select name="'+key+'">'+''.join('<option>'+E(t)+'</option>' for t in choices)+'</select></label>'
    form+='</div><fieldset><legend>What is getting in the way?</legend><div class="working-checks">'+''.join('<label><input type="checkbox" name="barriers" value="'+t+'">'+t+'</label>' for t in ['Access / eligibility','Capacity / reliability','Costs / funding','Software / data rights','Skills / onboarding','Staff / support time','Not yet known'])+'</div></fieldset>'
    form+='<details><summary>Optional detail · leave unknown quantities blank</summary><div class="needs-grid"><label>People or independent groups<input name="people" type="number" min="1" step="1" placeholder="Unknown"></label><label>Potential support hours/week<input name="hours" type="number" min="0" step="0.5" placeholder="Unknown"></label><label>Collaboration opportunity<select name="collaboration"><option>Not yet known</option><option>Within the college</option><option>Across the university</option><option>External partner / shared infrastructure</option></select></label></div>'
    for key,label,hint in [('requirements','Software, models, data or environment requirements','What must the workflow be able to do?'),('skills','RSE skills, technical support or training','Which tasks, expertise and support windows matter?'),('existing','Existing resource or workaround','What works, and where does it fall short?')]:form+='<label>'+label+'<textarea name="'+key+'" rows="2" maxlength="600" placeholder="'+hint+'"></textarea></label>'
    form+='</details><div class="guide-actions"><button class="guide-button" id="prepareWorkingBrief" type="submit" disabled>Prepare my brief</button><button class="needs-secondary" id="clearWorkingNeed" type="button">Clear fields</button></div></form><p id="workingError" class="needs-error" role="alert"></p><p id="workingStatus" role="status">Nothing has been submitted or saved.</p><section id="workingResults" class="needs-results" hidden><h2 id="workingResultsTitle" tabindex="-1">Your local needs brief</h2><p id="workingDraftType" class="guide-tag"></p><h3 id="workingActivity"></h3><p id="workingSummary"></p><p id="workingTypes"></p><p><strong>Barriers:</strong> <span id="workingBarriers"></span></p><p id="workingCapacity"></p><h3>Next steps to review</h3><ul id="workingNext"></ul><div class="guide-actions"><button class="guide-button" type="button" data-working-export="text" disabled>Download brief</button><button class="needs-secondary" type="button" data-working-export="json" disabled>Download JSON</button></div><p>Share the download through the group’s agreed university channel. No collection channel is configured on this public site.</p></section>'
    write('needs.md','Describe a resource need','''Start with the activity and what is getting in the way. **You do not need to know GPU hours or a budget.** Unknown quantities can stay unknown.

This tool works locally. It does not submit, collect or save responses. Use non-identifying descriptions; keep private research, student records and confidential staffing information out of this public planning tool.

<div class="guide-actions"><button class="needs-secondary" type="button" data-working-example="data">Try a software/data example</button><button class="needs-secondary" type="button" data-working-example="classroom">Try a classroom example</button></div>

'''+form+'''

## If technical sizing would help

Use the [optional compute estimator](compute-estimator.html) for CPU/GPU, concurrency and storage assumptions. It is one attachment to the need, not a requirement for participating. Measured demand and provider access still need confirmation.

<noscript><p class="guide-note">Local brief generation needs JavaScript. You can still use the <a href="ai-needs-register.csv">blank needs register</a> to record the activity, resource types, barriers, timing and unknowns, then share it through the agreed university channel.</p></noscript>

[How needs will be assessed](needs-assessment.html) · [Working-group deliverables](deliverables.html)''')
    # Downloadable draft artifacts. No respondent or internal personnel data.
    (public/'ai-working-group.json').write_text(json.dumps(g,indent=2)+'\n')
    def csvfile(name,keys,rows):
        with (public/name).open('w',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=keys,lineterminator='\n');writer.writeheader();writer.writerows(rows)
    csvfile('ai-resource-inventory.csv',list(g['inventory'][0]),g['inventory'])
    csvfile('ai-needs-register.csv',['need_id','activity','scope','current_or_anticipated','resource_types','barriers','people_or_groups','needed_by','impact','requirements','skills_support','potential_support_hours_week','funding_status','existing_workaround','evidence_basis','review_status'],[])
    csvfile('ai-recommendations-template.csv',['action','college_or_university','problem_evidence','users_served','owner_role','dependencies','effort_hours','recurring_obligations','funding_status','success_measure','review_point','decision_status'],[])
    packet=g['title']+'\nDRAFT WORKING PACKET | October 19, 2026\n\n'+g['scope']+'\n'+g['charter_status']+'\n\nOBJECTIVES\n'+'\n'.join(g['objectives'])+'\n\nDELIVERABLES\n'
    for r in g['deliverables']:packet+='\n'+r['name']+' | '+r['status']+'\nPreliminary draft: '+r['draft']+'\n'+r['url']+'\n'
    packet+='\nMILESTONES\n'
    for r in g['timeline']:packet+='\n'+r['when']+' | '+r['title']+'\n'+r['work']+'\nOutput: '+r['output']+'\n'
    packet+='\nUSE AND REVIEW\nThe site does not collect needs responses. Agree an approved university channel, deliverable owner roles and review process. No group endorsements, college-wide needs totals, staff availability or funding are assumed. The separate pilot retains its own zero-cash/ten-hour constraints.\n'
    packet+='\nSEEDED RESOURCE INVENTORY\n'
    for item in g['inventory']:packet+='\n'+item['name']+' | '+item['level']+' | '+item['status']+'\nAccess: '+item['access']+'\nCost: '+item['cost']+'\nSupport: '+item['support']+'\nLimits: '+item['limits']+'\nFunding: '+item['funding']+'\nSource: '+(item['source'] or 'Not yet identified')+'\nReview: '+item['checked']+'\n'
    for name in ['needs-assessment','approaches','recommendations','working-session']:packet+='\n'+(src/'pages'/f'{name}.md').read_text()+'\n'
    packet=packet.rstrip()+'\n'
    (public/'ai-working-group-packet.txt').write_text(packet)
    report=(public/'research-and-sources.txt').read_text()+'\n\nAI RESOURCES WORKING GROUP | October 19, 2026\n'+packet+'\nCAMPUS INVENTORY SOURCES\n'+'\n'.join(r['name']+' | '+r['source']+' | '+r['checked'] for r in g['inventory'][:6])+'\n'
    (public/'research-and-sources.txt').write_text(report);(root/'output/education-compute/research-and-sources.txt').write_text(report)
    write('research-report.md','Full research report','The earlier compute research is a supporting case study. The working-group context and campus inventory references are appended below. [Working-group deliverables](deliverables.html) · [Download complete text](research-and-sources.txt)\n\n<div class="guide-audit"><details><summary>Open the complete research report</summary><pre>'+E(report)+'</pre></details></div>',True)
    evidence=generated/'pages/evidence.md';evidence.write_text(evidence.read_text().replace('181 primary-source and verification records.','181 compute-history source and verification records. Current working-group campus sources are linked in the [resource inventory](inventory.html).',1))
