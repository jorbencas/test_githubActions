let selSemanaNoticias = { tipo: "all_recent", ini: null, fin: null };
let selSemanaVideos = { tipo: "all_recent", ini: null, fin: null };
let selCategoriaNoticias = "all";
let selBadgeNoticias = "all";
let selRssNoticias = "all";
let selCanalNoticias = "all";
let selCanalVideos = "all";
let allItems = [];
let herramientas = [];
let avatars = {};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const resp = await fetch(DATA_URL);
    const data = await resp.json();
    allItems = data.items || [];
    herramientas = data.herramientas || [];
    avatars = data.avatars || {};
    initDashboard();
  } catch (err) {
    console.error("Error loading data.json:", err);
    document.getElementById("news-list").innerHTML =
      '<li style="color:#dc2626; padding: 20px;">Error al cargar datos.</li>';
  }
});

function initDashboard() {
  renderStats(allItems);
  renderNewsCategoryChips(allItems);
  renderNewsBadgeChips(allItems);
  renderNewsRssChips(allItems);
  renderNewsWeekFilters(allItems);
  renderNewsChannelChips(allItems);
  renderVideoWeekFilters(allItems);
  renderVideoChannelChips(allItems);
  renderItems(allItems);
  renderGithubRanking(herramientas);
  aplicarFiltrosNoticias();
  aplicarFiltrosVideos();
  initScrollToTop();
  initGithubFilter();
}

function getNewsChannels(items) {
  const seen = new Set();
  items.forEach((item) => {
    if (item.id_video) return;
    const ch = (item.fuente || "").replace(" Shorts", "");
    if (!seen.has(ch)) seen.add(ch);
  });
  return Array.from(seen);
}

function getVideoChannels(items) {
  const seen = new Set();
  items.forEach((item) => {
    if (!item.id_video) return;
    const ch = (item.fuente || "").replace(" Shorts", "");
    if (!seen.has(ch)) seen.add(ch);
  });
  return Array.from(seen);
}

function renderStats(items) {
  const countTech = items.filter((i) => i.badge === "Tech").length;
  const countBecas = items.filter((i) => i.badge === "Beca").length;
  const countVids = items.filter((i) => i.id_video).length;
  document.getElementById("stats-bar").innerHTML = `
    <div class="stat-card"><b>${items.length}</b><span>Total</span></div>
    <div class="stat-card"><b>${countTech}</b><span>Tech</span></div>
    <div class="stat-card"><b>${countBecas}</b><span>Becas</span></div>
    <div class="stat-card"><b>${countVids}</b><span>Multimedia</span></div>`;
}

function generarSelectSemanas(items, prefix) {
  const select = document.createElement("select");
  select.id = `selectorSemanas_${prefix}`;
  select.style.cssText =
    "padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);";
  select.innerHTML = '<option value="all">📅 Archivo Histórico...</option>';

  const tsValues = items.map((i) => new Date(i.ts).getTime()).filter((t) => !isNaN(t));
  if (tsValues.length === 0) return select;
  const minTs = Math.min(...tsValues);
  const maxTs = Math.max(...tsValues);
  const startWeek = new Date(minTs);
  startWeek.setDate(startWeek.getDate() - startWeek.getDay());
  const endWeek = new Date(maxTs);
  endWeek.setDate(endWeek.getDate() + (6 - endWeek.getDay()));

  const monthCounts = {};
  items.forEach((i) => {
    const d = new Date(i.ts);
    if (!isNaN(d.getTime())) {
      const mk = d.toLocaleDateString("es-ES", { month: "long", year: "numeric" });
      monthCounts[mk] = (monthCounts[mk] || 0) + 1;
    }
  });

  let lastMonth = "";
  const weeks = [];
  let w = new Date(endWeek);
  while (w >= startWeek) {
    weeks.push(new Date(w));
    w.setDate(w.getDate() - 7);
  }

  for (const wk of weeks) {
    const fin = new Date(wk);
    fin.setDate(fin.getDate() + 6);
    const monthKey = wk.toLocaleDateString("es-ES", { month: "long", year: "numeric" });
    if (monthKey !== lastMonth) {
      if (lastMonth) select.innerHTML += "</optgroup>";
      select.innerHTML += `<optgroup label="── ${monthKey} (${monthCounts[monthKey] || 0} ítems) ──">`;
      lastMonth = monthKey;
    }
    const label = `Semana ${wk.toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit" })}`;
    select.innerHTML += `<option value="${wk.toISOString()}|${fin.toISOString()}">${label}</option>`;
  }
  if (lastMonth) select.innerHTML += "</optgroup>";
  return select;
}

