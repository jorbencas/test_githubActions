#!/usr/bin/env python3
"""
generate_weekly.py — Genera el weekly recap + dashboard HTML + PR al blog.
Toma los datos de noticias_historico.json y produce los entregables.

Uso:
    python generate_weekly.py                           # Modo normal
    python generate_weekly.py --no-pr                   # Genera sin crear PR
    python generate_weekly.py --blog-path ../blog        # Ruta al checkout del blog
"""
import argparse
import asyncio
import inspect
import json
import logging
import os
import re
import shutil
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from google import genai

from scripts.utils.constants_downloadfile import CONFIG, HTML_TEMPLATE, MD_TEMPLATE, SKILLS, LLMS, LENGUAJES, FRAMEWORKS, LIBRERIAS, CATEGORIAS, JS_CONFIG, FALLBACK_GITHUB_IMAGE, FALLBACK_SNEAK_PEEK, FALLBACK_NOTA_PERSONAL, SUBTIPO_KEY, TIPO_KEY, ORIGEN_KEY, SUB_VAL_GITHUB, TIPO_VAL_NOTICIA, VAL_RSS, ENLACE_KEY, FUENTE_KEY, TS_KEY, FECHA_PUB_KEY, CATEGORIA_KEY, ESTRELLAS_KEY, TITULO_KEY, FECHA_REAL_KEY, ID_VIDEO_KEY, LENGUAJE_KEY, DESCRIPCION_KEY, SUB_VAL_GITHUB_TOPIC, SUB_VAL_GITHUB_COLLECTION, SUB_VAL_PRODUCTHUNT, TIPO_VAL_HERRAMIENTA, TIPO_VAL_VIDEO, TIPO_VAL_SHORTS, TIPO_VAL_LIVE, FUENTES, YT_KEY

# Acceder a valores anidados dentro de JS_CONFIG
ALL_YT_CHANNELS = JS_CONFIG.get("ALL_YT_CHANNELS", [])
TABS_MULTIMEDIA = JS_CONFIG.get("TABS_MULTIMEDIA", [])
EMOJIS_CATEGORIA_MAP = {v: JS_CONFIG.get("EMOJIS_CATEGORIA", "⚡🤖💻🐳🔒📊🎓💡")[i] for i, v in enumerate(["Hardware", "IA", "Programacion", "DevOps", "Ciberseguridad", "Negocios", "General", "Otro"]) if i < len(JS_CONFIG.get("EMOJIS_CATEGORIA", "⚡🤖💻🐳🔒📊🎓💡"))}
from scripts.scrapers.scraper_base import ScraperPro
from scripts.utils.common import load_json, generar_imagen_noticia, obtener_recap_semanal_ia, deduplicar_items

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/weekly.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("weekly")



