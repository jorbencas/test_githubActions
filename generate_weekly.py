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
import hashlib
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

from constants_downloadfile import CONFIG, HTML_TEMPLATE, MD_TEMPLATE
from scraper_base import ScraperPro
from utils import generar_imagen_noticia, obtener_recap_semanal_ia, deduplicar_items

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


def load_json(path: str) -> list:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def cargar_herramientas() -> list:
    path = os.path.join(CONFIG["FOLDER"], "herramientas.json")
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia):
    historial.sort(key=lambda x: x.get("ts", ""), reverse=True)
    palabra_maestra = CONFIG.get("DOWNLOADER_API_TOKEN")
    fecha_hoy = datetime.utcnow().strftime("%Y-%m-%d")
    semilla = f"{palabra_maestra}-{fecha_hoy}"
    token_oculto = hashlib.sha256(semilla.encode()).hexdigest()

    herramientas_github = [
        h for h in herramientas
        if h.get("subtipo") == "github" and h.get("estrellas", "0").isdigit()
    ]
    herramientas_github.sort(key=lambda h: int(h.get("estrellas", "0")), reverse=True)
    top_github = herramientas_github[:20]

    os.makedirs("public", exist_ok=True)
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(
            HTML_TEMPLATE.format(
                fecha_hoy=fecha_h,
                resumen=resumen_ia,
                api_token=token_oculto,
                api_url="https://testactions1github-api-python.hf.space/download",
                api_salud="https://testactions1github-api-python.hf.space/health",
            )
        )
    with open("public/data.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "items": historial,
                "herramientas": top_github,
                "avatars": getattr(scr, "avatar_repo", None) and scr.avatar_repo.avatars or {},
            },
            f,
            indent=2,
            ensure_ascii=False,
        )
    logger.info(f"✅ Dashboard HTML + data.json generados ({len(historial)} registros, {len(top_github)} herramientas).")


def emoji_categoria(cat: str) -> str:
    return cat.split()[0] if cat and cat[0] in "⚡🤖💻🐳🔒📊🎓💡" else "💡"

def badge_str(item: dict) -> str:
    b = item.get("badge", "Tech")
    return f"`🎓 Beca`" if b == "Beca" else f"`💻 Tech`"

def origen_str(item: dict) -> str:
    return " `📡 RSS`" if item.get("origen") == "rss" else ""

async def generar_recap(noticias_web, client) -> str | None:
    ahora = datetime.now()
    fecha_iso = ahora.strftime("%Y-%m-%d")
    year, week, _ = ahora.isocalendar()

    noticias_blog = [n for n in noticias_web if "yout" not in n["enlace"]]
    if not noticias_blog:
        return None

    categoria_count = {}
    for n in noticias_blog:
        cat = n.get("categoria", "💡 General")
        categoria_count[cat] = categoria_count.get(cat, 0) + 1
    categorias_ordenadas = sorted(categoria_count.items(), key=lambda x: -x[1])

    fuente_count = {}
    for n in noticias_blog:
        fuente_count[n["fuente"]] = fuente_count.get(n["fuente"], 0) + 1
    fuentes_top = sorted(fuente_count.items(), key=lambda x: -x[1])[:5]

    total_rss = sum(1 for n in noticias_blog if n.get("origen") == "rss")

    semana_slug = f"{year}-w{week:02d}-tech-recap"
    path_md = f"./auto-news/{semana_slug}.md"
    os.makedirs("./auto-news", exist_ok=True)

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
    fuentes_unicas = len(set(n["fuente"] for n in noticias_blog))
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
        cat = n.get("categoria", "💡 General")
        noticias_por_cat.setdefault(cat, []).append(n)

    partes_lista = []
    for cat in [c[0] for c in categorias_ordenadas]:
        items = noticias_por_cat[cat]
        partes_lista.append(f"**{cat}** ({len(items)} noticias)")
        for n in items[:10]:
            badge = badge_str(n)
            origen = origen_str(n)
            fecha = f" ({n.get('fecha_publicacion', '')})" if n.get("fecha_publicacion") else ""
            partes_lista.append(f"  - {badge}{origen} [{n['fuente']}] {n.get('titulo', '')}{fecha}")

    lista_noticias = "\n".join(partes_lista)

    final_md = inspect.cleandoc(MD_TEMPLATE).format(
        titulo=f"Weekly Tech Recap W{week}",
        description=introduccion[:150].replace('"', "'"),
        fecha_iso=fecha_iso,
        author="Jorge Beneyto Castelló",
        ruta_imagen=img_recap
        or "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true",
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
        sneak_peek=data_ia.get("sneak_peek", "Seguiremos de cerca la evolución del sector. ¡No te lo pierdas!"),
        nota_personal=data_ia.get("nota_personal", "Keep coding!"),
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

    noticias_web = [n for n in historial if n.get("tipo") in ("noticia", "news")]
    resumen_ia = await generar_recap(historial, client)
    if not resumen_ia or "no ha sido posible" in resumen_ia or len(resumen_ia) < 50:
        logger.warning("⚠️ Generando resumen de emergencia con titulares.")
        titulares = [f"• {n['titulo']}" for n in noticias_web[:10]]
        resumen_ia = "Resumen de hoy:\n\n" + "\n".join(titulares)

    herramientas = cargar_herramientas()
    generar_dashboard_html(historial, herramientas, scr, fecha_h, ahora, resumen_ia or "Sin novedades hoy.")
    scr.guardar_avatars()

    logger.info("✅ generate_weekly.py completado.")
    if args.no_pr:
        logger.info("ℹ️ PR saltado (--no-pr).")


if __name__ == "__main__":
    asyncio.run(run())
