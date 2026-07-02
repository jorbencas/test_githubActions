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
import sys
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from google import genai

from constants_downloadfile import CONFIG, HTML_TEMPLATE, MD_TEMPLATE, SKILLS, LLMS, LENGUAJES, FRAMEWORKS, LIBRERIAS, CATEGORIAS, JS_CONFIG, FALLBACK_GITHUB_IMAGE, FALLBACK_SNEAK_PEEK, FALLBACK_NOTA_PERSONAL, SUBTIPO_KEY, TIPO_KEY, ORIGEN_KEY, SUB_VAL_GITHUB, TIPO_VAL_NOTICIA, VAL_RSS, ENLACE_KEY, FUENTE_KEY, TS_KEY, FECHA_PUB_KEY, CATEGORIA_KEY, ESTRELLAS_KEY, TITULO_KEY, FECHA_REAL_KEY, ID_VIDEO_KEY, LENGUAJE_KEY, DESCRIPCION_KEY, SUB_VAL_GITHUB_TOPIC, SUB_VAL_GITHUB_COLLECTION, SUB_VAL_PRODUCTHUNT, TIPO_VAL_HERRAMIENTA, TIPO_VAL_VIDEO, TIPO_VAL_SHORTS, TIPO_VAL_LIVE, TIPO_VAL_TREND, TIPO_VAL_SOCIAL
from scraper_base import ScraperPro
from utils import load_json, generar_imagen_noticia, obtener_recap_semanal_ia, deduplicar_items

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


