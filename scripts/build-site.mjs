import { mkdir, readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const routes = JSON.parse(await readFile(path.join(root, "src/data/routes.json"), "utf8"));
const site = JSON.parse(await readFile(path.join(root, "src/data/site.json"), "utf8"));
const sourceHtml = await readFile(path.join(root, "src/template.html"), "utf8");
const today = new Date().toISOString().slice(0, 10);

const routeByName = new Map(routes.map((route) => [route.name, route]));
const defaultRoute = routeByName.get(site.defaultRoute) || routes[0];
const rootRoute = {
  ...defaultRoute,
  url: "/",
  priority: "1.0",
  title: site.homeTitle || defaultRoute.title,
  description: site.homeDescription || defaultRoute.description
};
const compatibilityRoutes = site.compatibilityRoutes || [];
const routeUrls = new Set(routes.map((route) => route.url));

function escapeRegExp(value) {
  return value.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function escapeHtml(value) {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

function stripInternalComments(html) {
  return html.replace(/<!--[\s\S]*?-->/g, "");
}

function setMetaTag(head, name, content) {
  const escapedName = escapeRegExp(name);
  const tag = `<meta name="${name}" content="${content}">`;
  const pattern = new RegExp(`<meta\\s+name=["']${escapedName}["'][^>]*>`, "i");
  return pattern.test(head) ? head.replace(pattern, tag) : `${head}\n  ${tag}`;
}

function setPropertyTag(head, property, content) {
  const escapedProperty = escapeRegExp(property);
  const tag = `<meta property="${property}" content="${content}">`;
  const pattern = new RegExp(`<meta\\s+property=["']${escapedProperty}["'][^>]*>`, "i");
  return pattern.test(head) ? head.replace(pattern, tag) : `${head}\n  ${tag}`;
}

function setLinkTag(head, rel, href) {
  const escapedRel = escapeRegExp(rel);
  const tag = `<link rel="${rel}" href="${href}">`;
  const pattern = new RegExp(`<link\\s+rel=["']${escapedRel}["'][^>]*>`, "i");
  return pattern.test(head) ? head.replace(pattern, tag) : `${head}\n  ${tag}`;
}

function absoluteUrl(routeUrl) {
  return new URL(routeUrl, site.baseUrl).href;
}

function routeSchema(route, canonical) {
  const siteId = `${site.baseUrl}/#website`;
  const personId = `${site.baseUrl}/#person`;
  const pageId = `${canonical}#webpage`;
  const graph = [
    {
      "@type": "WebSite",
      "@id": siteId,
      "url": `${site.baseUrl}/`,
      "name": site.name,
      "publisher": { "@id": personId }
    },
    {
      "@type": "Person",
      "@id": personId,
      "name": site.name,
      "jobTitle": "Machine Learning Engineer and Data Scientist",
      "url": `${site.baseUrl}/`,
      "image": new URL(site.ogImage, site.baseUrl).href,
      "sameAs": site.sameAs || []
    }
  ];

  const pageType = {
    home: "ProfilePage",
    experience: "ProfilePage",
    "projects-research": "CollectionPage",
    writing: "Blog",
    services: "OfferCatalog",
    contact: "ContactPage"
  }[route.name] || "WebPage";

  const pageNode = {
    "@type": pageType,
    "@id": pageId,
    "url": canonical,
    "name": route.title,
    "description": route.description,
    "isPartOf": { "@id": siteId },
    "about": { "@id": personId }
  };

  if (pageType === "ProfilePage") {
    pageNode.mainEntity = { "@id": personId };
  }

  if (route.name !== "home") {
    pageNode.breadcrumb = { "@id": `${canonical}#breadcrumb` };
    graph.push({
      "@type": "BreadcrumbList",
      "@id": `${canonical}#breadcrumb`,
      "itemListElement": [
        {
          "@type": "ListItem",
          "position": 1,
          "name": "Home",
          "item": `${site.baseUrl}/`
        },
        {
          "@type": "ListItem",
          "position": 2,
          "name": route.label,
          "item": canonical
        }
      ]
    });
  }

  if (route.name === "services") {
    pageNode.itemListElement = [
      "AI Consulting",
      "Custom ML Development",
      "Data Pipelines & ETL",
      "MLOps & Deployment",
      "Technical Writing",
      "Tutoring & Training",
      "Dashboards & Visualisation",
      "Research & Prototyping",
      "Code Review & Mentorship"
    ].map((name) => ({
      "@type": "Offer",
      "itemOffered": {
        "@type": "Service",
        "name": name,
        "provider": { "@id": personId },
        "areaServed": "Worldwide"
      }
    }));
  }

  if (route.name === "projects-research") {
    pageNode.hasPart = [
      "Healthcare Service Standardisation & Claims Platform Migration",
      "People Counter on Edge",
      "Computer Pointer Controller",
      "Systematic Hyperparameter Optimization of CNNs for Pneumonia Detection",
      "DSN Expresso Churn Prediction Challenge"
    ].map((name) => ({
      "@type": "CreativeWork",
      "name": name,
      "creator": { "@id": personId }
    }));
  }

  if (route.name === "writing") {
    pageNode.blogPost = [
      "AI Can Do More Work Now. Can We Trust the Work?",
      "The Future of Work is Safe",
      "AI Models on Edge Devices with OpenVINO",
      "Getting into the Data Space",
      "Opportunity Cost of Knowledge",
      "Life is not fair: Opportunities & Exposure",
      "I ran my first marathon"
    ].map((headline) => ({
      "@type": "BlogPosting",
      "headline": headline,
      "author": { "@id": personId }
    }));
  }

  graph.push(pageNode);
  return JSON.stringify({ "@context": "https://schema.org", "@graph": graph }, null, 2);
}

function updateHead(html, route) {
  const canonical = route.canonicalUrl || absoluteUrl(route.url);
  const ogImage = new URL(site.ogImage, site.baseUrl).href;

  return html.replace(/<head>([\s\S]*?)<\/head>/i, (_match, headContent) => {
    let head = headContent;
    head = head.replace(/<title>[\s\S]*?<\/title>/i, `<title>${route.title}</title>`);
    head = setMetaTag(head, "description", route.description);
    head = setPropertyTag(head, "og:title", route.title);
    head = setPropertyTag(head, "og:description", route.description);
    head = setPropertyTag(head, "og:url", canonical);
    head = setPropertyTag(head, "og:type", "website");
    head = setPropertyTag(head, "og:image", ogImage);
    head = setMetaTag(head, "twitter:card", "summary_large_image");
    head = setMetaTag(head, "twitter:title", route.title);
    head = setMetaTag(head, "twitter:description", route.description);
    head = setMetaTag(head, "twitter:image", ogImage);
    head = setLinkTag(head, "canonical", canonical);
    head = head.replace(
      /<script type="application\/ld\+json">[\s\S]*?<\/script>/i,
      `<script type="application/ld+json">\n${routeSchema(route, canonical)}\n</script>`
    );
    return `<head>${head}</head>`;
  });
}

function setActiveRoute(html, routeName) {
  let next = html.replace(/<a class="navbar-link active"/g, '<a class="navbar-link"');
  for (const route of routes) {
    const href = escapeRegExp(route.url);
    const navPattern = new RegExp(`<a class="navbar-link" href="${href}">[^<]*</a>`);
    const navValue = `<a class="navbar-link${route.name === routeName ? " active" : ""}" href="${route.url}">${escapeHtml(route.label)}</a>`;
    next = next.replace(navPattern, navValue);
  }

  next = next.replace(/<article class="([^"]*?)\s+active"/g, '<article class="$1"');
  const articlePattern = new RegExp(`<article class="([^"]*?)"\\s+data-page="${escapeRegExp(routeName)}"`, "m");
  return next.replace(articlePattern, '<article class="$1 active"\n               data-page="' + routeName + '"');
}

function keepOnlyRouteArticle(html, routeName) {
  const articlePattern = /<article class="[^"]*"\s+data-page="([^"]+)">[\s\S]*?<\/article>/g;
  const articles = [...html.matchAll(articlePattern)];
  const routeArticle = articles.find((match) => match[1] === routeName);

  if (!routeArticle) {
    throw new Error(`Could not find article for route ${routeName}`);
  }

  let next = html.slice(0, articles[0].index) + routeArticle[0] + html.slice(articles.at(-1).index + articles.at(-1)[0].length);
  next = next.replace(/<h1 class="name"([\s\S]*?)<\/h1>/, '<p class="name"$1</p>');
  next = next.replace(/<h2 class="h2 article-title">([\s\S]*?)<\/h2>/, '<h1 class="h2 article-title">$1</h1>');
  return next;
}

function cleanHtml(html) {
  const optimizedImages = {
    "/assets/images/blog-life.png": "/assets/images/optimized/blog-life.webp",
    "/assets/images/blog-marathon-simple.png": "/assets/images/optimized/blog-marathon-simple.webp",
    "/assets/images/project-people-counter.jpg": "/assets/images/optimized/project-people-counter.webp",
    "/assets/images/icon-highlight-ai.png": "/assets/images/optimized/icon-highlight-ai.webp",
    "/assets/images/icon-highlight-community.png": "/assets/images/optimized/icon-highlight-community.webp",
    "/assets/images/icon-highlight-data.png": "/assets/images/optimized/icon-highlight-data.webp",
    "/assets/images/icon-highlight-ml.png": "/assets/images/optimized/icon-highlight-ml.webp",
    "/assets/images/NLP_MediMapAI.png": "/assets/images/optimized/NLP_MediMapAI.webp",
    "/assets/images/pneumonia-cnn-research.jpg": "/assets/images/optimized/pneumonia-cnn-research.webp"
  };

  let cleaned = stripInternalComments(html)
    .replace(/<div data-modal-text>\s*<p>\s*Modal text is loaded dynamically from the testimonial cards\s*above via script\.js\. You can customize the text, role, and\s*dates for each testimonial as needed\.\s*<\/p>\s*<\/div>/g, "<div data-modal-text></div>")
    .replace(/data-selecct-value/g, "data-select-value")
    .replace(/<script src="\/assets\/js\/script\.js\?v=\d+"><\/script>/g, '<script src="/assets/js/script.js?v=5"></script>')
    .replace(/[ \t]+$/gm, "")
    .replace(/\n{3,}/g, "\n\n");

  for (const [source, optimized] of Object.entries(optimizedImages)) {
    cleaned = cleaned.replaceAll(source, optimized);
  }

  return cleaned;
}

async function writeRoute(route, html) {
  const rendered = cleanHtml(keepOnlyRouteArticle(setActiveRoute(updateHead(html, route), route.name), route.name));
  const routeDir = path.join(root, route.url.replace(/^\//, "").replace(/\/$/, ""));
  if (route.url !== "/") {
    await mkdir(routeDir, { recursive: true });
    await writeFile(path.join(routeDir, "index.html"), rendered);
  }
  if (route.url !== "/") {
    await writeFile(path.join(root, `${route.name}.html`), rendered);
  }
}

for (const route of routes) {
  await writeRoute(route, sourceHtml);
}

const rootRendered = cleanHtml(keepOnlyRouteArticle(setActiveRoute(updateHead(sourceHtml, rootRoute), defaultRoute.name), defaultRoute.name));
await writeFile(path.join(root, "index.html"), rootRendered);

for (const alias of compatibilityRoutes) {
  const target = routeByName.get(alias.target);
  if (!target) continue;
  const aliasRoute = {
    ...target,
    url: alias.url,
    canonicalUrl: absoluteUrl(target.url)
  };
  if (!routeUrls.has(alias.url)) continue;
  const rendered = cleanHtml(keepOnlyRouteArticle(setActiveRoute(updateHead(sourceHtml, aliasRoute), target.name), target.name));
  const aliasDir = path.join(root, alias.url.replace(/^\//, "").replace(/\/$/, ""));
  await mkdir(aliasDir, { recursive: true });
  await writeFile(path.join(aliasDir, "index.html"), rendered);
  if (alias.file) {
    await writeFile(path.join(root, alias.file), rendered);
  }
}

const sitemapUrls = [
  { loc: `${site.baseUrl}/`, changefreq: "monthly", priority: "1.0" },
  ...routes.filter((route) => route.url !== "/").map((route) => ({
    loc: `${site.baseUrl}${route.url}`,
    changefreq: route.changefreq,
    priority: route.priority
  })),
  {
    loc: `${site.baseUrl}/assets/resume/david_olukolatimi_resume.pdf`,
    changefreq: "yearly",
    priority: "0.5"
  }
];

const sitemap = `<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
${sitemapUrls.map((url) => `  <url>
    <loc>${url.loc}</loc>
    <lastmod>${today}</lastmod>
    <changefreq>${url.changefreq}</changefreq>
    <priority>${url.priority}</priority>
  </url>`).join("\n\n")}
</urlset>
`;

await writeFile(path.join(root, "sitemap.xml"), sitemap);
await writeFile(path.join(root, "robots.txt"), `User-agent: *
Allow: /

Sitemap: ${site.baseUrl}/sitemap.xml
`);

console.log(`Generated ${routes.length} routes from shared route data.`);