function renderNewsWeekFilters(items) {
  const container = document.getElementById("news-week-filters");
  if (!container) return;
  container.innerHTML = "";

  const chipRecent = document.createElement("div");
  chipRecent.className = "chip active";
  chipRecent.textContent = "🔄 Últimas 2 Semanas";
  chipRecent.dataset.inicio = "all_recent";
  chipRecent.onclick = () => filtrarSemanaNoticias(chipRecent);
  container.appendChild(chipRecent);

  const select = generarSelectSemanas(items, "noticias");
  select.onchange = () => filtrarSemanaNoticiasDesdeSelector(select);
  container.appendChild(select);
}

function renderVideoWeekFilters(items) {
  const container = document.getElementById("video-week-filters");
  if (!container) return;
  container.innerHTML = "";

  const chipRecent = document.createElement("div");
  chipRecent.className = "chip active";
  chipRecent.textContent = "🔄 Últimas 2 Semanas";
  chipRecent.dataset.inicio = "all_recent";
  chipRecent.onclick = () => filtrarSemanaVideos(chipRecent);
  container.appendChild(chipRecent);

  const select = generarSelectSemanas(items, "videos");
  select.onchange = () => filtrarSemanaVideosDesdeSelector(select);
  container.appendChild(select);
}

function renderNewsChannelChips(items) {
  const channels = getNewsChannels(items);
  const container = document.getElementById("news-channel-filters");
  const allChip = document.createElement("div");
  allChip.className = "chip active";
  allChip.innerHTML = "<span>Todos</span>";
  allChip.dataset.filtro = "all";
  allChip.onclick = () => { selCanalNoticias = "all"; aplicarFiltrosNoticias(); actualizarChips(container, allChip); };
  container.appendChild(allChip);

  channels.forEach((ch) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.filtro = ch;
    chip.innerHTML = chipWithImage(ch, ch, items);
    chip.onclick = () => { selCanalNoticias = ch; aplicarFiltrosNoticias(); actualizarChips(container, chip); };
    container.appendChild(chip);
  });
}

function renderVideoChannelChips(items) {
  const channels = getVideoChannels(items);
  const container = document.getElementById("video-channel-filters");
  const allChip = document.createElement("div");
  allChip.className = "chip active";
  allChip.innerHTML = "<span>Todos</span>";
  allChip.dataset.filtro = "all";
  allChip.onclick = () => { selCanalVideos = "all"; aplicarFiltrosVideos(); actualizarChips(container, allChip); };
  container.appendChild(allChip);

  channels.forEach((ch) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.filtro = ch;
    chip.innerHTML = chipWithImage(ch, ch, items);
    chip.onclick = () => { selCanalVideos = ch; aplicarFiltrosVideos(); actualizarChips(container, chip); };
    container.appendChild(chip);
  });
}

function actualizarChips(container, activo) {
  container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  activo.classList.add("active");
}

function renderItems(items) {
  renderNews(items);
  renderVideos(items);
}

function renderNews(items) {
  const ul = document.getElementById("news-list");
  ul.innerHTML = items
    .filter((i) => !i.id_video)
    .map((i) => {
      const ts = i.ts || new Date().toISOString();
      const fuente = (i.fuente || "").replace(" Shorts", "");
      const fecha = i.fecha_real || i.f || "S/D";
      const badgeCls = i.badge === "Beca" ? "badge-beca" : "badge-tech";
      const badgeVal = i.badge || "Tech";
      const cat = i.categoria || "";
      const origen = i.origen || "web";
      const rssBadge = origen === "rss" ? '<span class="badge badge-rss">📡 RSS</span>' : "";
      return `<li class="news-item" data-ts="${ts}" data-fuente="${fuente}" data-categoria="${cat}" data-badge="${badgeVal}" data-origen="${origen}">
        <div class="meta">${i.fuente} | ${fecha}</div>
        <span class="badge ${badgeCls}">${badgeVal}</span>
        ${rssBadge}
        ${cat ? `<span class="badge badge-cat">${cat}</span>` : ""}
        <a href="${i.enlace}" target="_blank">${i.titulo || 'Ver noticia'}</a></li>`;
    })
    .join("");
}

