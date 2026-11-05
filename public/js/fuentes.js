/* ═══════════════════════════════════════════════════════════════
   Gestor de Fuentes — Tech Pulse
   Lee public/data/fuentes.json (snapshot), permite alta/baja con
   persistencia en localStorage y export del JSON resultante.
   ═══════════════════════════════════════════════════════════════ */
'use strict';

const LS_KEY = 'fuentes_web_v1';
const THEME_KEY = 'fuentes_theme';
const DATA_URL = 'data/fuentes.json';

let original = {};   // snapshot del servidor (para restaurar)
let state = {};      // estado de trabajo (lo que se ve/exporta)
let filterType = 'todas';
let filterProy = 'todas';
let query = '';

/* ── Tema ───────────────────────────────────────────────────── */
const themeBtn = document.getElementById('theme-toggle');

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    themeBtn.textContent = theme === 'dark' ? '☀️' : '🌙';
    try { localStorage.setItem(THEME_KEY, theme); } catch (_) {}
}

themeBtn.addEventListener('click', () => {
    const cur = document.documentElement.getAttribute('data-theme');
    applyTheme(cur === 'dark' ? 'light' : 'dark');
});

(function initTheme() {
    let saved = null;
    try { saved = localStorage.getItem(THEME_KEY); } catch (_) {}
    applyTheme(saved === 'light' ? 'light' : 'dark');
})();

/* ── Utilidades ─────────────────────────────────────────────── */
const $ = (id) => document.getElementById(id);

function clone(obj) { return JSON.parse(JSON.stringify(obj)); }

function toast(msg, kind = 'ok') {
    const el = $('toast');
    el.textContent = msg;
    el.className = 'toast ' + kind;
    el.hidden = false;
    // forzar reflow para reiniciar la transición
    void el.offsetWidth;
    el.classList.add('show');
    clearTimeout(toast._t);
    toast._t = setTimeout(() => {
        el.classList.remove('show');
        setTimeout(() => { el.hidden = true; }, 250);
    }, 2600);
}

function save() {
    try { localStorage.setItem(LS_KEY, JSON.stringify({ v: 1, fuentes: state })); }
    catch (_) { toast('No se pudo guardar en localStorage', 'err'); }
}

function loadSaved() {
    try {
        const raw = localStorage.getItem(LS_KEY);
        if (!raw) return null;
        const data = JSON.parse(raw);
        if (data && data.fuentes && typeof data.fuentes === 'object') return data.fuentes;
    } catch (_) {}
    return null;
}

function primaryUrl(info) {
    return info.url || info.rss || info.yt || '';
}

function isSafeUrl(u) {
    return /^https?:\/\//i.test(u);
}

function hasSubtipo(info, prefix) {
    return typeof info.subtipo === 'string' && info.subtipo.startsWith(prefix);
}

function matchesType(info, type) {
    switch (type) {
        case 'web': return !!info.url && !hasSubtipo(info, 'github');
        case 'yt': return !!info.yt;
        case 'rss': return !!info.rss;
        case 'github': return hasSubtipo(info, 'github') || info.subtipo === 'awesome';
        case 'herramienta': return info.tipo === 'herramienta';
        default: return true;
    }
}

/* ── Proyectos (etiqueta derivada de los campos de la fuente) ─ */
const PROYECTOS = {
    tech:         { label: '📰 Noticias tech',    cls: 'proy-tech',    aliases: 'noticias tech news' },
    herramientas: { label: '🛠 Herramientas/dev', cls: 'proy-herr',    aliases: 'herramientas tools dev github awesome producthunt' },
    cine:         { label: '🎬 Películas/series', cls: 'proy-cine',    aliases: 'cine peliculas pelicula series serie film estrenos television tv' },
    otros:        { label: '📚 Otros/recursos',   cls: 'proy-otros',   aliases: 'otros recursos resources blog' },
};

const CINE_RE = /(^|[^\w])(cines?|pel[ií]culas?|series?|netflix|trailers?|estrenos?|tvmaze|formulatv|sensacine|filmaffinity|filmin|imdb|tmdb)(?![\w])/i;

