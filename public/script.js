// ── Tech Pulse Dashboard — Minimal Interactivity (SSR by Python) ──
// Filters, tabs, search, scroll-to-top, dark theme. Content is pre-rendered in HTML.

(function () {
  "use strict";

  // ── State ──
  let state = {
    canalNoticias: "all",
    canalVideos: "all",
    tabMultimedia: "youtube",
  };

  // ── Chip click handlers ──
  function setupChipFilters(containerId, stateKey, filterFn) {
    const container = document.getElementById(containerId);
    if (!container) return;
    container.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      state[stateKey] = chip.dataset.channel || chip.dataset.category || chip.dataset.tab || "all";
      filterFn();
    });
  }

  // ── Search handlers ──
  function setupSearch(inputId, itemSelector, filterFn) {
    const input = document.getElementById(inputId);
    if (!input) return;
    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(filterFn, 200);
    });
  }

  // ── News filters ──
  function filtrarNoticias() {
    const q = (document.getElementById("news-search")?.value || "").toLowerCase().trim();
    document.querySelectorAll("#news-list .news-item").forEach((item) => {
      const source = item.dataset.source;
      const category = item.dataset.category;
      const title = (item.querySelector(".news-title") || {}).textContent || "";
      const okChannel = state.canalNoticias === "all" || source === state.canalNoticias;
      const okSearch = !q || title.toLowerCase().includes(q) || source.toLowerCase().includes(q);
      item.style.display = okChannel && okSearch ? "" : "none";
    });
  }

  // ── Video filters ──
  function filtrarVideos() {
    const q = (document.getElementById("video-search")?.value || "").toLowerCase().trim();
    document.querySelectorAll("#multimedia-content .video-card").forEach((item) => {
      const source = item.dataset.source;
      const type = item.dataset.tipo || "youtube";
      const title = (item.querySelector(".video-title") || {}).textContent || "";
      const okChannel = state.canalVideos === "all" || source === state.canalVideos;
      const okTab = state.tabMultimedia === "all" || type === state.tabMultimedia;
      const okSearch = !q || title.toLowerCase().includes(q) || source.toLowerCase().includes(q);
      item.style.display = okChannel && okTab && okSearch ? "" : "none";
    });
  }

  // ── Tab switching ──
  function setupTabs() {
    const container = document.getElementById("multimedia-tabs");
    if (!container) return;
    container.addEventListener("click", (e) => {
      const chip = e.target.closest(".chip");
      if (!chip) return;
      container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
      chip.classList.add("active");
      state.tabMultimedia = chip.dataset.tab || "youtube";
      filtrarVideos();
    });
  }

  // ── GitHub search ──
  function setupGithubSearch() {
    const input = document.getElementById("github-filter");
    if (!input) return;
    let timer;
    input.addEventListener("input", () => {
      clearTimeout(timer);
      timer = setTimeout(() => {
        const q = input.value.toLowerCase().trim();
        document.querySelectorAll("#github-ranking .github-item").forEach((item) => {
          const name = (item.querySelector(".github-name") || {}).textContent || "";
          const lang = item.dataset.lang || "";
          const desc = (item.querySelector(".github-desc") || {}).textContent || "";
          const match = !q || name.toLowerCase().includes(q) || lang.includes(q) || desc.toLowerCase().includes(q);
          item.style.display = match ? "" : "none";
        });
      }, 300);
    });
  }

  // ── Scroll to top ──
  function setupScrollTop() {
    const btn = document.createElement("button");
    btn.className = "scroll-top";
    btn.innerHTML = "&#8593;";
    btn.setAttribute("aria-label", "Volver arriba");
    document.body.appendChild(btn);
    window.addEventListener("scroll", () => btn.classList.toggle("visible", window.scrollY > 400), { passive: true });
    btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
  }

  // ── Dark theme with circular reveal ──
  function setupDarkTheme() {
    const btn = document.getElementById("theme-toggle");
    if (!btn) return;
    const saved = localStorage.getItem("theme");
    if (saved === "dark") document.body.classList.add("dark");
    updateThemeIcon();

    // Create overlay for circular transition
    const overlay = document.createElement("div");
    overlay.id = "theme-transition-overlay";
    overlay.style.cssText = "position:fixed;inset:0;z-index:9999;pointer-events:none;transition:clip-path 0.5s cubic-bezier(0.4,0,0.2,1);clip-path:circle(0% at 50% 50%);";
    document.body.appendChild(overlay);

    btn.addEventListener("click", (e) => {
      const goingDark = !document.body.classList.contains("dark");

      // Set overlay background to the TARGET theme
      overlay.style.background = goingDark ? "#18181b" : "#e8edf5";

      // Calculate center of the toggle button
      const rect = btn.getBoundingClientRect();
      const cx = rect.left + rect.width / 2;
      const cy = rect.top + rect.height / 2;

      // Start from 0%, expand to cover entire viewport
      overlay.style.clipPath = `circle(0% at ${cx}px ${cy}px)`;
      overlay.style.pointerEvents = "all";

      // Force reflow so the browser registers the start state
      void overlay.offsetWidth;

      // Expand to cover full screen
      const maxRadius = Math.hypot(Math.max(cx, window.innerWidth - cx), Math.max(cy, window.innerHeight - cy));
      const pct = Math.ceil((maxRadius / Math.hypot(window.innerWidth, window.innerHeight)) * 100) + 5;
      overlay.style.clipPath = `circle(${pct}% at ${cx}px ${cy}px)`;

      // Switch theme at midpoint
      setTimeout(() => {
        document.body.classList.toggle("dark");
        localStorage.setItem("theme", document.body.classList.contains("dark") ? "dark" : "light");
        updateThemeIcon();
      }, 250);

      // Remove overlay after transition
      setTimeout(() => {
        overlay.style.clipPath = `circle(0% at ${cx}px ${cy}px)`;
        overlay.style.pointerEvents = "none";
      }, 550);
    });

    function updateThemeIcon() {
      btn.textContent = document.body.classList.contains("dark") ? "\u2600\uFE0F" : "\uD83C\uDF19";
    }
  }

  // ── Init ──
  document.addEventListener("DOMContentLoaded", () => {
    setupSearch("news-search", "#news-list .news-item", filtrarNoticias);
    setupChipFilters("news-channel-filters", "canalNoticias", filtrarNoticias);
    setupSearch("video-search", "#multimedia-content .video-card", filtrarVideos);
    setupChipFilters("video-channel-filters", "canalVideos", filtrarVideos);
    setupTabs();
    setupGithubSearch();
    setupScrollTop();
    setupDarkTheme();
  });
})();
