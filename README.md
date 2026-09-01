# David Olukolatimi - Personal Portfolio

A responsive personal portfolio for David Olukolatimi, focused on machine learning engineering, data science, MLOps, cloud work, AI projects, services, writing, and contact enquiries.

The site stays intentionally lightweight: generated static HTML, shared CSS, vanilla JavaScript, and a small FastAPI backend for the contact form.

## Features

- Responsive portfolio pages for Home, Experience, Projects & Research, Writing, Services, and Contact Me
- Shared route metadata for page titles, descriptions, canonical URLs, sitemap, and social cards
- Vanilla JavaScript interactions for navigation, theme preference, filters, recommendations, service actions, currency display, and contact validation
- FastAPI contact endpoint using Resend
- No analytics or visitor tracking

## Project Structure

```plaintext
/
  assets/
    css/
    images/
    js/
    resume/
  backend/
    main.py
    requirements.txt
  scripts/
    build-site.mjs
    build-site.ps1
    check_content_markers.py
    check_local_assets.py
    check_route_metadata.py
    check-site.mjs
    enhance_html_images.py
    optimize-images.mjs
    optimize_images.py
  src/
    data/
      routes.json
      site.json
  index.html
  experience/
  projects-research/
  writing/
  services/
  contact/
  sitemap.xml
  robots.txt
```

## Local Workflow

Install Node.js, then run:

```bash
npm install
npm run build
npm run check
```

On Windows without Node available, the PowerShell generator can update the static pages:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-site.ps1
```

Image optimization uses Sharp:

```bash
npm run optimize:images
```

Review the generated files after optimization before switching image references to the optimized versions.

## Backend

The contact API lives in `backend/main.py`.

Required environment variables:

- `RESEND_API_KEY`
- `TO_EMAIL`
- `FROM_EMAIL`

Optional environment variables:

- `RATE_LIMIT_WINDOW_SECONDS` defaults to `900`
- `RATE_LIMIT_MAX_REQUESTS` defaults to `5`

Local backend start:

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## Render Deployment

Frontend:

- Build command: `npm install && npm run build`
- Publish directory: repository root, or the static directory configured for your Render static site

Backend:

- Root directory: `backend`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Add the required Resend environment variables listed above

Keep frontend domains aligned with the backend CORS allowlist in `backend/main.py`.

## Route Notes

Primary public routes:

- `/`
- `/experience/`
- `/projects-research/`
- `/writing/`
- `/services/`
- `/contact/`

Older links should be redirected at the host level when supported:

- `/about/` -> `/`
- `/resume/` -> `/experience/`
- `/portfolio/` -> `/projects-research/`
- `/blog/` -> `/writing/`