function proyectoDe(name, info) {
    if (info.proyecto && PROYECTOS[info.proyecto]) return info.proyecto;
    if (info.tipo === 'herramienta') return 'herramientas';
    if (info.tipo === 'recurso_blog') return 'otros';
    const hay = `${name} ${info.url || ''} ${info.rss || ''} ${info.yt || ''}`;
    if (CINE_RE.test(hay)) return 'cine';
    if (info.url || info.rss || info.yt) return 'tech';
    return 'otros';
}

function matchesProy(name, info, proy) {
    if (proy === 'todas') return true;
    return proyectoDe(name, info) === proy;
}

function matchesQuery(name, info) {
    if (!query) return true;
    const proy = PROYECTOS[proyectoDe(name, info)];
    const hay = (name + ' ' + Object.values(info).join(' ') + ' ' + proy.label + ' ' + proy.aliases).toLowerCase();
    return hay.includes(query);
}

/* ── Estadísticas ───────────────────────────────────────────── */
function renderStats() {
    const entries = Object.values(state);
    const count = (fn) => entries.filter(fn).length;
    const stats = [
        ['Total', entries.length],
        ['🌐 Web', count((i) => matchesType(i, 'web'))],
        ['▶️ YouTube', count((i) => matchesType(i, 'yt'))],
        ['📡 RSS', count((i) => matchesType(i, 'rss'))],
        ['🐙 GitHub', count((i) => matchesType(i, 'github'))],
        ['🛠 Herramientas', count((i) => matchesType(i, 'herramienta'))],
    ];
    $('stats').innerHTML = stats
        .map(([label, n]) => `<div class="stat"><b>${n}</b><span>${label}</span></div>`)
        .join('');
}

/* ── Contadores de la leyenda (div explicativo) ─────────────── */
function renderLeyenda() {
    const counts = { tech: 0, herramientas: 0, cine: 0, otros: 0 };
    for (const name of Object.keys(state)) {
        counts[proyectoDe(name, state[name])]++;
    }
    for (const key of Object.keys(counts)) {
        const el = document.getElementById('cnt-' + key);
        if (el) el.textContent = counts[key];
    }
}

/* ── Badges ─────────────────────────────────────────────────── */
function badgesFor(info) {
    const out = [];
    if (info.url && !hasSubtipo(info, 'github')) out.push('<span class="badge badge-web">🌐 web</span>');
    if (info.yt) out.push('<span class="badge badge-yt">▶️ yt</span>');
    if (info.rss) out.push('<span class="badge badge-rss">📡 rss</span>');
    if (hasSubtipo(info, 'github') || info.subtipo === 'awesome') out.push('<span class="badge badge-gh">🐙 github</span>');
    if (info.tipo === 'herramienta') out.push('<span class="badge badge-tool">🛠 herramienta</span>');
    if (info.tipo === 'noticia') out.push('<span class="badge badge-news">📰 noticia</span>');
    if (info.quick) out.push('<span class="badge badge-quick">⚡ quick</span>');
    if (info.subtipo && info.subtipo !== 'awesome' && !hasSubtipo(info, 'github')) {
        out.push(`<span class="badge badge-sub">${escapeHtml(info.subtipo)}</span>`);
    }
    return out.join('');
}

function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
}

