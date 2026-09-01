import { mkdir, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const sourceDir = path.join(root, "assets/images");
const outputDir = path.join(root, "assets/images/optimized");
const supported = new Set([".jpg", ".jpeg", ".png"]);
const targets = new Set([
  "blog-life.png",
  "blog-marathon-simple.png",
  "project-people-counter.jpg",
  "icon-highlight-ai.png",
  "icon-highlight-community.png",
  "icon-highlight-data.png",
  "icon-highlight-ml.png",
  "NLP_MediMapAI.png",
  "pneumonia-cnn-research.jpg"
]);

await mkdir(outputDir, { recursive: true });

const entries = await readdir(sourceDir, { withFileTypes: true });
let optimizedCount = 0;

for (const entry of entries) {
  if (!entry.isFile()) continue;
  const ext = path.extname(entry.name).toLowerCase();
  if (!supported.has(ext)) continue;
  if (!targets.has(entry.name)) continue;

  const sourcePath = path.join(sourceDir, entry.name);
  const sourceStat = await stat(sourcePath);
  if (sourceStat.size === 0) continue;

  const outputName = `${path.basename(entry.name, ext)}.webp`;
  const outputPath = path.join(outputDir, outputName);

  await sharp(sourcePath)
    .rotate()
    .resize({ width: 1400, height: 1400, fit: "inside", withoutEnlargement: true })
    .webp({ quality: 78, effort: 5 })
    .toFile(outputPath);

  optimizedCount += 1;
}

console.log(`Optimized ${optimizedCount} images to ${path.relative(root, outputDir)}.`);
