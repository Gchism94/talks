#!/usr/bin/env python3
"""Export reviewed talk files to the GitHub Pages docs directory. No dependencies."""

import html
import json
from pathlib import Path
import re
import shutil
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "docs"


def gallery_url():
    """Use the deck's public room link so classroom shortcuts cannot drift."""
    config = (ROOT / "site/workshop/config.js").read_text()
    match = re.search(r"^\s*gallery:\s*'([^']+)'", config, re.M)
    if not match:
        raise ValueError("Configure a classroom gallery link before publishing")
    value = match.group(1)
    url = urlsplit(value)
    if (url.scheme != "https" or url.netloc != "techbytes-sketch-gallery.gchism.chatgpt.site"
            or url.path != "/" or url.fragment or not re.fullmatch(r"room=[a-f0-9]{32}", url.query)):
        raise ValueError("Gallery shortcut requires the public classroom URL without private identity data")
    return value


def local_file(name):
    supplied = ROOT / name
    path = supplied.resolve()
    if not path.is_relative_to(ROOT) or supplied.is_symlink():
        raise ValueError(f"Source must be inside the collection: {name}")
    return path


def public_deck(text, include_notes):
    # The authored talk keeps its original local URL and fonts. Only its public
    # export gets collection navigation and the shared public asset path.
    text = text.replace('url("assets/', 'url("../assets/')
    text = text.replace('"site/workshop/', '"../assets/workshop/')
    text = re.sub(
        r'<span class="brand">.*?</span>',
        '<span class="brand"><a href="../">← All talks</a></span>',
        text,
        count=1,
    )
    collection_style = '.brand a { color:inherit; text-decoration:none; }'
    if collection_style not in text:
        text = text.replace("</style>", '\n' + collection_style + '\n'
                            '.brand a:hover { text-decoration:underline; }\n</style>', 1)
    if not include_notes:
        text = re.sub(
            r'(<aside class="speaker-notes">).*?(</aside>)',
            r'\1<p>Presenter notes are not included in this public edition.</p>\2',
            text,
            flags=re.S,
        )
        text = text.replace('<button id="notesBtn"', '<button hidden id="notesBtn"')
        text = text.replace('<kbd>N</kbd><span>Notes for this slide</span>', '')
        text = text.replace(' Notes appear on this screen; close them before presenting.', '')
        text = text.replace(
            "else if (event.key.toLowerCase() === 'n')",
            "else if (event.key.toLowerCase() === 'n' && !document.getElementById('notesBtn').hidden)",
        )
    return text