def cargar_trends() -> list:
    path = os.path.join(CONFIG["FOLDER"], "trends.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia, trends=None):
    historial.sort(key=lambda x: x.get(TS_KEY, ""), reverse=True)
    herramientas_github = [
        h for h in herramientas
        if h.get(SUBTIPO_KEY) == SUB_VAL_GITHUB and h.get(ESTRELLAS_KEY, "0").isdigit()
    ]
    herramientas_github.sort(key=lambda h: int(h.get(ESTRELLAS_KEY, "0")), reverse=True)
    top_github = herramientas_github[:20]

    # === Renderizar TODO en Python, inyectar en HTML_TEMPLATE ===
    
    # Separar noticias y vídeos
    noticias_web = [n for n in historial if n.get(TIPO_KEY) in (TIPO_VAL_NOTICIA, "news") and not n.get("id_video")]
    videos = [n for n in historial if n.get("id_video")]
    
    # Estadísticas
    total_noticias = len(noticias_web)
    total_videos = len(videos)
    total_items = len(historial)
    fuentes_unicas = len(set(n.get(FUENTE_KEY, "") for n in historial if n.get(FUENTE_KEY)))
    
    # Categorías de noticias
    cat_count = {}
    for n in noticias_web:
        cat = n.get(CATEGORIA_KEY, "💡 General")
        cat_count[cat] = cat_count.get(cat, 0) + 1
    cats_sorted = sorted(cat_count.items(), key=lambda x: -x[1])
    cats_stats = "\n".join(f'  <div class="stat-cell"><b>{cnt}</b><span>{cat}</span></div>' for cat, cnt in cats_sorted[:6])
    
    # Top fuentes
    fuente_count = {}
    for n in historial:
        f = n.get(FUENTE_KEY, "")
        if f: fuente_count[f] = fuente_count.get(f, 0) + 1
    fuentes_top = sorted(fuente_count.items(), key=lambda x: -x[1])[:5]
    fuentes_html = "\n".join(
        f'<div class="chip" style="background: #eef2ff; color: #4f46e5;">{f} <span style="opacity:.7">({c})</span></div>'
        for f, c in fuentes_top
    )
    
    # === Renderizar NOTICIAS ===
    def make_news_card(n):
        ts = n.get(TS_KEY, "")
        fuente = n.get(FUENTE_KEY, "")
        titulo = n.get(TITULO_KEY, "Sin título")
        enlace = n.get(ENLACE_KEY, "#")
        fecha = n.get(FECHA_PUB_KEY) or n.get(FECHA_REAL_KEY, "")
        origen = n.get(ORIGEN_KEY, "")
        badge = "📡 RSS" if origen == VAL_RSS else "💻 Tech"
        cat = n.get(CATEGORIA_KEY, "")
        origen_badge = f'<span class="badge badge-rss">{badge}</span>' if origen == VAL_RSS else f'<span class="badge badge-tech">{badge}</span>'
        cat_html = f'<span class="badge badge-cat">{cat}</span>' if cat else ""
        origen_badge_html = f'<span class="badge badge-rss">{badge}</span>' if origen == VAL_RSS else f'<span class="badge badge-tech">💻 Tech</span>'
        return f'<li class="news-item" data-ts="{ts}" data-fuente="{fuente}" data-categoria="{cat}" data-origen="{origen}"><div class="meta">{fuente} | {fecha}</div>{origen_badge_html}{cat_html}<a href="{enlace}" target="_blank">{titulo}</a></li>'
    
    noticias_html = "\n".join(make_news_card(n) for n in noticias_web[:50])
    
    # === Renderizar VÍDEOS YOUTUBE ===
    def make_video_card(n):
        ts = n.get(TS_KEY, "")
        fuente = n.get(FUENTE_KEY, "")
        titulo = n.get(TITULO_KEY, "Sin título")
        enlace = n.get(ENLACE_KEY, "#")
        fecha = n.get(FECHA_PUB_KEY) or n.get(FECHA_REAL_KEY, "")
        id_video = n.get("id_video", "")
        tipo = n.get(TIPO_KEY, "video")
        esLive = tipo == "live"
        esShorts = tipo == "shorts"
        clase = "tipo-live" if esLive else ("tipo-shorts" if esShorts else "tipo-video")
        live_badge = '<span class="badge-live">● EN DIRECTO</span>' if esLive else ""
        thumb = f"https://img.youtube.com/vi/{id_video}/mqdefault.jpg" if id_video else ""
        return f'<div class="card {clase}" data-ts="{ts}" data-fuente="{fuente}">{live_badge}<a href="{enlace}" target="_blank" class="video-thumb-link"><div class="video-thumb"><img src="{thumb}" alt="{titulo}" width="320" height="180" loading="lazy" class="video-thumb-img" onerror="this.classList.add(\'errored\');this.nextElementSibling.classList.add(\'visible\')"><div class="video-thumb-fallback">📺 {fuente or "YouTube"}</div></div></a><div class="card-content"><div class="meta">{fuente} | {fecha}</div><a href="{enlace}" target="_blank">{titulo}</a></div></div>'
    
    videos_html = "\n".join(make_video_card(v) for v in videos[:30])
    
    # === Renderizar TENDENCIAS ===
    trends_data = trends or []
    def make_trend_card(t):
        ts = t.get(TS_KEY, "")
        fecha = t.get(FECHA_PUB_KEY) or t.get(FECHA_REAL_KEY, "")
        tipo = t.get(TIPO_KEY, "trend")
        tipo_emoji = "📊" if tipo == "trend" else "🎵"
        tipo_label = "Google Trends" if tipo == "trend" else "TikTok"
        titulo = t.get(TITULO_KEY, "")
        enlace = t.get(ENLACE_KEY, "#")
        return f'<li class="news-item" data-ts="{ts}"><div class="meta">{tipo_emoji} {tipo_label} | {fecha}</div><span class="badge badge-tech">{tipo_label}</span><a href="{enlace}" target="_blank">{titulo}</a></li>'
    
    trends_html = "\n".join(make_trend_card(t) for t in trends_data[:20])
    
    # === Renderizar RANKING GITHUB ===
    def make_github_card(r, i):
        lang = r.get(LENGUAJE_KEY, "")
        stars = int(r.get(ESTRELLAS_KEY, "0") or 0)
        stars_str = f"{stars/1000:.1f}k" if stars >= 1000 else str(stars)
        lang_badge = f'<span class="badge badge-tech">{lang}</span>' if lang else ""
        desc = r.get("descripcion", "")
        desc_html = f'<div style="font-size:0.85em;color:#64748b;margin-top:4px;">{desc[:120]}</div>' if desc else ""
        return f'<div class="news-item" style="border-left-color:#f59e0b;"><div class="meta"><span>#{i+1} ⭐ {stars_str}</span>{lang_badge}</div><a href="{r.get(ENLACE_KEY, "#")}" target="_blank">{r.get(TITULO_KEY, "")}</a>{desc_html}</div>'
    
    github_html = "\n".join(make_github_card(r, i) for i, r in enumerate(top_github))
    
    # === Referencias ===
    def render_refs(refs_dict, title):
        if not refs_dict: return ""
        html = [f'<div class="filter-section"><strong>{title}</strong><div class="chip-container">']
        for group, items in refs_dict.items():
            html.append(f'<div style="margin-bottom:8px;"><strong style="font-size:0.85em;color:#555;display:block;margin-bottom:4px;">{group}</strong>')
            for item in items:
                html.append(f'<span class="chip" style="padding:2px 10px;font-size:12px;cursor:default;">{item}</span>')
            html.append('</div>')
        html.append('</div></div>')
        return "\n".join(html)
    
    refs_html = ""
    refs_html += render_refs(SKILLS, "🛠️ Skills")
    refs_html += render_refs(LLMS, "🧠 LLMs")
    refs_html += render_refs(LENGUAJES, "📝 Lenguajes")
    refs_html += render_refs(FRAMEWORKS, "📦 Frameworks")
    refs_html += render_refs(LIBRERIAS, "📚 Librerías")
    
    # === Stats bar ===
    stats_html = f'''
        <div class="stat-card"><b>{total_items}</b><span>Total</span></div>
        <div class="stat-card"><b>{total_noticias}</b><span>Noticias</span></div>
        <div class="stat-card"><b>{total_videos}</b><span>Multimedia</span></div>
        <div class="stat-card"><b>{fuentes_unicas}</b><span>Fuentes</span></div>
    '''
    
    # === Categorías para filtros ===
    cats_filter_html = "".join(
        f'<div class="chip" data-cat="{cat}">{cat} <span style="opacity:.7">({cnt})</span></div>'
        for cat, cnt in cats_sorted[:10]
    )
    
    # === Canales para filtros ===
    canales = sorted(set(n.get(FUENTE_KEY, "") for n in historial if n.get(FUENTE_KEY)))
    canales_html = "".join(f'<div class="chip" data-canal="{c}">{c}</div>' for c in canales[:15])
    
    # === RSS fuentes ===
    rss_sources = sorted(set(n.get(FUENTE_KEY, "") for n in historial if n.get(ORIGEN_KEY) == VAL_RSS))
    rss_html = "".join(f'<div class="chip" data-rss="{r}">📡 {r}</div>' for r in rss_sources[:10])
    
    # === Build full HTML ===
    os.makedirs("public", exist_ok=True)
    full_html = HTML_TEMPLATE.format(
        fecha_hoy=fecha_h,
        resumen=resumen_ia,
        stats_bar=stats_html,
        noticias_list=noticias_html,
        videos_grid=videos_html,
        trends_list=trends_html,
        github_ranking=github_html,
        references_section=refs_html,
        cats_filter=cats_filter_html,
        canales_filter=canales_html,
        rss_filter=rss_html,
    )
    
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(full_html)
    
    logger.info(f"✅ Dashboard HTML generado ({len(historial)} registros, {len(top_github)} herramientas, {len(videos)} vídeos).")


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

    categoria_count = {}
    for n in noticias_blog:
        cat = n.get(CATEGORIA_KEY, "💡 General")
        categoria_count[cat] = categoria_count.get(cat, 0) + 1
    categorias_ordenadas = sorted(categoria_count.items(), key=lambda x: -x[1])

    fuente_count = {}
    for n in noticias_blog:
        fuente_count[n[FUENTE_KEY]] = fuente_count.get(n[FUENTE_KEY], 0) + 1
    fuentes_top = sorted(fuente_count.items(), key=lambda x: -x[1])[:5]

    total_rss = sum(1 for n in noticias_blog if n.get(ORIGEN_KEY) == VAL_RSS)

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    if blog_path:
        auto_news_dir = os.path.join(blog_path, "src", "content", "auto-news")
    else:
        auto_news_dir = "./auto-news"
    path_md = os.path.join(auto_news_dir, f"{semana_slug}.md")
    os.makedirs(auto_news_dir, exist_ok=True)

    if os.path.exists(path_md):
        logger.info(f"⏭️ Recap semanal {semana_slug} ya existe. Saltando.")
        with open(path_md, "r", encoding="utf-8") as f:
            match = re.search(r'description: "(.*?)"', f.read())
            introduccion = match.group(1) if match else "Recap semanal disponible."
        return introduccion

    data_ia = await obtener_recap_semanal_ia(noticias_blog, client)
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
        for cat, cnt in categorias_ordenadas
    )

    noticias_por_cat: dict[str, list] = {}
    for n in noticias_blog:
        cat = n.get(CATEGORIA_KEY, "💡 General")
        noticias_por_cat.setdefault(cat, []).append(n)

    partes_lista = []
    for cat in [c[0] for c in categorias_ordenadas]:
        items = noticias_por_cat[cat]
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
    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

    noticias_web = [n for n in historial if n.get(TIPO_KEY) in (TIPO_VAL_NOTICIA, "news")]
    resumen_ia = await generar_recap(historial, client, blog_path=args.blog_path)
    if not resumen_ia or "no ha sido posible" in resumen_ia or len(resumen_ia) < 50:
        logger.warning("⚠️ Generando resumen de emergencia con titulares.")
        titulares = [f"• {n['titulo']}" for n in noticias_web[:10]]
        resumen_ia = "Resumen de hoy:\n\n" + "\n".join(titulares)

    herramientas = cargar_herramientas()
    trends = cargar_trends()
    generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.", trends)
    scr.guardar_avatars()

    logger.info("✅ generate_weekly.py completado.")
    if args.no_pr:
        logger.info("ℹ️ PR saltado (--no-pr).")


if __name__ == "__main__":
    asyncio.run(run())
