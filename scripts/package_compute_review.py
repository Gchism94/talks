#!/usr/bin/env python3
"""Refresh the portable educational-compute talk and its complete local review snapshot."""
import hashlib
import json
import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / 'output/education-compute'
BUNDLE = ROOT / 'education-compute'
PORTABLE = OUT / 'portable/teaching-on-borrowed-compute'


def build():
    ledger = json.loads((ROOT / 'docs/education-compute/evidence.json').read_text())
    PORTABLE.mkdir(parents=True, exist_ok=True)
    for src in (ROOT / 'docs/education-compute').rglob('*'):
        if src.is_file():
            target = PORTABLE / src.relative_to(ROOT / 'docs/education-compute')
            target.parent.mkdir(parents=True,exist_ok=True)
            if src.suffix in ['.html','.css']:
                text = src.read_text().replace('../assets/', 'assets/')
                text = text.replace('<span class="brand"><a href="../">← All talks</a></span>', '<span class="brand">Teaching on borrowed compute</span>')
                text = text.replace('<span class="brand"><a href="index.html">← Resource overview</a> · <a href="../">All talks</a></span>', '<span class="brand"><a href="index.html">← Resource overview</a></span>')
                target.write_text(text)
            else:
                shutil.copy2(src, target)
    for category in ['fonts', 'favicons']:
        shutil.copytree(ROOT / 'docs/assets' / category, PORTABLE / 'assets' / category, dirs_exist_ok=True)
    shutil.copy2(ROOT / 'site/covers/education-compute.png', PORTABLE / 'preview.png')
    start = PORTABLE / 'START-HERE.txt'
    text = (start.read_text() if start.exists() else 'TEACHING ON BORROWED COMPUTE\nOpen index.html for the working-group resource overview; talk.html contains the original presentation.\n').split('\nCODABENCH AND RESOURCE UPDATE')[0]
    text += '\nCODABENCH AND RESOURCE UPDATE | October 11, 2026\nSlide 3 adds a filterable Codabench & alternatives comparison. Open classroom-resources.html for all 13 resource comparisons and work boundaries; the degree comparison includes supplementary routes. Codabench provides free benchmark hosting and bounded CPU scoring, while code/GPU workers require separately supplied compute. CodaLab Competitions is a retired predecessor; EvalAI hosting is paid; ChaGrade readiness is unverified. The evidence ledger now contains ' + str(len(ledger['evidence'])) + ' records. This update does not reverify every October 8/10 policy.\n'
    if 'federal_platform_map' in ledger:
        text += '\nFEDERAL COMPUTE MAP | October 12, 2026\nOpen federal-compute.html for the interactive map of federally supported compute, data services, products and funding pathways. It covers '+str(len(ledger['federal_platform_map']))+' families, the six named 2026 IDSS projects including MESA, and eight missing layers. CSV/JSON exports are beside it. Slide 4 links to this reference. Federal development, current operating support, state subsidies and free approved use are distinct.\n'
    if 'classroom_assessment' in ledger:
        text += '\nCLASSROOM ROUTE ASSESSMENT | October 12, 2026\nOpen classroom-assessment.html for seven route/operations roles, a two-course 80-seat illustrative pilot, three interactive CPU sizing scenarios, optional fractional GPU accounting, seven readiness gates and unsent provider questions. JSON and capacity/readiness CSV exports are beside it. No allocation, signed-in entitlement or real classroom workload has been tested.\n'
    if 'pilot_program_summary' in ledger:
        text += '\nCOHESIVE PROGRAM AND PILOT PACKET | October 12, 2026\nStart with program.html for administrator, faculty and course-lead views. Open access-request.html for the unsubmitted request, pilot-plan.html for proposed INFO 521/LIS 671 components, budget.html for the support and funding plan and zero-cash/grant dependencies, readiness.html for thirteen planned/not-run checks; ACCESS CPU/GPU allocation as the classroom route, campus AWS only for CPU component tests, and free GPU benchmarks before piloting, and resource-library.html for the working tools. Report/evidence references are now grouped under report.html. Printable PDF and text/CSV/JSON downloads are included, alongside runnable DS/MLIS CPU tests, self-contained GPU notebooks and the ACCESS sizing helper (classroom-benchmarks.zip). No staff, money, course offering or provider capacity is approved by the site.\n'
    text += '\nCOHESIVE SITE REORGANIZATION | October 13, 2026\nStart at program.html for the core problem and solution. Six top-level sections: Overview, Staged plan (timeline.html), Classroom tools, Hours & funding, Report & evidence (report.html), and Talk. The six-stage timeline has keyboard navigation, key events, gates and shareable stage URLs. research-report.html preserves the entire text audit in a readable view; evidence.html keeps all 158 source records. Existing downloads and links remain available. No provider facts, awards, readiness status or benchmark results were promoted by this layout update.\n'
    text += '\nCLASSROOM 50 AND ARIZONA DESIGN | October 13, 2026\nclassroom50.html directly assesses the workable successor, external stewardship, organization control, unchanged Codespaces limits and pre-adoption checks. Source ledger: 163 records; 14 resource comparisons. The shared site and five-slide talk use Arizona navy, red, white and offline open-license typography inspired by infosci.arizona.edu. No adoption, grant, provider benchmark or integration is claimed.\n'
    text += '\nMODAL AND SIMILAR PLATFORMS | October 16, 2026\nOpen serverless-compute.html for nine provider assessments. The ledger now has 181 records and 22 resource comparisons. Modal has conditional monthly compute credits but requires a payment method; no purchases, accounts, provider jobs or grant applications were made. Preserve all zero-cash and ACCESS route constraints.\n'
    text += '\nPUMA CLASSROOM UPDATE | October 20, 2026\nCurrent HPC teaching policy permits Puma class groups. Research and classes share 150,000 CPU core-hours per PI/month; GPU jobs use that same CPU-based pool. The published standard ceiling is four GPUs and 3,290 CPUs per group, not reserved availability. No immediate start, assignment priority, individual student support or course reservation is promised. This supersedes the earlier Ocelote-only policy concern in the dated history below. Lynx/H200 is not available yet.\n'
    text += '\nREPORT SUMMARY OVERVIEW | October 19, 2026\nreport.html now opens with eight resource/status groups, a selected 2022–2026 loss/reduction history, a separately labeled Colab observation and upcoming OSF restrictions, plus the ACCESS response. All 181 records and detailed research links remain. Provider availability is not classroom readiness.\n'
    text += '\nCONCISE COMPUTE GUIDE | October 19, 2026\nprogram.html now uses a pinned Zensical guide with task-based navigation and client-side search. needs.html estimates research/classroom CPU core-hours, GPU device-hours, peak demand, storage and support, with text/JSON exports. publishing.html compares Zensical, Starlight and Quarto. Estimates are not measurements or awards. All 181 records and the five-slide deck remain.\n'
    text += '\nAI RESOURCES WORKING GROUP | October 19, 2026\nStart with program.html, inventory.html and deliverables.html. needs.html prepares a local qualitative brief; compute-estimator.html is optional. Draft inventory, needs framework, approaches, recommendations, working-session guide and Fall 2026 / early Spring 2027 milestones are included. CSV/JSON/text downloads do not contain collected responses or approved commitments. The original compute pilot and its constraints remain separate case-study material.\n'
    text += '\nCOLLEGE OF INFORMATION SCIENCE COMPUTING RESOURCES | October 19, 2026\nCurrent scope: Computing Resources Working Group, with Barney Maccabe as point person. Inventory: 33 entries (8 college, 19 university, 6 external), contacts/cost basis/access limits and dated sources. Campus HPC classroom permission needs clarification because the policy names retired Ocelote. DSI direct URLs failed verification; its published contact needs reconfirmation. needs.html offers local request drafts and optional public/synthetic AI Verde prompts; no LLM connection, response collection, API keys or paid inference is configured. Open computing-working-group-packet.txt for the current working packet. Legacy ai-* downloads remain aliases.\n'
    text += '\nDRAFTING ASSESSMENT AND POINT PEOPLE | October 19, 2026\nBarney Maccabe and Greg Chism are working-group point people; the college header link is Arizona navy. Browser inference worked in synthetic local tests, including a 360M worker with networking blocked after load. Both small-model candidates added unsupported details in examples, so no browser model is enabled on the public site. needs.html keeps the sourced request template and offers copy/download of a public/synthetic prompt for manual campus AI drafting. U of A GenAI advertises no-cost NetID access with early-access/data terms; AI Verde access and token budget need confirmation. No model service is connected and no key, charge or automated submission is required.\n'
    text += '\nOPTIONAL LUNA SERVICE AND CAMPUS TRANSITION | October 19, 2026\nEarlier entries above describe prior stages. needs.html now offers an explicit public/synthetic GPT-6 Luna rewrite through a server-side service; keys stay out of the browser. Current limits: 1,000 output tokens, 20 attempts/day, 200/month, five/network/day and a $1 monthly application reservation allowance at current rates. A private persistent ledger enforces reservations before calls; failures count and no automatic retry occurs. The local template and manual campus prompts remain. Wolfgang Jetner at ORAI, via Greg Chism, reports AI Verde will transition to Arizona AI Assistant with $200/month of Bedrock credit; campus-ai.html preserves the supplied twelve-model pricing snapshot and unconfirmed migration/credit terms. This site uses a separate direct OpenAI service, not campus credit. Hosting is separately metered. Source and operating instructions for the backend are in source/compute-drafter in the full local review; no runtime credential files are included.\n'
    text += '\nFOCUSED RESOURCE SITE | October 19, 2026\nPrimary pages: Overview (program.html), Resources (inventory.html), Primers (primers.html), Resource tool (needs.html), Report (report.html), Supplement (supplemental.html). report.html is the structured current assessment; research-report.html is the complete chronological archive in readable chapters. Earlier notices describe historical site layouts. The supplement groups working-group materials, platform references, the conditional instructional pilot, evidence and the talk. Existing URLs, source records, downloads and request safeguards are retained.\n'
    text += '\nLANDING PAGE AND NAVIGATION | October 20, 2026\nindex.html now opens the resource overview; program.html remains an alias. The original five-slide presentation is talk.html, linked under Supplement. Numeric slide hashes on the old root URL forward to the corresponding talk slide. The shared header omits Greg’s role; request and coordination materials retain it. Header and tabs stay together while scrolling. Earlier index.html talk references above describe the former routing.\n'
    text += '\nPLANS AND NEXT ORAI DRAFT | October 29, 2026\nGreg plans to draft an ORAI AI Innovation Pilot next. It is not submitted or accepted; no ORAI staff, ongoing operations or grant funding is committed. See the current overview, report and hours page.\n'
    start.write_text(text)
    archive = OUT / 'teaching-on-borrowed-compute.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for src in sorted(PORTABLE.rglob('*')):
            if src.is_file():
                z.write(src, 'teaching-on-borrowed-compute/' + src.relative_to(PORTABLE).as_posix())
    files = []
    def copy(src, rel):
        dst = BUNDLE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        files.append(dict(path=rel.as_posix(), original=src.relative_to(ROOT).as_posix(), bytes=dst.stat().st_size, sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))
    for src in sorted(PORTABLE.rglob('*')):
        if src.is_file(): copy(src, Path('talk') / src.relative_to(PORTABLE))
    copy(ROOT / 'education-compute.html', Path('source/education-compute.html'))
    for name in ['education-compute-pilot.json','education-compute-program.css','education-compute-program.js']:
        copy(ROOT / 'site' / name, Path('source') / name)
    copy(ROOT / 'site/covers/education-compute.png', Path('source/cover.png'))
    for src in sorted((ROOT/'site/compute-guide').rglob('*')):
        if src.is_file() and not any(x in src.parts for x in ['.cache','_site','__pycache__']): copy(src,Path('source/compute-guide')/src.relative_to(ROOT/'site/compute-guide'))
    for src in sorted((ROOT / 'docs/education-compute').rglob('*')):
        if src.is_file(): copy(src, Path('review/published-export') / src.relative_to(ROOT / 'docs/education-compute'))
    for src in sorted((ROOT/'benchmarks/education-compute').iterdir()):
        if src.is_file(): copy(src,Path('source/benchmarks')/src.name)
    for src in sorted(OUT.iterdir()):
        if src.is_dir():
            if src.name in ['codabench-research','federal-research','assessment-research','pilot-research']:
                for item in sorted(src.rglob('*')):
                    if item.is_file(): copy(item, Path('evidence') / src.name / item.relative_to(src))
            continue
        if src.name.endswith('-source.txt') or src.name == 'degree-home.html': target = Path('evidence/source-snapshots')
        elif src.name in ['evidence.json','degree-options.json','research-and-sources.txt','source-verification.json','service-source-verification.json']: target = Path('evidence')
        elif src.suffix in ['.py','.mjs','.js']: target = Path('review/checks') if src.name.startswith(('verify','inspect','live-controls','portable-check')) else Path('review/authoring-history')
        elif src.suffix == '.zip': target = Path('.')
        else: target = Path('review')
        copy(src, target / src.name)
    # Explicit backend source allowlist: never include runtime secrets or dependencies.
    for name in ['package.json','package-lock.json','vercel.json','README.md','init-ledger.mjs','data/inventory.json','lib/contracts.mjs','lib/quota.mjs','lib/handler.mjs','lib/blob-store.mjs','api/draft.mjs','test/service.test.mjs','api/requests.mjs','api/review.mjs','init-intake.mjs','lib/intake.mjs','lib/intake-store.mjs','test/intake.test.mjs','public/review/index.html','public/review/review.js','public/review/review.css']:
        copy(ROOT/'services/compute-drafter'/name,Path('source/compute-drafter')/name)
    for name in ['build_compute_evidence.py','build_compute_resources.py','build_federal_compute.py','build_classroom_assessment.py','build_compute_program.py','compute_program_views.py','compute_classroom50.py','compute_serverless.py','compute_report_overview.py','build_compute_guide.py','compute_working_group.py','compute_site_focus.py','test_working_group_needs.cjs','test_compute_request_llm.py','test_compute_needs.cjs','build_compute_pilot_pdfs.py','build_compute_benchmarks.py','build_site.py','check_site.py','package_compute_review.py']:
        copy(ROOT / 'scripts' / name, Path('review/builders') / name)
    for src in sorted((ROOT / 'output/playwright').iterdir()):
        if src.is_file() and src.name.startswith(('education-compute-','repositories-','service-evidence-','codabench-','federal-','assessment-','pilot-')):
            copy(src, Path('review/screenshots') / src.name)
    manifest = dict(title='Teaching on Borrowed Compute', assembled='2026-10-10', refreshed=ledger.get('updated_at','2026-10-11'), source_records=len(ledger['evidence']), resource_comparisons=len(ledger['classroom_resource_options']), federal_families=len(ledger.get('federal_platform_map',[])), assessment_roles=len(ledger.get('classroom_assessment',{}).get('providers',[])),
                    public_release_at_assembly='2fe7387524d1d5403bef100aaa3da5a4f896c96c',
                    purpose='Complete local review snapshot; canonical authoring and publishing paths remain in the parent repository. See validation.json for latest release status.',
                    excluded=['output/education-compute/site-build (whole-site cache includes unrelated talks)'], files=files)
    (BUNDLE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"Refreshed portable ZIP and {len(files)} gathered artifacts ({len(ledger['evidence'])} sources)")


if __name__ == '__main__':
    build()
