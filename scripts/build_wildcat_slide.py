#!/usr/bin/env python3
"""Build the single-slide companion to the unlisted Wildcat AI proposal."""
from pathlib import Path

from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen.canvas import Canvas
from reportlab.platypus import Paragraph

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site/wildcat-ai/wildcat-ai-in-one-slide.pdf"
URL = "https://gchism94.github.io/talks/education-compute/wildcat-ai/"
W, H = 1280, 720
NAVY, RED, WHITE, BLUE = "#0c234b", "#ab0520", "#ffffff", "#c7dbef"


def build():
    c = Canvas(str(OUT), pagesize=(W, H), invariant=1)
    c.setTitle("Wildcat AI in one slide")
    c.setAuthor("Greg Chism")
    c.setSubject("A working proposal for the University of Arizona; Fall 2027 pilot")
    c.setFillColor(HexColor(NAVY))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    def text(value, x, top, size=18, color=WHITE, width=700, bold=False, leading=None):
        style = ParagraphStyle("slide", fontName="Helvetica-Bold" if bold else "Helvetica",
                               fontSize=size, leading=leading or size * 1.27,
                               textColor=HexColor(color))
        p = Paragraph(value, style)
        _, height = p.wrap(width, H)
        p.drawOn(c, x, H - top - height)
        return height

    text("Wildcat <b>AI</b>", 48, 30, 23)
    text("A WORKING PROPOSAL FOR THE UNIVERSITY OF ARIZONA", 48, 76, 12, BLUE)
    # The site's concentric heart motif, drawn as vectors for sharp projection.
    for radius, alpha in [(190, .10), (176, .18), (164, .3)]:
        c.setStrokeAlpha(alpha)
        c.setStrokeColor(HexColor("#d9a0ae"))
        c.setLineWidth(1.2)
        c.circle(1037, H - 188, radius, fill=0, stroke=1)
    c.setStrokeAlpha(1)
    c.setFillColor(HexColor(RED))
    c.circle(1037, H - 188, 153, fill=1, stroke=0)
    text("Our people.<br/>Our possibility.", 935, 131, 29, width=240, bold=True)
    text("Human curiosity.<br/>Human judgment.", 935, 225, 17, width=240)

    text("People are<br/>the heart of AI.", 48, 112, 55, width=780, leading=57)
    text("Learn a hard concept. Prepare a class. Test an idea.<br/>Do the work, with help that fits.",
         48, 246, 21, BLUE, width=770)
    text("Clear data boundaries  /  Choice of tools  /  Human judgment", 48, 312, 15, BLUE)

    columns = [
        (48, "01 / THE PROBLEM", "Too much setup.<br/>Too little support.",
         "Finding the right account, software, and course rules shouldn’t be the hard part."),
        (454, "02 / THE PROPOSAL", "One place to work.<br/>Help when you need it.",
         "Bring U of A GenAI, EduCloud<sub>InfoSci</sub>, and permitted personal tools together."),
        (860, "03 / THE PEOPLE", "Shared decisions.<br/>A real say in what comes next.",
         "A campus team would own the service. People who choose no AI would help shape decisions and human alternatives."),
    ]
    for x, label, title, body in columns:
        c.setStrokeColor(HexColor("#48607f"))
        c.line(x, H - 367, x + 372, H - 367)
        text(label, x, 383, 12, BLUE, width=372)
        text(title, x, 408, 24, width=372, bold=True, leading=29)
        text(body, x, 479, 18, BLUE, width=365, leading=24)

    c.setFillColor(HexColor("#15345e"))
    c.roundRect(48, H - 657, 1184, 80, 8, fill=1, stroke=0)
    text("Fall 2027: start with a classroom pilot.", 70, 591, 23, bold=True, width=1120)
    text("Check learning, usability, privacy, and costs before deciding what to expand.",
         70, 626, 17, BLUE, width=1120)
    text("Proposed timing depends on staffing, access, and approval.", 48, 679, 12, BLUE)
    text("Explore the full proposal →", 1017, 678, 13, WHITE, width=230)
    c.linkURL(URL, (1010, 17, 1235, 45), relative=0)
    c.showPage()
    c.save()
    print(OUT)


if __name__ == "__main__":
    build()
