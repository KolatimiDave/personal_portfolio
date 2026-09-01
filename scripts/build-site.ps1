$ErrorActionPreference = "Stop"

$routes = Get-Content -Raw "src\data\routes.json" | ConvertFrom-Json
$site = Get-Content -Raw "src\data\site.json" | ConvertFrom-Json
$template = Get-Content -Raw "index.html"
$today = Get-Date -Format "yyyy-MM-dd"
$defaultRoute = $routes | Where-Object { $_.name -eq $site.defaultRoute } | Select-Object -First 1
if (-not $defaultRoute) {
  $defaultRoute = $routes[0]
}

function Set-MetaName {
  param($Head, $Name, $Content)
  $tag = "<meta name=""$Name"" content=""$Content"">"
  $pattern = "<meta\s+name=[""']$([regex]::Escape($Name))[""'][^>]*>"
  if ($Head -match $pattern) {
    return [regex]::Replace($Head, $pattern, $tag, 1)
  }
  return "$Head`n  $tag"
}

function Set-MetaProperty {
  param($Head, $Property, $Content)
  $tag = "<meta property=""$Property"" content=""$Content"">"
  $pattern = "<meta\s+property=[""']$([regex]::Escape($Property))[""'][^>]*>"
  if ($Head -match $pattern) {
    return [regex]::Replace($Head, $pattern, $tag, 1)
  }
  return "$Head`n  $tag"
}

function Set-LinkRel {
  param($Head, $Rel, $Href)
  $tag = "<link rel=""$Rel"" href=""$Href"">"
  $pattern = "<link\s+rel=[""']$([regex]::Escape($Rel))[""'][^>]*>"
  if ($Head -match $pattern) {
    return [regex]::Replace($Head, $pattern, $tag, 1)
  }
  return "$Head`n  $tag"
}

function Render-Route {
  param($Route)

  $html = $template
  $canonical = if ($Route.canonicalUrl) { $Route.canonicalUrl } else { "$($site.baseUrl)$($Route.url)" }
  $ogImage = "$($site.baseUrl)$($site.ogImage)"

  $html = [regex]::Replace($html, "<head>([\s\S]*?)</head>", {
    param($match)
    $head = $match.Groups[1].Value
    $head = [regex]::Replace($head, "<title>[\s\S]*?</title>", "<title>$($Route.title)</title>", 1)
    $head = Set-MetaName $head "description" $Route.description
    $head = Set-MetaProperty $head "og:title" $Route.title
    $head = Set-MetaProperty $head "og:description" $Route.description
    $head = Set-MetaProperty $head "og:url" $canonical
    $head = Set-MetaProperty $head "og:type" "website"
    $head = Set-MetaProperty $head "og:image" $ogImage
    $head = Set-MetaName $head "twitter:card" "summary_large_image"
    $head = Set-MetaName $head "twitter:title" $Route.title
    $head = Set-MetaName $head "twitter:description" $Route.description
    $head = Set-MetaName $head "twitter:image" $ogImage
    $head = Set-LinkRel $head "canonical" $canonical
    return "<head>$head</head>"
  }, 1)

  $html = $html.Replace('<a class="navbar-link active"', '<a class="navbar-link"')
foreach ($navRoute in $routes) {
    $from = '<a class="navbar-link" href="' + [regex]::Escape($navRoute.url) + '">[^<]*</a>'
    $activeClass = if ($navRoute.name -eq $Route.name) { " active" } else { "" }
    $label = $navRoute.label.Replace("&", "&amp;")
    $to = "<a class=""navbar-link$activeClass"" href=""$($navRoute.url)"">$label</a>"
    $html = [regex]::Replace($html, $from, $to, 1)
  }

  $html = [regex]::Replace($html, '<article class="([^"]*?)\s+active"', '<article class="$1"')
  $articlePattern = '<article class="([^"]*?)"\s+data-page="' + [regex]::Escape($Route.name) + '"'
  $articleReplacement = '<article class="$1 active"' + "`r`n" + '               data-page="' + $Route.name + '"'
  $html = [regex]::Replace($html, $articlePattern, $articleReplacement, 1)

  $html = [regex]::Replace($html, "<!--([\s\S]*?)-->", "")
  $html = $html.Replace("data-selecct-value", "data-select-value")
  $html = [regex]::Replace($html, '<script src="/assets/js/script\.js\?v=\d+"></script>', '<script src="/assets/js/script.js?v=4"></script>')
  $optimizedImages = @{
    "/assets/images/blog-life.png" = "/assets/images/optimized/blog-life.webp"
    "/assets/images/blog-marathon-simple.png" = "/assets/images/optimized/blog-marathon-simple.webp"
    "/assets/images/project-people-counter.jpg" = "/assets/images/optimized/project-people-counter.webp"
    "/assets/images/icon-highlight-ai.png" = "/assets/images/optimized/icon-highlight-ai.webp"
    "/assets/images/icon-highlight-community.png" = "/assets/images/optimized/icon-highlight-community.webp"
    "/assets/images/icon-highlight-data.png" = "/assets/images/optimized/icon-highlight-data.webp"
    "/assets/images/icon-highlight-ml.png" = "/assets/images/optimized/icon-highlight-ml.webp"
    "/assets/images/NLP_MediMapAI.png" = "/assets/images/optimized/NLP_MediMapAI.webp"
    "/assets/images/pneumonia-cnn-research.jpg" = "/assets/images/optimized/pneumonia-cnn-research.webp"
  }
  foreach ($source in $optimizedImages.Keys) {
    $html = $html.Replace($source, $optimizedImages[$source])
  }
  $html = [regex]::Replace($html, "[ \t]+\r?\n", "`r`n")
  $html = [regex]::Replace($html, "(\r?\n){3,}", "`r`n`r`n")
  return $html
}