function renderVideos(items) {
  const grid = document.getElementById("video-grid");
  const videos = items.filter((i) => i.id_video);

  if (videos.length === 0) {
    grid.innerHTML = '<p style="padding: 20px; color: #666; text-align:center;">No hay vídeos en este período.</p>';
    return;
  }

  grid.innerHTML = videos
    .map((i) => {
      const ts = i.ts || new Date().toISOString();
      const fuente = (i.fuente || "").replace(" Shorts", "");
      const fecha = i.fecha_real || i.f || "S/D";
      const tipo = i.tipo || "video";
      const esLive = tipo === "live";
      const clase = esLive ? "tipo-live" : tipo === "shorts" ? "tipo-shorts" : "tipo-video";
      const badgeLive = esLive ? '<span class="badge-live">● EN DIRECTO</span>' : "";
      const titulo = i.titulo || 'Ver video en YouTube';
      const canal = i.fuente || "YouTube";
      return `<div class="card ${clase}" data-ts="${ts}" data-fuente="${fuente}">
        ${badgeLive}
        <!-- <button onclick="descargarVideo('${i.enlace}', this)" class="btn-download">📥</button> -->
        <a href="${i.enlace}" target="_blank" class="video-thumb-link">
          <div class="video-thumb">
            <img src="https://img.youtube.com/vi/${i.id_video}/mqdefault.jpg" alt="${titulo}"
                 width="320" height="180" loading="lazy" class="video-thumb-img"
                 onerror="this.classList.add('errored');this.nextElementSibling.classList.add('visible')">
            <div class="video-thumb-fallback">📺 ${canal}</div>
          </div>
        </a>
        <div class="card-content">
          <div class="meta">${i.fuente} | ${fecha}</div>
          <a href="${i.enlace}" target="_blank">${titulo}</a>
        </div>
      </div>`;
    })
    .join("");
}

function itemDentroSemana(itemTS, selector) {
  const ahora = new Date().getTime();
  const limiteReciente = ahora - 14 * 24 * 60 * 60 * 1000;
  if (selector.tipo === "all_recent") {
    return itemTS >= limiteReciente;
  } else if (selector.tipo === "range") {
    return itemTS >= selector.ini && itemTS <= selector.fin;
  }
  return false;
}

function domainFromUrl(url) {
  try { return new URL(url).hostname; } catch(e) { return ""; }
}

function faviconForSource(sourceName, items) {
  const av = avatars[sourceName];
  if (av) return av;
  const item = items.find(i => (i.fuente || "").replace(" Shorts", "") === sourceName && i.enlace);
  if (item) return `https://www.google.com/s2/favicons?domain=${domainFromUrl(item.enlace)}&sz=32`;
  return "";
}

function chipWithImage(label, sourceName, items) {
  const imgSrc = faviconForSource(sourceName, items);
  if (imgSrc) {
    return `<img class="chip-img" src="${imgSrc}" onerror="this.style.display='none'" loading="lazy"><span class="chip-text">${label}</span>`;
  }
  return `<span class="chip-text">${label}</span>`;
}

function getNoticiasCategorias(items) {
  const cats = new Set();
  items.forEach((i) => { if (!i.id_video && i.categoria) cats.add(i.categoria); });
  return Array.from(cats);
}

function renderNewsCategoryChips(items) {
  const cats = getNoticiasCategorias(items);
  const container = document.getElementById("news-category-filters");
  if (!container) return;
  const allChip = document.createElement("div");
  allChip.className = "chip active";
  allChip.innerHTML = "<span>Todas</span>";
  allChip.dataset.filtro = "all";
  allChip.onclick = () => { selCategoriaNoticias = "all"; aplicarFiltrosNoticias(); actualizarChips(container, allChip); };
  container.appendChild(allChip);
  cats.forEach((cat) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.filtro = cat;
    chip.innerHTML = `<span class="chip-text">${cat}</span>`;
    chip.onclick = () => { selCategoriaNoticias = cat; aplicarFiltrosNoticias(); actualizarChips(container, chip); };
    container.appendChild(chip);
  });
}

