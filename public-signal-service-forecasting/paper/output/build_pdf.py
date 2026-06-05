"""Build the PDF submission document from the shared content module.

Renders paper/output/content.py with ReportLab. Uses the same content as the
Word builder, so the two deliverables carry identical text, tables, figures,
and references. Times-family fonts approximate the Word Times New Roman.
"""
from __future__ import annotations

from pathlib import Path
from xml.sax.saxutils import escape

import content as C
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    BaseDocTemplate,
    CondPageBreak,
    Frame,
    Image,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

PAPER = Path(__file__).resolve().parents[1]
FIG = PAPER / "figures"
OUT = PAPER / "output" / "public_signal_service_forecasting_final_submission.pdf"

PAGE_W, PAGE_H = letter
MARGIN = inch
CONTENT_W = PAGE_W - 2 * MARGIN
LEADING = 1.15

SERIF = "Times-Roman"
SERIF_B = "Times-Bold"
SERIF_I = "Times-Italic"


def _style(name, size, font=SERIF, align=TA_JUSTIFY, **kw):
    return ParagraphStyle(name, fontName=font, fontSize=size,
                          leading=size * LEADING, **{"alignment": align, **kw})


STYLES = {
    "title": _style("title", 18, SERIF_B, TA_CENTER, spaceBefore=24, spaceAfter=14),
    "author": _style("author", 12, SERIF_B, TA_CENTER, spaceAfter=2),
    "affil": _style("affil", 11, SERIF_I, TA_CENTER, spaceAfter=2),
    "email": _style("email", 11, SERIF, TA_CENTER, spaceAfter=18),
    "h1": _style("h1", 14, SERIF_B, TA_JUSTIFY, spaceBefore=12, spaceAfter=6, keepWithNext=1),
    "h2": _style("h2", 12, SERIF_B, TA_JUSTIFY, spaceBefore=12, spaceAfter=6, keepWithNext=1),
    "body": _style("body", 12, SERIF, TA_JUSTIFY, spaceAfter=6),
    "tcap": _style("tcap", 11, SERIF_B, TA_JUSTIFY, spaceBefore=8, spaceAfter=4, keepWithNext=1),
    "fcap": _style("fcap", 10, SERIF_I, TA_CENTER, spaceBefore=4, spaceAfter=6),
    "ref": _style("ref", 12, SERIF, TA_LEFT, leftIndent=36, firstLineIndent=-36, spaceAfter=6),
}


def _markup(text: str) -> str:
    """Convert **bold** spans to <b> markup, em-dash spaced hyphens, escape XML,
    and make any inline URL clickable."""
    import re
    text = text.replace(" - ", "—")
    out = []
    for i, part in enumerate(text.split("**")):
        if not part:
            continue
        out.append((f"<b>{escape(part)}</b>") if i % 2 == 1 else escape(part))
    joined = "".join(out)
    return re.sub(r"(https?://[^\s)]+)",
                  r'<a href="\1" color="#0030c0">\1</a>', joined)


def _col_widths(header, rows, font_size):
    """Proportional column widths with a per-column floor wide enough for the
    longest unbreakable word, so short headers (e.g. 'Crews') and identifier
    tokens (e.g. 'calendar_weather_augmented') do not break mid-word."""
    ncol = len(header)
    char_w = font_size * 0.55
    pad = 8.0
    longest_word = [0.0] * ncol
    total_len = [0.0] * ncol
    for j in range(ncol):
        cells = [header[j]] + [r[j] for r in rows]
        longest_word[j] = max(max((len(w) for w in c.split()), default=1) for c in cells)
        total_len[j] = max(len(c) for c in cells)
    floor = [lw * char_w + pad for lw in longest_word]
    tw = sum(total_len) or 1.0
    width = [max(CONTENT_W * total_len[j] / tw, floor[j]) for j in range(ncol)]
    scale = CONTENT_W / sum(width)
    return [w * scale for w in width]


class PdfRenderer:
    def __init__(self) -> None:
        self.story = []

    def title(self, title, author, affiliation, email) -> None:
        self.story.append(Paragraph(escape(title), STYLES["title"]))
        self.story.append(Paragraph(escape(author), STYLES["author"]))
        self.story.append(Paragraph(escape(affiliation), STYLES["affil"]))
        self.story.append(Paragraph(escape(email), STYLES["email"]))

    def h1(self, text) -> None:
        self.story.append(Paragraph(escape(text), STYLES["h1"]))

    def h2(self, text) -> None:
        self.story.append(Paragraph(escape(text), STYLES["h2"]))

    def body(self, text) -> None:
        self.story.append(Paragraph(_markup(text), STYLES["body"]))

    def figure(self, label, filename, caption, width_in: float = 6.0) -> None:
        path = FIG / filename
        iw, ih = PILImage.open(path).size
        w = width_in * inch
        h = w * ih / iw
        max_h = 8.0 * inch
        if h > max_h:
            h = max_h
            w = h * iw / ih
        img = Image(str(path), width=w, height=h)
        img.hAlign = "CENTER"
        cap = Paragraph(f"Figure {label}. {escape(caption)}", STYLES["fcap"])
        self.story.append(KeepTogether([img, Spacer(1, 4), cap]))

    def table_caption(self, text) -> None:
        # Keep the caption with the table header and first rows: if too little
        # vertical space remains, move the caption (and table) to the next page
        # rather than stranding a caption/header at the page bottom.
        self.story.append(CondPageBreak(2.2 * inch))
        self.story.append(Paragraph(escape(text), STYLES["tcap"]))

    def table(self, header, rows, font_size: int = 10) -> None:
        cell = _style("cell", font_size, SERIF, TA_LEFT)
        cellh = _style("cellh", font_size, SERIF_B, TA_CENTER)
        data = [[Paragraph(escape(h), cellh) for h in header]]
        for row in rows:
            data.append([Paragraph(escape(v), cell) for v in row])
        t = Table(data, colWidths=_col_widths(header, rows, font_size), repeatRows=1)
        t.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(0.9, 0.9, 0.9)),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
            ("RIGHTPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ]))
        t.hAlign = "CENTER"
        self.story.append(t)
        self.story.append(Spacer(1, 6))

    def page_break(self) -> None:
        self.story.append(PageBreak())

    def references(self, refs) -> None:
        import re
        for r in refs:
            # Make DOIs / URLs clickable; reportlab breaks long URLs at the margin.
            text = re.sub(r"(https?://\S+)",
                          r'<a href="\1" color="#0030c0">\1</a>', escape(r))
            self.story.append(Paragraph(text, STYLES["ref"]))


def _footer(canvas, doc):
    canvas.saveState()
    canvas.setFont(SERIF, 10)
    canvas.drawCentredString(PAGE_W / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()


def build() -> None:
    r = PdfRenderer()
    C.emit(r)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=MARGIN,
        title=("From Forecast Accuracy to Operational Value: "
               "Public Signal Augmentation for NYC 311 Service Demand"),
        author=C.AUTHOR, subject="", creator="", keywords="",
    )
    frame = Frame(MARGIN, MARGIN, CONTENT_W, PAGE_H - 2 * MARGIN, id="main")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=_footer)])
    doc.build(r.story)
    print("WROTE", OUT)


if __name__ == "__main__":
    build()
