// ── Observable Store ──
const store = (() => {
  const state = {
    semanaNoticias: { tipo: "all_recent", ini: null, fin: null },
    semanaVideos: { tipo: "all_recent", ini: null, fin: null },
    catNoticias: "all", rssNoticias: "all",
    canalNoticias: "all", canalVideos: "all",
    tipoFuente: "all", tabMultimedia: "youtube",
    items: [], herramientas: [], trends: [], avatars: {},
    refSkills: {}, refLlms: {}, refLenguajes: {}, refFrameworks: {}, refLibrerias: {},
    config: {},
  };
  const listeners = {};
  return {
    get(k) { return state[k]; },
    set(k, v) {
      state[k] = v;
      (listeners[k] || []).forEach(fn => fn(v));
    },
    on(k, fn) {
      (listeners[k] = listeners[k] || []).push(fn);
      return () => { listeners[k] = listeners[k].filter(f => f !== fn); };
    },
    _raw: state,
  };
})();

// ── Pure helpers ──
const limpiarFuente = (f) => (f || "").replace(" Shorts", "");

function tipoFuente(name) {
  const s = (name || "").toLowerCase();
  const yt = (store.get("config").ALL_YT_CHANNELS || []);
  if (yt.some(c => c.toLowerCase() === s)) return "youtube";
  if (s.includes("twitter") || s.includes("x.com")) return "twitter";
  return "web";
}

function tipoMultimedia(item) {
  if (item.id_video) return "youtube";
  const f = (item.fuente || "").toLowerCase();
  if (f.includes("tiktok")) return "tiktok";
  if (f.includes("instagram")) return "instagram";
  return null;
}

function dominioUrl(url) {
  try { return new URL(url).hostname; } catch(e) { return ""; }
}

function itemEnSemana(ts, sel) {
  const ahora = Date.now();
  const limite = ahora - 14 * 86400000;
  if (sel.tipo === "all_recent") return ts >= limite;
  if (sel.tipo === "range") return ts >= sel.ini && ts <= sel.fin;
  return false;
}

function faviconSrc(sourceName) {
  const av = store.get("avatars")[sourceName];
  if (av) return av;
  const item = store.get("items").find(i => limpiarFuente(i.fuente) === sourceName && i.enlace);
  return item ? `https://www.google.com/s2/favicons?domain=${dominioUrl(item.enlace)}&sz=32` : "";
}

function chipImg(label, sourceName) {
  const src = faviconSrc(sourceName);
  return src
    ? `<img class="chip-img" src="${src}" onerror="this.style.display='none'" loading="lazy"><span class="chip-text">${label}</span>`
    : `<span class="chip-text">${label}</span>`;
}

// ── Data ──
function cargarDatos() {
  document.addEventListener("DOMContentLoaded", async () => {
    try {
      const resp = await fetch(DATA_URL);
      const data = await resp.json();
      store._raw.items = data.items || [];
      store._raw.herramientas = data.herramientas || [];
      store._raw.trends = data.trends || [];
      store._raw.avatars = data.avatars || {};
      store._raw.refSkills = data.skills || {};
      store._raw.refLlms = data.llms || {};
      store._raw.refLenguajes = data.lenguajes || {};
      store._raw.refFrameworks = data.frameworks || {};
      store._raw.refLibrerias = data.librerias || {};
      store._raw.config = data.config_js || {};
      const now = new Date();
      document.getElementById("header-date").textContent =
        now.toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit", year: "numeric" });
      initDashboard();
    } catch (err) {
      console.error("Error loading data.json:", err);
      document.getElementById("news-list").innerHTML =
        '<li style="color:#dc2626; padding: 20px;">Error al cargar datos.</li>';
    }
  });
}

