'use strict';



// element toggle function
const elementToggleFunc = function (elem) { elem.classList.toggle("active"); }



// sidebar variables
const sidebar = document.querySelector("[data-sidebar]");
const sidebarBtn = document.querySelector("[data-sidebar-btn]");

// sidebar toggle functionality for mobile
sidebarBtn.addEventListener("click", function () { elementToggleFunc(sidebar); });



// testimonials variables
const testimonialsItem = document.querySelectorAll("[data-testimonials-item]");
const modalContainer = document.querySelector("[data-modal-container]");
const modalCloseBtn = document.querySelector("[data-modal-close-btn]");
const overlay = document.querySelector("[data-overlay]");

// modal variable
const modalImg = document.querySelector("[data-modal-img]");
const modalTitle = document.querySelector("[data-modal-title]");
const modalText = document.querySelector("[data-modal-text]");

// modal toggle function
const testimonialsModalFunc = function () {
  modalContainer.classList.toggle("active");
  overlay.classList.toggle("active");
}

// add click event to all modal items
for (let i = 0; i < testimonialsItem.length; i++) {

  testimonialsItem[i].addEventListener("click", function () {

    modalImg.src = this.querySelector("[data-testimonials-avatar]").src;
    modalImg.alt = this.querySelector("[data-testimonials-avatar]").alt;
    modalTitle.innerHTML = this.querySelector("[data-testimonials-title]").innerHTML;
    modalText.innerHTML = this.querySelector("[data-testimonials-text]").innerHTML;

    testimonialsModalFunc();

  });

}

// add click event to modal close button
modalCloseBtn.addEventListener("click", testimonialsModalFunc);
overlay.addEventListener("click", testimonialsModalFunc);



// custom select variables
const select = document.querySelector("[data-select]");
const selectItems = document.querySelectorAll("[data-select-item]");
const selectValue = document.querySelector("[data-selecct-value]");
const filterBtn = document.querySelectorAll("[data-filter-btn]");

select.addEventListener("click", function () { elementToggleFunc(this); });

// add event in all select items
for (let i = 0; i < selectItems.length; i++) {
  selectItems[i].addEventListener("click", function () {

    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    elementToggleFunc(select);
    filterFunc(selectedValue);

  });
}

// filter variables
const filterItems = document.querySelectorAll("[data-filter-item]");

const filterFunc = function (selectedValue) {

  for (let i = 0; i < filterItems.length; i++) {

    if (selectedValue === "all") {
      filterItems[i].classList.add("active");
    } else if (selectedValue === filterItems[i].dataset.category) {
      filterItems[i].classList.add("active");
    } else {
      filterItems[i].classList.remove("active");
    }

  }

}

// add event in all filter button items for large screen
let lastClickedBtn = filterBtn[0];

for (let i = 0; i < filterBtn.length; i++) {

  filterBtn[i].addEventListener("click", function () {

    let selectedValue = this.innerText.toLowerCase();
    selectValue.innerText = this.innerText;
    filterFunc(selectedValue);

    lastClickedBtn.classList.remove("active");
    this.classList.add("active");
    lastClickedBtn = this;

  });

}



// contact form variables
const form = document.querySelector("[data-form]");
const formInputs = document.querySelectorAll("[data-form-input]");
const formBtn = document.querySelector("[data-form-btn]");

// We no longer disable the submit button based on validity. Instead, we
// display helpful validation messages when the user submits an invalid form.


// page navigation variables
const navigationLinks = document.querySelectorAll("[data-nav-link]");
const pages = document.querySelectorAll("[data-page]");

/*
  Improved navigation logic: rather than relying on positional indexing of
  navigation links and pages (which can break if new pages are inserted),
  this handler maps each click to the page with a matching data-page value.
  It also updates the active class on navigation links based on their text.
*/
navigationLinks.forEach((link) => {
  link.addEventListener("click", function () {
    const clicked = this.innerText.trim().toLowerCase();

    pages.forEach((page) => {
      const target = page.dataset.page.trim().toLowerCase();
      if (target === clicked) {
        page.classList.add("active");
      } else {
        page.classList.remove("active");
      }
    });

    navigationLinks.forEach((lnk) => {
      const linkText = lnk.innerText.trim().toLowerCase();
      if (linkText === clicked) {
        lnk.classList.add("active");
      } else {
        lnk.classList.remove("active");
      }
    });

    // Scroll to top of the page after navigating
    window.scrollTo(0, 0);
  });
});

