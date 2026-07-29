#!/usr/bin/env python3
"""
send_email.py — Envía newsletter diaria por Mailgun con resumen IA por noticia.
Para cada noticia, obtiene el texto del artículo y genera un resumen con Gemini.

Uso:
    python send_email.py                             # Envía con resúmenes IA por noticia
    python send_email.py --dry-run                   # Muestra sin enviar
    python send_email.py --max-items 10              # Máx noticias a procesar
"""
import argparse
import asyncio
import json
import logging
import os
from datetime import datetime
from logging.handlers import RotatingFileHandler

from collections import defaultdict
import requests
from google import genai

from scripts.utils.constants_downloadfile import CONFIG, EMAIL_TEMPLATE, EMAIL_ROW_TEMPLATE, EMAIL_SOURCE_HEADER, EMAIL_VIDEO_HEADER, EMAIL_VIDEO_ROW, PROMPT_TRADUCIR_TITULOS, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, ID_VIDEO_KEY, BADGE_KEY, VAL_TECH, TIPO_KEY, NOTICIAS_FILENAME, LOGS_DIR, LOG_FILES
from scripts.utils.common import load_json, save_json, resumir_noticia, resumir_lote_noticias

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(LOGS_DIR, LOG_FILES["email"]), maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("email")

# Colores e iconos por fuente
SOURCE_STYLES = {
    "TechCrunch": {"color": "#16a34a", "icon": "📱"},
    "The Verge": {"color": "#7c3aed", "icon": "🔮"},
    "Wired": {"color": "#000000", "icon": "⚫"},
    "Ars Technica": {"color": "#ff4400", "icon": "🔬"},
    "Engadget": {"color": "#02b3e4", "icon": "📱"},
    "Hacker News": {"color": "#ff6600", "icon": "🔶"},
    "GitHub": {"color": "#24292e", "icon": "🐙"},
    "Google": {"color": "#4285f4", "icon": "🔍"},
    "Xataka": {"color": "#1d9bf0", "icon": "📰"},
    "OpenAI": {"color": "#10a37f", "icon": "🤖"},
    "Anthropic": {"color": "#d97706", "icon": "🧠"},
    "Astro": {"color": "#ff5d01", "icon": "🚀"},
    "Vercel": {"color": "#000000", "icon": "▲"},
    "Dev.to": {"color": "#0a0a23", "icon": "👨‍💻"},
    "Mozilla": {"color": "#ff9400", "icon": "🦊"},
    "Krebs": {"color": "#dc2626", "icon": "🔒"},
    "default": {"color": "#3b82f6", "icon": "💻"},
}

# Estilos para canales de video
VIDEO_CHANNEL_STYLES = {
    "Fernando Herrera": {"color": "#ff0000"},
    "Fazt Code": {"color": "#ff0000"},
    "HolaMundo": {"color": "#ff0000"},
    "CodelyTV": {"color": "#7c3aed"},
    "midudev": {"color": "#ff6600"},
    "Pildoras Informaticas": {"color": "#0066cc"},
    "Angel Vertex": {"color": "#00cc66"},
    "VisualStudioCode": {"color": "#007acc"},
    "freeCodeCamp": {"color": "#0a0a23"},
    "FalconMasters": {"color": "#ff4444"},
    "Carlos Azaustre": {"color": "#1e293b"},
    "Manz Dev": {"color": "#ff6600"},
    "default": {"color": "#64748b"},
}

def get_video_channel_style(canal: str) -> dict:
    for key, style in VIDEO_CHANNEL_STYLES.items():
        if key.lower() in canal.lower():
            return style
    return VIDEO_CHANNEL_STYLES["default"]

def get_source_style(fuente: str) -> dict:
    for key, style in SOURCE_STYLES.items():
        if key.lower() in fuente.lower():
            return style
    return SOURCE_STYLES["default"]

async def traducir_titulo(titulo: str, client) -> str:
    """Traduce un título al español usando Gemini."""
    modelos = CONFIG.get("AI_MODELS", ["gemini-2.5-flash", "gemini-2.5-pro"])
    prompt = PROMPT_TRADUCIR_TITULOS.format(texto_a_traducir=f"0|{titulo}")
    for modelo in modelos:
        try:
            response = client.models.generate_content(model=modelo, contents=prompt)
            if response and response.text:
                import json as _json
                data = _json.loads(response.text.strip().removeprefix("```json").removesuffix("```").strip())
                trads = data.get("traducciones", [])
                if trads and trads[0].get("tr"):
                    return trads[0]["tr"]
        except Exception:
            continue
    return titulo



def _es_multimedia(item: dict) -> bool:
    return item.get(ID_VIDEO_KEY) is not None

