#!/usr/bin/env python
"""Render the curated Apple review response; no store requests or credentials.

Requires reportlab. This deliberately supports only the Markdown constructs
used by the accompanying response, with explicit page breaks for review.
"""
import argparse
from html import escape
from pathlib import Path
import re

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer,
)


def inline(text):
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", escape(text))


def render(source, output):
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle("ReviewBody", fontName="Helvetica", fontSize=10,
                              leading=13, spaceAfter=7, textColor=colors.HexColor("#24313B")))
    styles.add(ParagraphStyle("ReviewBullet", parent=styles["ReviewBody"],
                              leftIndent=11, firstLineIndent=-8, spaceAfter=5))
    styles.add(ParagraphStyle("ReviewHeading", fontName="Helvetica-Bold", fontSize=13,
                              leading=16, spaceBefore=4, spaceAfter=10, keepWithNext=True,
                              textColor=colors.HexColor("#214F48")))
    styles.add(ParagraphStyle("ReviewTitle", parent=styles["ReviewHeading"],
                              fontSize=19, leading=23))
    styles.add(ParagraphStyle("ReviewCaption", parent=styles["ReviewBody"],
                              fontSize=8, leading=10, alignment=TA_CENTER))
    flow = []
    for block in source.read_text().split("\n\n"):
        block = block.strip()
        if not block:
            continue
        if block == "<!-- pagebreak -->":
            flow.append(PageBreak())
        elif block.startswith("# "):
            flow.append(Paragraph(inline(block[2:]), styles["ReviewTitle"]))
        elif block.startswith("## "):
            flow.append(Paragraph(inline(block[3:]), styles["ReviewHeading"]))
        elif block.startswith("!["):
            match = re.fullmatch(r"!\[(.+)\]\((.+)\)", block)
            if not match:
                raise ValueError("Invalid image block")
            picture = Image(str((source.parent / match[2]).resolve()))
            ratio = picture.imageHeight / picture.imageWidth
            picture.drawWidth, picture.drawHeight = 375, 375 * ratio
            flow += [picture, Spacer(1, 3), Paragraph(escape(match[1]), styles["ReviewCaption"])]
        elif block.startswith("- "):
            for item in re.split(r"\n(?=- )", block):
                flow.append(Paragraph("&#8226; " + inline(" ".join(item[2:].splitlines())),
                                      styles["ReviewBullet"]))
        else:
            flow.append(Paragraph(inline(" ".join(block.splitlines())), styles["ReviewBody"]))

    def footer(canvas, document):
        canvas.saveState()
        canvas.setStrokeColor(colors.HexColor("#C9D5D2"))
        canvas.line(42, 32, A4[0] - 42, 32)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#52605D"))
        canvas.drawString(42, 20, "LazyEdit Studio | App Review clarification | 6 October 2026")
        canvas.drawRightString(A4[0] - 42, 20, str(document.page))
        canvas.restoreState()

    output.parent.mkdir(parents=True, exist_ok=True)
    SimpleDocTemplate(str(output), pagesize=A4, rightMargin=42, leftMargin=42,
                      topMargin=38, bottomMargin=43,
                      title="LazyEdit Studio - App Review Response",
                      author="LazyingArt LLC").build(flow, onFirstPage=footer, onLaterPages=footer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    render(args.source.resolve(), args.output.resolve())
