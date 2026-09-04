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
from scripts.utils.constants_downloadfile import CONFIG, TELEGRAM_TTS_VOZ, TELEGRAM_TTS_VOZ_EN, TELEGRAM_DASHBOARD_URL, PROMPT_TRADUCIR_TITULOS, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, FECHA_PUB_KEY, F_KEY, ID_VIDEO_KEY, TS_KEY, NOTICIAS_FILENAME, TELEGRAM_SENT_FILENAME, TELEGRAM_VOICE_SENT_FILENAME, LOGS_DIR, LOG_FILES, FUENTES_INGLES
from scripts.utils.common import load_json, save_json

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(LOGS_DIR, LOG_FILES["telegram"]), maxBytes=1024 * 1024 * 5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("telegram")

SENT_LOG = TELEGRAM_SENT_FILENAME
VOICE_SENT_LOG = TELEGRAM_VOICE_SENT_FILENAME

CACHE = CacheManager(FileCache(SENT_LOG), ttl_hours=168)  # 7 días
VOICE_CACHE = CacheManager(FileCache(VOICE_SENT_LOG), ttl_hours=24)  # 1 día

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


# Palabras comunes en inglés para detección rápida
_ENCOMMON_WORDS = {
    "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would",
    "could", "should", "may", "might", "shall", "can", "need",
    "dare", "ought", "used", "to", "of", "in", "for", "on",
    "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "out", "off",
    "over", "under", "again", "further", "then", "once", "here",
    "there", "when", "where", "why", "how", "all", "both", "each",
    "few", "more", "most", "other", "some", "such", "no", "nor",
    "not", "only", "own", "same", "so", "than", "too", "very",
    "just", "because", "but", "and", "or", "if", "while", "about",
    "up", "it", "its", "this", "that", "these", "those", "what",
    "which", "who", "whom", "new", "first", "last", "long", "great",
    "little", "right", "big", "high", "old", "different", "small",
    "large", "next", "early", "young", "important", "public", "bad",
    "same", "able", "ai", "tech", "startup", "funding", "launch",
    "release", "update", "feature", "app", "data", "cloud", "code",
}


def detectar_idioma(texto: str, fuente: str = "") -> str:
    """Detecta si un texto está en inglés o español.
    Devuelve 'en' para inglés, 'es' para español."""
    texto_lower = texto.lower()
    fuente_lower = fuente.lower().strip()

    # 1) Heurísticas de caracteres españoles (más fuerte que fuente)
    if re.search(r'[áéíóúñ¿¡]', texto_lower):
        return "es"

    # 2) Patrones españoles claros (artículos, preposiciones específicas)
    es_strong = re.findall(r'\b(el|la|los|las|del|al|un|una|unos|unas|por|con|para|que|como|pero|más|también|muy|desde|hasta|según|entre|hacia|sobre|ante|bajo|tras|durante|mediante)\b', texto_lower)
    if len(es_strong) >= 3:
        return "es"

    # 3) Por fuente conocida
    if fuente_lower:
        for f in FUENTES_INGLES:
            if f in fuente_lower:
                return "en"

    # 4) Contar palabras comunes en inglés vs patrones españoles
    words = re.findall(r'\b[a-z]+\b', texto_lower)
    if not words:
        return "es"

    en_count = sum(1 for w in words if w in _ENCOMMON_WORDS)
    en_ratio = en_count / len(words)

    # Patrones españoles comunes
    es_patterns = re.findall(r'\b(el|la|los|las|de|del|en|un|una|por|con|para|que|se|no|lo|al|es|su|ce|yo)\b', texto_lower)
    es_ratio = len(es_patterns) / len(words)

    if en_ratio > 0.35 or (en_ratio > es_ratio and en_ratio > 0.2):
        return "en"
    return "es"


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


