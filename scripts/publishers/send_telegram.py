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
import sys
from datetime import datetime, timedelta
from html import escape as esc_html
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.logging_setup import setup_logging
from utils.cache import CacheManager, FileCache
from utils.telegram_client import TelegramClient
from utils.constants_downloadfile import CONFIG, TELEGRAM_TTS_VOZ, TELEGRAM_TTS_VOZ_EN, TELEGRAM_DASHBOARD_URL, PROMPT_TRADUCIR_TITULOS, ENLACE_KEY, FUENTE_KEY, TITULO_KEY, FECHA_PUB_KEY, F_KEY, ID_VIDEO_KEY, TS_KEY, NOTICIAS_FILENAME, TELEGRAM_SENT_FILENAME, TELEGRAM_VOICE_SENT_FILENAME, LOGS_DIR, LOG_FILES, FUENTES_INGLES
from utils.common import load_json, save_json
from utils.fechas import texto_es_reciente, MADRID
from utils.disponibilidad import filtrar_disponibles, log_descartes

logger = setup_logging("telegram", LOG_FILES["telegram"], LOGS_DIR)

SENT_LOG = TELEGRAM_SENT_FILENAME
VOICE_SENT_LOG = TELEGRAM_VOICE_SENT_FILENAME

# Límites del resumen de voz (evita HTTP 413 de Telegram con audios gigantes)
VOICE_MAX_POR_IDIOMA = 40
VOICE_MAX_CHARS_IDIOMA = 3500
VOICE_MAX_LOOKBACK_H = 48

CACHE = CacheManager(FileCache(SENT_LOG), ttl_hours=168)  # 7 días
_client = TelegramClient()

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
    """Traduce un título al español. Fallback: Gemini → Telegram translate."""
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
    # Fallback: Telegram translate
    try:
        from utils.telegram_translate import translate_to_spanish
        result = await translate_to_spanish(titulo)
        if result:
            return result
    except Exception:
        pass
    return titulo


def construir_mensaje_noticia(titulo: str, url: str) -> tuple:
    """Devuelve (html, plano) para una noticia del reporte tech.

    - html: parse_mode HTML → «Abrir noticia» es un <a href> azul clicable
      (nunca la URL cruda entre paréntesis).
    - plano: fallback sin parse_mode si Telegram rechaza el HTML.
    """
    titulo = titulo or ""
    url = url or ""
    html = f'💻 <b>{esc_html(titulo)}</b>\n\n<a href="{esc_html(url, quote=True)}">Abrir noticia</a>'
    plano = f"💻 {titulo}\n\n{url}"
    return html, plano


def enviar_mensaje(texto: str, chat_id: str, token: str,
                   reply_markup: dict | None = None,
                   texto_plano: str | None = None) -> bool:
    try:
        r = _client.send_message(
            texto, chat_id=chat_id, token=token,
            parse_mode="HTML", disable_web_page_preview=False,
            reply_markup=reply_markup, timeout=15,
        )
        if r is None:
            return False
        if r.ok:
            return True
        logger.warning(f"⚠️ Telegram error (HTML): {r.text}")
        fallback = texto_plano if texto_plano is not None else re.sub(r'<[^>]+>', '', texto)
        r = _client.send_message(
            fallback, chat_id=chat_id, token=token,
            parse_mode=None, disable_web_page_preview=False,
            timeout=15,
        )
        return bool(r is not None and r.ok)
    except Exception as e:
        logger.error(f"❌ Error enviando mensaje: {e}")
        return False


def _limitar_oraciones(oraciones: list[str]) -> list[str]:
    """Recorta a VOICE_MAX_POR_IDIOMA y VOICE_MAX_CHARS_IDIOMA (más largos primero)."""
    seleccion: list[str] = []
    chars = 0
    for texto in oraciones:
        if len(seleccion) >= VOICE_MAX_POR_IDIOMA:
            break
        # +2 por el ". " de unión
        if seleccion and chars + len(texto) + 2 > VOICE_MAX_CHARS_IDIOMA:
            continue
        seleccion.append(texto)
        chars += len(texto) + (2 if seleccion[:-1] else 0)
    return seleccion


