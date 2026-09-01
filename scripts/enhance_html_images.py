import re
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "home.html",
    *ROOT.glob("*.html"),
    *(ROOT / name / "index.html" for name in ["about", "resume", "portfolio", "services", "blog", "contact"]),
]


def image_size(src: str) -> tuple[int, int] | None:
    if not src.startswith("/assets/images/"):
        return None

    path = ROOT / src.lstrip("/")
    if not path.exists() or path.stat().st_size == 0:
        return None
    if path.suffix.lower() == ".svg":
        return None

    try:
        with Image.open(path) as image:
            return image.size
    except Exception:
        return None


def enhance_tag(match: re.Match[str]) -> str:
    tag = match.group(0).replace(" / decoding=", " decoding=")
    src_match = re.search(r'src="([^"]+)"', tag)
    if not src_match:
        return tag

    src = src_match.group(1)
    if src.endswith("/MyProfilePic.jpg"):
        tag = set_or_insert_attribute(tag, "width", "104")
        tag = set_or_insert_attribute(tag, "height", "104")
        if " decoding=" not in tag:
            tag = insert_attribute(tag, 'decoding="async"')
        if " loading=" not in tag:
            tag = insert_attribute(tag, 'loading="eager"')
        return tag

    size = image_size(src)
    if size is None:
        return tag

    width, height = size
    width_match = re.search(r'width="(\d+)"', tag)
    height_match = re.search(r'height="(\d+)"', tag)

    if width_match:
        declared_width = int(width_match.group(1))
        declared_height = max(1, round(height * declared_width / width))
        if height_match:
            tag = re.sub(r'height="\d+"', f'height="{declared_height}"', tag, count=1)
        else:
            tag = insert_attribute(tag, f'height="{declared_height}"')
    else:
        tag = insert_attribute(tag, f'width="{width}"')
        tag = insert_attribute(tag, f'height="{height}"')

    if " decoding=" not in tag:
        tag = insert_attribute(tag, 'decoding="async"')
    if " loading=" not in tag:
        loading = "eager" if "MyProfilePic" in src or "title_image" in src else "lazy"
        tag = insert_attribute(tag, f'loading="{loading}"')

    return tag


def insert_attribute(tag: str, attribute: str) -> str:
    tag = tag.replace(" / decoding=", " decoding=")
    if tag.endswith("/>"):
        return f"{tag[:-2].rstrip()} {attribute}>"
    return f"{tag[:-1]} {attribute}>"


def set_or_insert_attribute(tag: str, name: str, value: str) -> str:
    if re.search(rf'{name}="\d+"', tag):
        return re.sub(rf'{name}="\d+"', f'{name}="{value}"', tag, count=1)
    return insert_attribute(tag, f'{name}="{value}"')


def main() -> None:
    seen = set()
    for html_file in HTML_FILES:
        if html_file in seen or not html_file.exists():
            continue
        seen.add(html_file)
        html = html_file.read_text(encoding="utf-8")
        enhanced = re.sub(r"<img\b[^>]*>", enhance_tag, html)
        html_file.write_text(enhanced, encoding="utf-8")

    print(f"Enhanced images in {len(seen)} HTML files.")


if __name__ == "__main__":
    main()
