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
    for src in (ROOT / 'docs/education-compute').iterdir():
        if src.is_file():
            target = PORTABLE / src.name
            if src.suffix == '.html':
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
    copy(ROOT / 'site/covers/education-compute.png', Path('source/cover.png'))
    for src in sorted((ROOT / 'docs/education-compute').iterdir()):
        if src.is_file(): copy(src, Path('review/published-export') / src.name)
    for src in sorted(OUT.iterdir()):
        if src.is_dir():
            if src.name in ['codabench-research','federal-research']:
                for item in sorted(src.rglob('*')):
                    if item.is_file(): copy(item, Path('evidence') / src.name / item.relative_to(src))
            continue
        if src.name.endswith('-source.txt') or src.name == 'degree-home.html': target = Path('evidence/source-snapshots')
        elif src.name in ['evidence.json','degree-options.json','research-and-sources.txt','source-verification.json','service-source-verification.json']: target = Path('evidence')
        elif src.suffix in ['.py','.mjs','.js']: target = Path('review/checks') if src.name.startswith(('verify','inspect','live-controls','portable-check')) else Path('review/authoring-history')
        elif src.suffix == '.zip': target = Path('.')
        else: target = Path('review')
        copy(src, target / src.name)
    for name in ['build_compute_evidence.py','build_compute_resources.py','build_federal_compute.py','build_site.py','check_site.py','package_compute_review.py']:
        copy(ROOT / 'scripts' / name, Path('review/builders') / name)
    for src in sorted((ROOT / 'output/playwright').iterdir()):
        if src.is_file() and src.name.startswith(('education-compute-','repositories-','service-evidence-','codabench-','federal-')):
            copy(src, Path('review/screenshots') / src.name)
    manifest = dict(title='Teaching on Borrowed Compute', assembled='2026-10-10', refreshed=ledger.get('updated_at','2026-10-11'), source_records=len(ledger['evidence']), resource_comparisons=len(ledger['classroom_resource_options']), federal_families=len(ledger.get('federal_platform_map',[])),
                    public_release_at_assembly='2fe7387524d1d5403bef100aaa3da5a4f896c96c',
                    purpose='Complete local review snapshot; canonical authoring and publishing paths remain in the parent repository. See validation.json for latest release status.',
                    excluded=['output/education-compute/site-build (whole-site cache includes unrelated talks)'], files=files)
    (BUNDLE / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(f"Refreshed portable ZIP and {len(files)} gathered artifacts ({len(ledger['evidence'])} sources)")


if __name__ == '__main__':
    build()