async def enviar_audio_voz(titulares: list[tuple[str, str]], chat_id: str, token: str) -> int:
    """Envía audio de voz: un audio por idioma (ES y EN), con tope de tamaño.

    titulares: lista de (titulo, fuente) para detectar idioma.
    Devuelve el nº de idiomas enviados correctamente (0 = fallo total)."""
    if not titulares:
        return 0
    import edge_tts

    # Separar titulares por idioma (no consecutivos)
    por_idioma = {"es": [], "en": []}
    for titulo, fuente in titulares:
        texto = strip_emojis(titulo)
        if not texto.strip():
            continue
        idioma = detectar_idioma(texto, fuente)
        por_idioma[idioma].append(texto)

    # Tope por idioma: evita MP3 de horas y HTTP 413
    for idioma in por_idioma:
        antes = len(por_idioma[idioma])
        por_idioma[idioma] = _limitar_oraciones(por_idioma[idioma])
        if antes > len(por_idioma[idioma]):
            logger.info(
                f"✂️ Audio {idioma.upper()}: {antes} → {len(por_idioma[idioma])} titulares (tope)"
            )

    grupos = [(idioma, textos) for idioma, textos in por_idioma.items() if textos]

    if not grupos:
        logger.info("ℹ️ No hay texto para audio.")
        return 0

    logger.info(f"🎙️ Audio: {len(por_idioma['es'])} titulares ES, {len(por_idioma['en'])} titulares EN")
    enviados = 0
    total_partes = len(grupos)

    for i, (idioma, oraciones) in enumerate(grupos):
        voz = TELEGRAM_TTS_VOZ_EN if idioma == "en" else TELEGRAM_TTS_VOZ
        lang_label = "EN" if idioma == "en" else "ES"
        texto_parte = ". ".join(oraciones) + "."
        audio_path = f"resumen_diario_{idioma}.mp3"
        try:
            communicate = edge_tts.Communicate(texto_parte, voz)
            await communicate.save(audio_path)
            caption = f"Resumen diario ({lang_label})" if total_partes == 1 else f"Resumen diario ({lang_label}) ({i+1}/{total_partes})"
            r = _client.send_voice(audio_path, caption, chat_id=chat_id, token=token, timeout=120)
            if os.path.exists(audio_path):
                os.remove(audio_path)
            if r is None or not r.ok:
                logger.warning(f"⚠️ Audio {lang_label} falló: {r.text[:100] if r is not None else 'sin token/chat'}")
            else:
                enviados += 1
                logger.info(f"✅ Audio {lang_label} enviado ({len(oraciones)} titulares, voz: {voz})")
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"⚠️ Error TTS {lang_label}: {e}")
            if os.path.exists(audio_path):
                os.remove(audio_path)

    return enviados


def _leer_estado_voz() -> dict:
    """Lee el estado del audio de voz (last_voice_date / last_voice_ts / …)."""
    try:
        if os.path.exists(VOICE_SENT_LOG):
            with open(VOICE_SENT_LOG, "r", encoding="utf-8") as f:
                datos = json.load(f)
            if isinstance(datos, dict):
                return datos
    except (json.JSONDecodeError, OSError):
        pass
    return {}


def _escribir_estado_voz(datos: dict) -> None:
    """Persiste el estado del audio de voz de forma atómica."""
    tmp = VOICE_SENT_LOG + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    os.replace(tmp, VOICE_SENT_LOG)


def hoy_ya_se_envio_voz() -> bool:
    """Comprueba si ya se envió el audio de voz hoy (fecha en hora Madrid)."""
    fecha_hoy = datetime.now(MADRID).strftime("%Y-%m-%d")
    return _leer_estado_voz().get("last_voice_date") == fecha_hoy


