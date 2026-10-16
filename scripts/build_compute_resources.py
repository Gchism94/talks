#!/usr/bin/env python3
"""Render reviewed classroom resources into the talk and standalone references."""
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'docs/education-compute'


def resource_content(data, interactive=False):
    esc = html.escape
    controls = ('<div class="resource-filters" role="group" aria-label="Filter classroom resources">' +
                ''.join(f'<button data-resource-filter="{key}" aria-pressed="{str(key == "all").lower()}">{label}</button>'
                        for key, label in [('all', 'All'), ('manage', 'Classroom workflow'), ('cloud', 'Cloud credits & APIs'), ('evaluate', 'Benchmark & grade'), ('develop', 'Notebooks'), ('demo', 'GPU demos'), ('legacy', 'Retired')]) + '</div>') if interactive else ''
    cards = ''.join('<article class="resource-card" data-resource-category="' + esc(r['category']) + '">' +
                    '<p class="resource-tag">' + esc(r['access']) + '</p><h3>' + esc(r['name']) + '</h3>' +
                    '<p>' + esc(r['fit']) + '</p><p class="resource-limit"><strong>Boundary:</strong> ' + esc(r['limits']) + '</p>' +
                    '<p class="resource-refs">' + ' · '.join('<a target="_blank" rel="noopener noreferrer" href="' + esc(data['evidence'][k]['url'], quote=True) + '">' + esc(data['evidence'][k]['title']) + '</a>' for k in r['sources']) + '</p></article>'
                    for r in data['classroom_resource_options'])
    return '<p class="source-intro">Classroom 50 and Codespaces checked October 13; Modal and eight similar platforms checked October 16; earlier resource comparisons retain October 11 dates. <a href="serverless-compute.html">Cloud credits and paid-service boundaries ↗</a>. Free access supports particular assignments; it does not reserve a whole class or fund a semester service.</p><div class="resource-flow" aria-label="Classroom workflow"><div><strong>1 · Develop</strong><span>CPU / notebook / GPU quota</span></div><b aria-hidden="true">→</b><div><strong>2 · Submit</strong><span>Predictions or packaged code</span></div><b aria-hidden="true">→</b><div><strong>3 · Evaluate</strong><span>Scoring queue + leaderboard</span></div></div><p class="resource-callout"><strong>Codabench:</strong> free competition hosting and a shared CPU queue with a 20-minute job cap. Organizers supply their own queue for code submissions. GPU workers require separately supplied compute.</p>' + controls + '<div class="resource-grid">' + cards + '</div><p class="resource-callout"><strong>Proposed pilot:</strong> develop in a bounded notebook environment; evaluate approved assignments through a Codabench queue attached to reviewed ACCESS compute where permitted. Budget operators, isolated submission workers, durable storage and exports separately. Validate scheduling, network/container rules and real class load before promising this route. Keep code, scoring bundles, submissions and results portable; a leaderboard is not the full course grade.</p>'


RESOURCE_CSS = '''
.resource-filters{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0}.resource-filters button{font-size:14px;padding:8px 12px}.resource-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.resource-card{border:1px solid var(--line,#c5c3ba);border-radius:8px;padding:20px;min-width:0}.resource-card[hidden]{display:none}.resource-card h3{font-size:27px;margin:8px 0 14px}.resource-card p{font-size:15px;line-height:1.55;margin:10px 0}.resource-card .resource-tag{font-size:12px;color:var(--blue,#274fa3);font-weight:650}.resource-card .resource-limit{border-top:1px solid var(--line,#c5c3ba);padding-top:12px}.resource-card .resource-refs{font-size:12px;overflow-wrap:anywhere}.resource-flow{display:grid;grid-template-columns:1fr auto 1fr auto 1fr;gap:10px;align-items:center;margin:22px 0}.resource-flow div{border-top:3px solid var(--blue,#274fa3);padding:12px 8px}.resource-flow strong,.resource-flow span{display:block}.resource-flow strong{font-size:19px}.resource-flow span{font-size:13px;margin-top:7px}.resource-callout{font-size:16px;line-height:1.6;padding:16px 18px;border-left:3px solid var(--blue,#274fa3);background:#274fa30a;margin:20px 0}.resource-links{display:flex;gap:10px;flex-wrap:wrap}.resource-links button{font-size:13px;padding:5px 10px}@media(max-width:700px){.resource-grid{grid-template-columns:1fr}.resource-flow{gap:4px}.resource-flow strong{font-size:16px}.resource-flow span{font-size:11px}}@media print{.resource-grid{display:block}.resource-card{break-inside:avoid;margin-bottom:12px}.resource-filters{display:none}}
'''


