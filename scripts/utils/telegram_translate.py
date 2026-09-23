"""
telegram_translate.py — Fallback de traducción usando la API MTProto de Telegram.
Usa messages.translateText (disponible solo vía Telethon, no Bot API).

Requiere secrets en GitHub Actions:
  - TG_API_ID
  - TG_API_HASH
  - TG_SESSION_STRING
"""

import asyncio
import logging
import os

logger = logging.getLogger(__name__)

_api_id = int(os.environ.get("TG_API_ID", "0"))
_api_hash = os.environ.get("TG_API_HASH", "")
_session_string = os.environ.get("TG_SESSION_STRING", "")

_client = None


async def _get_client():
    """Devuelve un cliente Telethon reutilizado (lazy init)."""
    global _client
    if _client is not None:
        return _client
    if not _api_id or not _api_hash or not _session_string:
        logger.debug("Telegram translate: secrets no configurados, saltando")
        return None
    try:
        from telethon import TelegramClient
        from telethon.sessions import StringSession
        _client = TelegramClient(StringSession(_session_string), _api_id, _api_hash)
        await _client.connect()
        if not await _client.is_user_authorized():
            logger.warning("Telegram translate: sesión no autorizada")
            await _client.disconnect()
            _client = None
            return None
        return _client
    except Exception as e:
        logger.warning(f"Telegram translate: error inicializando cliente: {e}")
        _client = None
        return None


async def translate_to_spanish(text: str) -> str | None:
    """Traduce texto al español usando messages.translateText de Telegram.

    Devuelve el texto traducido o None si falla.
    """
    if not text or not text.strip():
        return None

    client = await _get_client()
    if client is None:
        return None

    try:
        from telethon import functions, types
        text_obj = types.TextWithEntities(text=text.strip(), entities=[])
        result = await client(functions.messages.TranslateTextRequest(
            text=[text_obj],
            to_lang="es"
        ))
        if result and result.result:
            translated = result.result[0].text
            if translated and translated.strip():
                return translated.strip()
    except Exception as e:
        logger.warning(f"Telegram translate: error traduciendo: {e}")

    return None


async def translate_batch(texts: list[str]) -> list[str]:
    """Traduce una lista de textos al español.

    Devuelve lista con textos traducidos o originales si falla.
    """
    client = await _get_client()
    if client is None:
        return texts

    try:
        from telethon import functions, types
        text_objs = [
            types.TextWithEntities(text=t.strip(), entities=[])
            for t in texts if t and t.strip()
        ]
        if not text_objs:
            return texts

        result = await client(functions.messages.TranslateTextRequest(
            text=text_objs,
            to_lang="es"
        ))

        translated_map = {}
        for item in result.result:
            if item.text:
                translated_map[item.text] = item.text

        return [
            translated_map.get(t.strip(), t)
            for t in texts
        ]
    except Exception as e:
        logger.warning(f"Telegram translate batch: error: {e}")
        return texts