function renderNewsBadgeChips(items) {
  const container = document.getElementById("news-badge-filters");
  if (!container) return;
  const allChip = document.createElement("div");
  allChip.className = "chip active";
  allChip.innerHTML = "<span>Todas</span>";
  allChip.dataset.filtro = "all";
  allChip.onclick = () => { selBadgeNoticias = "all"; aplicarFiltrosNoticias(); actualizarChips(container, allChip); };
  container.appendChild(allChip);
  ["Tech", "Beca", "RSS"].forEach((b) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.filtro = b;
    chip.innerHTML = `<span class="chip-text">${{"Tech": "💻 Tech", "Beca": "🎓 Beca", "RSS": "📡 RSS"}[b] || b}</span>`;
    chip.onclick = () => { selBadgeNoticias = b; aplicarFiltrosNoticias(); actualizarChips(container, chip); };
    container.appendChild(chip);
  });
}

function getRssSources(items) {
  return [...new Set(items.filter(i => i.origen === "rss").map(i => i.fuente))].sort();
}

function renderNewsRssChips(items) {
  const container = document.getElementById("news-rss-filters");
  if (!container) return;
  const rssSources = getRssSources(items);
  const allChip = document.createElement("div");
  allChip.className = "chip active";
  allChip.innerHTML = "<span>Todos</span>";
  allChip.dataset.filtro = "all";
  allChip.onclick = () => { selRssNoticias = "all"; aplicarFiltrosNoticias(); actualizarChips(container, allChip); };
  container.appendChild(allChip);
  rssSources.forEach((src) => {
    const chip = document.createElement("div");
    chip.className = "chip";
    chip.dataset.filtro = src;
    chip.innerHTML = chipWithImage(src, src, items);
    chip.onclick = () => { selRssNoticias = src; aplicarFiltrosNoticias(); actualizarChips(container, chip); };
    container.appendChild(chip);
  });
}

function aplicarFiltrosNoticias() {
  document.querySelectorAll(".news-item").forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return;
    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");
    const itemCat = item.getAttribute("data-categoria");
    const itemBadge = item.getAttribute("data-badge");
    const itemOrigen = item.getAttribute("data-origen") || "web";
    const okSemana = itemDentroSemana(itemTS, selSemanaNoticias);
    const okCanal = selCanalNoticias === "all" || itemFuente === selCanalNoticias;
    const okCategoria = selCategoriaNoticias === "all" || itemCat === selCategoriaNoticias;
    const okBadge = selBadgeNoticias === "all"
      || (selBadgeNoticias === "RSS" ? itemOrigen === "rss" : itemBadge === selBadgeNoticias);
    const okRss = selRssNoticias === "all"
      || (itemOrigen === "rss" && itemFuente === selRssNoticias);
    item.style.display = okSemana && okCanal && okCategoria && okBadge && okRss ? "list-item" : "none";
  });
}

function aplicarFiltrosVideos() {
  document.querySelectorAll(".card").forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return;
    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");
    const okSemana = itemDentroSemana(itemTS, selSemanaVideos);
    const okCanal = selCanalVideos === "all" || itemFuente === selCanalVideos;
    item.style.display = okSemana && okCanal ? "block" : "none";
  });
}

function filtrarSemanaNoticias(el) {
  const container = document.getElementById("news-week-filters");
  container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  const sel = document.getElementById("selectorSemanas_noticias");
  if (sel) sel.value = "all";
  el.classList.add("active");
  selSemanaNoticias.tipo = "all_recent";
  aplicarFiltrosNoticias();
}

function filtrarSemanaNoticiasDesdeSelector(el) {
  const container = document.getElementById("news-week-filters");
  if (el.value === "all") {
    selSemanaNoticias.tipo = "all_recent";
    const recent = container.querySelector('[data-inicio="all_recent"]');
    if (recent) recent.classList.add("active");
  } else {
    container.querySelectorAll('[data-inicio="all_recent"]').forEach((c) => c.classList.remove("active"));
    const [ini, fin] = el.value.split("|");
    selSemanaNoticias = { tipo: "range", ini: new Date(ini).getTime(), fin: new Date(fin).getTime() };
  }
  aplicarFiltrosNoticias();
}

