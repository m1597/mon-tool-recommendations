from pathlib import Path

import pdfplumber
from pypdf import PdfReader

root = Path(__file__).resolve().parents[1]
pdf_path = root / "output" / "pdf" / "MON-Tool-Recommendations.pdf"

if not pdf_path.exists():
    raise SystemExit(f"PDF 不存在：{pdf_path}")
if pdf_path.stat().st_size < 1_000_000:
    raise SystemExit("PDF 文件异常偏小，可能没有嵌入软件图片。")

expected_tools = [
    "OBS Studio", "Bandicam", "Typora", "Foxit PDF Reader", "Arctime",
    "Geek Uninstaller", "DeskBox", "Escrcpy", "Everything", "PowerToys",
    "WizTree", "火绒安全软件", "DeepSeek Harness", "Clash Verge Rev",
    "Neat Download Manager", "Internet Download Manager", "qBittorrent",
    "SakuraFrp 启动器", "foobar2000", "Honeyview", "PotPlayer", "Spotify",
    "Kazumi", "Lossless Scaling",
]

reader = PdfReader(str(pdf_path))
if len(reader.pages) != 26:
    raise SystemExit(f"PDF 应为 26 页，实际为 {len(reader.pages)} 页。")
if (reader.metadata.title or "") != "MON 常用工具推荐":
    raise SystemExit("PDF 标题元数据不正确。")

with pdfplumber.open(pdf_path) as pdf:
    texts = [(page.extract_text() or "").strip() for page in pdf.pages]
    if any(not text for text in texts):
        raise SystemExit("PDF 中存在空白页。")
    combined = "\n".join(texts)
    if "工具索引" not in texts[1] or "无分类" not in texts[0]:
        raise SystemExit("PDF 未显示无分类封面或工具索引。")
    forbidden_categories = [
        "录屏、创作与文档", "系统、效率与开发",
        "下载与网络", "影音与娱乐",
    ]
    found_categories = [name for name in forbidden_categories if name in combined]
    if found_categories:
        raise SystemExit("PDF 仍包含分类：" + ", ".join(found_categories))
    missing = [name for name in expected_tools if name not in combined]
    if missing:
        raise SystemExit("PDF 缺少工具：" + ", ".join(missing))
    image_counts = [len(page.images) for page in pdf.pages]
    if any(count != 1 for count in image_counts[2:]):
        raise SystemExit(f"软件页图片数量异常：{image_counts[2:]}")

print(
    f"PDF 检查通过：{len(reader.pages)} 页、"
    f"{len(expected_tools)} 个工具、24 个带图软件页。"
)