import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"


def extract_between(text: str, start_marker: str, end_marker: str) -> str:
    start = text.index(start_marker)
    end = text.index(end_marker, start)
    return text[start:end]


def extract_between_any(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.index(start_marker)
    end = min(
        text.index(marker, start)
        for marker in end_markers
        if marker in text[start:]
    )
    return text[start:end]


def replace_articles(html: str, articles: str) -> str:
    start = html.index('      <article class="about')
    end = html.index("\n\n    </div>", start)
    return html[:start] + articles + html[end:]


def main() -> None:
    html = INDEX.read_text(encoding="utf-8")

    recommendations_and_modal = extract_between(
        html,
        '        <section class="recommendations-section">',
        '        <section class="clients">',
    )
    clients = extract_between(
        html,
        '        <section class="clients">',
        "\n\n      </article>",
    )
    services_article = extract_between_any(
        html,
        '      <article class="services-page"',
        [
            '      <article class="blog"',
            '      <article class="blog writing"',
        ],
    )
    contact_inner = extract_between(
        html,
        '        <section class="contact-form">',
        "\n\n      </article>",
    )

    nav = """      <nav class="navbar">

        <ul class="navbar-list">

          <li class="navbar-item"><a class="navbar-link active" href="/">Home</a></li>

          <li class="navbar-item"><a class="navbar-link" href="/experience/">Experience</a></li>

          <li class="navbar-item"><a class="navbar-link" href="/projects-research/">Projects &amp; Research</a></li>

          <li class="navbar-item"><a class="navbar-link" href="/writing/">Writing</a></li>

          <li class="navbar-item"><a class="navbar-link" href="/services/">Services</a></li>

          <li class="navbar-item"><a class="navbar-link" href="/contact/">Contact Me</a></li>
        </ul>

        <button class="theme-btn" data-theme-toggle aria-label="Toggle light/dark mode">
          <ion-icon name="sunny-outline" class="theme-icon"></ion-icon>
        </button>

      </nav>"""

    home_article = f"""      <article class="about home active"
               data-page="home">

        <header class="home-hero">
          <h2 class="h2 article-title">David Olukolatimi</h2>
          <p class="hero-title">Data Scientist &amp; Machine Learning Engineer</p>
          <p class="hero-summary">
            Building production machine learning, AI, and data systems that move from experimentation into practical business use.
          </p>
          <div class="hero-actions">
            <a href="/experience/" class="hero-action">View Experience</a>
            <a href="/projects-research/" class="hero-action secondary">Projects &amp; Research</a>
            <a href="/assets/resume/david_olukolatimi_resume.pdf" class="hero-action secondary" download>Download Resume</a>
          </div>
        </header>

        <section class="about-text">
          <p>
            I help turn complex data into useful systems and clear insights that support better decisions. My work spans data science, machine learning engineering, and AI systems across insurance, education technology, and client projects. I have worked on everything from large scale data processing and model development to APIs, deployment, monitoring, and business automation.
          </p>
          <p>
            My focus is practical. I like taking a problem from raw data and experimentation through to something people can actually use. That has included healthcare service standardisation, vehicle valuation, recommendation systems, AI evaluation pipelines, analytics workflows, and client machine learning solutions.
          </p>
          <p>
            I also enjoy writing, research, mentoring, and community learning. I share ideas through technical articles, open source projects, published research, and professional communities. I care about making difficult ideas easier to understand and building with people who value curiosity, clarity, and useful work.
          </p>
        </section>

        <section class="service">
          <h3 class="h3 service-title">Quick Highlights</h3>
          <ul class="service-list">
            <li class="service-item">
              <div class="service-icon-box">
                <img src="/assets/images/optimized/icon-highlight-ml.webp" alt="Machine learning pipeline icon" width="40" height="40" decoding="async" loading="lazy">
              </div>
              <div class="service-content-box">
                <h4 class="h4 service-item-title">Production ML &amp; MLOps</h4>
                <p class="service-item-text">Designed and deployed machine learning services using FastAPI, Docker, Kubernetes, GCP, CI/CD, monitoring, and production workflows. My work includes turning models into reliable services that support live business processes.</p>
              </div>
            </li>
            <li class="service-item">
              <div class="service-icon-box">
                <img src="/assets/images/optimized/icon-highlight-ai.webp" alt="AI applications icon" width="40" height="40" decoding="async" loading="lazy">
              </div>
              <div class="service-content-box">
                <h4 class="h4 service-item-title">AI Applications &amp; Automation</h4>
                <p class="service-item-text">Built applied AI systems across healthcare, pricing, recommendations, and automated evaluation, including a healthcare matching pipeline that processed approximately 8 million legacy service records during a claims platform migration.</p>
              </div>
            </li>
            <li class="service-item">
              <div class="service-icon-box">
                <img src="/assets/images/optimized/icon-highlight-data.webp" alt="Data engineering icon" width="40" height="40" decoding="async" loading="lazy">
              </div>
              <div class="service-content-box">
                <h4 class="h4 service-item-title">Data Engineering</h4>
                <p class="service-item-text">Built Python and SQL ETL workflows that move, transform, and prepare production data for analytics and machine learning, including pipelines supporting more than 20 operational dashboards.</p>
              </div>
            </li>
            <li class="service-item">
              <div class="service-icon-box">
                <img src="/assets/images/optimized/icon-highlight-community.webp" alt="Community and collaboration icon" width="40" height="40" decoding="async" loading="lazy">
              </div>
              <div class="service-content-box">
                <h4 class="h4 service-item-title">Community &amp; Collaboration</h4>
                <p class="service-item-text">Co-led the AXA Data Science Community and taught practical data science skills to more than 40 employees. I have also contributed to Data Science Nigeria learning initiatives and technical communities.</p>
              </div>
            </li>
          </ul>
        </section>

        <section class="proof-strip">
          <div class="proof-card">
            <strong>8M</strong>
            <span>Legacy healthcare records processed</span>
            <a class="proof-link" href="/experience/" aria-label="View healthcare standardisation experience">Healthcare standardisation <span aria-hidden="true">-&gt;</span></a>
          </div>
          <div class="proof-card">
            <strong>30%</strong>
            <span>Throughput and latency improvement</span>
            <a class="proof-link" href="/experience/" aria-label="View ExamRocket AI pipelines experience">ExamRocket AI pipelines <span aria-hidden="true">-&gt;</span></a>
          </div>
          <div class="proof-card">
            <strong>2nd Place</strong>
            <span>DSN Expresso Churn Prediction</span>
            <a class="proof-link" href="/projects-research/" aria-label="View DSN Expresso competition solution">Competition solution <span aria-hidden="true">-&gt;</span></a>
          </div>
          <div class="proof-card">
            <strong>Published</strong>
            <span>Peer-reviewed medical AI research</span>
            <a class="proof-link" href="/projects-research/" aria-label="View pneumonia CNN paper">Pneumonia CNN paper <span aria-hidden="true">-&gt;</span></a>
          </div>
        </section>

        <section class="featured-work">
          <h3 class="h3 service-title">Featured Work</h3>
          <ul class="feature-card-list">
            <li class="feature-card">
              <p class="feature-card-kicker">Professional ML and Data System</p>
              <h4 class="h4">Healthcare Service Standardisation</h4>
              <p>Built a large scale matching pipeline that mapped approximately 8 million legacy healthcare tariff records to about 300,000 standardised services using cosine similarity, fuzzy matching, and batched processing.</p>
              <a href="/experience/">View Experience</a>
            </li>
            <li class="feature-card">
              <p class="feature-card-kicker">Published Research</p>
              <h4 class="h4">CNN Hyperparameter Optimisation for Pneumonia Detection</h4>
              <p>Co-authored peer-reviewed research on how hyperparameter interactions affect CNN performance for pneumonia detection from chest X-rays.</p>
              <a href="/projects-research/">View Research</a>
            </li>
            <li class="feature-card">
              <p class="feature-card-kicker">Machine Learning Competition</p>
              <h4 class="h4">Expresso Customer Churn Prediction</h4>
              <p>Placed second in the Data Science Nigeria Expresso Churn Prediction Challenge using feature engineering, CatBoost, XGBoost, cross validation, and model blending.</p>
              <a href="/projects-research/">View Competition</a>
            </li>
          </ul>
        </section>

{recommendations_and_modal}
{clients}

      </article>
"""

    experience_article = """      <article class="resume experience"
               data-page="experience">

        <header>
          <h2 class="h2 article-title">Experience</h2>
          <p class="page-intro">My work sits at the intersection of data science, machine learning engineering, and practical business execution. I have built systems across insurance, education technology, and client projects, from large scale data processing and ML APIs to AI evaluation pipelines and production model deployment.</p>
        </header>

        <section class="timeline">
          <div class="title-wrapper">
            <div class="icon-box"><ion-icon name="briefcase-outline"></ion-icon></div>
            <h3 class="h3">Professional Experience</h3>
          </div>
          <ol class="timeline-list">
            <li class="timeline-item">
              <h4 class="h4 timeline-item-title">Data Scientist - AXA Mansard</h4>
              <span>February 2022 to Present</span>
              <ul class="timeline-bullets">
                <li>Engineered a healthcare service matching pipeline that mapped approximately 8 million legacy tariff records to about 300,000 standardised services using cosine similarity, fuzzy matching, and batched processing.</li>
                <li>Built and deployed a FastAPI based car valuation service using machine learning models, enabling real time vehicle pricing and reducing reliance on external pricing vendors.</li>
                <li>Automated ETL pipelines with Python and SQL to extract, transform, and load production data into analytics systems, supporting more than 20 operational dashboards and eliminating manual data transfer workflows.</li>
                <li>Developed and deployed a personalised product recommendation system using Python and SQL to support targeted cross sell strategies across customer segments.</li>
              </ul>
              <p class="tag-list">Machine Learning &middot; Data Engineering &middot; Healthcare AI &middot; Insurance Analytics &middot; FastAPI &middot; Python &middot; SQL</p>
            </li>
            <li class="timeline-item">
              <h4 class="h4 timeline-item-title">Machine Learning Engineer, Contract - ExamRocket</h4>
              <span>January 2025 to November 2025</span>
              <ul class="timeline-bullets">
                <li>Redesigned AI model provider integrations using asynchronous execution, batching, request deduplication, retries, timeouts, and fallback handling, increasing throughput and reducing latency by 30 percent.</li>
                <li>Owned production deployment and operational reliability of AI components, implementing monitoring, error handling, and resilient execution flows to support stable real time evaluation.</li>
              </ul>
              <p class="tag-list">AI Systems &middot; Model Provider Integrations &middot; Asynchronous Processing &middot; Reliability &middot; Monitoring &middot; Production Deployment</p>
            </li>
            <li class="timeline-item">
              <h4 class="h4 timeline-item-title">Machine Learning Engineer, Freelance - Fiverr</h4>
              <span>October 2020 to February 2022</span>
              <ul class="timeline-bullets">
                <li>Designed and delivered more than 40 machine learning solutions spanning forecasting, classification, recommendation, NLP, computer vision, and time series modelling across multiple client domains.</li>
                <li>Built reusable data pipelines, preprocessing workflows, and model evaluation frameworks using Python and SQL to support both model training and production inference across client projects.</li>
                <li>Deployed machine learning services using Flask, FastAPI, Docker, and GCP, converting trained models into production applications used within client workflows.</li>
              </ul>
              <p class="tag-list">NLP &middot; Computer Vision &middot; Forecasting &middot; Recommendation Systems &middot; APIs &middot; Model Deployment</p>
            </li>
            <li class="timeline-item compact-timeline-item">
              <h4 class="h4 timeline-item-title">Data Science Intern - Hamoye</h4>
              <span>June 2020 to December 2020</span>
              <p class="timeline-summary">Worked on predictive modelling, NLP classification, exploratory analysis, and collaborative data science projects during the early stage of my machine learning career.</p>
            </li>
          </ol>
        </section>

        <section class="timeline">
          <div class="title-wrapper">
            <div class="icon-box"><ion-icon name="people-outline"></ion-icon></div>
            <h3 class="h3">Community, Teaching &amp; Leadership</h3>
          </div>
          <ol class="timeline-list">
            <li class="timeline-item"><h4 class="h4 timeline-item-title">AXA Data Science Community</h4><p class="timeline-summary">Co-led the community and taught practical data science concepts and applications to more than 40 employees.</p></li>
            <li class="timeline-item"><h4 class="h4 timeline-item-title">Part-time Trainer - Rubies Technologies</h4><span>May 2025 to November 2025</span><p class="timeline-summary">Delivered virtual student training, prepared weekly and monthly student progress reports, gave feedback on student development, and participated in skill-development meetings and programs.</p></li>
            <li class="timeline-item"><h4 class="h4 timeline-item-title">Data Science Nigeria</h4><p class="timeline-summary">Recognised in Data Science Nigeria material as an AI in Every City tutor, with active participation in competitions and community learning.</p></li>
            <li class="timeline-item"><h4 class="h4 timeline-item-title">Google Developer Student Community, University of Lagos</h4><p class="timeline-summary">Member and mentor during university.</p></li>
          </ol>
        </section>

        <section class="timeline">
          <div class="title-wrapper">
            <div class="icon-box"><ion-icon name="school-outline"></ion-icon></div>
            <h3 class="h3">Education &amp; Credentials</h3>
          </div>
          <ol class="timeline-list">
            <li class="timeline-item"><h4 class="h4 timeline-item-title">University of Lagos - B.Sc. Computer Science</h4><span>2025 &middot; Second Class Upper &middot; GPA 4.05 / 5.00</span><p class="timeline-summary">Studied core computer science areas including algorithms, data structures, databases, operating systems, computer networks, and software engineering.</p></li>
            <li class="timeline-item"><h4 class="h4 timeline-item-title">DataCamp - AI Engineer for Data Scientists Associate</h4><span>Issued June 2026</span><p class="timeline-summary">Practical AI engineering skills for data scientists and applied AI workflows.</p></li>
            <li class="timeline-item"><h4 class="h4 timeline-item-title">McKinsey.org Forward Program</h4><span>Completed 2025</span><p class="timeline-summary">Completed learning focused on structured problem solving, communication, adaptability, resilience, relationship building, and self leadership.</p></li>
          </ol>
        </section>

        <section class="skill grouped-skills-section">
          <h3 class="h3 skills-title">Technical Skills</h3>
          <ul class="skills-grid grouped-skills-grid">
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">Languages</h5><p>Python, SQL</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">Machine Learning</h5><p>PyTorch, TensorFlow, Scikit-learn, Transformers, NLP, Computer Vision</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">Data Engineering</h5><p>ETL Pipelines, Spark, BigQuery, Databricks</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">APIs &amp; Backend</h5><p>FastAPI, Flask, REST APIs</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">Cloud &amp; Infrastructure</h5><p>GCP, Docker, Kubernetes, CI/CD</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">ML Operations</h5><p>MLflow, Monitoring, Logging</p></li>
            <li class="skill-card grouped-skill"><h5 class="h5 skill-name">Developer Tools</h5><p>Git, Linux, Jupyter, Postman</p></li>
          </ul>
        </section>

        <section class="resume-card">
          <h3 class="h3">Resume</h3>
          <p>A concise overview of my professional experience, technical work, education, and selected achievements.</p>
          <a href="/assets/resume/david_olukolatimi_resume.pdf" download>Download Resume</a>
        </section>

      </article>
"""

    projects_article = """      <article class="portfolio projects-research"
               data-page="projects-research">

        <header>
          <h2 class="h2 article-title">Projects &amp; Research</h2>
          <p class="page-intro">This page brings together selected technical projects, published research, competitions, and open source work. Some projects began as learning experiments, while others came from professional or research problems.</p>
        </header>

        <section class="projects">
          <ul class="filter-list">
            <li class="filter-item"><button class="active" data-filter-btn>All</button></li>
            <li class="filter-item"><button data-filter-btn>Projects</button></li>
            <li class="filter-item"><button data-filter-btn>Published Research</button></li>
            <li class="filter-item"><button data-filter-btn>Hackathons &amp; Competitions</button></li>
            <li class="filter-item"><button data-filter-btn>GitHub Work</button></li>
          </ul>
          <div class="filter-select-box">
            <button class="filter-select" data-select><div class="select-value" data-select-value>Select category</div><div class="select-icon"><ion-icon name="chevron-down"></ion-icon></div></button>
            <ul class="select-list">
              <li class="select-item"><button data-select-item>All</button></li>
              <li class="select-item"><button data-select-item>Projects</button></li>
              <li class="select-item"><button data-select-item>Published Research</button></li>
              <li class="select-item"><button data-select-item>Hackathons &amp; Competitions</button></li>
              <li class="select-item"><button data-select-item>GitHub Work</button></li>
            </ul>
          </div>
          <ul class="project-list blueprint-project-list">
            <li class="project-item active featured-project-card" data-filter-item data-category="projects">
              <a href="/experience/">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="eye-outline"></ion-icon></div><img src="/assets/images/project-nlp-similarity.jpg" alt="Healthcare service matching project" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">Healthcare Service Standardisation &amp; Claims Platform Migration</h3>
                <p class="project-category">Professional Machine Learning and Data Engineering</p>
                <p class="project-description">Built a large scale healthcare service matching pipeline using text preprocessing, service categorisation, cosine similarity, fuzzy matching, batched processing, and ranked candidate selection.</p>
              </a>
            </li>
            <li class="project-item active featured-project-card" data-filter-item data-category="projects">
              <a href="https://github.com/KolatimiDave/People-Counter-App-On-Edge" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="eye-outline"></ion-icon></div><img src="/assets/images/optimized/project-people-counter.webp" alt="People Counter on Edge" loading="lazy" width="1400" height="788" decoding="async"></figure>
                <h3 class="project-title">People Counter on Edge</h3>
                <p class="project-category">Computer Vision &amp; Edge AI</p>
                <p class="project-description">A smart video IoT application built with Intel OpenVINO that detects people in a designated area and sends occupancy data to a local web service through MQTT.</p>
              </a>
            </li>
            <li class="project-item active featured-project-card" data-filter-item data-category="projects">
              <a href="https://github.com/KolatimiDave" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="eye-outline"></ion-icon></div><img src="/assets/images/project-pointer-controller.jpg" alt="Computer Pointer Controller" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">Computer Pointer Controller</h3>
                <p class="project-category">Computer Vision &amp; Gaze Interaction</p>
                <p class="project-description">A computer vision application that coordinates OpenVINO models for face detection, landmarks, head pose estimation, and gaze estimation before translating gaze into pointer movement.</p>
              </a>
            </li>
            <li class="project-item active featured-project-card" data-filter-item data-category="published research">
              <a href="https://doi.org/10.3311/PPee.43418" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="document-text-outline"></ion-icon></div><img src="/assets/images/pneumonia-cnn-research.jpg" alt="Chest X-ray samples from the published pneumonia CNN research" loading="lazy" width="1400" height="788" decoding="async"></figure>
                <h3 class="project-title">Systematic Hyperparameter Optimization of CNNs for Pneumonia Detection</h3>
                <p class="project-category">Published Research</p>
                <p class="project-description">Peer-reviewed research evaluating VGG16, ResNet50, InceptionV3, and MobileNetV2 on the RSNA Pneumonia Detection Challenge dataset. InceptionV3 reported a test F1 score of 92.5 percent and recall of 91.8 percent.</p>
              </a>
            </li>
            <li class="project-item active featured-project-card" data-filter-item data-category="hackathons & competitions">
              <a href="https://zindi.africa/competitions/dsn-pre-bootcamp-hackathon-expresso-churn-prediction-challenge/discussions/2792" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="trophy-outline"></ion-icon></div><img src="/assets/images/project-churn.jpg" alt="Expresso churn prediction competition" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">DSN Expresso Churn Prediction Challenge</h3>
                <p class="project-category">2nd Place Competition Solution</p>
                <p class="project-description">Predicted customer churn for Expresso using feature engineering, cross validation, CatBoost, XGBoost, and model blending.</p>
              </a>
            </li>
            <li class="project-item active" data-filter-item data-category="github work">
              <a href="https://github.com/KolatimiDave/Expresso-Customer-Churn-Prediction" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="logo-github"></ion-icon></div><img src="/assets/images/project-churn.jpg" alt="Expresso GitHub repository" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">Expresso Customer Churn Prediction</h3>
                <p class="project-category">GitHub Work</p>
              </a>
            </li>
            <li class="project-item active" data-filter-item data-category="projects">
              <a href="https://github.com/KolatimiDave" target="_blank" rel="noopener">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="eye-outline"></ion-icon></div><img src="/assets/images/project-house-prices.jpg" alt="House price prediction" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">House Price Prediction</h3>
                <p class="project-category">Regression Modelling</p>
              </a>
            </li>
            <li class="project-item active" data-filter-item data-category="projects">
              <a href="/experience/">
                <figure class="project-img"><div class="project-item-icon-box"><ion-icon name="eye-outline"></ion-icon></div><img src="/assets/images/project-renewal.jpg" alt="Customer renewal prediction" loading="lazy" width="1024" height="1024" decoding="async"></figure>
                <h3 class="project-title">Customer Renewal Prediction Pipeline</h3>
                <p class="project-category">Machine Learning &amp; MLOps</p>
              </a>
            </li>
          </ul>
        </section>

        <section class="resume-card github-work-card">
          <h3 class="h3">GitHub Work</h3>
          <p>I use GitHub to share competition solutions, computer vision experiments, research code, learning projects, and technical implementations.</p>
          <a href="https://github.com/KolatimiDave" target="_blank" rel="noopener">View All Repositories on GitHub</a>
        </section>

      </article>
"""

    services_article = services_article.replace('      <article class="services-page"', '      <article class="services-page"')

    writing_article = """      <article class="blog writing"
               data-page="writing">

        <header>
          <h2 class="h2 article-title">Writing</h2>
          <p class="page-intro">I write about artificial intelligence, engineering, learning, work, and the ideas that shape how people grow. Some pieces explain technical concepts and emerging technology. Others are more reflective and explore career, thought, behaviour, and personal development.</p>
        </header>

        <section class="blog-posts">
          <div class="blog-filter">
            <label for="blog-category-select" class="blog-filter-label">Filter by category:</label>
            <select id="blog-category-select" class="blog-filter-select">
              <option value="all" selected>All</option>
              <option value="ai & technology">AI &amp; Technology</option>
              <option value="career & learning">Career &amp; Learning</option>
              <option value="ideas & personal growth">Ideas &amp; Personal Growth</option>
            </select>
          </div>
          <ul class="blog-posts-list">
            <li class="blog-post-item" data-blog-category="ai & technology"><a href="https://olukolatimidavid.medium.com/" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/blog-5.jpg" alt="AI trust article thumbnail" loading="lazy" width="600" height="391" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">AI &amp; Technology</p><span class="dot"></span><time datetime="2026-01-01">2026</time></div><h3 class="h3 blog-item-title">AI Can Do More Work Now. Can We Trust the Work?</h3><p class="blog-text">Explores accountability, human review, identity, control, and the conditions required for people and organisations to trust AI generated work.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="ai & technology"><a href="https://olukolatimidavid.medium.com/" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/blog-6.jpg" alt="Future of work article thumbnail" loading="lazy" width="600" height="391" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">AI &amp; Technology</p><span class="dot"></span><time datetime="2026-03-01">Mar 2026</time></div><h3 class="h3 blog-item-title">The Future of Work is Safe</h3><p class="blog-text">A practical view of how automation changes work and why collaboration with AI matters more than simple replacement.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="ai & technology"><a href="https://medium.com/analytics-vidhya/ai-models-on-edge-devices-with-openvino-5a057bc50e07" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/blog-5.jpg" alt="AI Models on Edge Devices thumbnail" loading="lazy" width="600" height="391" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">AI &amp; Technology</p><span class="dot"></span><time datetime="2020-12-24">Dec 24, 2020</time></div><h3 class="h3 blog-item-title">AI Models on Edge Devices with OpenVINO</h3><p class="blog-text">An introduction to deploying AI models on edge hardware with Intel OpenVINO.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="career & learning"><a href="https://olukolatimidavid.medium.com/getting-into-the-data-space-my-experience-a92eb1650323" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/blog-3.jpg" alt="Getting into the Data Space thumbnail" loading="lazy" width="601" height="401" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">Career &amp; Learning</p><span class="dot"></span><time datetime="2024-09-17">Sep 17, 2024</time></div><h3 class="h3 blog-item-title">Getting into the Data Space</h3><p class="blog-text">A personal account of moving from university technology communities into data science.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="career & learning"><a href="https://olukolatimidavid.medium.com/opportunity-cost-of-knowledge-8341a439a7d9" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/blog-1.jpg" alt="Opportunity Cost of Knowledge thumbnail" loading="lazy" width="800" height="800" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">Career &amp; Learning</p><span class="dot"></span><time datetime="2025-01-30">Jan 30, 2025</time></div><h3 class="h3 blog-item-title">Opportunity Cost of Knowledge</h3><p class="blog-text">A reflection on why knowledge fades and why documenting learning gives us a way back to ideas.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="ideas & personal growth"><a href="https://medium.com/activated-thinker/life-is-not-fair-opportunities-and-exposure-14f95c5de647" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/optimized/blog-life.webp" alt="Life is not fair thumbnail" loading="lazy" width="1200" height="800" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">Ideas &amp; Personal Growth</p><span class="dot"></span><time datetime="2026-02-17">Feb 17, 2026</time></div><h3 class="h3 blog-item-title">Life is not fair: Opportunities &amp; Exposure</h3><p class="blog-text">A reflection on how exposure shapes what people believe is possible.</p></div></a></li>
            <li class="blog-post-item" data-blog-category="ideas & personal growth"><a href="https://olukolatimidavid.medium.com/i-ran-my-first-marathon-a05e912da9e7" target="_blank" rel="noopener"><figure class="blog-banner-box"><img src="/assets/images/optimized/blog-marathon-simple.webp" alt="I ran my first marathon thumbnail" loading="lazy" width="1400" height="933" decoding="async"></figure><div class="blog-content"><div class="blog-meta"><p class="blog-category">Ideas &amp; Personal Growth</p><span class="dot"></span><time datetime="2025-06-06">Jun 6, 2025</time></div><h3 class="h3 blog-item-title">I ran my first marathon</h3><p class="blog-text">A personal story about training, discomfort, consistency, and growth.</p></div></a></li>
          </ul>
          <div class="writing-actions"><a href="https://olukolatimidavid.medium.com/" target="_blank" rel="noopener">Read All Articles on Medium</a><a href="https://www.linkedin.com/in/olukolatimidavid/" target="_blank" rel="noopener">Follow My Writing on LinkedIn</a></div>
        </section>

      </article>
"""

    contact_article = f"""      <article class="contact"
               data-page="contact">

        <header>
          <h2 class="h2 article-title">Contact Me</h2>
          <p class="page-intro">Have a role, project, collaboration, research idea, training request, or technical problem you would like to discuss? Send me a message and I will get back to you.</p>
        </header>

        <section class="contact-details-strip">
          <div><span>Email</span><a href="mailto:davidolukolatimi@gmail.com">davidolukolatimi@gmail.com</a></div>
          <div><span>Phone</span><a href="tel:+2347041035041">+234 704 103 5041</a></div>
          <div><span>Location</span><p>Lagos, Nigeria</p></div>
        </section>

{contact_inner}

      </article>
"""

    articles = "\n".join([
        home_article,
        experience_article,
        projects_article,
        services_article,
        writing_article,
        contact_article,
    ])

    html = re.sub(r'      <nav class="navbar">[\s\S]*?      </nav>', nav, html, count=1)
    html = replace_articles(html, articles)
    html = re.sub(r'\s*<ul class="social-list top-social-list">[\s\S]*?</ul>', "", html, count=1)
    html = re.sub(r'\s*<ul class="social-list bottom-social-list">[\s\S]*?</ul>', "", html, count=1)
    html = re.sub(
        r'\s*<li class="contact-item">\s*<div class="icon-box">\s*<ion-icon name="calendar-outline"></ion-icon>\s*</div>\s*<div class="contact-info">\s*<p class="contact-title">\s*Date of Birth\s*</p>\s*<time datetime="11-11">\s*November 11\s*</time>\s*</div>\s*</li>',
        "",
        html,
        count=1,
    )
    html = html.replace("AI Engineer &amp; Data Scientist", "Data Scientist &amp; Machine Learning Engineer")

    footer = """  <footer class="site-footer">
    <nav class="footer-links" aria-label="Footer links">
      <a href="https://www.linkedin.com/in/olukolatimidavid/" target="_blank" rel="noopener">LinkedIn</a>
      <a href="https://github.com/KolatimiDave/" target="_blank" rel="noopener">GitHub</a>
      <a href="https://olukolatimidavid.medium.com/" target="_blank" rel="noopener">Medium</a>
      <a href="https://scholar.google.com/citations?hl=en&amp;user=iqIxgx4AAAAJ" target="_blank" rel="noopener">Google Scholar</a>
      <a href="/assets/resume/david_olukolatimi_resume.pdf">Resume</a>
      <a href="/contact/">Contact</a>
    </nav>
    <p>&copy; David Olukolatimi. Built around data, engineering, ideas, and practical impact.</p>
  </footer>
"""
    html = re.sub(r'\n\n  <footer class="site-footer">[\s\S]*?</footer>', "", html, count=1)
    html = re.sub(r'\n\n  <script src="/assets/js/script\.js\?v=4"></script>', f"\n\n{footer}\n  <script src=\"/assets/js/script.js?v=4\"></script>", html, count=1)

    INDEX.write_text(html, encoding="utf-8")
    print("Applied blueprint content to index.html source.")


if __name__ == "__main__":
    main()
