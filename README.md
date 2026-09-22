# Greg Chism · Talks

A browsable collection of presentations and workshops.

- Collection directory: this `talks` checkout
- Repository: [Gchism94/talks](https://github.com/Gchism94/talks)
- Website: [Greg Chism · Talks](https://gchism94.github.io/talks/)
- GitHub Pages publishing source: `main` branch, `/docs` folder.

## Classroom sketch gallery

Share [gchism94.github.io/talks/gallery/](https://gchism94.github.io/talks/gallery/)
with students, or use **Open sketch gallery** on the talks homepage. This short
address opens the public TechBytes classroom directly: no student sign-in or
room-code entry. Students can draw and submit ideas, then vote when the presenter
opens voting. Presenter controls still require the owner's sign-in.

The gallery itself stays on its existing host so saved work and browser-local
drafts remain intact. The shortcut uses the same classroom link as the slides in
`site/workshop/config.js`; changing that link and rebuilding updates both. It does
not forward query strings or participant identities from the shortcut URL.

## Organization

```text
talks/
├── catalog.json              # The talks listed on the website
├── site/                     # Collection page template and styling
├── scripts/build_site.py     # Exports approved files; no dependencies
├── docs/                     # Public website and published talk editions
│   ├── index.html
│   ├── assets/fonts/
│   └── design-what-you-know/index.html
└── working decks and notes   # Local only, excluded from Git
```

The existing working HTML files, facilitator guide, speaker cues, old drafts,
revision backups, and browser-test output remain local. The repository contains
the reviewed public editions under `docs/`, not a wholesale upload of the working
folder. Public editions are normal editable HTML, including when cloned onto a
different computer. The working originals are not backed up by this repository.
Collective, the sketch-gallery application, and the swift-roost prototype remain
separate projects; this collection only links to their public experiences.

`catalog.json` controls publication of companion documents. With `publish_notes`
set to `false`, the exported deck also removes embedded presenter notes and their
control. Turning it on publishes both embedded notes and the listed companions;
review those documents before enabling it. Previously published material remains
in Git history even if a later revision removes it.

## Update an existing talk

1. Edit the original local HTML deck and, if needed, its entry in `catalog.json`.
2. Run `python3 scripts/build_site.py`, then `python3 scripts/check_site.py`.
3. Review the changed files in `docs/`, commit, and push `main`.
4. GitHub Pages publishes the updated collection automatically.

On a fresh clone without the private working files, edit the public edition in
`docs/<slug>/index.html`. The export script preserves that edition if no working
source exists. To restore a working original, copy it to the `source` location
listed in the catalog; review its asset paths before exporting.

## Add another talk

1. Put its self-contained HTML working file in this directory.
2. Add an entry to `catalog.json` with a unique slug, source filename, title,
   description, event, format, duration, slide count, and topics.
3. Run the export and check scripts, review the result, then commit and push.

The current exporter supports these workshop decks and their shared font assets.
For a talk with additional images, video, or a different structure, extend the
explicit export list and validate its links before publication. Do not copy the
entire working directory into `docs/`.

## Preview locally

Run `python3 -m http.server 8765 --directory docs` and open
`http://localhost:8765/`. Open a talk from the collection and use its “All talks”
link to return. Font files and licenses are included, so the slides do not depend
on a font service. Live AI demonstrations still require internet access.

## Favicons

The collection, talk, and gallery use matching T lettermarks in their existing
charcoal/coral, brick-red, and cobalt palettes. SVG masters and their 32-pixel PNG
fallbacks and 180-pixel home-screen icons live in `site/favicons/`. The exporter
copies them into the public assets; the separate gallery references its existing
blue SVG and matching PNG files through its shared page metadata.

## Fonts

Barlow Condensed, Literata, and IBM Plex Sans are included with their original
license files in `docs/assets/fonts/`.

## Validate before publishing

With Python 3.10+ and Node.js installed, run:

```sh
python3 scripts/build_site.py
python3 scripts/check_site.py
node scripts/verify_workshop_urls.mjs
node scripts/verify_sketch_drafts.mjs
node scripts/verify_title_preview.mjs
node scripts/verify_mobile_logic.mjs
node --check site/workshop/workshop.js
node --check site/workshop/sketch.js
git diff --check
```

These checks validate the public export, links, URL restrictions, and sketch-draft
storage. Rehearse the slides and externally hosted activities before each event.
The gallery backend and Collective are hosted independently of GitHub Pages.
The native poll interface is static; saved responses use the gallery backend.

## Mobile workshop edition

The 13-slide edition starts with a static QR code to the public talk and a
30-second takeaways slide before Google Maps. The opening still totals two
minutes; the 45-minute workshop schedule is unchanged. The QR is a local SVG,
with a direct link for readers already on a phone—no QR service or tracking.
`scripts/generate_talk_qr.py` emits the SVG using ReportLab. The QR destination is
the published deck, not a presenter session or private room-management link.

Phone widths and short landscape windows use the same scrollable, all-sections
layout. All embedded apps use static launch cards on phones, opening full screen
with a persistent external link. Closing restores a readable card, not a tiny live
iframe. The two workshop choices stack on phone widths and their diagram stays
inside the card. Dark-slide launch buttons use an explicit contrasting palette.
The workshop menu contains the outline and student resources; presenter URL
configuration is under **Menu → Presenter setup → Configure workshop links**.

The default Student prototype now opens an accessible HTML companion at
`assets/workshop/prototype.html`. It is explicitly labeled sample content and
does not collect or save responses. The shared Figma design remains linked for
viewing/editing. A custom Figma URL configured by the presenter still embeds the
custom prototype. The original Figma button-reaction problem is not fixed by
this companion; the companion provides a separate classroom path.

The browser suites `scripts/verify_workshop_browser.mjs` and
`scripts/verify_embeds_browser.mjs` target the public export served at
`http://127.0.0.1:8765/`. They use intercepted API/app fixtures, never live
classroom writes. Run them with `playwright-cli run-code --filename <script>`.
They cover both routes, 208 slide/viewport combinations, short landscape
scroll reachability, native polls, overlay focus, and the complete HTML starter.
Both browser suites passed on September 21 after session access was restored:
208 slide/viewport combinations and the overlay/starter interaction checks.
The release check also caught and corrected a desktop Spotify-slide footer
overlap. Provider behavior and real finger/virtual-keyboard testing still require
a separate phone rehearsal; browser viewport tests are not physical-device tests.

`scripts/verify_mobile_interactions_browser.mjs` adds 28 phone app-view checks,
wildcard graphic bounds, slide-10 button contrast, and a complete drawing/reload/
mocked-submission/undo/navigation check. All remote writes are intercepted. On
phones, **Draw** opts into canvas gestures; **Done drawing** restores scrolling.
Drawing paints only new segments once per animation frame, rather than resizing
and repainting the whole bitmap on every pointer event. Existing draft keys,
coordinates, consent, and classroom submission behavior are unchanged.

## Live title preview

On desktop, the TechBytes title slide plays Collective's Salem swifts in a
`?embed=title&experience=original` view. On phones, it starts as a still launch
card: **Watch the flock** opens the scene full screen, where the playback-speed
control offers 0.5×. The simulation's underlying speed/model is unchanged.
**Pause preview** unloads the desktop scene;
**Replay birds** starts a fresh flock. Leaving the slide or hiding the browser tab
also unloads it. A reduced-motion preference starts with a still image instead.
**Watch full screen** keeps the storage-free scene with a close button returning
to the slide. **Open separately** opens the full app. The simulation requires
internet; the still image is the fallback.

## Native discussion polls

The slides and https://gchism94.github.io/talks/polls/ use native five-position polls. Responses save in separate tables in the existing gallery’s Cloudflare D1 database. This does not depend on the unfinished independent-hosting migration.

- Four questions: Google Maps, Apple Maps, Spotify, Apple Music. Only the first app in each pair is a required vote; comparisons fit the existing five-minute opening.
- No default answer or automatic submission. Save explicitly; revise while open. One response per browser, room, and app. Clearing storage or another browser can vote again: informal classroom discussion, not a verified ballot.
- No names or free text. Storage holds a room-specific hash of a random browser identity and the chosen position. Public distributions stay hidden until revealed. No averages or correct-answer grading.
- Sign in to the gallery as the room owner, expand **Discussion polls**, close/reopen each question, reveal/hide results, and download aggregate CSV totals. Poll controls are independent of sketch collection/voting.
- **Menu → Presenter setup → Configure workshop links → Classroom sketch gallery link** selects the room. Share the phone poll link including its room parameter for another session. Create a fresh gallery room for a fresh workshop; do not reset old contributions.
- Switching between the talk and poll page on the same talks-site origin keeps the identity. Third-party origins have separate browser storage.
- Network failure: the page shows an error and does not claim success. Retry safely, or use a show of hands without implying it was saved.

Existing Poll Everywhere links remain optional external backups; previous responses are not imported. No new service or paid account is required.