async def enviar_audio_voz(titulares: list[tuple[str, str]], chat_id: str, token: str) -> bool:
    """Envía audio de voz: un audio por idioma (ES y EN), cada uno lo más largo posible.
    titulares: lista de (titulo, fuente) para detectar idioma."""
    if not titulares:
        return False

    # Separar TODOS los titulares por idioma (no consecutivos)
    por_idioma = {"es": [], "en": []}
    for titulo, fuente in titulares:
        texto = strip_emojis(titulo)
        if not texto.strip():
            continue
        idioma = detectar_idioma(texto, fuente)
        por_idioma[idioma].append(texto)

    # Filtrar idiomas que tengan contenido
    grupos = [(idioma, textos) for idioma, textos in por_idioma.items() if textos]

    if not grupos:
        logger.info("ℹ️ No hay texto para audio.")
        return False

    logger.info(f"🎙️ Audio: {len(por_idioma['es'])} titulares ES, {len(por_idioma['en'])} titulares EN")
    enviado_ok = True
    total_partes = len(grupos)

    for i, (idioma, oraciones) in enumerate(grupos):
        voz = TELEGRAM_TTS_VOZ_EN if idioma == "en" else TELEGRAM_TTS_VOZ
        lang_label = "EN" if idioma == "en" else "ES"
        texto_parte = ". ".join(oraciones) + "."
        audio_path = f"resumen_diario_{idioma}.mp3"
        try:
            communicate = edge_tts.Communicate(texto_parte, voz)
            await communicate.save(audio_path)
            url = f"https://api.telegram.org/bot{token}/sendVoice"
            with open(audio_path, "rb") as f:
                files = {"voice": (audio_path, f, "audio/mpeg")}
                caption = f"Resumen diario ({lang_label})" if total_partes == 1 else f"Resumen diario ({lang_label}) ({i+1}/{total_partes})"
                payload = {
                    "chat_id": chat_id,
                    "caption": caption,
                }
                r = requests.post(url, data=payload, files=files, timeout=120)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if not r.ok:
                logger.warning(f"⚠️ Audio {lang_label} falló: {r.text[:100]}")
                enviado_ok = False
            else:
                logger.info(f"✅ Audio {lang_label} enviado ({len(oraciones)} titulares, voz: {voz})")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"⚠️ Error TTS {lang_label}: {e}")
            if os.path.exists(audio_path):
                os.remove(audio_path)
            enviado_ok = False

    return enviado_ok


def hoy_ya_se_envio_voz() -> bool:
    """Comprueba si ya se envió el audio de voz hoy."""
    fecha_hoy = datetime.now().strftime("%Y-%m-%d")
    # Intentar leer del CacheManager primero
    try:
        if hasattr(VOICE_CACHE, "_load"):
            datos = VOICE_CACHE._load()
            if isinstance(datos, dict) and datos.get("last_voice_date") == fecha_hoy:
                return True
    except Exception:
        pass
    # Fallback: leer directamente el archivo
    try:
        if os.path.exists(VOICE_SENT_LOG):
            with open(VOICE_SENT_LOG, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, dict) and datos.get("last_voice_date") == fecha_hoy:
                return True
    except (json.JSONDecodeError, OSError):
        pass
    return False


def marcar_voz_enviada(noticias_titles: list[str] | None = None):
    """Marca que se envió el audio de voz, con timestamp y noticias incluidas."""
    datos = {
        "last_voice_date": datetime.now().strftime("%Y-%m-%d"),
        "last_voice_ts": datetime.now().isoformat(),
        "news_count": len(noticias_titles) if noticias_titles else 0,
        "news_titles": (noticias_titles or [])[:50],
    }
    if hasattr(VOICE_CACHE, "_save"):
        VOICE_CACHE._save(datos)
    else:
        with open(VOICE_SENT_LOG, "w") as f:
            json.dump(datos, f)


def obtener_timestamp_ultimo_audio() -> datetime | None:
    """Obtiene el timestamp del último audio enviado."""
    try:
        if hasattr(VOICE_CACHE, "_load"):
            datos = VOICE_CACHE._load()
            if isinstance(datos, dict) and datos.get("last_voice_ts"):
                return datetime.fromisoformat(datos["last_voice_ts"])
    except Exception:
        pass
    try:
        if os.path.exists(VOICE_SENT_LOG):
            with open(VOICE_SENT_LOG, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, dict) and datos.get("last_voice_ts"):
                return datetime.fromisoformat(datos["last_voice_ts"])
    except (json.JSONDecodeError, OSError):
        pass
    return None