def build():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    include_notes = catalog.get("publish_notes", False)
    repository = f"https://github.com/{catalog['owner']}/{catalog['repository']}"
    PUBLIC.mkdir(exist_ok=True)
    fonts = ROOT / "assets/fonts"
    if fonts.is_dir():
        shutil.copytree(fonts, PUBLIC / "assets/fonts", dirs_exist_ok=True)
    if not (PUBLIC / "assets/fonts/ibm-plex-sans.ttf").is_file():
        raise FileNotFoundError("Local fonts or previously exported public fonts are required.")
    shutil.copyfile(ROOT / "site/library.css", PUBLIC / "assets/library.css")
    if (ROOT / "site/workshop").is_dir():
        shutil.copytree(ROOT / "site/workshop", PUBLIC / "assets/workshop", dirs_exist_ok=True)
    gallery = PUBLIC / "gallery"
    gallery.mkdir(exist_ok=True)
    gallery_page = (ROOT / "site/gallery.html").read_text()
    (gallery / "index.html").write_text(gallery_page.replace("@@GALLERY_URL@@", html.escape(gallery_url(), quote=True)))
    cards, seen = [], set()
    for number, talk in enumerate(catalog["talks"], 1):
        slug = talk["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen or slug in {"assets", "gallery"}:
            raise ValueError(f"Invalid or duplicate talk slug: {slug}")
        seen.add(slug)
        destination = PUBLIC / slug
        destination.mkdir(exist_ok=True)
        source = local_file(talk["source"])
        exported = destination / "index.html"
        if source.is_file():
            exported.write_text(public_deck(source.read_text(), include_notes))
        elif exported.is_file():
            exported.write_text(public_deck(exported.read_text(), include_notes))
        else:
            raise FileNotFoundError(f"No working source or published copy for {slug}")
        # A fresh clone can use its checked-in public editions; local originals
        # and presenter documents are deliberately not required for that flow.
        links = []
        if include_notes:
            for key, label in [("speaker_cues", "Speaker cues"), ("facilitator_guide", "Facilitator guide")]:
                filename = talk.get(key)
                if not filename:
                    continue
                source_note = local_file(filename)
                note = destination / Path(filename).name
                if source_note.is_file():
                    content = source_note.read_text().replace(str(ROOT) + "/", "")
                    live_talk = f"https://{catalog['owner'].lower()}.github.io/{catalog['repository']}/{slug}/#1"
                    content = content.replace(f'({talk["source"]})', f'({live_talk})')
                    note.write_text(content)
                elif not note.is_file():
                    raise FileNotFoundError(f"Requested public notes are missing: {filename}")
                url = f"{repository}/blob/main/docs/{slug}/{note.name}"
                links.append(f'<a href="{html.escape(url, quote=True)}">{label}</a>')
        else:
            for key in ["speaker_cues", "facilitator_guide"]:
                filename = talk.get(key)
                if filename:
                    # Remove only this talk's known generated companions, never
                    # the local originals or unrelated files.
                    (destination / Path(filename).name).unlink(missing_ok=True)
        notes = '<div class="notes">' + ''.join(links) + '</div>' if links else ''
        topics = ''.join(f'<li>{html.escape(topic)}</li>' for topic in talk["topics"])
        esc = lambda key: html.escape(str(talk[key]))
        cover = ''
        if talk.get("cover"):
            cover_source = local_file(talk["cover"])
            cover_destination = PUBLIC / "assets/covers" / (slug + cover_source.suffix)
            cover_destination.parent.mkdir(exist_ok=True)
            shutil.copyfile(cover_source, cover_destination)
            cover = (f'<img src="assets/covers/{html.escape(cover_destination.name, quote=True)}" '
                     'alt="" width="1280" height="720" decoding="async">')
        else:
            cover = f'<span class="cover-title">{esc("title")}</span>'
        cards.append(f'''      <article class="talk" aria-labelledby="{slug}-title">
        <div class="talk-visual">
          <div class="cover-heading"><span class="number">{number:02} / Presentation</span><span>{esc('slides')} slides</span></div>
          <a class="cover" href="{slug}/#1" aria-label="Preview and open {html.escape(talk['title'], quote=True)}">
            {cover}
            <span class="cover-open" aria-hidden="true">↗</span>
          </a>
          <div class="cover-caption"><span>{esc('format')}</span><span>{esc('duration')}</span></div>
        </div>
        <div class="talk-content">
          <p class="event">{esc('event')}</p>
          <h2 id="{slug}-title"><a href="{slug}/#1">{esc('title')}</a></h2>
          <p class="subtitle">{esc('subtitle')}</p>
          <p class="description">{esc('description')}</p>
          <ul class="topics" aria-label="Topics">{topics}</ul>
          <a class="launch" href="{slug}/#1" aria-label="Open {html.escape(talk['title'], quote=True)}">Open presentation <span aria-hidden="true">↗</span></a>
          {notes}
        </div>
      </article>''')
    page = (ROOT / "site/index.html").read_text()
    repo_link = (f'<a class="repository" href="{html.escape(repository, quote=True)}">'
                 'View on GitHub <span aria-hidden="true">↗</span></a>'
                 if catalog.get("repository_live") else
                 '<span class="repository pending"><span aria-hidden="true"></span>Local preview</span>')
    page = page.replace("@@REPOSITORY_LINK@@", repo_link)
    page = page.replace("@@TALKS@@", "\n".join(cards))
    count = len(cards)
    page = page.replace("@@TALK_COUNT@@", f'{count:02} {"talk" if count == 1 else "talks"}')
    (PUBLIC / "index.html").write_text("\n".join(line.rstrip() for line in page.splitlines()) + "\n")
    (PUBLIC / ".nojekyll").touch()
    print(f"Exported {len(seen)} talk(s) to {PUBLIC}; companion notes: {include_notes}")


if __name__ == "__main__":
    build()
