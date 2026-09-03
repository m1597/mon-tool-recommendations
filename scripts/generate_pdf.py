from __future__ import annotations

import re
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
OUTPUT = ROOT / "output" / "pdf" / "MON-Tool-Recommendations.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 1.65 * cm
MARGIN_TOP = 1.45 * cm
MARGIN_BOTTOM = 1.45 * cm

NAVY = colors.HexColor("#17233C")
BLUE = colors.HexColor("#3767E8")
CYAN = colors.HexColor("#2BA7A0")
PALE = colors.HexColor("#F3F6FC")
INK = colors.HexColor("#20283A")
MUTED = colors.HexColor("#667085")
LINE = colors.HexColor("#D9E1F2")

regular_font = Path("C:/Windows/Fonts/msyh.ttc")
bold_font = Path("C:/Windows/Fonts/msyhbd.ttc")
if not regular_font.exists():
    regular_font = Path("C:/Windows/Fonts/simhei.ttf")
if not bold_font.exists():
    bold_font = regular_font

pdfmetrics.registerFont(TTFont("CN", str(regular_font)))
pdfmetrics.registerFont(TTFont("CN-Bold", str(bold_font)))

styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitleCN",
        fontName="CN-Bold",
        fontSize=28,
        leading=38,
        textColor=colors.white,
        alignment=TA_LEFT,
        spaceAfter=14,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSubtitleCN",
        fontName="CN",
        fontSize=12,
        leading=21,
        textColor=colors.HexColor("#DCE6FF"),
    )
)
styles.add(
    ParagraphStyle(
        name="CategoryCN",
        fontName="CN-Bold",
        fontSize=12,
        leading=18,
        textColor=BLUE,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="ToolTitleCN",
        fontName="CN-Bold",
        fontSize=22,
        leading=29,
        textColor=NAVY,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCN",
        fontName="CN",
        fontSize=9.5,
        leading=15,
        textColor=INK,
        spaceAfter=7,
    )
)
styles.add(
    ParagraphStyle(
        name="BulletCN",
        fontName="CN",
        fontSize=9.1,
        leading=14,
        leftIndent=10,
        firstLineIndent=-10,
        bulletIndent=0,
        textColor=INK,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="CaptionCN",
        fontName="CN",
        fontSize=7.4,
        leading=10,
        textColor=MUTED,
        alignment=TA_CENTER,
        spaceBefore=3,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="ContentsTitleCN",
        fontName="CN-Bold",
        fontSize=22,
        leading=30,
        textColor=NAVY,
        spaceAfter=14,
    )
)
styles.add(
    ParagraphStyle(
        name="ContentsCategoryCN",
        fontName="CN-Bold",
        fontSize=11,
        leading=17,
        textColor=BLUE,
        spaceBefore=6,
        spaceAfter=2,
    )
)
styles.add(
    ParagraphStyle(
        name="ContentsItemCN",
        fontName="CN",
        fontSize=8.8,
        leading=13,
        textColor=INK,
        leftIndent=10,
    )
)


def parse_readme(path: Path):
    categories = []
    current_category = None
    current_tool = None
    lines = path.read_text(encoding="utf-8").splitlines()

    for line in lines:
        if line.startswith("## ") and line[3:] not in {"目录", "关于本清单"}:
            current_category = {"name": line[3:].strip(), "tools": []}
            categories.append(current_category)
            current_tool = None
        elif line.startswith("### ") and current_category is not None:
            current_tool = {
                "name": line[4:].strip(),
                "description": "",
                "fields": [],
                "image": None,
            }
            current_category["tools"].append(current_tool)
        elif current_tool is not None:
            image_match = re.match(r"!\[[^\]]*\]\(([^)]+)\)", line)
            field_match = re.match(r"- \*\*([^*]+)\*\*\s*(.*)", line)
            if image_match:
                current_tool["image"] = image_match.group(1)
            elif field_match:
                current_tool["fields"].append((field_match.group(1), field_match.group(2)))
            elif line and not line.startswith(">") and not current_tool["description"]:
                current_tool["description"] = line.strip()

    return categories


def markdown_inline(text: str) -> str:
    parts = []
    cursor = 0
    for match in re.finditer(r"\[([^\]]+)\]\((https://[^)]+)\)", text):
        parts.append(escape(text[cursor : match.start()]))
        label = escape(match.group(1))
        url = escape(match.group(2), {'"': "&quot;"})
        parts.append(f'<link href="{url}" color="#3767E8"><u>{label}</u></link>')
        cursor = match.end()
    parts.append(escape(text[cursor:]))
    return "".join(parts)


