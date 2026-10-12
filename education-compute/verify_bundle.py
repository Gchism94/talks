"""Check this local snapshot without changing it or contacting external services."""
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import zipfile


def sha256(data):
    return hashlib.sha256(data).hexdigest()


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = []

    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in {"href", "src"} and value:
                self.urls.append(value)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare-originals", action="store_true")
    args = parser.parse_args()
    base = Path(__file__).resolve().parent
    manifest = json.loads((base / "manifest.json").read_text())
    failures = []
    for entry in manifest["files"]:
        path = base / entry["path"]
        if not path.is_file() or sha256(path.read_bytes()) != entry["sha256"]:
            failures.append(f"Missing or changed snapshot: {entry['path']}")
        if args.compare_originals:
            original = base.parent / entry["original"]
            if not original.is_file() or sha256(original.read_bytes()) != entry["sha256"]:
                failures.append(f"Original has changed or is missing: {entry['original']}")

    for path in (base / "talk").glob("*.html"):
        links = Links()
        links.feed(path.read_text())
        for url in links.urls:
            if "${" in url:
                continue
            parsed = urlsplit(url)
            if parsed.scheme or parsed.netloc or not parsed.path:
                continue
            target = path.parent / unquote(parsed.path)
            if not target.exists():
                failures.append(f"Missing portable link in {path.name}: {url}")

    ledger = json.loads((base / "evidence/evidence.json").read_text())
    expected_sources = manifest.get("source_records", 73)
    if len(ledger["evidence"]) != expected_sources:
        failures.append(f"This snapshot should have {expected_sources} source records")
    if (base / "evidence/evidence.json").read_bytes() != (base / "talk/evidence.json").read_bytes():
        failures.append("Portable and research ledgers differ")
    if not (base / "talk/evidence.html").is_file():
        failures.append("Saved appendix is missing")

    with zipfile.ZipFile(base / "teaching-on-borrowed-compute.zip") as archive:
        for path in (base / "talk").rglob("*"):
            if not path.is_file():
                continue
            member = "teaching-on-borrowed-compute/" + path.relative_to(base / "talk").as_posix()
            try:
                if archive.read(member) != path.read_bytes():
                    failures.append(f"ZIP differs from portable file: {path.name}")
            except KeyError:
                failures.append(f"ZIP missing portable file: {path.name}")

    if failures:
        raise SystemExit("\n".join(failures))
    print(f"Verified {len(manifest['files'])} saved artifacts, portable links, {expected_sources} sources, appendix, and ZIP.")
    if args.compare_originals:
        print("All gathered artifacts match their original files.")


if __name__ == "__main__":
    main()
