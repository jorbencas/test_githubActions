let selSemana = { tipo: "all_recent", ini: null, fin: null };
let selCanalNoticias = "all";
let selCanalVideos = "all";
let allItems = [];
let avatars = {};

document.addEventListener("DOMContentLoaded", async () => {
  try {
    const resp = await fetch(DATA_URL);
    const data = await resp.json();
    allItems = data.items || [];
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
  renderWeekFilters(allItems);
  renderNewsChannelChips(allItems);
  renderVideoChannelChips(allItems);
  renderItems(allItems);
  aplicarFiltrosNoticias();
  aplicarFiltrosVideos();
  initScrollToTop();
}

function getNewsChannels(items) {
  const seen = new Set();
  items.forEach((item) => {
    if (item.id_video) return;
    const ch = (item.fuente || "").replace(" Shorts", "");
    if (!seen.has(ch)) {
      seen.add(ch);
    }
  });
  return Array.from(seen);
}

function getVideoChannels(items) {
  const seen = new Set();
  items.forEach((item) => {
    if (!item.id_video) return;
    const ch = (item.fuente || "").replace(" Shorts", "");
    if (!seen.has(ch)) {
      seen.add(ch);
    }
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

function renderWeekFilters(items) {
  const container = document.getElementById("week-filters");
  const now = new Date();
  const chipRecent = document.createElement("div");
  chipRecent.className = "chip active";
  chipRecent.textContent = "🔄 Últimas 2 Semanas";
  chipRecent.dataset.inicio = "all_recent";
  chipRecent.onclick = () => filtrarSemana(chipRecent);
  container.appendChild(chipRecent);

  const select = document.createElement("select");
  select.id = "selectorSemanas";
  select.style.cssText =
    "padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);";
  select.innerHTML = '<option value="all">📅 Archivo Histórico...</option>';
  select.onchange = () => filtrarDesdeSelector(select);

  const tsValues = items.map((i) => new Date(i.ts).getTime()).filter((t) => !isNaN(t));
  if (tsValues.length === 0) return;
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
    const avatarUrl = avatars[ch];
    if (avatarUrl) {
      chip.innerHTML = `<img class="chip-img" src="${avatarUrl}" onerror="this.style.display='none'"><span class="chip-text">${ch}</span>`;
    } else {
      chip.innerHTML = `<span class="chip-text">${ch}</span>`;
    }
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
    const avatarUrl = avatars[ch];
    if (avatarUrl) {
      chip.innerHTML = `<img class="chip-img" src="${avatarUrl}" onerror="this.style.display='none'"><span class="chip-text">${ch}</span>`;
    } else {
      chip.innerHTML = `<span class="chip-text">${ch}</span>`;
    }
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
      const badge = i.badge === "Beca" ? "badge-beca" : "badge-tech";
      return `<li class="news-item" data-ts="${ts}" data-fuente="${fuente}">
        <div class="meta">${i.fuente} | ${fecha}</div>
        <span class="badge ${badge}">${i.badge || "Tech"}</span>
        <a href="${i.enlace}" target="_blank">${i.titulo || 'Ver noticia'}</a></li>`;
    })
    .join("");
}

function renderVideos(items) {
  const grid = document.getElementById("video-grid");
  const videos = items.filter((i) => i.id_video);
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
      return `<div class="card ${clase}" data-ts="${ts}" data-fuente="${fuente}" style="aspect-ratio: 16/9; contain: layout style;">
        ${badgeLive}
        <button onclick="descargarVideo('${i.enlace}', this)" class="btn-download">📥</button>
        <a href="${i.enlace}" target="_blank">
          <img src="https://img.youtube.com/vi/${i.id_video}/mqdefault.jpg" alt="${titulo}"
               width="320" height="180" loading="lazy"
               style="width:100%; height:auto; aspect-ratio: 16/9; background: #eee;">
        </a>
        <div class="card-content">
          <div class="meta">${i.fuente} | ${fecha}</div>
          <a href="${i.enlace}" target="_blank">${titulo}</a>
        </div>
      </div>`;
    })
    .join("");
}

function filtrarSemana(el) {
  el.parentElement.querySelectorAll(".chip").forEach((c) => c.classList.remove("active"));
  const sel = document.getElementById("selectorSemanas");
  if (sel) sel.value = "all";
  el.classList.add("active");
  selSemana.tipo = el.dataset.inicio === "all_recent" ? "all_recent" : "range";
  aplicarFiltrosNoticias();
  aplicarFiltrosVideos();
}

function filtrarDesdeSelector(el) {
  if (el.value === "all") {
    selSemana.tipo = "all_recent";
    const recent = document.querySelector('[data-inicio="all_recent"]');
    if (recent) recent.classList.add("active");
  } else {
    document.querySelectorAll('[data-inicio="all_recent"]').forEach((c) => c.classList.remove("active"));
    const [ini, fin] = el.value.split("|");
    selSemana = { tipo: "range", ini: new Date(ini).getTime(), fin: new Date(fin).getTime() };
  }
  aplicarFiltrosNoticias();
  aplicarFiltrosVideos();
}

function itemDentroSemana(itemTS) {
  const ahora = new Date().getTime();
  const limiteReciente = ahora - 14 * 24 * 60 * 60 * 1000;
  if (selSemana.tipo === "all_recent") {
    return itemTS >= limiteReciente;
  } else if (selSemana.tipo === "range") {
    return itemTS >= selSemana.ini && itemTS <= selSemana.fin;
  }
  return false;
}

function aplicarFiltrosNoticias() {
  document.querySelectorAll(".news-item").forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return;
    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");
    const okSemana = itemDentroSemana(itemTS);
    const okCanal = selCanalNoticias === "all" || itemFuente === selCanalNoticias;
    item.style.display = okSemana && okCanal ? "list-item" : "none";
  });
}

function aplicarFiltrosVideos() {
  document.querySelectorAll(".card").forEach((item) => {
    const tsAttr = item.getAttribute("data-ts");
    if (!tsAttr) return;
    const itemTS = new Date(tsAttr).getTime();
    const itemFuente = item.getAttribute("data-fuente");
    const okSemana = itemDentroSemana(itemTS);
    const okCanal = selCanalVideos === "all" || itemFuente === selCanalVideos;
    item.style.display = okSemana && okCanal ? "block" : "none";
  });
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

async function descargarVideo(urlVideo, boton) {
  const originalText = boton.innerHTML;
  boton.innerHTML = "⏳...";
  try {
    const response = await fetch(
      `${API_BASE}?url=${encodeURIComponent(urlVideo)}`,
      {
        method: "GET",
        headers: {
          "X-API-Key": atob(TOKEN),
          "Content-Type": "application/json",
        },
      }
    );
    const data = await response.json();
    if (data.url) {
      const a = document.createElement("a");
      a.href = data.url;
      a.download = data.title + ".mp4";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      boton.innerHTML = "✅";
    } else {
      alert("No se pudo obtener el link directo.");
      boton.innerHTML = "❌";
    }
  } catch (error) {
    console.error("Error:", error);
    boton.innerHTML = "❌";
  } finally {
    setTimeout(() => (boton.innerHTML = originalText), 3000);
  }
}
