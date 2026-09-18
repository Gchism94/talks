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
node --check site/workshop/workshop.js
node --check site/workshop/sketch.js
git diff --check
```

These checks validate the public export, links, URL restrictions, and sketch-draft
storage. Rehearse the slides and externally hosted activities before each event.
Poll Everywhere, the gallery, and Collective are hosted independently of GitHub
Pages.

## Live title preview

The TechBytes title slide plays Collective's Salem swifts in a phone-shaped
`?embed=title&experience=original` view. **Pause preview** unloads the scene;
**Replay birds** starts a fresh flock. Leaving the slide or hiding the browser tab
also unloads it. A reduced-motion preference starts with a still image instead.
**Explore** opens the full interactive app, with a close button that returns to
the slide. The simulation requires internet; the still image is the fallback.

## Workshop polls

The Google Maps and Spotify slides use separate Poll Everywhere response links.
Students can respond as guests without an account or a presenter activating the
poll. Each question has the same five-point mētis–epistēmē spectrum, single-select
responses, and changeable answers. Results start hidden; reveal them from the
corresponding poll in your signed-in Poll Everywhere workspace when ready to discuss.
The slide embeds collect responses; they are not the presenter results screen.

The response links currently have no closing date. Use **Share → Participants** in
Poll Everywhere to disable a link or set its availability after the workshop. Check
your plan's audience limit and trial status before the event. No test votes were
submitted while connecting the polls.

If a browser has older saved workshop links, open **Links** in the deck and update
the two poll fields (or use **Use defaults** to reset all workshop links). To change
the defaults for everyone, edit `site/workshop/config.js`, rebuild, and publish.

Poll Everywhere documents this flow in
[Embedding Response Links](https://support.polleverywhere.com/hc/en-us/articles/46214073740059-Embedding-Poll-Everywhere-Response-Links).
