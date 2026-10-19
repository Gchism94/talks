"""Source-linked report synopsis; documented availability is not a readiness claim."""
from html import escape as E


def refs(data, keys):
    return ' · '.join('<a href="evidence.html#' + E(key) + '">' + E(data['evidence'][key]['title']) + '</a>' for key in keys)


def render(data):
    a = data['report_overview']
    cards = []
    for row in a['available']:
        cards.append('<article class="report-resource" id="resource-' + E(row['id']) + '">'
                     '<p class="report-status ' + E(row['status_key']) + '">' + E(row['status']) + '</p>'
                     '<h3>' + E(row['title']) + '</h3><p class="report-providers">' + E(row['names']) + '</p>'
                     '<p>' + E(row['fit']) + '</p><p class="report-resource-boundary">' + E(row['boundary']) + '</p>'
                     '<details><summary>Sources and check dates</summary><p class="pg-refs">' + refs(data, row['sources']) + '</p><p class="pg-small">Check dates remain in the linked source records; a policy check is not an account or classroom test.</p></details>'
                     '<a class="report-detail" href="' + E(row['detail'], quote=True) + '">Details and limits ↗</a></article>')
    years = []
    for year in a['years']:
        entries = []
        for event in year['events']:
            entries.append('<li><p class="report-event-date">' + E(event['date']) + '</p><h4>' + E(event['title']) + '</h4>'
                           '<p class="report-change"><span>' + E(event['before']) + '</span><b aria-hidden="true">→</b>'
                           '<span><span class="sr-only">Changed to: </span>' + E(event['after']) + '</span></p>'
                           '<p class="pg-refs">' + refs(data, event['sources']) + '</p></li>')
        years.append('<li class="report-year"><h3>' + E(year['year']) + '</h3><ol>' + ''.join(entries) + '</ol></li>')
    notes = []
    for key in ['observation', 'upcoming']:
        row = a[key]
        notes.append('<article class="report-caveat" id="trend-' + key + '"><p class="pg-kicker">' + E(row['label']) + '</p>'
                     '<h3>' + E(row['title']) + '</h3><p>' + E(row['body']) + '</p><p class="pg-refs">' + refs(data, row['sources']) + '</p></article>')
    return '''<div id="report-overview" class="report-overview"><p class="pg-small">Summary updated October 19, 2026 · provider records checked October 8–19; check dates and scopes remain with each source.</p>
<div class="report-thesis"><p class="pg-kicker">The core problem</p><h2>''' + E(a['core_statement']) + '''.</h2><p>''' + E(a['interpretation']) + '''</p></div>
<nav class="report-jump" aria-label="Report overview sections"><a href="#available-resources">Available resources ↓</a><a href="#resource-trend">Losses and reductions ↓</a><a href="#program-response">Our response ↓</a><a href="#research-library">Full report and evidence ↓</a></nav>
<div class="report-snapshot" aria-label="Scope of this evidence collection"><p><strong>''' + str(len(data['classroom_resource_options'])) + '''</strong><span>resource comparisons<br>including paid and retired options</span></p><p><strong>''' + str(len(data['federal_platform_map'])) + '''</strong><span>federal platform/product families<br>including tools and funding routes</span></p><p><strong>''' + str(len(data['evidence'])) + '''</strong><span>source records<br>with dates and scope boundaries</span></p></div>
<section id="available-resources"><p class="pg-kicker">What remains available</p><h2>Useful resources. Different conditions.</h2><p class="pg-note">''' + E(a['readiness']) + ''' <a href="readiness.html">Review the 13 checks ↗</a></p><div class="report-resource-grid">''' + ''.join(cards) + '''</div><p class="pg-small report-paid-note">''' + E(a['paid_note']) + ''' <a href="serverless-compute.html">Read the commercial-platform assessment ↗</a>.</p></section>
<section id="resource-trend"><p class="pg-kicker">Selected documented changes · 2022–2026</p><h2>How dependable free access has narrowed.</h2><p>These cases show four pressures: services close, new cohorts lose eligibility, free-use periods shrink, and team/storage limits constrain assignments. Each example applies to a specific product or plan.</p><ol class="report-history" aria-label="Selected historical losses and reductions">''' + ''.join(years) + '''</ol><div class="pg-grid report-trend-notes">''' + ''.join(notes) + '''</div><p class="pg-small report-trend-boundary">''' + E(a['boundary']) + '''</p></section>
<section id="program-response" class="report-response"><p class="pg-kicker">The key solution</p><h2>Build a service around measured ACCESS capacity.</h2><p>''' + E(a['next_step']) + '''</p><p>NAIRR Classroom is an additional instructor-pilot route. CloudBank remains conditional through ACCESS. Keep portable code, independent recovery and approved student exports alongside the compute allocation.</p><div class="pg-actions"><a class="pg-link primary" href="timeline.html">Staged plan ↗</a><a class="pg-link" href="access-request.html">ACCESS CPU + GPU draft ↗</a><a class="pg-link" href="budget.html">Hours and grant dependencies ↗</a></div></section></div>'''
