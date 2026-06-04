"""Build the Word submission document from the shared content module.

Renders paper/output/content.py to a formatted .docx with embedded images,
real Word tables, styled headings, page numbers, and a clean References
section. All text, numbers, and figures come from content.py, which is the
single source shared with the PDF builder.
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt

import content as C

PAPER = Path(__file__).resolve().parents[1]
FIG = PAPER / "figures"
OUT = PAPER / "output" / "public_signal_service_forecasting_final_submission.docx"

BODY_FONT = "Times New Roman"
BODY_SIZE = Pt(12)
LINE_SPACING = 1.15


def _set_run_font(run, size=BODY_SIZE, bold=False, italic=False):
    run.font.name = BODY_FONT
    run.font.size = size
    run.bold = bold
    run.italic = italic
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.find(qn("w:rFonts"))
    if rfonts is None:
        rfonts = OxmlElement("w:rFonts"); rpr.append(rfonts)
    rfonts.set(qn("w:ascii"), BODY_FONT)
    rfonts.set(qn("w:hAnsi"), BODY_FONT)


def _row_cant_split(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    trPr.append(OxmlElement("w:cantSplit"))


def _row_repeat_header(row) -> None:
    trPr = row._tr.get_or_add_trPr()
    th = OxmlElement("w:tblHeader"); th.set(qn("w:val"), "true")
    trPr.append(th)


class DocxRenderer:
    def __init__(self) -> None:
        self.doc = Document()
        self._set_base_style()
        self._add_page_number_footer()

    # --- setup -----------------------------------------------------------
    def _set_base_style(self) -> None:
        normal = self.doc.styles["Normal"]
        normal.font.name = BODY_FONT
        normal.font.size = BODY_SIZE
        normal._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
        pf = normal.paragraph_format
        pf.line_spacing = LINE_SPACING
        pf.space_after = Pt(6)
        for section in self.doc.sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)

    def _add_page_number_footer(self) -> None:
        section = self.doc.sections[0]
        p = section.footer.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        fld1 = OxmlElement("w:fldChar"); fld1.set(qn("w:fldCharType"), "begin")
        instr = OxmlElement("w:instrText"); instr.set(qn("xml:space"), "preserve"); instr.text = "PAGE"
        fld2 = OxmlElement("w:fldChar"); fld2.set(qn("w:fldCharType"), "end")
        run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
        _set_run_font(run)

    # --- renderer interface ---------------------------------------------
    def title(self, title, author, affiliation, email) -> None:
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(24)
        p.paragraph_format.space_after = Pt(14)
        p.paragraph_format.keep_with_next = True
        _set_run_font(p.add_run(title), size=Pt(18), bold=True)

        ap = self.doc.add_paragraph()
        ap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ap.paragraph_format.space_after = Pt(2)
        _set_run_font(ap.add_run(author), size=Pt(12), bold=True)

        afp = self.doc.add_paragraph()
        afp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        afp.paragraph_format.space_after = Pt(2)
        _set_run_font(afp.add_run(affiliation), size=Pt(11), italic=True)

        ep = self.doc.add_paragraph()
        ep.alignment = WD_ALIGN_PARAGRAPH.CENTER
        ep.paragraph_format.space_after = Pt(18)
        _set_run_font(ep.add_run(email), size=Pt(11))

    def _heading(self, text, size) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(12)
        p.paragraph_format.space_after = Pt(6)
        p.paragraph_format.keep_with_next = True
        _set_run_font(p.add_run(text), size=Pt(size), bold=True)

    def h1(self, text) -> None:
        self._heading(text, 14)

    def h2(self, text) -> None:
        self._heading(text, 12)

    def body(self, text) -> None:
        # True em dash for parenthetical dashes (spaced hyphens only).
        text = text.replace(" - ", "—")
        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        for i, part in enumerate(text.split("**")):
            if not part:
                continue
            _set_run_font(p.add_run(part), bold=(i % 2 == 1))

    def figure(self, label, filename, caption, width_in: float = 6.0) -> None:
        fp = self.doc.add_paragraph()
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fp.paragraph_format.keep_with_next = True
        fp.paragraph_format.keep_together = True
        fp.paragraph_format.space_before = Pt(6)
        fp.add_run().add_picture(str(FIG / filename), width=Inches(width_in))
        cap = self.doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.keep_together = True
        _set_run_font(cap.add_run(f"Figure {label}. {caption}"), size=Pt(10), italic=True)

    def table_caption(self, text) -> None:
        p = self.doc.add_paragraph()
        p.paragraph_format.space_before = Pt(8)
        p.paragraph_format.keep_with_next = True
        _set_run_font(p.add_run(text), size=Pt(11), bold=True)

    def table(self, header, rows, font_size: int = 10) -> None:
        table = self.doc.add_table(rows=1, cols=len(header))
        table.style = "Table Grid"
        table.alignment = WD_ALIGN_PARAGRAPH.CENTER
        hdr_row = table.rows[0]
        for j, h in enumerate(header):
            hdr_row.cells[j].text = ""
            _set_run_font(hdr_row.cells[j].paragraphs[0].add_run(h), size=Pt(font_size), bold=True)
        _row_repeat_header(hdr_row)
        _row_cant_split(hdr_row)
        for row in rows:
            tr = table.add_row()
            _row_cant_split(tr)
            for j, val in enumerate(row):
                tr.cells[j].text = ""
                _set_run_font(tr.cells[j].paragraphs[0].add_run(val), size=Pt(font_size))
        self.doc.add_paragraph()

    def page_break(self) -> None:
        self.doc.add_page_break()

    def references(self, refs) -> None:
        for r in refs:
            p = self.doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.5)
            p.paragraph_format.first_line_indent = Inches(-0.5)
            p.paragraph_format.space_after = Pt(6)
            _set_run_font(p.add_run(r))

    def save(self) -> None:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        self.doc.save(str(OUT))


def build() -> None:
    r = DocxRenderer()
    C.emit(r)
    r.save()
    print("WROTE", OUT)


if __name__ == "__main__":
    build()