// ── Week selector ──
function crearSelectSemanas(items, prefix) {
  const select = document.createElement("select");
  select.id = `selectorSemanas_${prefix}`;
  select.style.cssText =
    "padding:10px 15px;border-radius:20px;border:2px solid #007bff;background:white;color:#007bff;font-weight:bold;cursor:pointer;outline:none;margin-left:10px;box-shadow:0 2px 4px rgba(0,0,0,0.05)";
  select.innerHTML = '<option value="all">📅 Archivo Histórico...</option>';
  const timestamps = items.map(i => new Date(i.ts).getTime()).filter(t => !isNaN(t));
  if (timestamps.length === 0) return select;
  const minTs = Math.min(...timestamps);
  const maxTs = Math.max(...timestamps);
  const start = new Date(minTs); start.setDate(start.getDate() - start.getDay());
  const end = new Date(maxTs); end.setDate(end.getDate() + (6 - end.getDay()));
  const monthCounts = {};
  items.forEach(i => {
    const d = new Date(i.ts);
    if (!isNaN(d)) {
      const mk = d.toLocaleDateString("es-ES", { month: "long", year: "numeric" });
      monthCounts[mk] = (monthCounts[mk] || 0) + 1;
    }
  });
  let lastMonth = "";
  for (let w = new Date(end); w >= start; w.setDate(w.getDate() - 7)) {
    const fin = new Date(w); fin.setDate(fin.getDate() + 6);
    const mk = w.toLocaleDateString("es-ES", { month: "long", year: "numeric" });
    if (mk !== lastMonth) {
      if (lastMonth) select.innerHTML += "</optgroup>";
      select.innerHTML += `<optgroup label="── ${mk} (${monthCounts[mk] || 0} ítems) ──">`;
      lastMonth = mk;
    }
    select.innerHTML += `<option value="${w.toISOString()}|${fin.toISOString()}">Semana ${w.toLocaleDateString("es-ES", { day:"2-digit", month:"2-digit" })}</option>`;
  }
  if (lastMonth) select.innerHTML += "</optgroup>";
  return select;
}

function renderWeekFilter(containerId, selectPrefix, storeKey, items) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.innerHTML = "";
  const chip = document.createElement("div");
  chip.className = "chip active";
  chip.textContent = "🔄 Últimas 2 Semanas";
  chip.onclick = () => {
    store.set(storeKey, { tipo: "all_recent", ini: null, fin: null });
    const sel = document.getElementById(`selectorSemanas_${selectPrefix}`);
    if (sel) sel.value = "all";
    container.querySelectorAll(".chip").forEach(c => c.classList.remove("active"));
    chip.classList.add("active");
  };
  container.appendChild(chip);
  const select = crearSelectSemanas(items, selectPrefix);
  select.onchange = () => {
    if (select.value === "all") {
      store.set(storeKey, { tipo: "all_recent", ini: null, fin: null });
    } else {
      container.querySelectorAll('[data-inicio="all_recent"]').forEach(c => c.classList.remove("active"));
      const [ini, fin] = select.value.split("|");
      store.set(storeKey, { tipo: "range", ini: new Date(ini).getTime(), fin: new Date(fin).getTime() });
    }
  };
  container.appendChild(select);
}

// ── Channel lists ──
function canalesNoticias(items) {
  const seen = new Set();
  const tf = store.get("tipoFuente");
  const yt = (store.get("config").ALL_YT_CHANNELS || []);
  if (tf === "all" || tf === "youtube") yt.forEach(c => seen.add(c));
  items.forEach(i => {
    if (i.id_video) return;
    const ch = limpiarFuente(i.fuente);
    if (tf !== "all" && tipoFuente(ch) !== tf) return;
    seen.add(ch);
  });
  return [...seen].sort();
}

function canalesVideos(items) {
  const seen = new Set();
  const tab = store.get("tabMultimedia");
  const yt = (store.get("config").ALL_YT_CHANNELS || []);
  if (tab === "youtube") yt.forEach(c => seen.add(c));
  items.forEach(i => {
    if (tipoMultimedia(i) !== tab) return;
    const ch = limpiarFuente(i.fuente);
    seen.add(ch);
  });
  return [...seen].sort();
}

