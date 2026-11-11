#!/usr/bin/env python3
"""Export the unlisted Wildcat AI proposal without adding it to site indexes."""
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parent.parent


def build():
    source = ROOT / "site/wildcat-ai"
    destination = ROOT / "docs/education-compute/wildcat-ai"
    destination.mkdir(parents=True, exist_ok=True)
    proposal = (source / "proposal.html").read_text()
    start_marker = "<!-- PROPOSAL_DETAILS_START -->"
    end_marker = "<!-- PROPOSAL_DETAILS_END -->"
    if proposal.count(start_marker) != 1 or proposal.count(end_marker) != 1:
        raise ValueError("Expected one canonical proposal details region")
    details = proposal.split(start_marker, 1)[1].split(end_marker, 1)[0]
    footer = "<footer" + proposal.split("<footer", 1)[1].split("</footer>", 1)[0] + "</footer>"
    template = (source / "index.html").read_text()
    for marker in ("<!-- PROPOSAL_DETAILS -->", "<!-- PROPOSAL_FOOTER -->", "<!-- DESIGN_SWITCHER -->"):
        if template.count(marker) != 1:
            raise ValueError(f"Expected one {marker} in index.html")
    rendered = template.replace("<!-- PROPOSAL_DETAILS -->", details).replace("<!-- PROPOSAL_FOOTER -->", footer).replace("<!-- DESIGN_SWITCHER -->", "")
    (destination / "index.html").write_text(rendered)
    for name in ("proposal.html", "wildcat.css", "journey.css", "directions.css", "wildcat.js"):
        shutil.copyfile(source / name, destination / name)
    print("Built unlisted Wildcat AI proposal; excluded from navigation, search and sitemap.")


if __name__ == "__main__":
    build()
