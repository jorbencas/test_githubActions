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

  // ── Select (combobox) handlers ──
  function setupSelectFilters(selectId, stateKey, filterFn) {
    const sel = document.getElementById(selectId);
    if (!sel) return;
    sel.addEventListener("change", () => {
      state[stateKey] = sel.value || "all";
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
    setupSelectFilters("selectorSemanas", "semanaNoticias", filtrarNoticias);
    setupChipFilters("news-channel-filters", "canalNoticias", filtrarNoticias);
    setupChipFilters("news-category-filters", "catNoticias", filtrarNoticias);
    setupSelectFilters("selectorSemanasVideos", "semanaVideos", filtrarVideos);
    setupChipFilters("video-channel-filters", "canalVideos", filtrarVideos);
    setupTabs();
    setupGithubSearch();
    setupScrollTop();
  });
})();

// ── Video Download (disabled — was used for Hugging Face API integration) ──
// async function descargarVideo(urlVideo, boton) {
//   const originalText = boton.innerHTML;
//   boton.innerHTML = "⏳...";
//
//   const tokenElement = document.getElementById("api-base-token");
//   const TOKEN_BASE = tokenElement ? tokenElement.content : "";
//   if (!TOKEN_BASE) {
//     console.error("Error de configuración: No se encontró el token base.");
//     return;
//   }
//
//   const fechaHoy = new Date().toISOString().split("T")[0];
//   const semilla = `${TOKEN_BASE}-${fechaHoy}`;
//   const tokenHashed = await generarSHA256(semilla);
//
//   const apiUrl = `https://testactions1github-api-python.hf.space/download?url=${encodeURIComponent(urlVideo)}`;
//
//   try {
//     const response = await fetch(apiUrl, {
//       method: "GET",
//       headers: {
//         "X-API-Key": tokenHashed,
//         "Content-Type": "application/json",
//       },
//     });
//
//     if (!response.ok) {
//       const errorData = await response.json();
//       throw new Error(errorData.detail || "Error en el servidor");
//     }
//
//     const data = await response.json();
//     const a = document.createElement("a");
//     a.href = data.url;
//     a.target = "_blank";
//     a.download = `${data.title}.mp4`;
//     document.body.appendChild(a);
//     a.click();
//     a.remove();
//   } catch (error) {
//     console.error("Error:", error.message);
//     boton.innerHTML = "❌";
//   } finally {
//     setTimeout(() => (boton.innerHTML = originalText), 3000);
//   }
// }
//
// async function generarSHA256(mensaje) {
//   const encoder = new TextEncoder();
//   const data = encoder.encode(mensaje);
//   const hashBuffer = await crypto.subtle.digest("SHA-256", data);
//   const hashArray = Array.from(new Uint8Array(hashBuffer));
//   return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
// }