// ── Renderers ──
function renderChips(containerId, opts) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const { options, stateKey, withImage } = opts;
  const render = () => {
    const active = store.get(stateKey);
    container.innerHTML = "";
    options.forEach(opt => {
      const chip = document.createElement("div");
      chip.className = "chip" + (active === opt.id ? " active" : "");
      chip.innerHTML = withImage ? chipImg(opt.label, opt.id) : `<span class="chip-text">${opt.label}</span>`;
      chip.onclick = () => store.set(stateKey, opt.id);
      container.appendChild(chip);
    });
  };
  store.on(stateKey, render);
  render();
}

function renderCanalChips(containerId, channels, stateKey) {
  const container = document.getElementById(containerId);
  if (!container) return;
  const opts = [{ id: "all", label: "Todos" }, ...channels.map(c => ({ id: c, label: c }))];
  const render = () => {
    const active = store.get(stateKey);
    container.innerHTML = "";
    opts.forEach(opt => {
      const chip = document.createElement("div");
      chip.className = "chip" + (active === opt.id ? " active" : "");
      chip.innerHTML = opt.id === "all" ? "<span>Todos</span>" : chipImg(opt.label, opt.id);
      chip.onclick = () => store.set(stateKey, opt.id);
      container.appendChild(chip);
    });
  };
  store.on(stateKey, render);
  render();
}

function renderStats(items) {
  const news = items.filter(i => tipoMultimedia(i) === null);
  const multimedia = items.filter(i => tipoMultimedia(i) !== null);
  document.getElementById("stats-bar").innerHTML = `
    <div class="stat-card"><b>${items.length}</b><span>Total</span></div>
    <div class="stat-card"><b>${news.filter(i => i.badge === "Tech").length}</b><span>Tech</span></div>
    <div class="stat-card"><b>${multimedia.length}</b><span>Multimedia</span></div>`;
}

function renderNoticias(items) {
  const ul = document.getElementById("news-list");
  ul.innerHTML = items
    .filter(i => tipoMultimedia(i) === null)
    .map(i => {
      const ts = i.ts || new Date().toISOString();
      const fuente = limpiarFuente(i.fuente);
      const badge = i.badge || "Tech";
      const cat = i.categoria || "";
      const tf = tipoFuente(i.fuente);
      const badges = [];
      if (i.origen === "rss") badges.push('<span class="badge badge-rss">📡 RSS</span>');
      return `<li class="news-item" data-ts="${ts}" data-fuente="${fuente}" data-categoria="${cat}" data-origen="${i.origen || "web"}" data-tipo-fuente="${tf}">
        <div class="meta">${i.fuente} | ${i.fecha_publicacion || i.fecha_real || i.f || "S/D"}</div>
        <span class="badge badge-tech">${badge}</span>
        ${badges.join("")}
        ${cat ? `<span class="badge badge-cat">${cat}</span>` : ""}
        <a href="${i.enlace}" target="_blank">${i.titulo || "Ver noticia"}</a></li>`;
    }).join("");
}

// ── Filters (operan sobre DOM, reaccionan a cambios de store) ──
function aplicarFiltrosNoticias() {
  document.querySelectorAll(".news-item").forEach(item => {
    const ts = item.getAttribute("data-ts");
    if (!ts) return;
    const ok = itemEnSemana(new Date(ts).getTime(), store.get("semanaNoticias"))
      && (store.get("canalNoticias") === "all" || item.getAttribute("data-fuente") === store.get("canalNoticias"))
      && (store.get("catNoticias") === "all" || item.getAttribute("data-categoria") === store.get("catNoticias"))
      && (store.get("tipoFuente") === "all" || (item.getAttribute("data-tipo-fuente") || "") === store.get("tipoFuente"))
      && (store.get("rssNoticias") === "all" || (item.getAttribute("data-origen") === "rss" && item.getAttribute("data-fuente") === store.get("rssNoticias")));
    item.style.display = ok ? "list-item" : "none";
  });
}

