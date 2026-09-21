#!/usr/bin/env python3
"""Check the published allowlist, local links, fonts, and slide export boundaries."""

from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

from build_site import ROOT, PUBLIC, public_deck, gallery_url


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.slides = 0
        self.icons = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.references.extend(attrs[key] for key in ("href", "src") if key in attrs)
        if tag == "link" and attrs.get("rel") in {"icon", "apple-touch-icon"}:
            self.icons.append(attrs)
        if tag == "section" and "slide" in attrs.get("class", "").split():
            self.slides += 1


def check_reference(source, value):
    url = urlsplit(value)
    if url.scheme or url.netloc or not url.path:
        return
    target = (source.parent / unquote(url.path)).resolve()
    if not target.is_relative_to(PUBLIC.resolve()):
        raise AssertionError(f"Link escapes public site: {source}: {value}")
    if target.is_dir():
        target = target / "index.html"
    assert target.is_file(), f"Broken local link: {source}: {value}"


def check():
    catalog = json.loads((ROOT / "catalog.json").read_text())
    assert (PUBLIC / "index.html").is_file()
    assert (PUBLIC / ".nojekyll").is_file()
    allowed_roots = {"assets", "gallery", "polls", "index.html", ".nojekyll"} | {t["slug"] for t in catalog["talks"]}
    assert {p.name for p in PUBLIC.iterdir()} <= allowed_roots, "Unexpected public files: review export"
    home = (PUBLIC / "index.html").read_text()
    assert 'href="gallery/"' in home, "Gallery must be reachable from the talks homepage"
    assert 'href="polls/"' in home, "Native polls must be reachable from the talks homepage"
    polls = (PUBLIC / "polls/index.html").read_text()
    assert 'data-poll-page' in polls and 'data-native-poll="maps"' in polls and 'data-native-poll="music"' in polls
    assert 'localhost' not in polls, "Never publish a local test backend"
    gallery = (PUBLIC / "gallery/index.html").read_text()
    assert f'id="open-gallery" class="gallery-launch" href="{gallery_url()}"' in gallery
    assert "<noscript>" in gallery, "Preserve a usable gallery link without JavaScript"
    assert "location.search" not in gallery and "location.hash" not in gallery, "Do not forward arbitrary room or identity data"
    checked = 0
    for source in PUBLIC.rglob("*"):
        if not source.is_file() or source.suffix not in {".html", ".css", ".md"}:
            continue
        text = source.read_text()
        assert "/Users/" not in text, f"Local machine path in public file: {source}"
        assert "@@" not in text, f"Unresolved template field: {source}"
        if source.suffix == ".html":
            links = Links()
            links.feed(text)
            assert any(i.get("type") == "image/svg+xml" for i in links.icons), f"Missing SVG favicon: {source}"
            assert any(i.get("type") == "image/png" and i.get("sizes") == "32x32" for i in links.icons), f"Missing favicon fallback: {source}"
            assert any(i.get("rel") == "apple-touch-icon" for i in links.icons), f"Missing mobile home-screen icon: {source}"
            assert all(not i.get("href", "").startswith("data:,") for i in links.icons), f"Empty favicon: {source}"
            for reference in links.references:
                check_reference(source, reference)
                checked += 1
        if source.suffix in {".html", ".css"}:
            for reference in re.findall(r'url\([\"\']?([^\"\')]+)', text):
                check_reference(source, reference)
                checked += 1
    for talk in catalog["talks"]:
        destination = PUBLIC / talk["slug"]
        deck = (destination / "index.html").read_text()
        parsed = Links()
        parsed.feed(deck)
        assert parsed.slides == talk["slides"], f"Wrong slide count for {talk['slug']}"
        assert 'href="../"' in deck, "Missing collection return link"
        if not catalog.get("publish_notes"):
            assert '<button hidden id="notesBtn"' in deck
            assert not list(destination.glob("*.md")), "Unapproved companion document"
            notes = re.findall(r'<aside class="speaker-notes">(.*?)</aside>', deck, re.S)
            assert notes and all(n == '<p>Presenter notes are not included in this public edition.</p>' for n in notes)
            assert public_deck(deck, False) == deck, "Re-export must be stable"
    print(f"Checked {len(catalog['talks'])} talk(s), {checked} local/external references, and publication boundaries.")


if __name__ == "__main__":
    check()
