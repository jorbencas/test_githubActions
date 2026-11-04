#!/usr/bin/env python3
"""
generate_weekly.py — Genera el weekly recap del blog (IA + archivado SEO).
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
from pathlib import Path

import google.genai as genai

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logging_setup import setup_logging
from utils.constants_downloadfile import CONFIG, MD_TEMPLATE, SKILLS, LLMS, LENGUAJES, FRAMEWORKS, LIBRERIAS, CATEGORIAS, FALLBACK_GITHUB_IMAGE, FALLBACK_SNEAK_PEEK, FALLBACK_NOTA_PERSONAL, TIPO_KEY, ORIGEN_KEY, TIPO_VAL_NOTICIA, VAL_RSS, ENLACE_KEY, FUENTE_KEY, FECHA_PUB_KEY, CATEGORIA_KEY, TITULO_KEY, ID_VIDEO_KEY, SUB_VAL_GITHUB_TOPIC, SUB_VAL_GITHUB_COLLECTION, SUB_VAL_PRODUCTHUNT, NOTICIAS_FILENAME, LOGS_DIR, LOG_FILES, AUTO_NEWS_DIR, BLOG_AUTO_NEWS_REL

from utils.common import load_json, save_json, generar_imagen_noticia, obtener_recap_semanal_ia, deduplicar_items, traducir_titulos_ia

logger = setup_logging("weekly", LOG_FILES["weekly"], LOGS_DIR)


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


def _detectar_efemerides(dt: datetime) -> list[str]:
    """Detecta efemérides y festividades cercanas a la fecha dada."""
    efemerides = []
    dia, mes = dt.day, dt.month

    # Festividades fijas
    FESTIVIDADES = {
        (1, 1): "Año Nuevo",
        (1, 6): "Día de Reyes",
        (2, 14): "San Valentín",
        (3, 8): "Día de la Mujer",
        (4, 23): "Día del Libro",
        (5, 1): "Día del Trabajo",
        (5, 15): "Día de la Madre",
        (6, 23): "Noche de San Juan",
        (6, 24): "San Juan",
        (7, 25): "Santiago Apostol",
        (8, 15): "Asunción de la Virgen",
        (10, 12): "Hispanidad",
        (10, 31): "Halloween",
        (11, 1): "Día de Todos los Santos",
        (11, 9): "Día de la Innovación",
        (12, 6): "Día de la Constitución",
        (12, 22): "Inicio de Navidades",
        (12, 24): "Nochebuena",
        (12, 25): "Navidad",
        (12, 28): "Día de los Santos Inocentes",
        (12, 31): "Fin de Año",
    }

    if (mes, dia) in FESTIVIDADES:
        efemerides.append(FESTIVIDADES[(mes, dia)])

    # Buscar ±3 días para contextos cercanos
    from datetime import timedelta
    for offset in [-3, -2, -1, 1, 2, 3]:
        d = dt + timedelta(days=offset)
        key = (d.month, d.day)
        if key in FESTIVIDADES:
            if offset > 0:
                efemerides.append(f"viene {FESTIVIDADES[key]} en {abs(offset)} días")
            else:
                efemerides.append(f"acaba de pasar {FESTIVIDADES[key]}")

    # Eventos tech conocidos
    # CES: ~8-12 enero
    if mes == 1 and 5 <= dia <= 15:
        efemerides.append("CES en Las Vegas")
    # MWC: ~24-27 febrero
    if mes == 2 and 20 <= dia <= 28:
        efemerides.append("MWC en Barcelona")
    # Google I/O: ~mayo
    if mes == 5 and 10 <= dia <= 25:
        efemerides.append("Google I/O")
    # WWDC Apple: ~junio
    if mes == 6 and 1 <= dia <= 15:
        efemerides.append("WWDC de Apple")
    # Black Friday: ~viernes anterior a noviembre
    if mes == 11 and 20 <= dia <= 30:
        efemerides.append("Black Friday")
    # Cyber Monday
    if mes == 11 and dia <= 5:
        efemerides.append("Cyber Monday")

    return efemerides


def _build_semana_info(dt: datetime) -> tuple[str, str]:
    """Devuelve (fecha_actual, semana_info) para el prompt."""
    year, week, _ = dt.isocalendar()
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    fecha_str = f"{dias[dt.weekday()]} {dt.day} de {meses[dt.month-1]} de {dt.year}"

    efemerides = _detectar_efemerides(dt)
    partes = [f"Semana {week} del {year}"]
    if efemerides:
        partes.append(f"Efemérides/contexto: {', '.join(efemerides)}")

    return fecha_str, " | ".join(partes)


MESES_ES = {
    1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
    5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
    9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre",
}


def _format_fecha_es(fecha: str) -> str:
    """Convierte fecha ISO o RFC2822 a formato largo en español: '4 de julio de 2026'."""
    if not fecha:
        return ""
    try:
        # Intentar ISO format primero
        dt = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
    except Exception:
        try:
            # Intentar RFC2822: "Sat, 04 Jul 2026 09:08:09 +0000"
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(fecha)
        except Exception:
            return fecha
    dia = dt.day
    mes = MESES_ES.get(dt.month, "")
    anio = dt.year
    return f"{dia} de {mes} de {anio}"


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
        auto_news_dir = os.path.join(blog_path, *BLOG_AUTO_NEWS_REL)
    else:
        auto_news_dir = os.path.join(".", AUTO_NEWS_DIR)
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

    # ── Contexto de fecha para la IA ──
    fecha_actual, semana_info = _build_semana_info(ahora)

    # ── Llamar a la IA ──
    data_ia = await obtener_recap_semanal_ia(
        noticias_blog, client,
        resumen_cats=resumen_cats,
        total_rss=total_rss,
        texto_noticias=texto_noticias,
        fuentes_top=fuentes_top,
        categorias_ordenadas=categorias_ordenadas,
        fecha_actual=fecha_actual,
        semana_info=semana_info,
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
            for i, n in enumerate(noticias_raw[:10])
        )
    else:
        bloque_noticias = str(noticias_raw)

    tldr_raw = data_ia.get("tldr", [])
    if isinstance(tldr_raw, list):
        conclusion_tldr = "\n".join(f"- {p}" for p in tldr_raw[:6])
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

    # Sección de categorías desde IA
    cat_resumen = data_ia.get("categorias_resumen", {})
    if cat_resumen:
        partes_cat = []
        for cat, resumen in cat_resumen.items():
            if resumen and resumen.strip():
                partes_cat.append(f"### {cat}\n\n{resumen}")
        categorias_seccion = "\n\n".join(partes_cat) if partes_cat else "_No hay resumen por categorías._"
    else:
        # Fallback: generar desde datos locales
        partes_cat = []
        for cat, items in categorias_ordenadas[:6]:
            titulares = ", ".join(n[TITULO_KEY][:60] for n in items[:3])
            partes_cat.append(f"### {cat}\n\n{len(items)} noticias. Destacados: {titulares}")
        categorias_seccion = "\n\n".join(partes_cat) if partes_cat else "_No hay categorías esta semana._"

    # Agrupar noticias por fuente (sin duplicados)
    from collections import defaultdict, OrderedDict
    por_fuente = OrderedDict()
    seen_titles = set()
    for n in noticias_blog:
        titulo = n.get(TITULO_KEY, "")
        if titulo.lower() in seen_titles:
            continue
        seen_titles.add(titulo.lower())
        fuente = n[FUENTE_KEY]
        por_fuente.setdefault(fuente, []).append(n)

    partes_por_fuente = []
    for fuente, items in por_fuente.items():
        partes_por_fuente.append(f"### 📰 {fuente} ({len(items)} noticias)\n")
        for n in items[:10]:
            badge = badge_str(n)
            origen = origen_str(n)
            fecha = f" ({n.get(FECHA_PUB_KEY, '')})" if n.get(FECHA_PUB_KEY) else ""
            partes_por_fuente.append(f"- {badge}{origen} {n.get('titulo', '')}{fecha}")
        partes_por_fuente.append("")

    noticias_por_fuente = "\n".join(partes_por_fuente)

    # Sección de videos
    videos = [n for n in noticias_blog if n.get(ID_VIDEO_KEY)]
    if videos:
        partes_videos = []
        for v in videos[:10]:
            canal = v.get(FUENTE_KEY, "YouTube")
            titulo = v.get(TITULO_KEY, "Sin título")
            enlace = v.get(ENLACE_KEY, "#")
            partes_videos.append(f"- 🎬 **{canal}** — [{titulo}]({enlace})")
        videos_seccion = "\n".join(partes_videos)
    else:
        videos_seccion = "_No hay videos destacados esta semana._"

    # Tags: asegurar mínimo 8, merge IA + fuentes_top
    tags_ia = data_ia.get("tags", ["tech"])
    tags_fuentes = [f.lower().replace(" ", "-") for f, _ in fuentes_top[:2]]
    tags_merged = list(dict.fromkeys(["tech", "weekly-recap"] + tags_ia + tags_fuentes))
    if len(tags_merged) < 8:
        tags_extra = ["programacion", "desarrollo-web", "open-source", "herramientas", "inteligencia-artificial"]
        for t in tags_extra:
            if t not in tags_merged:
                tags_merged.append(t)
            if len(tags_merged) >= 10:
                break

    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=introduccion[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap or FALLBACK_GITHUB_IMAGE,
        tags=json.dumps(tags_merged[:10]),
        slug_name=semana_slug,
        introduccion=introduccion,
        stats_categorias=stats_categorias,
        bloque_noticias=bloque_noticias,
        categorias_seccion=categorias_seccion,
        tiempo_lectura=tiempo_lectura,
        noticias_por_fuente=noticias_por_fuente,
        videos_seccion=videos_seccion,
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
    parser = argparse.ArgumentParser(description="Generate weekly recap + blog PR")
    parser.add_argument("--no-pr", action="store_true", help="Skip PR creation")
    parser.add_argument("--blog-path", default=None, help="Path to blog checkout")
    args = parser.parse_args()

    logger.info("🚀 Iniciando generate_weekly.py")

    path_json = os.path.join(CONFIG["FOLDER"], NOTICIAS_FILENAME)
    historial = load_json(path_json)
    if not historial:
        logger.warning("⚠️ No hay noticias en el histórico. Ejecuta scrape_news.py primero.")
        return
    historial = deduplicar_items(historial)

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    # Traducir títulos pendientes antes de renderizar
    historial = await traducir_titulos_ia(historial, client)
    save_json(path_json, historial)
    noticias_web = [n for n in historial if n.get(TIPO_KEY) in (TIPO_VAL_NOTICIA, "news")]
    resumen_ia = await generar_recap(historial, client, blog_path=args.blog_path)
    if not resumen_ia or "no ha sido posible" in resumen_ia or len(resumen_ia) < 50:
        logger.warning("⚠️ Generando resumen de emergencia con titulares.")
        titulares = [f"• {n['titulo']}" for n in noticias_web[:10]]
        resumen_ia = "Resumen de hoy:\n\n" + "\n".join(titulares)

    logger.info("✅ generate_weekly.py completado.")
    if args.no_pr:
        logger.info("ℹ️ PR saltado.")


if __name__ == "__main__":
    asyncio.run(run())
