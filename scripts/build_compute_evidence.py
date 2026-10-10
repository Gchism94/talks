#!/usr/bin/env python3
"""Build the teaching-compute evidence appendix from its reviewed JSON ledger."""
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEST = ROOT / 'docs/education-compute'


def build():
    data = json.loads((DEST / 'evidence.json').read_text())
    evidence = data['evidence']
    esc = html.escape

    def refs(keys):
        return ' · '.join(f'<a href="#{esc(k)}">{esc(evidence[k]["title"])}</a>' for k in keys)

    def cards(rows):
        return ''.join('<article class="finding"><p class="tag">' + esc(r['status']) +
                       '</p><h3>' + esc(r['title']) + '</h3><p class="date">' + esc(r['date']) +
                       '</p><p>' + esc(r['finding']) + '</p><p class="boundary">' + esc(r['boundary']) +
                       '</p><p class="refs">' + refs(r['sources']) + '</p></article>' for r in rows)

    options = ''.join('<tr><th scope="row">' + esc(r['platform']) + '</th><td>' + esc(r['fit']) +
                      '</td><td>' + esc(r['limits']) + '</td><td>' + refs(r['sources']) + '</td></tr>'
                      for r in data['hosting_database_options'])
    plan = ''.join('<li><h3>' + esc(r['title']) + '</h3><p>' + esc(r['body']) +
                   '</p><p class="date">' + esc(r['owner']) + '</p></li>'
                   for r in data['service_continuity_plan'])
    ledger = ''.join('<details id="' + esc(k) + '"><summary>' + esc(e['title']) +
                     '</summary><p class="date">' + esc(e['date']) + ' · ' + esc(e['quality']) +
                     '</p><p>' + esc(e['claim']) + '</p><p><strong>Scope:</strong> ' + esc(e['scope']) +
                     '</p><p><a href="' + esc(e['url'], quote=True) +
                     '" target="_blank" rel="noopener noreferrer">' + esc(e.get('link_label', 'Read source ↗')) + '</a></p></details>'
                     for k, e in evidence.items())
    counts = f'{len(evidence)} evidence records · five-slide talk · checked October 10, 2026'
    page = '''<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Evidence appendix · Teaching on Borrowed Compute</title>
<link rel="icon" href="../assets/favicons/talk.svg" type="image/svg+xml">
<style>
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f4efe3;color:#282c37;font:18px/1.55 system-ui,sans-serif}main{max-width:1180px;margin:auto;padding:40px 28px 80px}header{background:#202938;color:#fff;padding:34px;border-radius:18px}h1{font-size:clamp(32px,5vw,58px);line-height:1.08;max-width:900px;margin:15px 0}h2{font-size:32px;margin:0 0 18px}h3{font-size:23px;line-height:1.2;margin:8px 0 14px}p{margin:12px 0}a{color:#2852a0;text-underline-offset:3px}header a{color:#bbd7ff}nav{display:flex;flex-wrap:wrap;gap:12px;margin:24px 0}nav a{padding:8px 12px;border:1px solid #b4b4a9;border-radius:8px}.meta,.date,.refs{font-size:14px}.meta{color:#c9d4df}.lead{font-size:21px}.explain{padding:18px 22px;background:#e2e8e8;border-left:4px solid #416b69;border-radius:6px}section{margin:45px 0;scroll-margin-top:20px}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.finding{background:#fffcf5;border:1px solid #cfcbbf;border-radius:12px;padding:22px}.tag{font-size:12px;font-weight:750;text-transform:uppercase;letter-spacing:.08em;color:#875523}.boundary{font-size:16px;color:#4d535b;border-top:1px solid #dedbd1;padding-top:12px}.refs a{overflow-wrap:anywhere}.table-scroll{overflow:auto}table{border-collapse:collapse;width:100%;background:#fffcf5;font-size:16px}th,td{text-align:left;vertical-align:top;padding:16px;border:1px solid #d4d0c5}thead{background:#202938;color:#fff}th[scope=row]{min-width:150px}td{min-width:210px}ol{padding-left:28px}li{padding:12px 16px;margin-bottom:14px;background:#fffcf5;border:1px solid #d4d0c5;border-radius:10px}details{border-bottom:1px solid #c9c6bb;padding:14px 0;scroll-margin-top:20px}summary{cursor:pointer;font-weight:650}details:target{background:#e2e8e8;padding:18px;border-radius:8px}button{font:inherit;color:#fff;background:#2852a0;border:0;border-radius:8px;padding:10px 16px;cursor:pointer}:focus-visible{outline:3px solid #b26722;outline-offset:4px}@media(max-width:700px){main{padding:18px 16px 45px}header{padding:24px}.grid{grid-template-columns:1fr}h2{font-size:27px}body{font-size:17px}.finding{padding:20px}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}@media print{body{font-size:12px;background:white}main{padding:0}header{background:white;color:black;padding:0}.meta{color:black}nav,button{display:none}.grid{display:block}.finding,li{break-inside:avoid;margin-bottom:12px}h1{font-size:28px}h2{font-size:22px}h3{font-size:17px}table{font-size:11px}th,td{min-width:0;padding:8px}details{break-inside:avoid}}
</style></head><body><main><header><a href="index.html">← Open the talk</a><p class="meta">''' + counts + '''</p>
<h1>What we have previously relied on can no longer be guaranteed</h1>
<p class="lead">Evidence across computing, repositories, app hosting, databases, and preservation.</p></header>
<nav aria-label="Evidence sections"><a href="#library">Library repositories</a><a href="#hosting">Hosting &amp; databases</a><a href="#options">Free options now</a><a href="#plan">Proposed response</a><a href="#ledger">Source ledger</a></nav>
<p class="explain">Historical window: October 10, 2021–October 10, 2026. Upcoming announced changes appear separately. A shutdown, a billing requirement, a current quota, and an availability incident are different findings. This selected history does not measure market-wide capacity or prove that every free route is shrinking.</p>
<section id="library"><h2>Library and research repositories</h2><p>These services preserve, publish, describe, or organize scholarly and cultural materials. Working cloud storage feeds those repositories but is not itself a preservation service.</p><div class="grid">''' + cards(data['library_repository_findings']) + '''</div></section>
<section id="hosting"><h2>Free hosting and databases</h2><p>General-purpose services used in teaching. Service shutdowns include paid users; free-plan changes have narrower scope. One provider may appear in both hosting and database layers, without counting it as two vanished companies.</p><div class="grid">''' + cards(data['hosting_database_findings']) + '''</div></section>
<section id="options"><h2>Free routes that remain viable</h2><p>Recommendations for bounded coursework, based on current documentation. Benchmark a full class and check the actual account quota before teaching. Existing limits below are not claimed as recent cuts.</p><div class="table-scroll"><table><thead><tr><th>Platform</th><th>Classroom fit</th><th>Work boundary</th><th>Evidence</th></tr></thead><tbody>''' + options + '''</tbody></table></div></section>
<section id="plan"><h2>A proposed continuity program</h2><p>Pair reviewed ACCESS / NAIRR compute with institution-funded application hosting, databases, durable storage, and Libraries stewardship. This is a proposed pilot, not an existing service, approved award, migration, or account change.</p><ol>''' + plan + '''</ol><p class="explain">Pilot two courses before scaling. Readiness requires a named operator, a funded service period, correct access controls, a tested cross-host restore, and a usable export at the end of term. Allocation expiry and vendor policy changes must have a rehearsed fallback.</p></section>
<section id="ledger"><h2>Source ledger</h2><p>''' + counts + '''. Original compute research was checked October 8; expanded repository, hosting and database records were checked October 10. Claims and interpretation boundaries are recorded per source.</p><p><a href="evidence.json" download>Download structured evidence</a> · <a href="research-and-sources.txt" download>Download research audit</a></p><button id="expand" type="button" aria-expanded="false">Expand all sources</button>''' + ledger + '''</section>
<footer><p>Teaching on Borrowed Compute · Greg Chism · University of Arizona InfoSci</p><p><a href="index.html">Talk</a> · <a href="degree-options.html">Nine-degree comparison</a> · <a href="repository-plan.html">Git repository plan</a></p></footer></main>
<script>const entries=[...document.querySelectorAll('details')];const button=document.getElementById('expand');button.onclick=()=>{const open=button.getAttribute('aria-expanded')!=='true';entries.forEach(e=>e.open=open);button.setAttribute('aria-expanded',String(open));button.textContent=open?'Collapse all sources':'Expand all sources'};function revealHash(){const el=document.getElementById(location.hash.slice(1));if(el?.tagName==='DETAILS')el.open=true}document.addEventListener('click',event=>{const link=event.target.closest('a[href^="#"]');if(link){const el=document.getElementById(link.getAttribute('href').slice(1));if(el?.tagName==='DETAILS')el.open=true}});addEventListener('hashchange',revealHash);revealHash();let beforePrint;addEventListener('beforeprint',()=>{beforePrint=entries.map(e=>e.open);entries.forEach(e=>e.open=true)});addEventListener('afterprint',()=>{entries.forEach((e,i)=>e.open=beforePrint?.[i]??false)})</script></body></html>'''
    (DEST / 'evidence.html').write_text(page)
    print(f'Built evidence appendix with {len(evidence)} source records')


if __name__ == '__main__':
    build()