// theme toggle button
const themeToggleBtn = document.querySelector("[data-theme-toggle]");
if (themeToggleBtn) {
  // initialize icon based on stored preference or default dark
  const themeIcon = themeToggleBtn.querySelector("ion-icon");
  const storedTheme = localStorage.getItem("theme");
  if (storedTheme === "light") {
    document.body.classList.add("light-theme");
    if (themeIcon) themeIcon.setAttribute("name", "moon-outline");
  }
  themeToggleBtn.addEventListener("click", function () {
    const isLight = document.body.classList.toggle("light-theme");
    // swap icon
    if (themeIcon) {
      themeIcon.setAttribute("name", isLight ? "moon-outline" : "sunny-outline");
    }
    // persist preference
    localStorage.setItem("theme", isLight ? "light" : "dark");
  });
}

/* -----------------------------------------------------------------
 * SERVICES: currency conversion and contact buttons
 *
 * The Services page lists project and hourly offerings with price ranges
 * defined in USD via data attributes (data-min, data-max and data-billing).
 * Visitors can select a different currency (USD, NGN, EUR, GBP, JPY) from
 * the drop‑down; the prices are then converted in real time using a
 * free exchange rate API.  Conversion rates are cached to minimise
 * network requests.  Prices are always rounded to the nearest whole
 * number and appended with a currency symbol.  For hourly services,
 * "/hr" is appended.
 *
 * Each service card also features a "Contact Me" button.  Clicking the
 * button navigates the visitor to the Contact page and pre‑populates
 * the message textarea with a randomly selected template specific to
 * that service.  This helps reduce repetitive messages when users
 * inquire about multiple offerings.
 */