def fit_image(path: Path, max_width=17.0 * cm, max_height=9.1 * cm):
    with PILImage.open(path) as image:
        width, height = image.size
    scale = min(max_width / width, max_height / height)
    return Image(str(path), width=width * scale, height=height * scale, hAlign="CENTER")


def page_chrome(canvas, doc):
    canvas.saveState()
    page = canvas.getPageNumber()
    if page > 1:
        canvas.setStrokeColor(LINE)
        canvas.setLineWidth(0.6)
        canvas.line(MARGIN_X, 1.05 * cm, PAGE_WIDTH - MARGIN_X, 1.05 * cm)
        canvas.setFont("CN", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(MARGIN_X, 0.62 * cm, "MON 常用工具推荐")
        canvas.drawRightString(PAGE_WIDTH - MARGIN_X, 0.62 * cm, f"{page}")
    canvas.restoreState()


def first_page(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_WIDTH, PAGE_HEIGHT, fill=1, stroke=0)
    canvas.setFillColor(BLUE)
    canvas.circle(PAGE_WIDTH - 1.2 * cm, PAGE_HEIGHT - 1.6 * cm, 5.2 * cm, fill=1, stroke=0)
    canvas.setFillColor(CYAN)
    canvas.circle(PAGE_WIDTH - 2.0 * cm, 1.5 * cm, 3.4 * cm, fill=1, stroke=0)
    canvas.restoreState()


def build_pdf():
    categories = parse_readme(README)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=MARGIN_X,
        leftMargin=MARGIN_X,
        topMargin=MARGIN_TOP,
        bottomMargin=MARGIN_BOTTOM,
        title="MON 常用工具推荐",
        author="MON",
        subject="常用软件工具的功能、优点、官网与开源仓库推荐",
    )

    story = [
        Spacer(1, 5.0 * cm),
        Paragraph("MON 常用工具推荐", styles["CoverTitleCN"]),
        Paragraph(
            "24 款日常软件的图文指南<br/>功能、优点、官方网站与开源仓库",
            styles["CoverSubtitleCN"],
        ),
        Spacer(1, 1.0 * cm),
    ]

    overview = Table(
        [
            [
                Paragraph("<b>24</b><br/>款工具", styles["BodyCN"]),
                Paragraph("<b>4</b><br/>个大类", styles["BodyCN"]),
                Paragraph("<b>图文</b><br/>界面展示", styles["BodyCN"]),
            ]
        ],
        colWidths=[4.3 * cm] * 3,
        rowHeights=[1.6 * cm],
    )
    overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#EEF3FF")),
                ("TEXTCOLOR", (0, 0), (-1, -1), NAVY),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#B8CAFA")),
                ("INNERGRID", (0, 0), (-1, -1), 0.7, colors.HexColor("#B8CAFA")),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend(
        [
            overview,
            Spacer(1, 1.0 * cm),
            Paragraph(
                "配图来自对应软件的官方网站或官方 GitHub 页面。<br/>请在法律、服务条款与内容授权允许的范围内使用相关工具。",
                styles["CoverSubtitleCN"],
            ),
            PageBreak(),
            Paragraph("目录", styles["ContentsTitleCN"]),
        ]
    )

    for category in categories:
        story.append(Paragraph(category["name"], styles["ContentsCategoryCN"]))
        names = " · ".join(tool["name"] for tool in category["tools"])
        story.append(Paragraph(escape(names), styles["ContentsItemCN"]))

    story.extend(
        [
            Spacer(1, 0.5 * cm),
            Paragraph(
                "本文档为中文版图文版；仓库同时保留中文和英文 Markdown。",
                styles["BodyCN"],
            ),
        ]
    )

    for category in categories:
        for index, tool in enumerate(category["tools"]):
            story.append(PageBreak())
            story.append(Paragraph(escape(category["name"]), styles["CategoryCN"]))
            story.append(Paragraph(escape(tool["name"]), styles["ToolTitleCN"]))

            image_path = ROOT / tool["image"] if tool["image"] else None
            if image_path and image_path.exists():
                story.append(fit_image(image_path))
                story.append(
                    Paragraph(
                        "图片来源：对应软件官方网站或官方 GitHub 页面",
                        styles["CaptionCN"],
                    )
                )

            story.append(Paragraph(markdown_inline(tool["description"]), styles["BodyCN"]))

            for label, value in tool["fields"]:
                text = f"<b>{escape(label)}</b> {markdown_inline(value)}"
                story.append(Paragraph("• " + text, styles["BulletCN"]))

            if index == len(category["tools"]) - 1:
                story.append(Spacer(1, 0.3 * cm))

    doc.build(story, onFirstPage=first_page, onLaterPages=page_chrome)
    print(OUTPUT)


if __name__ == "__main__":
    build_pdf()