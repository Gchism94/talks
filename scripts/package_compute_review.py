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
                target.write_text(text)
            else:
                shutil.copy2(src, target)
    for category in ['fonts', 'favicons']:
        shutil.copytree(ROOT / 'docs/assets' / category, PORTABLE / 'assets' / category, dirs_exist_ok=True)
    shutil.copy2(ROOT / 'site/covers/education-compute.png', PORTABLE / 'preview.png')
    start = PORTABLE / 'START-HERE.txt'
    text = start.read_text().split('\nCODABENCH AND RESOURCE UPDATE')[0]
    text += '\nCODABENCH AND RESOURCE UPDATE | October 11, 2026\nSlide 3 adds a filterable Codabench & alternatives comparison. Open classroom-resources.html for all 13 resource comparisons and work boundaries; the degree comparison includes supplementary routes. Codabench provides free benchmark hosting and bounded CPU scoring, while code/GPU workers require separately supplied compute. CodaLab Competitions is a retired predecessor; EvalAI hosting is paid; ChaGrade readiness is unverified. The evidence ledger now contains ' + str(len(ledger['evidence'])) + ' records. This update does not reverify every October 8/10 policy.\n'
    if 'federal_platform_map' in ledger:
        text += '\nFEDERAL COMPUTE MAP | October 12, 2026\nOpen federal-compute.html for the interactive map of federally supported compute, data services, products and funding pathways. It covers '+str(len(ledger['federal_platform_map']))+' families, the six named 2026 IDSS projects including MESA, and eight missing layers. CSV/JSON exports are beside it. Slide 4 links to this reference. Federal development, current operating support, state subsidies and free approved use are distinct.\n'
    if 'classroom_assessment' in ledger:
        text += '\nCLASSROOM ROUTE ASSESSMENT | October 12, 2026\nOpen classroom-assessment.html for seven route/operations roles, a two-course 80-seat illustrative pilot, three interactive CPU sizing scenarios, optional fractional GPU accounting, seven readiness gates and unsent provider questions. JSON and capacity/readiness CSV exports are beside it. No allocation, signed-in entitlement or real classroom workload has been tested.\n'
    if 'pilot_program_summary' in ledger:
        text += '\nCOHESIVE PROGRAM AND PILOT PACKET | October 12, 2026\nStart with program.html for administrator, faculty and course-lead views. Open access-request.html for the unsubmitted request, pilot-plan.html for proposed INFO 521/LIS 671 components, budget.html for the ten-hour weekly effort planner and zero-cash/grant dependencies, readiness.html for thirteen planned/not-run checks; ACCESS CPU/GPU allocation as the classroom route, campus AWS only for CPU component tests, and free GPU benchmarks before piloting, and resource-library.html for the working tools. Report/evidence references are now grouped under report.html. Printable PDF and text/CSV/JSON downloads are included, alongside runnable DS/MLIS CPU tests, self-contained GPU notebooks and the ACCESS sizing helper (classroom-benchmarks.zip). No staff, money, course offering or provider capacity is approved by the site.\n'
    text += '\nCOHESIVE SITE REORGANIZATION | October 13, 2026\nStart at program.html for the core problem and solution. Six top-level sections: Overview, Staged plan (timeline.html), Classroom tools, Hours & funding, Report & evidence (report.html), and Talk. The six-stage timeline has keyboard navigation, key events, gates and shareable stage URLs. research-report.html preserves the entire text audit in a readable view; evidence.html keeps all 158 source records. Existing downloads and links remain available. No provider facts, awards, readiness status or benchmark results were promoted by this layout update.\n'
    text += '\nCLASSROOM 50 AND ARIZONA DESIGN | October 13, 2026\nclassroom50.html directly assesses the workable successor, external stewardship, organization control, unchanged Codespaces limits and pre-adoption checks. Source ledger: 163 records; 14 resource comparisons. The shared site and five-slide talk use Arizona navy, red, white and offline open-license typography inspired by infosci.arizona.edu. No adoption, grant, provider benchmark or integration is claimed.\n'
    text += '\nMODAL AND SIMILAR PLATFORMS | October 16, 2026\nOpen serverless-compute.html for nine provider assessments. The ledger now has 181 records and 22 resource comparisons. Modal has conditional monthly compute credits but requires a payment method; no purchases, accounts, provider jobs or grant applications were made. Preserve all zero-cash, ten-hour and ACCESS route constraints.\n'
    text += '\nREPORT SUMMARY OVERVIEW | October 19, 2026\nreport.html now opens with eight resource/status groups, a selected 2022–2026 loss/reduction history, a separately labeled Colab observation and upcoming OSF restrictions, plus the ACCESS response. All 181 records and detailed research links remain. Provider availability is not classroom readiness.\n'
    text += '\nCONCISE COMPUTE GUIDE | October 19, 2026\nprogram.html now uses a pinned Zensical guide with task-based navigation and client-side search. needs.html estimates research/classroom CPU core-hours, GPU device-hours, peak demand, storage and support, with text/JSON exports. publishing.html compares Zensical, Starlight and Quarto. Estimates are not measurements or awards. All 181 records and the five-slide deck remain.\n'
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
    for name in ['build_compute_evidence.py','build_compute_resources.py','build_federal_compute.py','build_classroom_assessment.py','build_compute_program.py','compute_program_views.py','compute_classroom50.py','compute_serverless.py','compute_report_overview.py','build_compute_guide.py','test_compute_needs.cjs','build_compute_pilot_pdfs.py','build_compute_benchmarks.py','build_site.py','check_site.py','package_compute_review.py']:
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
