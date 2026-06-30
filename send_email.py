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

from constants_downloadfile import CONFIG, EMAIL_TEMPLATE
from utils import resumir_noticia

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


def load_json(path: str) -> list:
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


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

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    nuevos = historial[:args.max_items]
    top_titular = nuevos[0]["titulo"]
    asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"

    c_tech = len([x for x in nuevos if x.get("badge") == "Tech"])
    c_becas = len([x for x in nuevos if x.get("badge") == "Beca"])
    c_vids = len([x for x in nuevos if x.get("id_video")])

    logger.info(f"🤖 Generando resúmenes IA para {len(nuevos)} noticias...")
    filas_noticias = ""
    for i, n in enumerate(nuevos):
        icon = "📺" if n.get("id_video") else ("🎓" if n.get("badge") == "Beca" else "💻")
        logger.info(f"  [{i+1}/{len(nuevos)}] Resumiendo: {n['titulo'][:60]}...")
        resumen = await resumir_noticia(n, client)
        resumen_html = f'<p style="color: #475569; font-size: 13px; line-height: 1.5; margin: 6px 0 0 0; padding-left: 26px;">📝 {resumen}</p>' if resumen else ""

        filas_noticias += f"""
        <tr>
            <td style="padding: 16px 0; border-bottom: 1px solid #f1f5f9;">
                <span style="font-size: 18px; margin-right: 8px; vertical-align: middle;">{icon}</span>
                <span style="color: #64748b; font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px; vertical-align: middle;">{n['fuente']}</span><br>
                <div style="margin-top: 4px;">
                    <a href="{n['enlace']}" target="_blank" style="color: #4f46e5; text-decoration: none; font-weight: 600; font-size: 15px; line-height: 1.4;">{n['titulo']}</a>
                </div>
                {resumen_html}
            </td>
        </tr>
        """

    temas_clave = ", ".join(list(set([n["fuente"] for n in nuevos[:3]])))
    html_final = EMAIL_TEMPLATE.format(
        fecha_hoy=datetime.now().strftime("%d de %B, %Y"),
        contenido_html="",
        lista_email=filas_noticias,
        count_tech=c_tech,
        count_becas=c_becas,
        count_vids=c_vids,
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