/* ── Tabla ──────────────────────────────────────────────────── */
function renderTable() {
    const tbody = $('tbody');
    const names = Object.keys(state).filter((n) =>
        matchesType(state[n], filterType) &&
        matchesProy(n, state[n], filterProy) &&
        matchesQuery(n, state[n]));

    tbody.innerHTML = '';
    $('search-count').textContent = names.length === Object.keys(state).length
        ? `${names.length}`
        : `${names.length} / ${Object.keys(state).length}`;

    const emptyBox = $('empty');
    if (names.length === 0) {
        emptyBox.hidden = false;
        emptyBox.querySelector('p').textContent = Object.keys(state).length === 0
            ? 'No hay fuentes. Añade la primera con «➕ Añadir fuente».'
            : 'No hay fuentes que coincidan con la búsqueda.';
        return;
    }
    emptyBox.hidden = true;

    const frag = document.createDocumentFragment();
    for (const name of names) {
        const info = state[name];
        const url = primaryUrl(info);

        const tr = document.createElement('tr');

        const tdName = document.createElement('td');
        tdName.className = 'f-name';
        tdName.textContent = name;
        tr.appendChild(tdName);

        const proy = PROYECTOS[proyectoDe(name, info)];
        const tdProy = document.createElement('td');
        tdProy.className = 'f-proy';
        tdProy.innerHTML = `<span class="badge proy ${proy.cls}">${escapeHtml(proy.label)}</span>`;
        tr.appendChild(tdProy);

        const tdBadges = document.createElement('td');
        tdBadges.className = 'badges';
        tdBadges.innerHTML = badgesFor(info);
        tr.appendChild(tdBadges);

        const tdUrl = document.createElement('td');
        if (url && isSafeUrl(url)) {
            const a = document.createElement('a');
            a.className = 'f-url';
            a.href = url;
            a.target = '_blank';
            a.rel = 'noopener noreferrer';
            a.title = url;
            a.textContent = url;
            tdUrl.appendChild(a);
        } else {
            tdUrl.innerHTML = '<span class="f-url">—</span>';
        }
        tr.appendChild(tdUrl);

        const tdActions = document.createElement('td');
        tdActions.className = 'col-actions';
        const wrap = document.createElement('div');
        wrap.className = 'row-actions';
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'btn-del';
        btn.textContent = '🗑 Eliminar';
        btn.setAttribute('aria-label', `Eliminar ${name}`);
        attachDelete(btn, name);
        wrap.appendChild(btn);
        tdActions.appendChild(wrap);
        tr.appendChild(tdActions);

        frag.appendChild(tr);
    }
    tbody.appendChild(frag);
}

function attachDelete(btn, name) {
    let armed = false;
    let timer = null;
    const reset = () => {
        armed = false;
        btn.classList.remove('confirming');
        btn.textContent = '🗑 Eliminar';
        clearTimeout(timer);
    };
    btn.addEventListener('click', () => {
        if (!armed) {
            armed = true;
            btn.classList.add('confirming');
            btn.textContent = '¿Seguro?';
            timer = setTimeout(reset, 3000);
            return;
        }
        delete state[name];
        reset();
        save();
        render();
        toast(`Fuente «${name}» eliminada`, 'ok');
    });
}

function render() {
    renderStats();
    renderLeyenda();
    renderTable();
}

/* ── Filtros ────────────────────────────────────────────────── */
document.querySelectorAll('#type-filters .chip').forEach((chip) => {
    chip.addEventListener('click', () => {
        document.querySelectorAll('#type-filters .chip').forEach((c) => {
            c.classList.remove('active');
            c.setAttribute('aria-selected', 'false');
        });
        chip.classList.add('active');
        chip.setAttribute('aria-selected', 'true');
        filterType = chip.dataset.type;
        renderTable();
    });
});

document.querySelectorAll('#proy-filters .chip').forEach((chip) => {
    chip.addEventListener('click', () => {
        document.querySelectorAll('#proy-filters .chip').forEach((c) => {
            c.classList.remove('active');
            c.setAttribute('aria-selected', 'false');
        });
        chip.classList.add('active');
        chip.setAttribute('aria-selected', 'true');
        filterProy = chip.dataset.proy;
        renderTable();
    });
});

$('search').addEventListener('input', (e) => {
    query = e.target.value.trim().toLowerCase();
    renderTable();
});

/* ── Formulario de alta ─────────────────────────────────────── */
const form = $('add-form');
const fTipo = $('f-tipo');
const fieldUrlWeb = $('field-url-web');
const fieldUrlYt = $('field-url-yt');
const fieldSelector = $('field-selector');
const fUrl = $('f-url');
const fYt = $('f-yt');
const fSelector = $('f-selector');

function syncFormToType() {
    const t = fTipo.value;
    fieldUrlWeb.hidden = (t === 'yt');
    fieldUrlYt.hidden = (t !== 'yt' && t !== 'dual');
    fieldSelector.hidden = (t === 'yt' || t === 'rss' || t === 'github');

    if (t === 'yt') {
        fUrl.placeholder = 'https://www.youtube.com/@canal';
    } else if (t === 'rss') {
        fUrl.placeholder = 'https://ejemplo.com/feed.xml';
    } else {
        fUrl.placeholder = 'https://ejemplo.com/blog';
    }
    if (t === 'github') {
        fUrl.placeholder = 'https://github.com/topics/ia?o=desc&s=stars';
        fSelector.value = 'article a[href]';
    }
    fieldUrlWeb.querySelector('span').textContent =
        (t === 'rss' ? 'URL del feed *' : 'URL *');
    fUrl.required = (t !== 'yt');
    fYt.required = (t === 'yt');
}

