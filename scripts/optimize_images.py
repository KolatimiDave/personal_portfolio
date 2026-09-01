from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "assets" / "images"
OUTPUT_DIR = SOURCE_DIR / "optimized"
MAX_WIDTH = 1400
QUALITY = 78
TARGETS = {
    "blog-life.png",
    "blog-marathon-simple.png",
    "project-people-counter.jpg",
    "icon-highlight-ai.png",
    "icon-highlight-community.png",
    "icon-highlight-data.png",
    "icon-highlight-ml.png",
    "NLP_MediMapAI.png",
    "pneumonia-cnn-research.jpg",
}


def optimize_image(path: Path) -> None:
    with Image.open(path) as image:
        image = image.convert("RGB")
        image.thumbnail((MAX_WIDTH, MAX_WIDTH), Image.Resampling.LANCZOS)
        output_path = OUTPUT_DIR / f"{path.stem}.webp"
        image.save(output_path, "WEBP", quality=QUALITY, method=6)


def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)
    optimized = 0

    for filename in sorted(TARGETS):
      path = SOURCE_DIR / filename
      if path.exists() and path.stat().st_size > 0:
          optimize_image(path)
          optimized += 1

    print(f"Optimized {optimized} referenced images.")


if __name__ == "__main__":
    main()