function aplicarFiltrosVideos() {
  document.querySelectorAll("#multimedia-content .card, #multimedia-content .news-item").forEach(item => {
    const ts = item.getAttribute("data-ts");
    if (!ts) return;
    const ok = itemEnSemana(new Date(ts).getTime(), store.get("semanaVideos"))
      && (store.get("canalVideos") === "all" || item.getAttribute("data-fuente") === store.get("canalVideos"));
    item.style.display = ok ? "block" : "none";
  });
}

// ── Multimedia tabs ──
function renderTabsMultimedia() {
  const container = document.getElementById("multimedia-tabs");
  if (!container) return;
  const tabs = (store.get("config").TABS_MULTIMEDIA || []);
  const render = () => {
    const active = store.get("tabMultimedia");
    container.innerHTML = "";
    tabs.forEach(t => {
      const chip = document.createElement("div");
      chip.className = "chip" + (active === t.id ? " active" : "");
      chip.innerHTML = `<span class="chip-text">${t.label}</span>`;
      chip.onclick = () => store.set("tabMultimedia", t.id);
      container.appendChild(chip);
    });
  };
  store.on("tabMultimedia", render);
  render();
}

function renderContenidoMultimedia(items) {
  const c = document.getElementById("multimedia-content");
  if (!c) return;
  const tab = store.get("tabMultimedia");
  if (tab === "youtube") return renderYouTube(items, c);
  if (tab === "tiktok") return renderSocial(items, c, "tiktok", "🎵");
  if (tab === "instagram") return renderSocial(items, c, "instagram", "📸");
}

function renderYouTube(items, container) {
  const videos = items.filter(i => i.id_video);
  if (videos.length === 0) {
    container.innerHTML = '<p style="padding:20px;color:#666;text-align:center;">No hay vídeos en este período.</p>';
    return;
  }
  container.innerHTML = videos.map(i => {
    const ts = i.ts || new Date().toISOString();
    const fuente = limpiarFuente(i.fuente);
    const fecha = i.fecha_publicacion || i.fecha_real || i.f || "S/D";
    const tipo = i.tipo || "video";
    const esLive = tipo === "live";
    const clase = esLive ? "tipo-live" : tipo === "shorts" ? "tipo-shorts" : "tipo-video";
    return `<div class="card ${clase}" data-ts="${ts}" data-fuente="${fuente}" data-tipo-fuente="youtube">
      ${esLive ? '<span class="badge-live">● EN DIRECTO</span>' : ""}
      <a href="${i.enlace}" target="_blank" class="video-thumb-link">
        <div class="video-thumb">
          <img src="https://img.youtube.com/vi/${i.id_video}/mqdefault.jpg" alt="${i.titulo || ""}" width="320" height="180" loading="lazy" class="video-thumb-img" onerror="this.classList.add('errored');this.nextElementSibling.classList.add('visible')">
          <div class="video-thumb-fallback">📺 ${i.fuente || "YouTube"}</div>
        </div>
      </a>
      <div class="card-content">
        <div class="meta">${i.fuente} | ${fecha}</div>
        <a href="${i.enlace}" target="_blank">${i.titulo || "Ver video en YouTube"}</a>
      </div>
    </div>`;
  }).join("");
}

function renderSocial(items, container, type, emoji) {
  const filtered = items.filter(i => tipoMultimedia(i) === type);
  if (filtered.length === 0) {
    container.innerHTML = `<p style="padding:20px;color:#666;text-align:center;">No hay contenido de ${type} en este período.</p>`;
    return;
  }
  container.innerHTML = filtered.map(i => {
    const ts = i.ts || new Date().toISOString();
    const fuente = limpiarFuente(i.fuente);
    const fecha = i.fecha_publicacion || i.fecha_real || i.f || "S/D";
    return `<div class="news-item" data-ts="${ts}" data-fuente="${fuente}" data-tipo-fuente="${tipoFuente(i.fuente)}">
      <div class="meta">${emoji} ${i.fuente} | ${fecha}</div>
      <a href="${i.enlace}" target="_blank">${i.titulo || "Ver contenido"}</a>
    </div>`;
  }).join("");
}

