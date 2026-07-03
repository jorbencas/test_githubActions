#!/usr/bin/env python3
"""
send_telegram.py — Envía noticias individuales por Telegram con resumen IA + audio TTS.
Cada noticia nueva se envía como un mensaje separado con su propio resumen generado por IA.
Usa telegram_sent.json para no repetir noticias ya enviadas.

Uso:
    python send_telegram.py                          # Envía noticias nuevas
    python send_telegram.py --dry-run                # Muestra sin enviar
"""
import argparse
import asyncio
import json
import logging
import os
import re
from datetime import datetime
from logging.handlers import RotatingFileHandler

import edge_tts
import requests
from google import genai

from scripts.utils.cache import CacheManager, FileCache
from scripts.utils.constants_downloadfile import CONFIG, TELEGRAM_TTS_VOZ, TELEGRAM_DASHBOARD_URL, TELEGRAM_MENSAJE_TEMPLATE, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, FECHA_PUB_KEY, F_KEY, ID_VIDEO_KEY, TIPO_KEY, TIPO_VAL_TREND, TIPO_VAL_SOCIAL
from scripts.utils.common import load_json, resumir_noticia

os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler("logs/telegram.log", maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("telegram")



SENT_LOG = "telegram_sent.json"

CACHE = CacheManager(FileCache(SENT_LOG))


def enviar_mensaje(texto: str, chat_id: str, token: str, reply_markup: dict | None = None) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": texto,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
    try:
        r = requests.post(url, data=payload, timeout=15)
        if r.ok:
            return True
        logger.warning(f"⚠️ Telegram error (sin markdown): {r.text}")
        payload.pop("parse_mode")
        payload["text"] = texto.replace("_", " ").replace("*", "").replace("[", "").replace("]", "")
        r = requests.post(url, data=payload, timeout=15)
        return r.ok
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje: {e}")
        return False


def truncar_texto_voz(texto: str, max_chars: int = 800) -> str:
    texto = re.sub(r'[_*\[\]()~`>#+\-=|{}.!]', '', texto)
    if len(texto) > max_chars:
        texto = texto[:max_chars] + "..."
    return texto


async def enviar_audio_voz(texto: str, chat_id: str, token: str) -> bool:
    audio_path = "resumen.mp3"
    voz = TELEGRAM_TTS_VOZ
    texto_limpio = truncar_texto_voz(texto)
    try:
        communicate = edge_tts.Communicate(texto_limpio, voz)
        await communicate.save(audio_path)
        url = f"https://api.telegram.org/bot{token}/sendVoice"
        with open(audio_path, "rb") as f:
            files = {"voice": (audio_path, f, "audio/mpeg")}
            payload = {
                "chat_id": chat_id,
                "caption": "🎙️ *Resumen por voz*",
                "parse_mode": "Markdown",
            }
            r = requests.post(url, data=payload, files=files, timeout=30)
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return r.ok
    except Exception as e:
        logger.error(f"⚠️ Error TTS: {e}")
        if os.path.exists(audio_path):
            os.remove(audio_path)
        return False


async def run():
    parser = argparse.ArgumentParser(description="Send Telegram notification per news item")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-items", type=int, default=5, help="Max news to send per run (default 5)")
    args = parser.parse_args()

    if not CONFIG.get("TELEGRAM_TOKEN") or not CONFIG.get("TELEGRAM_CHAT_ID"):
        logger.warning("⚠️ Configuración de Telegram incompleta. Revisa secrets.")
        return

    logger.info("📱 Iniciando send_telegram.py (por noticia)")
    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    if not historial:
        logger.info("📭 No hay noticias en el histórico.")
        return

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    historial = [n for n in historial if n.get(TIPO_KEY) not in (TIPO_VAL_TREND, TIPO_VAL_SOCIAL)]
    nuevos = [n for n in historial if CACHE.is_new(n.get(ENLACE_KEY, ""))][:args.max_items]
    if not nuevos:
        logger.info("📭 No hay noticias nuevas desde el último envío.")
        return

    logger.info(f"📰 {len(nuevos)} noticias nuevas para enviar.")
    chat_id = CONFIG["TELEGRAM_CHAT_ID"]
    token = CONFIG["TELEGRAM_TOKEN"]
    dashboard_kb = {"inline_keyboard": [[{"text": "🌐 Dashboard", "url": TELEGRAM_DASHBOARD_URL}]]}

    for n in nuevos:
        icono = "📺" if n.get(ID_VIDEO_KEY) else "💻"
        fuente = n[FUENTE_KEY].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        fecha = n.get(FECHA_PUB_KEY) or n.get(F_KEY, "")
        titulo = n[TITULO_KEY].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

        logger.info(f"🤖 Generando resumen para: {n['titulo'][:60]}...")
        resumen = await resumir_noticia(n, client)

        cuerpo = f"📝 {resumen}\n\n" if resumen else f"📝 {titulo}\n\n"
        mensaje = TELEGRAM_MENSAJE_TEMPLATE.format(
            icono=icono, titulo=titulo, fuente=fuente, fecha=fecha,
            cuerpo=cuerpo, enlace=n[ENLACE_KEY], dashboard_url=TELEGRAM_DASHBOARD_URL,
        )

        if args.dry_run:
            print(f"\n{'='*50}")
            print(mensaje)
            logger.info(f"📋 Dry-run: {n['titulo'][:60]}...")
            continue

        ok = enviar_mensaje(mensaje, chat_id, token, dashboard_kb)
        if ok:
            logger.info(f"✅ Enviado: {n['titulo'][:60]}...")
            CACHE.mark_sent(n.get(ENLACE_KEY, ""))
            await asyncio.sleep(1)
            await enviar_audio_voz(f"{icono} {n['titulo']}. {resumen or n['titulo']}", chat_id, token)
            await asyncio.sleep(2)
        else:
            logger.error(f"❌ Fallo al enviar: {n['titulo'][:60]}")

    if not args.dry_run:
        CACHE.flush()

    logger.info("✅ send_telegram.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