(() => {
  // Only run after DOM has loaded
  document.addEventListener("DOMContentLoaded", function () {
    // Currency conversion
    const currencySelect = document.getElementById("currency-select");
    const priceElements = document.querySelectorAll(".service-card-price");
    // Cache exchange rates to avoid redundant requests
    const rateCache = { USD: 1 };
    const symbols = { USD: "$", NGN: "₦", EUR: "€", GBP: "£", JPY: "¥" };

    async function getRate(currency) {
      // Return 1 for USD (base currency)
      if (currency === "USD") return 1;
      // Use cached rate if available
      if (rateCache[currency]) return rateCache[currency];
      try {
        /*
         * Use the open.er-api.com service which returns a free JSON payload
         * containing exchange rates for all currencies based off USD. This
         * endpoint is reliable and requires no API key. We fetch the rates
         * only once and cache them in the rateCache object. If the call
         * fails for some reason (e.g. network error), we'll fall back to
         * returning 1 (which results in no conversion) to avoid breaking
         * the UI.
         */
        if (!rateCache._allRates) {
          // Try Open Exchange Rates API first (no API key required)
          try {
            const res1 = await fetch("https://open.er-api.com/v6/latest/USD");
            const data1 = await res1.json();
            if (data1 && data1.rates) {
              rateCache._allRates = data1.rates;
            }
          } catch (e) {
            console.warn("Open ER API unavailable, falling back to exchangerate.host");
          }
          // If still undefined, try exchangerate.host as secondary
          if (!rateCache._allRates) {
            try {
              const res2 = await fetch("https://api.exchangerate.host/latest?base=USD");
              const data2 = await res2.json();
              if (data2 && data2.rates) {
                rateCache._allRates = data2.rates;
              }
            } catch (e) {
              console.warn("exchangerate.host API unavailable", e);
            }
          }
          // If both APIs failed, initialise with approximate rates (Feb 2026 values)
          if (!rateCache._allRates) {
            rateCache._allRates = {
              NGN: 1350,
              EUR: 0.92,
              GBP: 0.79,
              JPY: 150
            };
          }
        }
        const rate = rateCache._allRates && rateCache._allRates[currency];
        if (rate) {
          rateCache[currency] = rate;
          return rate;
        }
      } catch (err) {
        console.error("Failed to fetch currency rates", err);
      }
      // Fallback to 1 if API fails completely
      return 1;
    }

    async function updatePrices() {
      const selected = currencySelect ? currencySelect.value : "USD";
      const rate = await getRate(selected);
      priceElements.forEach((el) => {
        const billing = el.dataset.billing; // hourly or project
        const min = parseFloat(el.dataset.min);
        const max = parseFloat(el.dataset.max);
        let displayMin = min;
        let displayMax = max;
        // convert if not USD
        if (selected !== "USD") {
          displayMin = Math.round(min * rate);
          displayMax = Math.round(max * rate);
        }
        const symbol = symbols[selected] || "";
        const suffix = billing === "hourly" ? "/hr" : "";
        // update strong element inside price container
        const priceLabel = el.querySelector(".price-display");
        if (priceLabel) {
          priceLabel.textContent = `${symbol}${displayMin}\u2013${symbol}${displayMax}${suffix}`;
        }
      });
    }

    if (currencySelect) {
      currencySelect.addEventListener("change", updatePrices);
      // Initialise on page load
      updatePrices();
    }

    // -----------------------------------------------------------------
    // BLOG FILTER: Show or hide posts based on selected category
    // When the user changes the blog category select box, we filter
    // blog posts by their data-blog-category attribute.  A value of
    // "all" shows every post.
    // -----------------------------------------------------------------
    const blogCategorySelect = document.getElementById("blog-category-select");
    if (blogCategorySelect) {
      blogCategorySelect.addEventListener("change", function () {
        const selectedCategory = this.value;
        document.querySelectorAll(".blog-post-item").forEach((item) => {
          const category = item.getAttribute("data-blog-category");
          if (!selectedCategory || selectedCategory === "all" || category === selectedCategory) {
            item.style.display = "block";
          } else {
            item.style.display = "none";
          }
        });
      });
    }

    // -----------------------------------------------------------------
    // RECOMMENDATIONS SLIDER AND READ MORE
    // Show one recommendation card at a time with previous/next controls.
    // Cards longer than their max height are truncated; clicking "Read more"
    // toggles the expanded state to reveal the full text.  Clicking again
    // collapses the card.
    // -----------------------------------------------------------------
    const slider = document.querySelector(".recommendations-slider");
    if (slider) {
      const slides = slider.querySelectorAll(".slide");
      let current = 0;
      function updateSlider() {
        slides.forEach((s, idx) => {
          s.classList.toggle("active", idx === current);
        });
      }
      updateSlider();
      const prevBtn = slider.querySelector(".slider-btn.prev");
      const nextBtn = slider.querySelector(".slider-btn.next");
      if (prevBtn) {
        prevBtn.addEventListener("click", () => {
          current = (current - 1 + slides.length) % slides.length;
          updateSlider();
        });
      }
      if (nextBtn) {
        nextBtn.addEventListener("click", () => {
          current = (current + 1) % slides.length;
          updateSlider();
        });
      }
      // Read more toggle
      slider.querySelectorAll(".read-more-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          const card = btn.closest(".recommendation-card");
          if (!card) return;
          const expanded = card.classList.toggle("expanded");
          btn.textContent = expanded ? "Show less" : "Read more";
        });
      });
    }

    // -----------------------------------------------------------------
    // PROMO TEXT ROTATION
    // Rotate messages in the top banner every few seconds.  The text
    // scrolls via CSS marquee animation, but we replace the content
    // periodically to keep it interesting.  Feel free to add more
    // messages to the array for variety.
    // -----------------------------------------------------------------
    // const promoTextEl = document.getElementById("promo-text");
    // if (promoTextEl) {
    //   /*
    //    * Promotional messages used in the top banner.  These phrases are
    //    * intentionally succinct and inspiring, touching on AI, innovation,
    //    * mentoring, open source and data‑driven impact.  The array contains
    //    * 20 entries to minimise repetition.  "Let's build something
    //    * amazing together" is intentionally omitted here (it is reserved for
    //    * the bottom banner).
    //    */
    //   /*
    //    * Curated promotional messages for the top banner.
    //    * These taglines emphasise clarity, innovation and impact in the AI/ML domain.
    //    * We removed the bottom tagline "Let’s build something amazing together" from
    //    * this list so it appears exclusively in the footer.  Feel free to update
    //    * these phrases to better reflect your evolving brand voice.
    //    */
    //   const promoMessages = [
    //     "Transforming data into decisions",
    //     "Precision. Performance. Progress.",
    //     "Building smarter solutions for everyday problems",
    //     "Unlocking insights with intelligence",
    //     "Empower your data journey",
    //     "Innovate today, lead tomorrow",
    //     "Data‑driven solutions for modern challenges",
    //     "Crafting intelligence for every industry",
    //     "Next‑gen solutions for a smarter tomorrow",
    //     "Intelligence that evolves with you",
    //     "Your vision, our technology",
    //     "Streamlining your world with machine learning",
    //     "Where technology meets brilliance",
    //     "Smart tech, real results",
    //     "Inspiring growth through intelligent systems",
    //     "Bridge insights with automated learning",
    //     "Excellence in every line of code",
    //     "Harness knowledge, fuel progress",
    //     "From ideas to intelligent algorithms",
    //     "Amplifying potential with machine learning"
    //   ];
    //   let promoIndex = 0;
    //   // Ensure the promo text element fades gracefully between messages.
    //   promoTextEl.style.transition = "opacity 0.6s ease-in-out";
    //   function cyclePromo() {
    //     // Fade out the current message
    //     promoTextEl.style.opacity = 0;
    //     setTimeout(() => {
    //       // Switch to the next message
    //       promoIndex = (promoIndex + 1) % promoMessages.length;
    //       promoTextEl.textContent = promoMessages[promoIndex];
    //       // Restart the horizontal scroll animation so the new message flows from right to left.
    //       promoTextEl.style.animation = "none";
    //       // Force reflow to reset the animation
    //       void promoTextEl.offsetWidth;
    //       promoTextEl.style.animation = "promo-scroll 14s linear infinite";
    //       // Fade back in
    //       promoTextEl.style.opacity = 1;
    //       // Schedule the next cycle: display for 5 seconds, then fade and
    //       // delay for 1 second before the next message starts
    //       setTimeout(cyclePromo, 5000);
    //     }, 1000);
    //   }
    //   // Initialise with the first message
    //   promoTextEl.textContent = promoMessages[0];
    //   promoTextEl.style.opacity = 1;
    //   // Start cycling after a delay so the first message is visible for 5s
    //   setTimeout(cyclePromo, 5000);
    // }

    const promoTextEl = document.getElementById("promo-text");

    if (promoTextEl) {
      const promoMessages = [
        "Transforming data into decisions",
        "Precision. Performance. Progress.",
        "Building smarter solutions for everyday problems",
        "Unlocking insights with intelligence",
        "Empower your data journey",
        "Innovate today, lead tomorrow",
        "Data-driven solutions for modern challenges",
        "Crafting intelligence for every industry",
        "Next-gen solutions for a smarter tomorrow",
        "Intelligence that evolves with you",
        "Your vision, our technology",
        "Streamlining your world with machine learning",
        "Where technology meets brilliance",
        "Smart tech, real results",
        "Inspiring growth through intelligent systems",
        "Bridge insights with automated learning",
        "Excellence in every line of code",
        "Harness knowledge, fuel progress",
        "From ideas to intelligent algorithms",
        "Amplifying potential with machine learning"
      ];

      const scrollMs = 14000;
      const fadeMs = 1000;

      let promoIndex = 0;

      function restartScroll() {
        promoTextEl.style.animation = "none";
        void promoTextEl.offsetWidth;
        promoTextEl.style.animation = "promo-scroll 14s linear infinite";
      }

      function nextCycle() {
        setTimeout(() => {
          promoTextEl.style.opacity = "0";

          setTimeout(() => {
            promoIndex = (promoIndex + 1) % promoMessages.length;
            promoTextEl.textContent = promoMessages[promoIndex];

            restartScroll();

            promoTextEl.style.opacity = "1";

            nextCycle();
          }, fadeMs);
        }, scrollMs);
      }

      promoTextEl.textContent = promoMessages[0];
      promoTextEl.style.opacity = "1";
      restartScroll();
      nextCycle();
    }

    // Service contact templates
    const contactTemplates = {
      "AI Consulting": [
        "Hello David, I came across your AI consulting service and would like to schedule a meeting to discuss my project.",
        "Hi David, I'm interested in your AI consulting offering—could we chat about how you can help my business?",
        "Hello David, I'd love to learn more about your AI consulting services; can we arrange a call?",
        "Hi David, I'm reaching out regarding your AI consulting package. Let's talk details.",
        "Hello, I saw your AI consulting service and need advice on implementing machine learning in my company.",
        "Hi there, I'd like to engage your AI consulting expertise; when are you available?",
        "Hello David, could we discuss your AI consulting service for an upcoming project?",
        "Hi David, please provide more information about your AI consulting and pricing.",
        "Hello, I'm looking for guidance on AI strategy and saw your consulting service.",
        "Hi David, I'd like to schedule an AI consulting session to explore collaboration."
      ],
      "Custom ML Development": [
        "Hello David, I came across your custom ML development service and would like to discuss a potential project.",
        "Hi David, I'm interested in having a predictive model built. Could we chat about your custom ML development offering?",
        "Hello David, I'd love to learn more about your custom ML development services. Can we arrange a call?",
        "Hi David, I'm reaching out regarding your custom ML development package. Let's talk details.",
        "Hello, I saw your custom ML development service and need a bespoke model for my use case.",
        "Hi there, I'd like to engage your custom ML development expertise; when are you available?",
        "Hello David, could we discuss a custom ML project I'm planning?",
        "Hi David, please provide more information about your custom ML development service and pricing.",
        "Hello, I'm looking for a tailored machine learning solution and saw your service.",
        "Hi David, I'd like to schedule a call to explore your custom ML development services."
      ],
      "Data Pipelines & ETL": [
        "Hello David, I'm interested in your data pipelines & ETL service and would like to discuss building a pipeline.",
        "Hi David, could we talk about designing a robust ETL pipeline for my project?",
        "Hello David, I came across your data pipeline service—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your ETL expertise. Let's discuss how you can help my team.",
        "Hello, I'm looking for someone to engineer a data pipeline; your service seems ideal.",
        "Hi there, I'd like to engage your ETL services; when are you available?",
        "Hello David, could we discuss building a scalable data pipeline for my business?",
        "Hi David, please provide more information about your data pipelines & ETL offering and pricing.",
        "Hello, I need help setting up an ETL workflow and saw your service.",
        "Hi David, I'd like to schedule a call to talk through your data pipelines service."
      ],
      "MLOps & Deployment": [
        "Hello David, I'm interested in your MLOps & deployment service and would like to discuss containerising my models.",
        "Hi David, could we chat about setting up CI/CD for my machine learning projects?",
        "Hello David, I saw your MLOps & deployment offering—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your MLOps expertise. Let's talk about taking my models to production.",
        "Hello, I'd like to learn how you can deploy models at scale using MLOps best practices.",
        "Hi there, I'd like to engage your MLOps & deployment services; when are you available?",
        "Hello David, could we discuss designing a deployment pipeline for my ML project?",
        "Hi David, please provide more information about your MLOps & deployment services and pricing.",
        "Hello, I'm looking for help deploying an existing model and saw your service.",
        "Hi David, I'd like to schedule a call to explore your MLOps & deployment expertise."
      ],
      "Technical Writing": [
        "Hello David, I came across your technical writing service and would like help with documentation.",
        "Hi David, could we talk about crafting a whitepaper for my product?",
        "Hello David, I'm interested in your technical writing services—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your writing expertise. Let's discuss creating blog posts for my platform.",
        "Hello, I'd like to commission technical documentation and saw your service.",
        "Hi there, I'd like to engage your technical writing services; when are you available?",
        "Hello David, could we discuss producing clear docs for my project?",
        "Hi David, please provide more information about your technical writing services and pricing.",
        "Hello, I'm looking for help writing about a complex topic and saw your service.",
        "Hi David, I'd like to schedule a call to explore your technical writing offering."
      ],
      "Tutoring & Training": [
        "Hello David, I'd like to book a tutoring session with you. Can we set up a time?",
        "Hi David, I'm interested in your tutoring & training services—could we chat about scheduling?",
        "Hello David, I came across your tutoring service and would like guidance on data science topics.",
        "Hi David, I'm reaching out about your training offerings. Let's discuss a workshop for my team.",
        "Hello, I'm looking for personalised coaching and saw your tutoring service.",
        "Hi there, I'd like to engage your tutoring expertise; when are you available?",
        "Hello David, could we discuss a custom training programme?",
        "Hi David, please provide more information about your tutoring & training services and pricing.",
        "Hello, I'm seeking a mentor for ML and saw your tutoring service.",
        "Hi David, I'd like to schedule a call to explore your tutoring offerings."
      ],
      "Dashboards & Visualisation": [
        "Hello David, I'm interested in your dashboards & visualisation service and would like to discuss building a dashboard.",
        "Hi David, could we chat about creating an interactive dashboard for my data?",
        "Hello David, I came across your visualisation service—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your dashboard expertise. Let's talk details.",
        "Hello, I'd like to visualise my data and saw your dashboards service.",
        "Hi there, I'd like to engage your dashboards & visualisation services; when are you available?",
        "Hello David, could we discuss a dashboard project I'm planning?",
        "Hi David, please provide more information about your dashboards & visualisation service and pricing.",
        "Hello, I'm looking for help building reports and saw your visualisation service.",
        "Hi David, I'd like to schedule a call to explore your dashboards & visualisation offerings."
      ],
      "Research & Prototyping": [
        "Hello David, I'm interested in your research & prototyping service and would like to discuss an idea.",
        "Hi David, could we chat about exploring a proof‑of‑concept prototype?",
        "Hello David, I came across your research & prototyping offering—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your research expertise. Let's talk details.",
        "Hello, I'd like to build a quick prototype and saw your service.",
        "Hi there, I'd like to engage your research & prototyping services; when are you available?",
        "Hello David, could we discuss developing a proof of concept for my project?",
        "Hi David, please provide more information about your research & prototyping service and pricing.",
        "Hello, I'm looking for innovative research help and saw your service.",
        "Hi David, I'd like to schedule a call to explore your research & prototyping expertise."
      ],
      "Code Review & Mentorship": [
        "Hello David, I saw your code review & mentorship service and would like feedback on my project.",
        "Hi David, could we chat about mentorship and reviewing my machine learning code?",
        "Hello David, I'm interested in your code review services—can we arrange a consultation?",
        "Hi David, I'm reaching out regarding your mentorship offering. Let's talk details.",
        "Hello, I need guidance on best practices and saw your code review service.",
        "Hi there, I'd like to engage your code review & mentorship services; when are you available?",
        "Hello David, could we discuss a mentorship plan for improving my ML codebase?",
        "Hi David, please provide more information about your code review & mentorship services and pricing.",
        "Hello, I'm looking for a mentor in AI and saw your service.",
        "Hi David, I'd like to schedule a call to explore your code review & mentorship offerings."
      ]
    };

    const serviceButtons = document.querySelectorAll(".service-contact-btn");
    serviceButtons.forEach((btn) => {
      btn.addEventListener("click", () => {
        const serviceName = btn.dataset.service;
        const templates = contactTemplates[serviceName] || [
          `Hello David, I came about your ${serviceName} service. I would like to schedule a meeting to discuss this with you.`
        ];
        const message = templates[Math.floor(Math.random() * templates.length)];
        // Navigate to contact page by clicking the nav link with text "contact"
        navigationLinks.forEach((link) => {
          if (link.innerText.trim().toLowerCase() === "contact") {
            link.click();
          }
        });
        // After navigation, prefill the message field
        setTimeout(() => {
          const messageField = document.querySelector("textarea[name='message']");
          if (messageField) messageField.value = message;
          // Trigger input event so validation updates the send button
          messageField && messageField.dispatchEvent(new Event('input', { bubbles: true }));
        }, 300);
      });
    });

    // Contact form submission via API
    const contactForm = document.getElementById("contactForm");
    if (contactForm) {
      contactForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const payload = {
          name: contactForm.fullname.value.trim(),
          email: contactForm.email.value.trim(),
          message: contactForm.message.value.trim()
        };
        const errorEl = document.getElementById("contact-error");
        if (errorEl) errorEl.textContent = "";

        // Basic validation checks
        if (!payload.name) {
          if (errorEl) errorEl.textContent = "Please enter your full name.";
          return;
        }
        // simple email regex: contains @ and . after it
        const emailPattern = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
        if (!emailPattern.test(payload.email)) {
          if (errorEl) errorEl.textContent = "Please enter a valid email address (example@domain.com).";
          return;
        }
        if (!payload.message) {
          if (errorEl) errorEl.textContent = "Please enter your message.";
          return;
        }
        if (payload.message.length > 500) {
          if (errorEl) errorEl.textContent = "Your message must be at most 500 characters.";
          return;
        }
        try {
          const res = await fetch("/api/contact", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
          });
          const data = await res.json();
          if (data.ok) {
            if (errorEl) errorEl.textContent = "Message sent successfully ✅";
            contactForm.reset();
          } else {
            if (errorEl) errorEl.textContent = data.error || "Failed to send message.";
          }
        } catch (err) {
          if (errorEl) errorEl.textContent = "Failed to send message: " + err.message;
        }
      });
    }

    // ---------------------------------------------------------------
    // PORTFOLIO ORDERING
    // Reverse the order of projects so that the newest or most
    // significant work appears first.  This avoids manual reordering
    // of the HTML markup and makes it easier to adjust ordering later.
    const projectList = document.querySelector(".project-list");
    if (projectList) {
      const projects = Array.from(projectList.children);
      projects.reverse().forEach((item) => projectList.appendChild(item));
    }
  });
})();