// ── GitHub ranking ──
function renderRanking(items) {
  const container = document.getElementById("github-ranking");
  if (!container) return;
  if (!items || items.length === 0) {
    container.innerHTML = '<p style="padding:20px;color:#666;text-align:center;">No hay datos de repositorios.</p>';
    return;
  }
  container.innerHTML = items.map((r, i) => {
    const lang = r.lenguaje || "";
    const stars = Number(r.estrellas) || 0;
    return `<div class="news-item" style="border-left-color:#f59e0b;">
      <div class="meta"><span>#${i+1} ⭐ ${stars >= 1000 ? (stars/1000).toFixed(1)+"k" : stars}</span>${lang ? `<span class="badge badge-tech">${lang}</span>` : ""}</div>
      <a href="${r.enlace}" target="_blank">${r.titulo}</a>
      ${r.descripcion ? `<div style="font-size:0.85em;color:#64748b;margin-top:4px;">${r.descripcion.slice(0,120)}</div>` : ""}
    </div>`;
  }).join("");
}

// ── Reference ──
function renderRefGroup(containerId, data) {
  const container = document.getElementById(containerId);
  if (!container || !data) return;
  container.innerHTML = "";
  Object.entries(data).forEach(([group, items]) => {
    const groupDiv = document.createElement("div");
    groupDiv.style.cssText = "margin-bottom:8px;";
    groupDiv.innerHTML = `<strong style="font-size:0.85em;color:#555;display:block;margin-bottom:4px;">${group}</strong>`;
    items.forEach(item => {
      const chip = document.createElement("span");
      chip.className = "chip";
      chip.style.cssText = "padding:2px 10px;font-size:12px;cursor:default;";
      chip.textContent = item;
      groupDiv.appendChild(chip);
    });
    container.appendChild(groupDiv);
  });
}

function renderReference() {
  renderRefGroup("ref-skills", store.get("refSkills"));
  renderRefGroup("ref-llms", store.get("refLlms"));
  renderRefGroup("ref-lenguajes", store.get("refLenguajes"));
  renderRefGroup("ref-frameworks", store.get("refFrameworks"));
  renderRefGroup("ref-librerias", store.get("refLibrerias"));
}

// ── Trends ──
function renderTrends(items) {
  const container = document.getElementById("trends-list");
  if (!container) return;
  const trendType = store.get("trendType");
  const filtered = trendType === "all" ? items : items.filter(i => i.tipo === trendType);
  if (filtered.length === 0) {
    container.innerHTML = '<p style="padding:20px;color:#666;text-align:center;">No hay tendencias en este período.</p>';
    return;
  }
  container.innerHTML = filtered.map(i => {
    const ts = i.ts || "";
    const fecha = i.fecha_publicacion || i.fecha_real || i.f || "";
    const tipo = i.tipo === "trend" ? "📊" : "🎵";
    const tipoLabel = i.tipo === "trend" ? "Google Trends" : "TikTok";
    return `<li class="news-item" data-ts="${ts}">
      <div class="meta">${tipo} ${tipoLabel} | ${fecha}</div>
      <span class="badge badge-tech">${tipoLabel}</span>
      <a href="${i.enlace}" target="_blank">${i.titulo || "Ver tendencia"}</a>
    </li>`;
  }).join("");
}