def degree_content(data):
    esc = html.escape
    rows = ''.join('<tr><th scope="row"><a href="' + esc(d['url'], quote=True) + '">' + esc(d['name']) + '</a></th><td>' + esc(' + '.join(data['platforms'][k]['name'] for k in d['tools'])) + '</td><td>' + esc(d['good']) + '</td><td>' + esc(d['supplement']) + '</td><td>' + esc(d['limit'] + ' ' + d['handoff']) + '</td></tr>' for d in data['degree_options'])
    ledger = ''.join('<p><strong>' + esc(p['name']) + ' · ' + esc(p['kind']) + '</strong><br>' + esc(p['quota'] + ' ' + p['detail']) + ' <a href="' + esc(p['url'], quote=True) + '">Provider ↗</a></p>' for p in data['platforms'].values())
    return '<p class="source-intro">Nine current non-cyber UArizona InfoSci degrees. Assignment-level recommendations; no free provider replaces an entire degree. Original degree mapping checked October 8; supplementary resources checked October 11, 2026.</p><div class="degree-table-scroll"><table class="degree-table"><thead><tr><th>Degree</th><th>Free starting point</th><th>Suitable work</th><th>Optional benchmark / demo route</th><th>Boundary and next step</th></tr></thead><tbody>' + rows + '</tbody></table></div><div class="degree-platform-ledger">' + ledger + '<p><strong>Codabench:</strong> competition hosting and bounded CPU scoring, with organizer-supplied workers for code / GPUs. <a href="classroom-resources.html">Compare every researched resource and its limits ↗</a>.</p><p>Use public or institution-approved teaching data. Check account eligibility, actual quota, software/data fit, simultaneous class access, exports and operating costs before adoption.</p></div>'


def standalone(title, content, css=''):
    return '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + html.escape(title) + '</title><link rel="icon" href="../assets/favicons/talk.svg" type="image/svg+xml"><link rel="icon" href="../assets/favicons/talk-32.png" type="image/png" sizes="32x32"><link rel="apple-touch-icon" href="../assets/favicons/talk-180.png" sizes="180x180"><style>body{font:17px/1.55 system-ui;margin:0;background:#f3eddf;color:#292b36}main{max-width:1180px;margin:auto;padding:35px 24px 60px}a{color:#274fa3}h1{font-size:clamp(30px,5vw,48px);line-height:1.15}table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:15px;text-align:left;vertical-align:top;border-bottom:1px solid #aaa;min-width:190px}.degree-table-scroll{overflow:auto}.degree-platform-ledger{margin-top:30px}@media print{body{font-size:11px}main{padding:0}td,th{min-width:0;padding:8px}tr{break-inside:avoid}}' + RESOURCE_CSS + css + '</style></head><body><main><p><a href="index.html#3">← Talk</a> · <a href="evidence.html">Evidence appendix</a></p><h1>' + html.escape(title) + '</h1>' + content + '</main></body></html>'


def build():
    data = json.loads((DEST / 'evidence.json').read_text())
    source = ROOT / 'education-compute.html'
    text = source.read_text()
    text = re.sub(r'const evidence=.*?;\n(?=const changes=)', lambda m: 'const evidence=' + json.dumps(data['evidence'], ensure_ascii=False) + ';\n', text, flags=re.S)
    text = re.sub(r'const changes=.*?;\n', lambda m: 'const changes=' + json.dumps(data['changes'], ensure_ascii=False) + ';\n', text, count=1, flags=re.S)
    text = re.sub(r'const degrees=.*?;\n(?=function platformIcon)', lambda m: 'const degrees=' + json.dumps(data['degree_options'], ensure_ascii=False) + ',platforms=' + json.dumps(data['platforms'], ensure_ascii=False) + ';\n', text, flags=re.S)
    resources = resource_content(data, interactive=True)
    degree = degree_content(data)
    text = re.sub(r'(<div id="resourcesBody">).*?(</div><!-- /resourcesBody -->)', lambda m: m[1] + resources + m[2], text, flags=re.S)
    text = re.sub(r"\$\('degreesBody'\)\.innerHTML=.*?;\n(?=\$\('degreesBtn'\))", lambda m: "$('degreesBody').innerHTML=" + json.dumps(degree, ensure_ascii=False) + ';\n', text, flags=re.S)
    repo_articles = ''.join('<article><h3>' + html.escape(r['title']) + '</h3><p>' + html.escape(r['body']) + '</p><p class="owner">' + html.escape(r['owner']) + '</p></article>' for r in data['repository_plan'])
    text = re.sub(r'(<div class="repo-plan">).*?(</div><p class="repo-plan-note">)', lambda m: m[1] + repo_articles + m[2], text, flags=re.S)
    repository = DEST / 'repository-plan.html'
    repo_text = re.sub(r'(<div class="repo-plan">).*?(</div><p class="repo-plan-note">)', lambda m: m[1] + repo_articles + m[2], repository.read_text(), flags=re.S)
    repo_text = repo_text.replace('updated October 10, 2026', 'Classroom 50 consideration updated October 13, 2026')
    repository.write_text(repo_text)
    source.write_text(text)
    (DEST / 'classroom-resources.html').write_text(standalone('Codabench & classroom alternatives', resource_content(data)))
    (DEST / 'degree-options.html').write_text(standalone('Free classroom options by degree', degree))
    print(f"Built {len(data['classroom_resource_options'])} resource comparisons and nine-degree reference")


if __name__ == '__main__':
    build()
