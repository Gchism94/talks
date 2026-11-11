# Wildcat AI proposal

Unlisted proposal inside the InfoSci computing site. The approved Heart design
is the published version; other design explorations are not part of this export.

Edit `index.html` for the opening and `proposal.html` for canonical details and
footer. Run `python3 scripts/build_wildcat_proposal.py` to export the public
files to `docs/education-compute/wildcat-ai/`. Existing site/guide build entry
points also export this page. For a page-only release, use the standalone
exporter to avoid rebuilding unrelated content, then run the site checks.

The hero links to `wildcat-ai-in-one-slide.pdf`, a single 16:9 overview with
selectable text and a link back to the proposal. To revise it, edit
`scripts/build_wildcat_slide.py`, run it with Python and ReportLab installed,
then run the proposal exporter. Render and inspect the PDF before publishing.
Keep the summary aligned with the current site and its proposed pilot timing.

Do not add the proposal to navigation, catalog, search data, or sitemap.
`noindex, nofollow, noarchive` requests search exclusion; it is not access control.
The proposal remains a working name and design, not an approved campus service.

The five main sections are opening, problem, audiences, system, and pilot.
Audience cards share natural grid sizing, with longer cases under More detail.
Keyboard navigation, reduced motion, human support, AI-off work and university
participation remain part of the experience. Personal-account specifications
are under a disclosure within the system. Print exposes all audiences/details;
without JavaScript, all audience sections remain available.

No model calls, credentials, forms, analytics or tracking are included. Local
fonts and shared favicons are served from the existing site assets.

Publication authorized November 10, 2026. The release contains only this page,
its source, and narrow build hooks. The rest of the existing site stays unchanged.