// ── Side effects registrados (se ejecutan al cambiar el key correspondiente) ──
function registrarEventos() {
  store.on("tipoFuente", () => {
    const rssSection = document.getElementById("news-rss-filters");
    if (rssSection) rssSection.style.display = store.get("tipoFuente") === "rss" ? "" : "none";
    renderCanalChips("news-channel-filters", canalesNoticias(store.get("items")), "canalNoticias");
    renderCanalChips("video-channel-filters", canalesVideos(store.get("items")), "canalVideos");
    renderContenidoMultimedia(store.get("items"));
    aplicarFiltrosVideos();
  });

  store.on("tabMultimedia", () => {
    renderContenidoMultimedia(store.get("items"));
    aplicarFiltrosVideos();
  });

  store.on("semanaNoticias", aplicarFiltrosNoticias);
  store.on("canalNoticias", aplicarFiltrosNoticias);
  store.on("catNoticias", aplicarFiltrosNoticias);
  store.on("rssNoticias", aplicarFiltrosNoticias);
  store.on("semanaVideos", aplicarFiltrosVideos);
  store.on("canalVideos", aplicarFiltrosVideos);
  store.on("trendType", () => renderTrends(store.get("trends")));
}

// ── Init ──
function initScrollTop() {
  const btn = document.createElement("button");
  btn.className = "scroll-top";
  btn.innerHTML = "&#8593;";
  btn.setAttribute("aria-label", "Volver arriba");
  document.body.appendChild(btn);
  window.addEventListener("scroll", () => btn.classList.toggle("visible", window.scrollY > 400), { passive: true });
  btn.addEventListener("click", () => window.scrollTo({ top: 0, behavior: "smooth" }));
}

function initGithubFilter() {
  const input = document.getElementById("github-filter");
  if (!input) return;
  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const q = input.value.toLowerCase().trim();
      renderRanking(q ? store.get("herramientas").filter(r =>
        (r.titulo || "").toLowerCase().includes(q) ||
        (r.lenguaje || "").toLowerCase().includes(q) ||
        (r.descripcion || "").toLowerCase().includes(q)
      ) : store.get("herramientas"));
    }, 300);
  });
}

function initDashboard() {
  const items = store.get("items");
  renderStats(items);
  registrarEventos();

  renderChips("news-tipo-fuente-filters", {
    options: (store.get("config").FILTRO_TIPO_FUENTE || []),
    stateKey: "tipoFuente",
  });

  const topCats = Object.entries(
    items.filter(i => !i.id_video && i.categoria)
      .reduce((acc, i) => { acc[i.categoria] = (acc[i.categoria] || 0) + 1; return acc; }, {})
  ).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([cat]) => cat);

  renderChips("news-category-filters", {
    options: [{ id: "all", label: "Todas" }, ...topCats.map(c => ({ id: c, label: c }))],
    stateKey: "catNoticias",
  });

  const rssSources = [...new Set(items.filter(i => i.origen === "rss").map(i => i.fuente))].sort();
  renderChips("news-rss-filters", {
    options: [{ id: "all", label: "Todas" }, ...rssSources.map(s => ({ id: s, label: s }))],
    stateKey: "rssNoticias",
    withImage: true,
  });

  renderWeekFilter("news-week-filters", "noticias", "semanaNoticias", items);
  renderCanalChips("news-channel-filters", canalesNoticias(items), "canalNoticias");
  renderWeekFilter("video-week-filters", "videos", "semanaVideos", items);
  renderCanalChips("video-channel-filters", canalesVideos(items), "canalVideos");
  renderTabsMultimedia();
  renderContenidoMultimedia(items);
  renderNoticias(items);
  renderRanking(store.get("herramientas"));
  renderReference();
  renderTrends(store.get("trends"));
  renderChips("trend-type-filters", {
    options: [
      { id: "all", label: "Todas" },
      { id: "trend", label: "📊 Google Trends" },
      { id: "social", label: "🎵 TikTok" },
    ],
    stateKey: "trendType",
  });
  aplicarFiltrosNoticias();
  aplicarFiltrosVideos();
  initScrollTop();
  initGithubFilter();
}

cargarDatos();
