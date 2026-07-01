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

import requests
from google import genai

from constants_downloadfile import CONFIG, EMAIL_TEMPLATE, EMAIL_ROW_TEMPLATE, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, ID_VIDEO_KEY, BADGE_KEY, VAL_TECH
from utils import load_json, resumir_noticia, resumir_lote_noticias

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/email.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("email")



def _es_multimedia(item: dict) -> bool:
    if item.get(ID_VIDEO_KEY):
        return None
    fuente = (item.get(FUENTE_KEY) or "").lower()
    return "tiktok" in fuente or "instagram" in fuente

async def run():
    parser = argparse.ArgumentParser(description="Send email newsletter with AI per-news summaries")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-items", type=int, default=10, help="Max news to process (default 10)")
    args = parser.parse_args()

    if not CONFIG.get("MAIL_KEY") or not CONFIG.get("MAIL_DOMAIN") or not CONFIG.get("EMAIL_TO"):
        logger.warning("⚠️ Configuración de Mailgun incompleta. Revisa secrets.")
        return

    logger.info("📧 Iniciando send_email.py (con resúmenes IA por noticia)")
    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    if not historial:
        logger.info("📭 No hay noticias para enviar.")
        return

    historial = [n for n in historial if not _es_multimedia(n)]
    if not historial:
        logger.info("📭 No hay noticias (solo multimedia) para enviar.")
        return

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    nuevos = historial[:args.max_items]
    if not nuevos:
        logger.info("📭 No hay noticias (solo multimedia) para enviar.")
        return
    top_titular = nuevos[0][TITULO_KEY]
    asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"

    c_tech = len([x for x in nuevos if x.get(BADGE_KEY) == VAL_TECH])

    logger.info(f"🤖 Generando resúmenes IA para {len(nuevos)} noticias...")
    filas_noticias = ""
    for i, n in enumerate(nuevos):
        icon = "💻"
        logger.info(f"  [{i+1}/{len(nuevos)}] Resumiendo: {n['titulo'][:60]}...")
        resumen = await resumir_noticia(n, client)
        resumen_html = f'<p style="color: #475569; font-size: 13px; line-height: 1.5; margin: 6px 0 0 0; padding-left: 26px;">📝 {resumen}</p>' if resumen else ""

        filas_noticias += EMAIL_ROW_TEMPLATE.format(
            icon=icon, fuente=n['fuente'], enlace=n['enlace'],
            titulo=n['titulo'], resumen_html=resumen_html,
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
        count_tech=c_tech,
        total_noticias=len(nuevos),
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
        else:
            logger.error(f"❌ Error Mailgun ({r.status_code}): {r.text}")
    except Exception as e:
        logger.error(f"❌ Error enviando email: {e}")


if __name__ == "__main__":
    asyncio.run(run())
