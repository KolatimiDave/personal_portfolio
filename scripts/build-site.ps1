$ErrorActionPreference = "Stop"

$routes = Get-Content -Raw "src\data\routes.json" | ConvertFrom-Json
$site = Get-Content -Raw "src\data\site.json" | ConvertFrom-Json
$template = Get-Content -Raw "src\template.html"
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

function Get-RouteSchema {
  param($Route, $Canonical)

  $personId = "$($site.baseUrl)/#person"
  $siteId = "$($site.baseUrl)/#website"
  $pageId = "$Canonical#webpage"
  $pageType = switch ($Route.name) {
    "home" { "ProfilePage" }
    "experience" { "ProfilePage" }
    "projects-research" { "CollectionPage" }
    "writing" { "Blog" }
    "services" { "OfferCatalog" }
    "contact" { "ContactPage" }
    default { "WebPage" }
  }

  $graph = [System.Collections.ArrayList]::new()
  [void]$graph.Add([ordered]@{
    "@type" = "WebSite"
    "@id" = $siteId
    url = "$($site.baseUrl)/"
    name = $site.name
    publisher = @{ "@id" = $personId }
  })
  [void]$graph.Add([ordered]@{
    "@type" = "Person"
    "@id" = $personId
    name = $site.name
    jobTitle = "Machine Learning Engineer and Data Scientist"
    url = "$($site.baseUrl)/"
    image = "$($site.baseUrl)$($site.ogImage)"
    sameAs = @($site.sameAs)
  })

  $page = [ordered]@{
    "@type" = $pageType
    "@id" = $pageId
    url = $Canonical
    name = $Route.title
    description = $Route.description
    isPartOf = @{ "@id" = $siteId }
    about = @{ "@id" = $personId }
  }

  if ($pageType -eq "ProfilePage") {
    $page.mainEntity = @{ "@id" = $personId }
  }

  if ($Route.name -ne "home") {
    $page.breadcrumb = @{ "@id" = "$Canonical#breadcrumb" }
    [void]$graph.Add([ordered]@{
      "@type" = "BreadcrumbList"
      "@id" = "$Canonical#breadcrumb"
      itemListElement = @(
        @{ "@type" = "ListItem"; position = 1; name = "Home"; item = "$($site.baseUrl)/" },
        @{ "@type" = "ListItem"; position = 2; name = $Route.label; item = $Canonical }
      )
    })
  }

  if ($Route.name -eq "services") {
    $page.itemListElement = @(
      "AI Consulting", "Custom ML Development", "Data Pipelines & ETL", "MLOps & Deployment",
      "Technical Writing", "Tutoring & Training", "Dashboards & Visualisation", "Research & Prototyping",
      "Code Review & Mentorship"
    ) | ForEach-Object {
      @{ "@type" = "Offer"; itemOffered = @{ "@type" = "Service"; name = $_; provider = @{ "@id" = $personId }; areaServed = "Worldwide" } }
    }
  }

  if ($Route.name -eq "projects-research") {
    $page.hasPart = @(
      "Healthcare Service Standardisation & Claims Platform Migration", "People Counter on Edge",
      "Computer Pointer Controller", "Systematic Hyperparameter Optimization of CNNs for Pneumonia Detection",
      "DSN Expresso Churn Prediction Challenge"
    ) | ForEach-Object { @{ "@type" = "CreativeWork"; name = $_; creator = @{ "@id" = $personId } } }
  }

  if ($Route.name -eq "writing") {
    $page.blogPost = @(
      "AI Can Do More Work Now. Can We Trust the Work?", "The Future of Work is Safe",
      "AI Models on Edge Devices with OpenVINO", "Getting into the Data Space",
      "Opportunity Cost of Knowledge", "Life is not fair: Opportunities & Exposure", "I ran my first marathon"
    ) | ForEach-Object { @{ "@type" = "BlogPosting"; headline = $_; author = @{ "@id" = $personId } } }
  }

  [void]$graph.Add($page)
  return (@{ "@context" = "https://schema.org"; "@graph" = $graph } | ConvertTo-Json -Depth 10)
}

function Keep-OnlyRouteArticle {
  param($Html, $RouteName)

  $articlePattern = '<article class="[^"]*"\s+data-page="([^"]+)">[\s\S]*?</article>'
  $matches = [regex]::Matches($Html, $articlePattern)
  $routeArticle = $matches | Where-Object { $_.Groups[1].Value -eq $RouteName } | Select-Object -First 1
  if (-not $routeArticle) {
    throw "Could not find article for route $RouteName"
  }

  $first = $matches[0]
  $last = $matches[$matches.Count - 1]
  $next = $Html.Substring(0, $first.Index) + $routeArticle.Value + $Html.Substring($last.Index + $last.Length)
  $next = [regex]::Replace($next, '<h1 class="name"([\s\S]*?)</h1>', '<p class="name"$1</p>', 1)
  $next = [regex]::Replace($next, '<h2 class="h2 article-title">([\s\S]*?)</h2>', '<h1 class="h2 article-title">$1</h1>', 1)
  return $next
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
    $schema = Get-RouteSchema $Route $canonical
    $head = [regex]::Replace($head, '<script type="application/ld\+json">[\s\S]*?</script>', "<script type=""application/ld+json"">`n$schema`n</script>", 1)
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

  $html = Keep-OnlyRouteArticle $html $Route.name
  $html = [regex]::Replace($html, "<!--([\s\S]*?)-->", "")
  $html = $html.Replace("data-selecct-value", "data-select-value")
  $html = [regex]::Replace($html, '<script src="/assets/js/script\.js\?v=\d+"></script>', '<script src="/assets/js/script.js?v=5"></script>')
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
  if ($route.url -ne "/" -and -not (Test-Path $route.name)) {
    New-Item -ItemType Directory -Path $route.name | Out-Null
  }
  if ($route.url -ne "/") {
    Set-Content -Path (Join-Path $route.name "index.html") -Value $rendered -NoNewline
  }
  if ($route.url -ne "/") {
    Set-Content -Path "$($route.name).html" -Value $rendered -NoNewline
  }
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