def cargar_herramientas() -> list:
    path = os.path.join(CONFIG["FOLDER"], "herramientas.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def archivar_recaps_antiguos(auto_news_dir: str, semana_actual: str) -> int:
    """Mueve recaps antiguos (>2 semanas) a subcarpeta /archive/. Devuelve cantidad movidos."""
    archive_dir = os.path.join(auto_news_dir, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    moved = 0
    if not os.path.isdir(auto_news_dir):
        return 0
    for fname in os.listdir(auto_news_dir):
        if not fname.endswith(".md"):
            continue
        match = re.match(r"(\d{4})-w(\d{2})-tech-recap\.md", fname)
        if not match:
            continue
        file_week = f"{match.group(1)}-W{match.group(2)}"
        if file_week < semana_actual:
            src = os.path.join(auto_news_dir, fname)
            dst = os.path.join(archive_dir, fname)
            try:
                shutil.move(src, dst)
                moved += 1
                logger.info(f"📦 Archivado: {fname} → archive/")
            except Exception as e:
                logger.warning(f"⚠️ No se pudo archivar {fname}: {e}")
    return moved


def eliminar_duplicados_semana(auto_news_dir: str, semana_slug: str) -> bool:
    """Elimina posts duplicados de la misma semana. Devuelve True si ya existe uno."""
    if not os.path.isdir(auto_news_dir):
        return False
    count = 0
    for fname in os.listdir(auto_news_dir):
        if fname.endswith(".md") and semana_slug in fname:
            count += 1
    return count > 0



# ==============================================================================
# FUNCIONES DE RENDERIZADO HTML (SSR)
# ==============================================================================

def _escape_html(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def _favicon_src(source_name: str, avatars: dict) -> str:
    nombre_c = source_name.replace(" Shorts", "")
    if nombre_c in avatars:
        return avatars[nombre_c]
    try:
        from urllib.parse import urlparse
        domain = urlparse(FUENTES.get(nombre_c, {}).get("url", "")).netloc
        if domain:
            return f"https://www.google.com/s2/favicons?domain={domain}&sz=32"
    except Exception:
        pass
    return f"https://ui-avatars.com/api/?name={nombre_c}&background=random"


def _item_timestamp(item: dict) -> str:
    ts = item.get(TS_KEY) or item.get(FECHA_REAL_KEY) or ""
    return str(ts)


def render_stats(items: list) -> str:
    total = len(items)
    tech_count = sum(1 for i in items if i.get("badge") == "Tech")
    multimedia_count = sum(1 for i in items if i.get(ID_VIDEO_KEY))
    return (
        f'<span class="stat"><strong>{total}</strong> Total</span>'
        f'<span class="stat"><strong>{tech_count}</strong> Tech</span>'
        f'<span class="stat"><strong>{multimedia_count}</strong> Multimedia</span>'
    )


def render_news_item(item: dict, avatars: dict) -> str:
    titulo = _escape_html(item.get(TITULO_KEY, "Sin título"))
    enlace = item.get(ENLACE_KEY, "#")
    fuente = _escape_html(item.get(FUENTE_KEY, ""))
    fecha = item.get(FECHA_PUB_KEY, "")
    badge = item.get("badge", "")
    origen = item.get(ORIGEN_KEY, "")
    ts = _item_timestamp(item)
    categoria = item.get(CATEGORIA_KEY, "")
    favicon = _favicon_src(fuente, avatars)

    badge_html = ""
    if badge == "Tech":
        badge_html = '<span class="badge-tech">Tech</span>'
    if origen == VAL_RSS:
        badge_html += '<span class="badge-rss">RSS</span>'

    cat_emoji = ""
    if categoria:
        cat_emoji = EMOJIS_CATEGORIA_MAP.get(categoria.split()[0] if categoria else "", "")
        if not cat_emoji:
            cat_emoji = "💡"

    return (
        f'<li class="news-item" data-source="{_escape_html(fuente)}" data-category="{_escape_html(categoria)}" data-ts="{ts}">'
        f'<a href="{enlace}" target="_blank" rel="noopener">'
        f'<img class="favicon" src="{favicon}" alt="{fuente}" width="16" height="16" loading="lazy">'
        f'<div class="news-text">'
        f'<span class="news-title">{titulo}</span>'
        f'<span class="news-meta">{fuente} · {fecha} {badge_html}</span>'
        f'</div></a></li>'
    )


def render_news_list(items: list, avatars: dict) -> str:
    return "".join(render_news_item(i, avatars) for i in items)


def render_week_selector(items: list, prefix: str) -> str:
    weeks: dict[str, list] = {}
    for item in items:
        ts = _item_timestamp(item)
        if not ts:
            continue
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            iso_year, iso_week, _ = dt.isocalendar()
            key = f"{iso_year}-W{iso_week:02d}"
            weeks.setdefault(key, []).append(item)
        except Exception:
            continue

    if not weeks:
        return '<button class="chip active" data-week="all">Últimas 2 semanas</button>'

    sorted_weeks = sorted(weeks.keys(), reverse=True)
    html = '<button class="chip active" data-week="all">Últimas 2 semanas</button>'
    for week_key in sorted_weeks[:8]:
        count = len(weeks[week_key])
        html += f'<button class="chip" data-week="{week_key}">{week_key} ({count})</button>'
    return html


def render_channel_chips(items: list, state_key: str, avatars: dict) -> str:
    channels: dict[str, int] = {}
    for item in items:
        fuente = item.get(FUENTE_KEY, "")
        if fuente:
            channels[fuente] = channels.get(fuente, 0) + 1

    html = f'<button class="chip active" data-channel="all">Todos</button>'
    for ch, count in sorted(channels.items(), key=lambda x: -x[1])[:20]:
        favicon = _favicon_src(ch, avatars)
        html += (
            f'<button class="chip" data-channel="{_escape_html(ch)}">'
            f'<img src="{favicon}" class="chip-icon" alt="" width="14" height="14" loading="lazy">'
            f'{_escape_html(ch)} ({count})</button>'
        )
    return html


def render_category_chips(items: list) -> str:
    cats: dict[str, int] = {}
    for item in items:
        cat = item.get(CATEGORIA_KEY, "💡 General")
        cats[cat] = cats.get(cat, 0) + 1

    html = '<button class="chip active" data-category="all">Todas</button>'
    for cat, count in sorted(cats.items(), key=lambda x: -x[1])[:10]:
        emoji = EMOJIS_CATEGORIA_MAP.get(cat.split()[0] if cat else "", "💡")
        html += f'<button class="chip" data-category="{_escape_html(cat)}">{emoji} {_escape_html(cat)} ({count})</button>'
    return html


def render_multimedia_tabs() -> str:
    html = ""
    for tab in TABS_MULTIMEDIA:
        label = tab.get("label", "")
        key = tab.get("id", "")
        active = " active" if key == "youtube" else ""
        html += f'<button class="chip{active}" data-tab="{key}">{label}</button>'
    return html



def render_multimedia_content(items: list, avatars: dict) -> str:
    html = ""
    for item in items:
        if item.get(ID_VIDEO_KEY):
            html += render_youtube_card(item, avatars)
    return html


def render_youtube_card(item: dict, avatars: dict) -> str:
    titulo = _escape_html(item.get(TITULO_KEY, ""))
    enlace = item.get(ENLACE_KEY, "#")
    fuente = _escape_html(item.get(FUENTE_KEY, ""))
    id_video = item.get(ID_VIDEO_KEY, "")
    ts = _item_timestamp(item)
    fecha = item.get(FECHA_PUB_KEY, "")
    favicon = _favicon_src(fuente, avatars)

    thumbnail = f"https://img.youtube.com/vi/{id_video}/mqdefault.jpg" if id_video else ""
    is_live = item.get("is_live", False)
    live_badge = '<span class="badge-live">🔴 LIVE</span>' if is_live else ""

    return (
        f'<div class="video-card" data-source="{fuente}" data-ts="{ts}">'
        f'<a href="{enlace}" target="_blank" rel="noopener">'
        f'<img src="{thumbnail}" alt="{titulo}" class="video-thumb" loading="lazy" onerror="this.src=\'https://via.placeholder.com/320x180?text=No+Preview\'">'
        f'</a>'
        f'<div class="video-info">'
        f'<a href="{enlace}" target="_blank" rel="noopener" class="video-title">{titulo}</a>'
        f'<span class="video-meta"><img src="{favicon}" class="chip-icon" alt="" width="14" height="14" loading="lazy"> {fuente} · {fecha} {live_badge}</span>'
        f'</div></div>'
    )


def render_multimedia_content(items: list, avatars: dict) -> str:
    html = ""
    for item in items:
        if item.get(ID_VIDEO_KEY):
            html += render_youtube_card(item, avatars)
    return html


def render_github_ranking(herramientas: list) -> str:
    html = ""
    for i, h in enumerate(herramientas):
        nombre = _escape_html(h.get(TITULO_KEY, ""))
        enlace = h.get(ENLACE_KEY, "#")
        estrellas = h.get(ESTRELLAS_KEY, "0")
        lenguaje = _escape_html(h.get(LENGUAJE_KEY, ""))
        desc = _escape_html(h.get(DESCRIPCION_KEY, "")[:120])

        lang_badge = f'<span class="badge-lang">{lenguaje}</span>' if lenguaje else ""

        html += (
            f'<div class="github-item" data-lang="{lenguaje.lower()}">'
            f'<span class="rank">#{i+1}</span>'
            f'<div class="github-info">'
            f'<a href="{enlace}" target="_blank" rel="noopener" class="github-name">{nombre}</a>'
            f'<span class="github-desc">{desc}</span>'
            f'</div>'
            f'<div class="github-stars">⭐ {estrellas} {lang_badge}</div>'
            f'</div>'
        )
    return html



def generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia):
    historial.sort(key=lambda x: x.get(TS_KEY, ""), reverse=True)
    herramientas_github = [
        h for h in herramientas
        if h.get(SUBTIPO_KEY) == SUB_VAL_GITHUB and h.get(ESTRELLAS_KEY, "0").isdigit()
    ]
    herramientas_github.sort(key=lambda h: int(h.get(ESTRELLAS_KEY, "0")), reverse=True)
    top_github = herramientas_github[:20]

    # Completar avatares
    avatars_known = getattr(scr, "avatar_repo", None) and scr.avatar_repo.avatars or {}
    for nombre, info in FUENTES.items():
        if YT_KEY in info:
            nombre_c = nombre.replace(" Shorts", "")
            if nombre_c not in avatars_known:
                avatars_known[nombre_c] = f"https://ui-avatars.com/api/?name={nombre_c}&background=random"

    # === Renderizar todas las secciones ===
    stats_html = render_stats(historial)
    news_list_html = render_news_list(historial, avatars_known)
    news_week_filters_html = render_week_selector(historial, "news")
    news_channel_filters_html = render_channel_chips(historial, "canalNoticias", avatars_known)
    news_category_filters_html = render_category_chips(historial)
    video_week_filters_html = render_week_selector(historial, "video")
    multimedia_tabs_html = render_multimedia_tabs()
    video_channel_filters_html = render_channel_chips(historial, "canalVideos", avatars_known)
    multimedia_content_html = render_multimedia_content(historial, avatars_known)
    github_ranking_html = render_github_ranking(top_github)

    # === Escribir index.html con todo pre-renderizado ===
    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(
            HTML_TEMPLATE.format(
                fecha_hoy=fecha_h,
                resumen=resumen_ia,
                downloader_api_token=CONFIG.get("DOWNLOADER_API_TOKEN"),
                stats_html=stats_html,
                news_list_html=news_list_html,
                news_week_filters_html=news_week_filters_html,
                news_channel_filters_html=news_channel_filters_html,
                news_category_filters_html=news_category_filters_html,
                video_week_filters_html=video_week_filters_html,
                multimedia_tabs_html=multimedia_tabs_html,
                video_channel_filters_html=video_channel_filters_html,
                multimedia_content_html=multimedia_content_html,
                github_ranking_html=github_ranking_html,
            )
        )

    logger.info(f"✅ Dashboard HTML pre-renderizado ({len(historial)} registros, {len(top_github)} herramientas).")


def emoji_categoria(cat: str) -> str:
    return cat.split()[0] if cat and cat[0] in JS_CONFIG["EMOJIS_CATEGORIA"] else "💡"

def badge_str(item: dict) -> str:
    return "`💻 Tech`"

def origen_str(item: dict) -> str:
    return " `📡 RSS`" if item.get(ORIGEN_KEY) == VAL_RSS else ""

async def generar_recap(noticias_web, client, blog_path: str | None = None) -> str | None:
    ahora = datetime.now()
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    noticias_blog = [n for n in noticias_web if "yout" not in n[ENLACE_KEY]]
    if not noticias_blog:
        return None

    # ── Archivar recaps antiguos (>2 semanas) ──
    semana_actual = f"{year}-W{week:02d}"
    if blog_path:
        auto_news_dir = os.path.join(blog_path, "src", "content", "auto-news")
    else:
        auto_news_dir = "./auto-news"
    os.makedirs(auto_news_dir, exist_ok=True)
    archivados = archivar_recaps_antiguos(auto_news_dir, semana_actual)
    if archivados:
        logger.info(f"📦 {archivados} recaps antiguos archivados.")

    # ── SEO: un solo post por semana ──
    semana_slug = f"{year}-w{week:02d}-tech-recap"
    path_md = os.path.join(auto_news_dir, f"{semana_slug}.md")
    if os.path.exists(path_md):
        logger.info(f"⏭️ Recap semanal {semana_slug} ya existe. Saltando.")
        with open(path_md, "r", encoding="utf-8") as f:
            match = re.search(r'description: "(.*?)"', f.read())
            introduccion = match.group(1) if match else "Recap semanal disponible."
        return introduccion

    # ── Agrupar noticias por categoría para mejor contexto IA ──
    noticias_por_cat: dict[str, list] = {}
    for n in noticias_blog:
        cat = n.get(CATEGORIA_KEY, "💡 General")
        noticias_por_cat.setdefault(cat, []).append(n)

    categorias_ordenadas = sorted(noticias_por_cat.items(), key=lambda x: -len(x[1]))

    # Estadísticas para el prompt
    total_rss = sum(1 for n in noticias_blog if n.get(ORIGEN_KEY) == VAL_RSS)
    fuente_count = {}
    for n in noticias_blog:
        fuente_count[n[FUENTE_KEY]] = fuente_count.get(n[FUENTE_KEY], 0) + 1
    fuentes_top = sorted(fuente_count.items(), key=lambda x: -x[1])[:5]

    resumen_cats = "\n".join(
        f"  [{cat}] ({len(items)} noticias): " + ", ".join(n[TITULO_KEY][:50] for n in items[:3])
        for cat, items in categorias_ordenadas[:6]
    )

    # Texto agrupado por categoría (mejor contexto para la IA)
    texto_agrupado = []
    for cat, items in categorias_ordenadas:
        texto_agrupado.append(f"\n=== {cat} ({len(items)} noticias) ===")
        for n in items[:8]:
            origen = "RSS" if n.get(ORIGEN_KEY) == VAL_RSS else "web"
            texto_agrupado.append(f"  [{n[FUENTE_KEY]}] {n[TITULO_KEY]} (origen: {origen})")
    texto_noticias = "\n".join(texto_agrupado)

    # ── Llamar a la IA ──
    data_ia = await obtener_recap_semanal_ia(
        noticias_blog, client,
        resumen_cats=resumen_cats,
        total_rss=total_rss,
        texto_noticias=texto_noticias,
        fuentes_top=fuentes_top,
        categorias_ordenadas=categorias_ordenadas,
    )
    if not data_ia:
        return None
    img_recap = await generar_imagen_noticia(f"Recap {week}", client)
    await asyncio.sleep(3)

    introduccion = data_ia.get("introduccion", "")
    noticias_raw = data_ia.get("noticias_destacadas", [])
    if isinstance(noticias_raw, list):
        bloque_noticias = "\n\n".join(
            f'### {i+1}. {n.get("titulo", "")}\n**El suceso:** {n.get("suceso", "")}\n**Impacto:** {n.get("impacto", "")}'
            for i, n in enumerate(noticias_raw[:5])
        )
    else:
        bloque_noticias = str(noticias_raw)

    tldr_raw = data_ia.get("tldr", [])
    if isinstance(tldr_raw, list):
        conclusion_tldr = "\n".join(f"- {p}" for p in tldr_raw[:5])
    else:
        conclusion_tldr = str(tldr_raw)

    total_noticias = len(noticias_blog)
    fuentes_unicas = len(set(n[FUENTE_KEY] for n in noticias_blog))
    tiempo_lectura = max(3, total_noticias * 2)
    fuentes_top_str = "\n".join(
        f"  - {f} — **{c}** noticias" for f, c in fuentes_top
    )
    top_categorias = ", ".join(
        f"{c} ({n})" for c, n in categorias_ordenadas[:3]
    )
    stats_categorias = "\n".join(
        f"  - {cat}: **{cnt}** noticias ({cnt * 100 // total_noticias}%)"
        for cat, cnt in [(c, len(i)) for c, i in categorias_ordenadas]
    )

    partes_lista = []
    for cat, items in categorias_ordenadas:
        partes_lista.append(f"**{cat}** ({len(items)} noticias)")
        for n in items[:10]:
            badge = badge_str(n)
            origen = origen_str(n)
            fecha = f" ({n.get(FECHA_PUB_KEY, '')})" if n.get(FECHA_PUB_KEY) else ""
            partes_lista.append(f"  - {badge}{origen} [{n['fuente']}] {n.get('titulo', '')}{fecha}")

    lista_noticias = "\n".join(partes_lista)

    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=introduccion[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap or FALLBACK_GITHUB_IMAGE,
        tags=json.dumps(data_ia.get("tags", ["tech"])),
        slug_name=semana_slug,
        introduccion=introduccion,
        bloque_noticias=bloque_noticias,
        total_noticias=total_noticias,
        total_fuentes=fuentes_unicas,
        tiempo_lectura=tiempo_lectura,
        total_rss=total_rss,
        top_categorias=top_categorias,
        stats_categorias=stats_categorias,
        fuentes_top=fuentes_top_str,
        lista_noticias=lista_noticias,
        repo_name=data_ia.get("repo", {}).get("nombre", "Tool"),
        repo_url=data_ia.get("repo", {}).get("url", "#"),
        repo_desc=data_ia.get("repo", {}).get("desc", ""),
        conclusion_tldr=conclusion_tldr,
        sneak_peek=data_ia.get("sneak_peek", FALLBACK_SNEAK_PEEK),
        nota_personal=data_ia.get("nota_personal", FALLBACK_NOTA_PERSONAL),
    )

    with open(path_md, "w", encoding="utf-8") as f:
        f.write(final_md)
    logger.info(f"✅ Recap generado: {path_md}")
    return introduccion


async def run():
    parser = argparse.ArgumentParser(description="Generate weekly recap + dashboard + PR")
    parser.add_argument("--no-pr", action="store_true", help="Skip PR creation")
    parser.add_argument("--dashboard-only", action="store_true", help="Only regenerate dashboard HTML (skip AI recap and blog PR)")
    parser.add_argument("--blog-path", default=None, help="Path to blog checkout")
    args = parser.parse_args()

    logger.info("🚀 Iniciando generate_weekly.py")
    scr = ScraperPro()

    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    if not historial:
        logger.warning("⚠️ No hay noticias en el histórico. Ejecuta scrape_news.py primero.")
        return
    historial = deduplicar_items(historial)

    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")

    if args.dashboard_only:
        logger.info("ℹ️ Modo --dashboard-only: saltando recap IA y PR.")
        resumen_ia = "Resumen generado localmente sin IA."
    else:
        client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
        noticias_web = [n for n in historial if n.get(TIPO_KEY) in (TIPO_VAL_NOTICIA, "news")]
        resumen_ia = await generar_recap(historial, client, blog_path=args.blog_path)
        if not resumen_ia or "no ha sido posible" in resumen_ia or len(resumen_ia) < 50:
            logger.warning("⚠️ Generando resumen de emergencia con titulares.")
            titulares = [f"• {n['titulo']}" for n in noticias_web[:10]]
            resumen_ia = "Resumen de hoy:\n\n" + "\n".join(titulares)

    # Precargar avatares de todos los canales YouTube
    for nombre, info in FUENTES.items():
        if YT_KEY in info:
            nombre_c = nombre.replace(" Shorts", "")
            yt_url = info[YT_KEY]
            scr.obtener_avatar_canal(nombre_c, yt_url)

    herramientas = cargar_herramientas()
    generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.")
    scr.guardar_avatars()

    logger.info("✅ generate_weekly.py completado.")
    if args.no_pr or args.dashboard_only:
        logger.info("ℹ️ PR saltado.")


if __name__ == "__main__":
    asyncio.run(run())