window.addEventListener("DOMContentLoaded", () => {
  const communities = [
    "AI Saturdays Lagos",
    "Data Science Nigeria",
    "CYESEC Tech",
    "GDSC",
    "Zindi",
    "Udacity Nanodegree"
  ];

  function findProgramsMetaLine() {
    const all = Array.from(document.querySelectorAll("p, span, div"));
    const targetText = "Data Science";
    const targetText2 = "AI Programs";

    for (const node of all) {
      const t = (node.textContent || "").trim();
      if (t.includes(targetText) && t.includes(targetText2)) {
        let next = node.nextElementSibling;
        while (next) {
          const tn = (next.textContent || "").trim();
          if (tn.length) return next;
          next = next.nextElementSibling;
        }
      }
    }

    for (const node of all) {
      const t = (node.textContent || "").trim();
      if (t.startsWith("Various")) return node;
    }

    return null;
  }

  const metaLine = findProgramsMetaLine();
  if (!metaLine) return;

  metaLine.textContent = "";
  metaLine.style.display = "flex";
  metaLine.style.flexWrap = "wrap";
  metaLine.style.gap = "8px";
  metaLine.style.alignItems = "center";

  for (const name of communities) {
    const tag = document.createElement("span");
    tag.textContent = name;

    tag.style.display = "inline-flex";
    tag.style.alignItems = "center";
    tag.style.padding = "4px 10px";
    tag.style.borderRadius = "999px";
    tag.style.fontSize = "0.9em";
    tag.style.fontWeight = "500";
    tag.style.lineHeight = "1";

    tag.style.backgroundColor = "rgba(51, 102, 255, 0.18)";
    tag.style.color = "inherit";
    tag.style.border = "1px solid rgba(51, 102, 255, 0.35)";

    metaLine.appendChild(tag);
  }
});