from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MARKERS = [
    "Modal text",
    "lorem ipsum",
    "TODO",
    "FIXME",
    "Â",
    "â",
    "ðŸ",
    "�",
    "data-selecct-value",
    "/script.js?v=3",
    "FastAPI Web Service",
    "Date of Birth",
    "DATE OF BIRTH",
    "Birthday",
    "November 11",
    "Machine Learning Engineer / Data Engineer",
    "AI Engineer / AI Pipeline",
    "Freelance AI Engineer",
    "Cloud & DevOps (Azure, AWS, Docker, CI/CD)",
    "Analytics & BI (PowerBI, Notebooks)",
    "top-social-list",
    "bottom-social-list",
    'data-page="resume"',
    'data-page="portfolio"',
    'data-page="blog"',
]
SEARCH_ROOTS = [
    ROOT / "README.md",
    ROOT / "assets" / "js" / "script.js",
    ROOT / "assets" / "css" / "style.css",
    ROOT / "backend" / "main.py",
    *ROOT.glob("*.html"),
    *(ROOT / name / "index.html" for name in [
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
    ]),
]


def main() -> None:
    failures: list[str] = []
    seen: set[Path] = set()

    for path in SEARCH_ROOTS:
        if path in seen or not path.exists():
            continue
        seen.add(path)
        text = path.read_text(encoding="utf-8")
        for marker in MARKERS:
            if marker in text:
                failures.append(f"{path.relative_to(ROOT)} contains {marker!r}")

    if failures:
        raise SystemExit("\n".join(failures))

    print("Content marker checks passed.")


if __name__ == "__main__":
    main()
