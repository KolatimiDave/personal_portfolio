import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [
    ROOT / "index.html",
    ROOT / "home.html",
    *ROOT.glob("*.html"),
    *(
        ROOT / name / "index.html"
        for name in [
            "home",
            "experience",
            "projects-research",
            "writing",
            "services",
            "contact",
            "about",
            "resume",
            "portfolio",
            "blog",
        ]
    ),
]


def local_target(url: str) -> Path:
    clean = url.split("#", 1)[0].split("?", 1)[0]
    if clean.endswith("/"):
        return ROOT / clean.lstrip("/") / "index.html"
    return ROOT / clean.lstrip("/")


def main() -> None:
    failures: list[str] = []
    seen: set[Path] = set()

    for html_file in HTML_FILES:
        if html_file in seen:
            continue
        seen.add(html_file)

        if not html_file.exists():
            failures.append(f"Missing HTML file: {html_file.relative_to(ROOT)}")
            continue

        html = html_file.read_text(encoding="utf-8")
        for match in re.finditer(r'(?:href|src)="(/[^"#]+)', html):
            url = match.group(1)
            if url.startswith("//"):
                continue

            target = local_target(url)
            if not target.exists():
                failures.append(f"{html_file.relative_to(ROOT)} references missing {url}")
            elif target.is_file() and target.stat().st_size == 0:
                failures.append(f"{html_file.relative_to(ROOT)} references zero-byte file {url}")

    if failures:
        raise SystemExit("\n".join(failures))

    print("Local asset checks passed.")


if __name__ == "__main__":
    main()