function filtrarSemanaVideos(el) {
  const container = document.getElementById("video-week-filters");
  container.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  const sel = document.getElementById("selectorSemanas_videos");
  if (sel) sel.value = "all";
  el.classList.add("active");
  selSemanaVideos.tipo = "all_recent";
  aplicarFiltrosVideos();
}

function filtrarSemanaVideosDesdeSelector(el) {
  const container = document.getElementById("video-week-filters");
  if (el.value === "all") {
    selSemanaVideos.tipo = "all_recent";
    const recent = container.querySelector('[data-inicio="all_recent"]');
    if (recent) recent.classList.add("active");
  } else {
    container.querySelectorAll('[data-inicio="all_recent"]').forEach((c) => c.classList.remove("active"));
    const [ini, fin] = el.value.split("|");
    selSemanaVideos = { tipo: "range", ini: new Date(ini).getTime(), fin: new Date(fin).getTime() };
  }
  aplicarFiltrosVideos();
}

function initScrollToTop() {
  const btn = document.createElement("button");
  btn.className = "scroll-top";
  btn.innerHTML = "&#8593;";
  btn.setAttribute("aria-label", "Volver arriba");
  document.body.appendChild(btn);

  window.addEventListener("scroll", () => {
    btn.classList.toggle("visible", window.scrollY > 400);
  }, { passive: true });

  btn.addEventListener("click", () => {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
}

function renderGithubRanking(items) {
  const container = document.getElementById("github-ranking");
  if (!container) return;
  if (!items || items.length === 0) {
    container.innerHTML = '<p style="padding: 20px; color: #666; text-align:center;">No hay datos de repositorios.</p>';
    return;
  }
  container.innerHTML = items.map((r, i) => {
    const lang = r.lenguaje || "";
    const langBadge = lang ? `<span class="badge badge-tech">${lang}</span>` : "";
    const stars = Number(r.estrellas) || 0;
    const starsFormatted = stars >= 1000 ? (stars / 1000).toFixed(1) + "k" : stars;
    const desc = r.descripcion ? r.descripcion.slice(0, 120) : "";
    return `<div class="news-item" style="border-left-color: #f59e0b;">
      <div class="meta">
        <span>#${i + 1} ⭐ ${starsFormatted}</span>
        ${langBadge}
      </div>
      <a href="${r.enlace}" target="_blank">${r.titulo}</a>
      ${desc ? `<div style="font-size: 0.85em; color: #64748b; margin-top: 4px;">${desc}</div>` : ""}
    </div>`;
  }).join("");
}

function initGithubFilter() {
  const input = document.getElementById("github-filter");
  if (!input) return;
  let timer;
  input.addEventListener("input", () => {
    clearTimeout(timer);
    timer = setTimeout(() => {
      const q = input.value.toLowerCase().trim();
      const filtered = q ? herramientas.filter(r =>
        (r.titulo || "").toLowerCase().includes(q) ||
        (r.lenguaje || "").toLowerCase().includes(q) ||
        (r.descripcion || "").toLowerCase().includes(q)
      ) : herramientas;
      renderGithubRanking(filtered);
    }, 300);
  });
}

// function descargarVideo — desactivada: API no funcional
// async function descargarVideo(urlVideo, boton) {
//   const originalText = boton.innerHTML;
//   boton.innerHTML = "⏳...";
//   try {
//     const response = await fetch(
//       `${API_BASE}?url=${encodeURIComponent(urlVideo)}`,
//       {
//         method: "GET",
//         headers: {
//           "X-API-Key": atob(TOKEN),
//           "Content-Type": "application/json",
//         },
//       }
//     );
//     const data = await response.json();
//     if (data.url) {
//       const a = document.createElement("a");
//       a.href = data.url;
//       a.download = data.title + ".mp4";
//       document.body.appendChild(a);
//       a.click();
//       document.body.removeChild(a);
//       boton.innerHTML = "✅";
//     } else {
//       alert("No se pudo obtener el link directo.");
//       boton.innerHTML = "❌";
//     }
//   } catch (error) {
//     console.error("Error:", error);
//     boton.innerHTML = "❌";
//   } finally {
//     setTimeout(() => (boton.innerHTML = originalText), 3000);
//   }
// }