foreach ($route in $routes) {
  $rendered = Render-Route $route
  if (-not (Test-Path $route.name)) {
    New-Item -ItemType Directory -Path $route.name | Out-Null
  }
  Set-Content -Path (Join-Path $route.name "index.html") -Value $rendered -NoNewline
  Set-Content -Path "$($route.name).html" -Value $rendered -NoNewline
}

$rootRoute = [pscustomobject]@{
  name = $defaultRoute.name
  label = $defaultRoute.label
  url = "/"
  title = if ($site.homeTitle) { $site.homeTitle } else { $defaultRoute.title }
  description = if ($site.homeDescription) { $site.homeDescription } else { $defaultRoute.description }
  priority = "1.0"
  changefreq = "monthly"
}
$rootRendered = Render-Route $rootRoute
Set-Content -Path "index.html" -Value $rootRendered -NoNewline
Set-Content -Path "home.html" -Value $rootRendered -NoNewline

foreach ($alias in $site.compatibilityRoutes) {
  $target = $routes | Where-Object { $_.name -eq $alias.target } | Select-Object -First 1
  if (-not $target) {
    continue
  }

  $aliasRoute = [pscustomobject]@{
    name = $target.name
    label = $target.label
    url = $alias.url
    title = $target.title
    description = $target.description
    priority = $target.priority
    changefreq = $target.changefreq
    canonicalUrl = "$($site.baseUrl)$($target.url)"
  }

  $rendered = Render-Route $aliasRoute
  $aliasDirName = $alias.url.Trim("/")
  if ($aliasDirName -and -not (Test-Path $aliasDirName)) {
    New-Item -ItemType Directory -Path $aliasDirName | Out-Null
  }
  if ($aliasDirName) {
    Set-Content -Path (Join-Path $aliasDirName "index.html") -Value $rendered -NoNewline
  }
  if ($alias.file) {
    Set-Content -Path $alias.file -Value $rendered -NoNewline
  }
}

$sitemapUrls = @(
  @{ loc = "$($site.baseUrl)/"; changefreq = "monthly"; priority = "1.0" }
)
foreach ($route in $routes) {
  if ($route.url -ne "/") {
    $sitemapUrls += @{ loc = "$($site.baseUrl)$($route.url)"; changefreq = $route.changefreq; priority = $route.priority }
  }
}
$sitemapUrls += @{ loc = "$($site.baseUrl)/assets/resume/david_olukolatimi_resume.pdf"; changefreq = "yearly"; priority = "0.5" }

$items = foreach ($url in $sitemapUrls) {
  "  <url>`n    <loc>$($url.loc)</loc>`n    <lastmod>$today</lastmod>`n    <changefreq>$($url.changefreq)</changefreq>`n    <priority>$($url.priority)</priority>`n  </url>"
}

$sitemap = "<?xml version=""1.0"" encoding=""UTF-8""?>`n<urlset xmlns=""http://www.sitemaps.org/schemas/sitemap/0.9"">`n$($items -join "`n`n")`n</urlset>`n"
Set-Content -Path "sitemap.xml" -Value $sitemap -NoNewline

$robots = "User-agent: *`nAllow: /`n`nSitemap: $($site.baseUrl)/sitemap.xml`n"
Set-Content -Path "robots.txt" -Value $robots -NoNewline

python "scripts\enhance_html_images.py"

Write-Host "Generated $($routes.Count) routes from shared route data."
