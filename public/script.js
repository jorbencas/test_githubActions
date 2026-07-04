// ── Tech Pulse Dashboard — Minimal Interactivity (SSR by Python) ──
// Filters, tabs, search, scroll-to-top. Content is pre-rendered in HTML.

(function () {
  "use strict";

  // ── Helpers ──
  function itemEnSemana(ts, sel) {
    if (!ts) return false;
    const ahora = Date.now();
    const limite = ahora - 14 * 86400000;
    if (sel === "all" || sel === "all_recent") return new Date(ts).getTime() >= limite;
    // Week key format: "2026-W27"
    const itemDate = new Date(ts);
    const [year, week] = sel.split("-W").map(Number);
    const itemYear = itemDate.getFullYear();
    const itemWeek = getISOWeek(itemDate);
    return itemYear === year && itemWeek === week;
  }

  function getISOWeek(date) {
    const d = new Date(date);
    d.setHours(0, 0, 0, 0);
    d.setDate(d.getDate() + 3 - ((d.getDay() + 6) % 7));
    const week1 = new Date(d.getFullYear(), 0, 4);
    return 1 + Math.round(((d - week1) / 86400000 - 3 + ((week1.getDay() + 6) % 7)) / 7);
  }

  // ── State ──
  let state = {
    semanaNoticias: "all",
    canalNoticias: "all",
    catNoticias: "all",
    semanaVideos: "all",
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
      state[stateKey] = chip.dataset.week || chip.dataset.channel || chip.dataset.category || chip.dataset.tab || "all";
      filterFn();
    });
  }

  // ── News filters ──
  function filtrarNoticias() {
    document.querySelectorAll("#news-list .news-item").forEach((item) => {
      const ts = item.dataset.ts;
      const source = item.dataset.source;
      const category = item.dataset.category;
      const okWeek = itemEnSemana(ts, state.semanaNoticias);
      const okChannel = state.canalNoticias === "all" || source === state.canalNoticias;
      const okCategory = state.catNoticias === "all" || category === state.catNoticias;
      item.style.display = okWeek && okChannel && okCategory ? "" : "none";
    });
  }

  // ── Video filters ──
  function filtrarVideos() {
    document.querySelectorAll("#multimedia-content .video-card").forEach((item) => {
      const ts = item.dataset.ts;
      const source = item.dataset.source;
      const type = item.dataset.type || "youtube";
      const okWeek = itemEnSemana(ts, state.semanaVideos);
      const okChannel = state.canalVideos === "all" || source === state.canalVideos;
      const okTab = state.tabMultimedia === "all" || type === state.tabMultimedia;
      item.style.display = okWeek && okChannel && okTab ? "" : "none";
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

  // ── Init ──
  document.addEventListener("DOMContentLoaded", () => {
    setupChipFilters("news-week-filters", "semanaNoticias", filtrarNoticias);
    setupChipFilters("news-channel-filters", "canalNoticias", filtrarNoticias);
    setupChipFilters("news-category-filters", "catNoticias", filtrarNoticias);
    setupChipFilters("video-week-filters", "semanaVideos", filtrarVideos);
    setupChipFilters("video-channel-filters", "canalVideos", filtrarVideos);
    setupTabs();
    setupGithubSearch();
    setupScrollTop();
  });
})();