async def run():
    parser = argparse.ArgumentParser(description="Send Telegram notifications")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-items", type=int, default=15, help="Max news to send per run (default 15)")
    parser.add_argument("--force-voice", action="store_true", help="Force voice message even if already sent today")
    args = parser.parse_args()

    if not CONFIG.get("TELEGRAM_TOKEN") or not CONFIG.get("TELEGRAM_CHAT_ID"):
        logger.warning("⚠️ Configuración de Telegram incompleta. Revisa secrets.")
        return

    logger.info("📱 Iniciando send_telegram.py")
    path_json = os.path.join(CONFIG["FOLDER"], NOTICIAS_FILENAME)
    historial = load_json(path_json)
    if not historial:
        logger.info("📭 No hay noticias en el histórico.")
        return

    client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))

    # Filtrar noticias recientes (últimas 24h) y que no estén en caché
    from datetime import timedelta
    cutoff = datetime.now() - timedelta(hours=24)
    recientes = []
    for n in historial:
        if n.get(ID_VIDEO_KEY):
            continue
        ts = n.get(TS_KEY, "")
        if ts:
            try:
                fecha = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
                if fecha < cutoff:
                    continue
            except (ValueError, AttributeError):
                pass
        if CACHE.is_new(n.get(ENLACE_KEY, "")):
            recientes.append(n)

    nuevos = recientes[:args.max_items]
    if not nuevos:
        logger.info("📭 No hay noticias nuevas desde el último envío.")
        return

    logger.info(f"📰 {len(nuevos)} noticias nuevas para enviar.")
    chat_id = CONFIG["TELEGRAM_CHAT_ID"]
    token = CONFIG["TELEGRAM_TOKEN"]

    titulares_enviados = []

    for n in nuevos:
        icono = "💻"
        titulo_original = n[TITULO_KEY]

        if n.get('traducido'):
            titulo_es = titulo_original
        else:
            logger.info(f"🤖 Traduciendo: {titulo_original[:60]}...")
            titulo_es = await traducir_titulo(titulo_original, client)
            n['traducido'] = True

        titulo_safe = titulo_es.replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        mensaje = f"{icono} *{titulo_safe}*\n\n[Abrir noticia]({n[ENLACE_KEY]})"

        if args.dry_run:
            print(f"\n{'='*50}")
            print(mensaje)
            logger.info(f"📋 Dry-run: {titulo_es[:60]}...")
            continue

        ok = enviar_mensaje(mensaje, chat_id, token)
        if ok:
            logger.info(f"✅ Enviado: {titulo_es[:60]}...")
            CACHE.mark_sent(n.get(ENLACE_KEY, ""))
            titulares_enviados.append(titulo_es)
            await asyncio.sleep(1)
        else:
            logger.error(f"❌ Fallo al enviar: {titulo_es[:60]}")

    # Audio de voz: 1 vez al día con resumen de TODAS las noticias desde el último audio
    if not args.dry_run:
        hora_actual = datetime.now().hour
        if args.force_voice or (not hoy_ya_se_envio_voz() and hora_actual >= 21):
            # Recopilar TODAS las noticias desde el último audio enviado
            ts_ultimo_audio = obtener_timestamp_ultimo_audio()
            if ts_ultimo_audio:
                cutoff_voz = ts_ultimo_audio
                logger.info(f"🎙️ Buscando noticias desde último audio: {ts_ultimo_audio.strftime('%Y-%m-%d %H:%M')}")
            else:
                cutoff_voz = datetime.now() - timedelta(hours=24)
                logger.info("🎙️ No hay audio previo, usando últimas 24h")
            todas_hoy = []
            for n in historial:
                if n.get(ID_VIDEO_KEY):
                    continue
                ts = n.get(TS_KEY, "")
                if ts:
                    try:
                        fecha = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
                        if fecha < cutoff_voz:
                            continue
                    except (ValueError, AttributeError):
                        pass
                titulo = n.get(TITULO_KEY, "")
                fuente = n.get(FUENTE_KEY, "")
                if titulo:
                    todas_hoy.append((titulo, fuente))

            if todas_hoy:
                logger.info(f"🎙️ Enviando resumen de voz diario ({len(todas_hoy)} noticias)...")
                ok = await enviar_audio_voz(todas_hoy, chat_id, token)
                if ok:
                    marcar_voz_enviada([t for t, _ in todas_hoy[:50]])
                    logger.info("✅ Audio de voz enviado.")
                else:
                    logger.warning("⚠️ Fallo al enviar audio de voz.")
            else:
                logger.info("ℹ️ No hay noticias hoy para audio.")
        elif hoy_ya_se_envio_voz():
            logger.info("ℹ️ Audio de voz ya enviado hoy. Saltando.")
        else:
            logger.info(f"ℹ️ Audio de voz se enviará a las 21:00 (hora actual: {hora_actual}:00).")

    if not args.dry_run:
        CACHE.flush()
        save_json(path_json, historial)

    logger.info("✅ send_telegram.py completado.")


if __name__ == "__main__":
    asyncio.run(run())
