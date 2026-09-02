import { access, readdir, readFile, stat } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const routes = JSON.parse(await readFile(path.join(root, "src/data/routes.json"), "utf8"));
const failures = [];
const referencedLocalAssets = new Set();

async function exists(relativePath) {
  try {
    await access(path.join(root, relativePath));
    return true;
  } catch {
    return false;
  }
}

async function collectHtmlFiles(dir = root) {
  const entries = await readdir(dir, { withFileTypes: true });
  const files = [];

  for (const entry of entries) {
    if (entry.name === ".git" || entry.name === "node_modules") continue;
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      files.push(...await collectHtmlFiles(fullPath));
    } else if (entry.name.endsWith(".html") && !fullPath.includes(`${path.sep}src${path.sep}`)) {
      files.push(fullPath);
    }
  }

  return files;
}

function asArray(value) {
  return Array.isArray(value) ? value : [value];
}

function validateStructuredData(html, relative) {
  const scripts = [...html.matchAll(/<script\s+type=["']application\/ld\+json["'][^>]*>([\s\S]*?)<\/script>/gi)];

  for (const [index, script] of scripts.entries()) {
    let data;
    try {
      data = JSON.parse(script[1]);
    } catch (error) {
      failures.push(`Invalid JSON-LD in ${relative} script ${index + 1}: ${error.message}`);
      continue;
    }

    const graph = data["@graph"] ? asArray(data["@graph"]) : [data];
    const personIds = new Set(
      graph
        .filter((node) => node && asArray(node["@type"]).includes("Person") && node["@id"])
        .map((node) => node["@id"])
    );

    for (const node of graph) {
      if (!node || !asArray(node["@type"]).includes("ProfilePage")) continue;

      if (!node.mainEntity) {
        failures.push(`ProfilePage missing mainEntity in ${relative}`);
        continue;
      }

      const mainEntityId = node.mainEntity["@id"];
      if (!mainEntityId) {
        failures.push(`ProfilePage mainEntity missing @id in ${relative}`);
      } else if (!personIds.has(mainEntityId)) {
        failures.push(`ProfilePage mainEntity does not reference a Person node in ${relative}: ${mainEntityId}`);
      }
    }
  }
}

for (const route of routes) {
  const file = route.url === "/" ? "index.html" : `${route.name}/index.html`;
  if (!await exists(file)) failures.push(`Missing generated route: ${file}`);
}

for (const legacyRoute of ["about", "resume", "portfolio", "blog"]) {
  if (await exists(`${legacyRoute}/index.html`) || await exists(`${legacyRoute}.html`)) {
    failures.push(`Removed legacy route still exists: ${legacyRoute}`);
  }
}

for (const file of await collectHtmlFiles()) {
  const html = await readFile(file, "utf8");
  const relative = path.relative(root, file);

  if (/Modal text is loaded|lorem ipsum|TODO|FIXME|â|ðŸ|�/i.test(html)) {
    failures.push(`Placeholder or encoding artifact found in ${relative}`);
  }

  if (!/<meta name="description" content="[^"]{30,}"/i.test(html)) {
    failures.push(`Missing useful meta description in ${relative}`);
  }

  if (!/<meta property="og:image"/i.test(html)) {
    failures.push(`Missing Open Graph image in ${relative}`);
  }

  validateStructuredData(html, relative);

  const h1Count = (html.match(/<h1\b/gi) || []).length;
  const articleCount = (html.match(/<article\b/gi) || []).length;
  if (h1Count !== 1) failures.push(`Expected exactly one h1 in ${relative}, found ${h1Count}`);
  if (articleCount !== 1) failures.push(`Expected exactly one article in ${relative}, found ${articleCount}`);

  const ids = [...html.matchAll(/\sid="([^"]+)"/g)].map((match) => match[1]);
  const duplicateIds = ids.filter((id, index) => ids.indexOf(id) !== index);
  if (duplicateIds.length) {
    failures.push(`Duplicate ids in ${relative}: ${[...new Set(duplicateIds)].join(", ")}`);
  }

  const localLinks = [...html.matchAll(/(?:href|src)="(\/[^"#?]+)[^"]*"/g)].map((match) => match[1]);
  for (const link of localLinks) {
    if (link.startsWith("//")) continue;
    referencedLocalAssets.add(link);
    const target = link.endsWith("/") ? `${link.slice(1)}index.html` : link.slice(1);
    if (!await exists(target)) failures.push(`Broken local asset/link in ${relative}: ${link}`);
  }
}

const imageEntries = await readdir(path.join(root, "assets/images"), { withFileTypes: true });
for (const entry of imageEntries) {
  if (!entry.isFile()) continue;
  const imageStat = await stat(path.join(root, "assets/images", entry.name));
  if (imageStat.size === 0) failures.push(`Zero-byte image: assets/images/${entry.name}`);
  const publicPath = `/assets/images/${entry.name}`;
  if (referencedLocalAssets.has(publicPath) && imageStat.size > 1_000_000 && !entry.name.endsWith(".webp")) {
    failures.push(`Large referenced image: assets/images/${entry.name}`);
  }
}

if (failures.length) {
  throw new Error(failures.join("\n"));
}

console.log("Site checks passed.");