async def run():
    parser = argparse.ArgumentParser(description="Send email newsletter with AI per-news summaries")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-items", type=int, default=10, help="Max news to process (default 10)")
    args = parser.parse_args()

    if not CONFIG.get("MAIL_KEY") or not CONFIG.get("MAIL_DOMAIN") or not CONFIG.get("EMAIL_TO"):
        logger.warning("⚠️ Configuración de Mailgun incompleta. Revisa secrets.")
        return

    logger.info("📧 Iniciando send_email.py (con resúmenes IA por noticia)")
    path_json = os.path.join(CONFIG["FOLDER"], NOTICIAS_FILENAME)
    historial = load_json(path_json)

    if not historial:
        logger.info("📭 No hay noticias para enviar.")
        return

    # Separar videos y noticias
    todos_videos = [n for n in historial if _es_multimedia(n)][:10]
    historial = [n for n in historial if not _es_multimedia(n)]

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    nuevos = historial[:args.max_items]

    # Generar sección de videos
    filas_videos = ""
    if todos_videos:
        filas_videos += EMAIL_VIDEO_HEADER.format(video_count=len(todos_videos))
        for v in todos_videos:
            canal = v.get(FUENTE_KEY, "YouTube")
            thumbnail = v.get("thumbnail", f"https://img.youtube.com/vi/{v.get(ID_VIDEO_KEY, '')}/mqdefault.jpg")
            enlace = v.get(ENLACE_KEY, "#")
            titulo = v.get(TITULO_KEY, "Sin título")
            duracion = v.get("duracion", "")
            duracion_html = f' · {duracion}' if duracion else ""

            filas_videos += EMAIL_VIDEO_ROW.format(
                thumbnail=thumbnail,
                canal=canal,
                enlace=enlace,
                titulo=titulo,
                duracion=duracion_html,
            )

    if not nuevos:
        top_titular = "Tech Pulse"
        asunto = f"📊 Tech Pulse — sin noticias destacadas hoy"
        c_tech = 0
        filas_noticias = ""
        temas_clave = ""
        resumen_lote = None
        contenido_html = "<p style='font-size:15px;line-height:1.7;margin:0;color:#64748b;'>No hay noticias destacadas hoy.</p>"
    else:
        top_titular = nuevos[0][TITULO_KEY]
        asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"
        c_tech = len([x for x in nuevos if x.get(BADGE_KEY) == VAL_TECH])

        logger.info(f"🤖 Generando resúmenes IA para {len(nuevos)} noticias...")

        # Agrupar noticias por fuente
        por_fuente = defaultdict(list)
        for n in nuevos:
            por_fuente[n[FUENTE_KEY]].append(n)

        filas_noticias = ""
        for fuente, items in por_fuente.items():
            style = get_source_style(fuente)
            filas_noticias += EMAIL_SOURCE_HEADER.format(
                source_name=fuente,
                source_count=len(items),
                source_color=style["color"],
                source_icon=style["icon"],
            )
            for n in items:
                icon = style["icon"]
                titulo_original = n['titulo']

                if n.get('traducido'):
                    titulo_es = titulo_original
                else:
                    logger.info(f"  Traduciendo: {titulo_original[:60]}...")
                    titulo_es = await traducir_titulo(titulo_original, client)

                resumen = n.get('resumen')
                if not resumen:
                    logger.info(f"  Resumiendo: {titulo_original[:60]}...")
                    resumen = await resumir_noticia(n, client)
                    if resumen:
                        n['resumen'] = resumen

                resumen_html = f'<p style="color: #64748b; font-size: 12px; line-height: 1.4; margin: 4px 0 0 0; padding-left: 0; font-style: italic;">{resumen}</p>' if resumen else ""

                filas_noticias += EMAIL_ROW_TEMPLATE.format(
                    icon=icon, enlace=n['enlace'],
                    titulo=titulo_es, resumen_html=resumen_html,
                )

        temas_clave = ", ".join(list(set([n[FUENTE_KEY] for n in nuevos[:3]])))
        logger.info("🤖 Generando resumen general del lote...")
        resumen_lote = await resumir_lote_noticias(nuevos, client)
        contenido_html = f"<p style='font-size:15px;line-height:1.7;margin:0;'>{resumen_lote}</p>" if resumen_lote else ""
        if not contenido_html:
            contenido_html = "<p style='font-size:15px;line-height:1.7;margin:0;color:#64748b;'>" + " · ".join(n['titulo'][:60] for n in nuevos[:3]) + "</p>"

    html_final = EMAIL_TEMPLATE.format(
        fecha_hoy=datetime.now().strftime("%d de %B, %Y"),
        contenido_html=contenido_html,
        lista_email=filas_noticias,
        videos_html=filas_videos,
        count_tech=c_tech,
        total_noticias=len(nuevos or []),
        temas_clave=temas_clave,
        year=datetime.now().year,
    )

    if args.dry_run:
        print(f"Asunto: {asunto}")
        print(f"HTML ({len(html_final)} chars):")
        print(html_final[:1000])
        print("...")
        logger.info("📋 Dry-run completado.")
        return

    try:
        url_mailgun = f"https://api.mailgun.net/v3/{CONFIG.get('MAIL_DOMAIN')}/messages"
        auth = ("api", CONFIG["MAIL_KEY"])
        data = {
            "from": f"Tech Pulse <mailgun@{CONFIG.get('MAIL_DOMAIN')}>",
            "to": [CONFIG.get("EMAIL_TO")],
            "subject": asunto,
            "html": html_final,
        }
        r = requests.post(url_mailgun, auth=auth, data=data, timeout=30)
        if r.status_code == 200:
            logger.info("✅ Newsletter con resúmenes IA enviada exitosamente.")
            save_json(path_json, historial)
        else:
            logger.error(f"❌ Error Mailgun ({r.status_code}): {r.text}")
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")


if __name__ == "__main__":
    asyncio.run(run())
