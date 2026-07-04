#!/usr/bin/env python3
"""
send_telegram.py — Envía noticias por Telegram con resumen IA.
Envía noticias individuales como texto. Audio TTS una vez al día como resumen.

Uso:
    python send_telegram.py                          # Envía noticias nuevas
    python send_telegram.py --dry-run                # Muestra sin enviar
    python send_telegram.py --force-voice            # Fuerza envío de audio
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
from scripts.utils.constants_downloadfile import CONFIG, TELEGRAM_TTS_VOZ, TELEGRAM_DASHBOARD_URL, TELEGRAM_MENSAJE_TEMPLATE, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, FECHA_PUB_KEY, F_KEY, ID_VIDEO_KEY
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
VOICE_SENT_LOG = "telegram_voice_sent.json"

CACHE = CacheManager(FileCache(SENT_LOG))
VOICE_CACHE = CacheManager(FileCache(VOICE_SENT_LOG))

# Emojis para stripping del texto de voz
EMOJI_PATTERN = re.compile(
    "[\U0001F600-\U0001F64F"
    "\U0001F300-\U0001F5FF"
    "\U0001F680-\U0001F6FF"
    "\U0001F1E0-\U0001F1FF"
    "\U00002702-\U000027B0"
    "\U000024C2-\U0001F251"
    "\U0001f926-\U0001f937"
    "\U00010000-\U0010ffff"
    "\u200d\u2640-\u2642\u2600-\u2B55\u23cf\u23e9\u231a\ufe0f\u3030]+",
    flags=re.UNICODE,
)


def strip_emojis(text: str) -> str:
    return EMOJI_PATTERN.sub("", text).strip()


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


async def enviar_audio_voz(texto: str, chat_id: str, token: str) -> bool:
    audio_path = "resumen_diario.mp3"
    voz = TELEGRAM_TTS_VOZ
    texto_limpio = strip_emojis(texto)
    if len(texto_limpio) > 800:
        texto_limpio = texto_limpio[:800] + "..."
    try:
        communicate = edge_tts.Communicate(texto_limpio, voz)
        await communicate.save(audio_path)
        url = f"https://api.telegram.org/bot{token}/sendVoice"
        with open(audio_path, "rb") as f:
            files = {"voice": (audio_path, f, "audio/mpeg")}
            payload = {
                "chat_id": chat_id,
                "caption": "Resumen diario por voz",
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


def hoy_ya_se_envio_voz() -> bool:
    """Comprueba si ya se envió el audio de voz hoy."""
    datos = VOICE_CACHE._load() if hasattr(VOICE_CACHE, "_load") else {}
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    return datos.get("last_voice_date") == fecha_hoy


def marcar_voz_enviada():
    """Marca que se envió el audio de voz hoy."""
    if hasattr(VOICE_CACHE, "_save"):
        VOICE_CACHE._save({"last_voice_date": datetime.now().strftime("%Y-%m-%d")})
    else:
        with open(VOICE_SENT_LOG, "w") as f:
            json.dump({"last_voice_date": datetime.now().strftime("%Y-%m-%d")}, f)


async def run():
    parser = argparse.ArgumentParser(description="Send Telegram notifications")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-items", type=int, default=5, help="Max news to send per run (default 5)")
    parser.add_argument("--force-voice", action="store_true", help="Force voice message even if already sent today")
    args = parser.parse_args()

    if not CONFIG.get("TELEGRAM_TOKEN") or not CONFIG.get("TELEGRAM_CHAT_ID"):
        logger.warning("⚠️ Configuración de Telegram incompleta. Revisa secrets.")
        return

    logger.info("📱 Iniciando send_telegram.py")
    path_json = os.path.join(CONFIG["FOLDER"], "noticias_historico.json")
    historial = load_json(path_json)
    if not historial:
        logger.info("📭 No hay noticias en el histórico.")
        return

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    nuevos = [n for n in historial if CACHE.is_new(n.get(ENLACE_KEY, ""))][:args.max_items]
    if not nuevos:
        logger.info("📭 No hay noticias nuevas desde el último envío.")
        return

    logger.info(f"📰 {len(nuevos)} noticias nuevas para enviar.")
    chat_id = CONFIG["TELEGRAM_CHAT_ID"]
    token = CONFIG["TELEGRAM_TOKEN"]
    dashboard_kb = {"inline_keyboard": [[{"text": "Dashboard", "url": TELEGRAM_DASHBOARD_URL}]]}

    titulares_enviados = []

    for n in nuevos:
        icono = "📺" if n.get(ID_VIDEO_KEY) else "💻"
        fuente = n[FUENTE_KEY].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        titulo = n[TITULO_KEY].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")

        logger.info(f"🤖 Generando resumen para: {n['titulo'][:60]}...")
        resumen = await resumir_noticia(n, client)

        cuerpo = f"{resumen}\n\n" if resumen else ""
        mensaje = f"{icono} *{titulo}*\n`{fuente}`\n\n{cuerpo}[Abrir noticia]({n[ENLACE_KEY]})"

        if args.dry_run:
            print(f"\n{'='*50}")
            print(mensaje)
            logger.info(f"📋 Dry-run: {n['titulo'][:60]}...")
            continue

        ok = enviar_mensaje(mensaje, chat_id, token, dashboard_kb)
        if ok:
            logger.info(f"✅ Enviado: {n['titulo'][:60]}...")
            CACHE.mark_sent(n.get(ENLACE_KEY, ""))
            titulares_enviados.append(n[TITULO_KEY])
            await asyncio.sleep(1)
        else:
            logger.error(f"❌ Fallo al enviar: {n['titulo'][:60]}")

    # Audio de voz: 1 vez al día con resumen de todos los titulares
    if not args.dry_run and titulares_enviados:
        if args.force_voice or not hoy_ya_se_envio_voz():
            resumen_voz = "Hoy en tecnología. " + ". ".join(titulares_enviados) + ". Fin del resumen."
            logger.info("🎙️ Enviando resumen de voz diario...")
            ok = await enviar_audio_voz(resumen_voz, chat_id, token)
            if ok:
                marcar_voz_enviada()
                logger.info("✅ Audio de voz enviado.")
            else:
                logger.warning("⚠️ Fallo al enviar audio de voz.")
        else:
            logger.info("ℹ️ Audio de voz ya enviado hoy. Saltando.")

    if not args.dry_run:
        CACHE.flush()

    logger.info("✅ send_telegram.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