fTipo.addEventListener('change', syncFormToType);
syncFormToType();

$('btn-add').addEventListener('click', () => {
    form.hidden = !form.hidden;
    if (!form.hidden) {
        $('f-nombre').focus();
        form.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
});

$('btn-cancel').addEventListener('click', () => {
    form.reset();
    form.hidden = true;
    syncFormToType();
});

form.addEventListener('submit', (e) => {
    e.preventDefault();

    const nombre = $('f-nombre').value.trim();
    const tipo = fTipo.value;
    const url = fUrl.value.trim();
    const yt = fYt.value.trim();
    const selector = fSelector.value.trim();

    if (!nombre) { toast('El nombre es obligatorio', 'err'); return; }
    if (state.hasOwnProperty(nombre)) { toast(`Ya existe una fuente llamada «${nombre}»`, 'err'); return; }

    const info = {};

    if (tipo === 'yt') {
        if (!isSafeUrl(yt)) { toast('La URL de YouTube no es válida', 'err'); return; }
        info.yt = yt;
    } else if (tipo === 'rss') {
        if (!isSafeUrl(url)) { toast('La URL del feed RSS no es válida', 'err'); return; }
        info.rss = url;
    } else if (tipo === 'dual') {
        if (!isSafeUrl(url) || !isSafeUrl(yt)) { toast('Las dos URLs deben ser válidas', 'err'); return; }
        info.url = url;
        info.yt = yt;
        if (selector) info.selector = selector;
    } else if (tipo === 'github') {
        if (!isSafeUrl(url)) { toast('La URL no es válida', 'err'); return; }
        info.url = url;
        info.selector = selector || 'article a[href]';
        info.tipo = 'herramienta';
        info.subtipo = 'github-topic';
    } else { // web
        if (!isSafeUrl(url)) { toast('La URL no es válida', 'err'); return; }
        info.url = url;
        if (selector) info.selector = selector;
    }

    // Opciones avanzadas (no aplican a github, que fuerza su propio tipo)
    if (tipo !== 'github') {
        const cat = $('f-categoria').value;
        if (cat) info.tipo = cat;
        const rss = $('f-rss').value.trim();
        if (rss && isSafeUrl(rss)) info.rss = rss;
        const org = $('f-org').value.trim();
        if (org) info.org = org;
        if ($('f-quick').checked) info.quick = true;
        if ($('f-solotech').checked) info.solo_tech = true;
    }

    state[nombre] = info;
    save();
    render();
    form.reset();
    form.hidden = true;
    syncFormToType();
    toast(`Fuente «${nombre}» añadida (${Object.keys(state).length} en total)`, 'ok');
});

/* ── Exportar / Restaurar ───────────────────────────────────── */
$('btn-export').addEventListener('click', () => {
    const blob = new Blob([JSON.stringify(state, null, 2) + '\n'], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = 'fuentes.json';
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 4000);
    toast(`fuentes.json descargado (${Object.keys(state).length} fuentes)`, 'ok');
});

$('btn-restore').addEventListener('click', () => {
    if (!window.confirm('¿Descartar los cambios locales y volver al snapshot original?')) return;
    try { localStorage.removeItem(LS_KEY); } catch (_) {}
    state = clone(original);
    render();
    toast('Snapshot original restaurado', 'ok');
});

/* ── Init ───────────────────────────────────────────────────── */
(async function init() {
    try {
        const resp = await fetch(DATA_URL, { cache: 'no-cache' });
        if (!resp.ok) throw new Error('HTTP ' + resp.status);
        original = await resp.json();
    } catch (err) {
        $('loading').innerHTML = '<span aria-hidden="true">⚠️</span><p>No se pudo cargar data/fuentes.json (' +
            escapeHtml(err.message) + '). ¿Estás abriendo la página en local? Sirve la carpeta con un servidor HTTP.</p>';
        return;
    }

    const saved = loadSaved();
    state = saved || clone(original);

    $('loading').hidden = true;
    render();

    if (saved) {
        const n = Object.keys(state).length - Object.keys(original).length;
        const extra = n > 0 ? ` (+${n} locales)` : n < 0 ? ` (${n} locales)` : '';
        toast(`Cambios locales cargados: ${Object.keys(state).length} fuentes${extra}`, 'ok');
    }
})();
