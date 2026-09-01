from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "index.html": ("https://davidolukolatimi.cv/", "/", "Home"),
    "experience/index.html": ("https://davidolukolatimi.cv/experience/", "/experience/", "Experience"),
    "projects-research/index.html": ("https://davidolukolatimi.cv/projects-research/", "/projects-research/", "Projects &amp; Research"),
    "writing/index.html": ("https://davidolukolatimi.cv/writing/", "/writing/", "Writing"),
    "services/index.html": ("https://davidolukolatimi.cv/services/", "/services/", "Services"),
    "contact/index.html": ("https://davidolukolatimi.cv/contact/", "/contact/", "Contact Me"),
}
REMOVED = [
    "about/index.html",
    "resume/index.html",
    "portfolio/index.html",
    "blog/index.html",
]


def get(pattern: str, text: str, path: str) -> str:
    match = re.search(pattern, text)
    if not match:
        raise AssertionError(f"{path} missing pattern {pattern}")
    return match.group(1)


def main() -> None:
    failures: list[str] = []

    for path, (expected_canonical, expected_href, expected_label) in EXPECTED.items():
        html = (ROOT / path).read_text(encoding="utf-8")
        canonical = get(r'<link rel="canonical" href="([^"]+)"', html, path)
        active = re.search(r'<a class="navbar-link active" href="([^"]+)">([^<]+)</a>', html)
        h1s = re.findall(r"<h1\b", html)
        articles = re.findall(r"<article\b", html)

        if canonical != expected_canonical:
            failures.append(f"{path} canonical {canonical!r} != {expected_canonical!r}")
        if not active:
            failures.append(f"{path} missing active nav link")
        elif active.groups() != (expected_href, expected_label):
            failures.append(f"{path} active nav {active.groups()!r} != {(expected_href, expected_label)!r}")
        if len(h1s) != 1:
            failures.append(f"{path} expected exactly one h1, found {len(h1s)}")
        if len(articles) != 1:
            failures.append(f"{path} expected exactly one article, found {len(articles)}")

    for path in REMOVED:
        if (ROOT / path).exists():
            failures.append(f"Removed legacy route still exists: {path}")

    if failures:
        raise SystemExit("\n".join(failures))

    print("Route metadata checks passed.")


if __name__ == "__main__":
    main()