def marcar_voz_enviada(noticias_titles: list[str] | None = None):
    """Marca que se envió el audio de voz, con timestamp y noticias incluidas."""
    ahora = datetime.now(MADRID)
    datos = _leer_estado_voz()
    datos.update({
        "last_voice_date": ahora.strftime("%Y-%m-%d"),
        "last_voice_ts": ahora.isoformat(),
        "news_count": len(noticias_titles) if noticias_titles else 0,
        "news_titles": (noticias_titles or [])[:50],
    })
    _escribir_estado_voz(datos)


def obtener_timestamp_ultimo_audio() -> datetime | None:
    """Obtiene el timestamp del último audio enviado."""
    ts = _leer_estado_voz().get("last_voice_ts")
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts)
    except (ValueError, TypeError):
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

    try:
        from google import genai
        client = genai.Client(api_key=CONFIG.get("GEMINI_KEY"))
    except Exception as e:
        logger.warning(f"⚠️ Gemini no disponible ({e}); se usarán títulos originales")
        client = None

    # Filtrar noticias recientes: publicación ≤24 h (no basta con que se haya
    # scrapeado hoy) y que no estén en caché
    cutoff = datetime.now() - timedelta(hours=24)
    recientes = []
    viejas = 0
    for n in historial:
        if n.get(ID_VIDEO_KEY):
            continue
        if texto_es_reciente(n.get(FECHA_PUB_KEY, "")) is False:
            viejas += 1
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
    if viejas:
        logger.info(f"🗓️ {viejas} noticias descartadas: publicadas con más de 24 h.")

    # Enlaces vivos: solo se envían noticias cuya URL responde
    recientes, muertos = filtrar_disponibles(recientes, campo=ENLACE_KEY)
    log_descartes(muertos)

    chat_id = CONFIG["TELEGRAM_CHAT_ID"]
    token = CONFIG["TELEGRAM_TOKEN"]

    nuevos = recientes[:args.max_items]
    if nuevos:
        logger.info(f"📰 {len(nuevos)} noticias nuevas para enviar.")
        titulares_enviados = []

        for n in nuevos:
            titulo_original = n[TITULO_KEY]

            if n.get('traducido'):
                titulo_es = titulo_original
            else:
                logger.info(f"🤖 Traduciendo: {titulo_original[:60]}...")
                titulo_es = await traducir_titulo(titulo_original, client)
                n['traducido'] = True

            mensaje, mensaje_plano = construir_mensaje_noticia(titulo_es, n[ENLACE_KEY])

            if args.dry_run:
                print(f"\n{'='*50}")
                print(mensaje)
                logger.info(f"📋 Dry-run: {titulo_es[:60]}...")
                continue

            ok = enviar_mensaje(mensaje, chat_id, token, texto_plano=mensaje_plano)
            if ok:
                logger.info(f"✅ Enviado: {titulo_es[:60]}...")
                CACHE.mark_sent(n.get(ENLACE_KEY, ""))
                titulares_enviados.append(titulo_es)
                await asyncio.sleep(1)
            else:
                logger.error(f"❌ Fallo al enviar: {titulo_es[:60]}")
    else:
        logger.info("📭 No hay noticias nuevas desde el último envío.")

    # Audio de voz: 1 vez al día con resumen de TODAS las noticias desde el
    # último audio. Independiente de si hay noticias nuevas de texto (antes un
    # `return` temprano impedía llegar aquí cuando todo ya estaba en caché).
    if not args.dry_run:
        try:
            hora_actual = datetime.now(MADRID).hour
            # Ventana 19:00–23:59 Madrid (antes solo ≥21: casi ningún run de
            # Actions caía ahí y el audio no salía).
            if args.force_voice or (not hoy_ya_se_envio_voz() and hora_actual >= 19):
                # Recopilar noticias desde el último audio, con tope de ventana
                # para no acumular semanas enteras (→ MP3 gigante → HTTP 413).
                # cutoff naive para poder comparar con TS_KEY (se parsea sin tz).
                ts_ultimo_audio = obtener_timestamp_ultimo_audio()
                cutoff_min = datetime.now() - timedelta(hours=VOICE_MAX_LOOKBACK_H)
                if ts_ultimo_audio:
                    if ts_ultimo_audio.tzinfo is not None:
                        # A hora local naive del sistema (UTC en Actions) para
                        # comparar con TS_KEY / datetime.now() sin tz.
                        ts_ultimo_audio = ts_ultimo_audio.astimezone().replace(tzinfo=None)
                    cutoff_voz = max(ts_ultimo_audio, cutoff_min)
                    if cutoff_voz > ts_ultimo_audio:
                        logger.info(
                            f"🎙️ Último audio antiguo; limitando búsqueda a {VOICE_MAX_LOOKBACK_H} h"
                        )
                    logger.info(f"🎙️ Buscando noticias desde último audio: {ts_ultimo_audio.strftime('%Y-%m-%d %H:%M')}")
                else:
                    cutoff_voz = cutoff_min
                    logger.info("🎙️ No hay audio previo, usando últimas 24h")
                candidatos_voz = []
                for n in historial:
                    if n.get(ID_VIDEO_KEY):
                        continue
                    if texto_es_reciente(n.get(FECHA_PUB_KEY, "")) is False:
                        continue
                    ts = n.get(TS_KEY, "")
                    if ts:
                        try:
                            fecha = datetime.fromisoformat(ts.replace("Z", "+00:00").replace("+00:00", ""))
                            if fecha < cutoff_voz:
                                continue
                        except (ValueError, AttributeError):
                            pass
                    if n.get(TITULO_KEY):
                        candidatos_voz.append(n)

                # Enlaces vivos también para el resumen de voz
                vivos_voz, muertos_voz = filtrar_disponibles(candidatos_voz, campo=ENLACE_KEY)
                if muertos_voz:
                    log_descartes(muertos_voz, contexto="noticias de voz")
                # Más recientes primero (histórico puede no venir ordenado)
                def _ts_n(n: dict) -> str:
                    return n.get(TS_KEY, "") or n.get(FECHA_PUB_KEY, "") or ""
                vivos_voz.sort(key=_ts_n, reverse=True)
                todas_hoy = [(v[TITULO_KEY], v.get(FUENTE_KEY, "")) for v in vivos_voz]

                if todas_hoy:
                    logger.info(f"🎙️ Enviando resumen de voz diario ({len(todas_hoy)} noticias)...")
                    enviados = await enviar_audio_voz(todas_hoy, chat_id, token)
                    if enviados > 0:
                        # Basta un idioma OK para no reintentar y acumular más
                        marcar_voz_enviada([t for t, _ in todas_hoy[:50]])
                        logger.info(f"✅ Audio de voz enviado ({enviados} idioma(s)).")
                    else:
                        logger.warning("⚠️ Fallo al enviar audio de voz.")
                else:
                    logger.info("ℹ️ No hay noticias hoy para audio.")
            elif hoy_ya_se_envio_voz():
                logger.info("ℹ️ Audio de voz ya enviado hoy. Saltando.")
            else:
                logger.info(f"ℹ️ Audio de voz se enviará a partir de las 19:00 (hora actual: {hora_actual}:00).")
        except Exception:
            # Un fallo del TTS/audio no debe impedir flush de textos ya enviados
            logger.exception("⚠️ Error inesperado en el bloque de audio de voz.")

    if not args.dry_run:
        CACHE.flush()
        save_json(path_json, historial)

    logger.info("✅ send_telegram.py completado.")


if __name__ == "__main__":
    asyncio.run(run())