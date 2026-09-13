"""
telegram_client.py — Transporte único para la Bot API de Telegram (SRP).
Encapsula URL, sesión HTTP y peticiones (texto, foto, voz) usando `requests`.
Los llamadores deciden qué enviar y cómo tratar la respuesta (`requests.Response`).
"""

import json
import os
from pathlib import Path

import requests


class TelegramClient:
    """Cliente HTTP del Bot API de Telegram (principio de responsabilidad única:
    solo se encarga del transporte; no define contenido ni políticas de envío).

    `bot_token`/`chat_id` opcionales se usan como valores por defecto cuando la
    llamada no los suministra explícitamente.
    """

    API_BASE = "https://api.telegram.org/bot{token}/{method}"

    def __init__(self, bot_token: str = "", chat_id: str = ""):
        self.bot_token = bot_token or ""
        self.chat_id = chat_id or ""
        self._session = requests.Session()

    # ── Transporte base ──────────────────────────────────────────────────────

    def _post(self, method: str, data: dict | None = None, files: dict | None = None,
              timeout: int = 30, chat_id: str | None = None, token: str | None = None):
        """Envía la petición al método indicado. Devuelve `requests.Response` o
        `None` si faltan token o chat_id."""
        token = token or self.bot_token
        chat_id = chat_id or self.chat_id
        if not token or not chat_id:
            return None
        body = dict(data or {})
        body["chat_id"] = chat_id
        url = self.API_BASE.format(token=token, method=method)
        return self._session.post(url, data=body or None, files=files, timeout=timeout)

    # ── Métodos del Bot API ──────────────────────────────────────────────────

    def send_message(self, text: str, *, chat_id: str | None = None, token: str | None = None,
                     parse_mode: str | None = "Markdown", reply_markup: dict | None = None,
                     disable_web_page_preview: bool = False, timeout: int = 30):
        body = {
            "text": text,
            "disable_web_page_preview": disable_web_page_preview,
        }
        if parse_mode:
            body["parse_mode"] = parse_mode
        if reply_markup is not None:
            body["reply_markup"] = json.dumps(reply_markup, ensure_ascii=False)
        return self._post("sendMessage", body, timeout=timeout, chat_id=chat_id, token=token)

    def send_photo(self, photo, caption: str | None = None, *, chat_id: str | None = None,
                   token: str | None = None, parse_mode: str = "Markdown", timeout: int = 60):
        """Envía una foto. `photo` puede ser una URL (str) o una tupla
        `(filename, bytes, content_type)` para subir contenido binario."""
        if isinstance(photo, str):
            body = {"photo": photo}
            files = None
        else:
            body = {}
            files = {"photo": photo}
        if caption is not None:
            body["caption"] = caption
            if parse_mode:
                body["parse_mode"] = parse_mode
        return self._post("sendPhoto", body, files=files, timeout=timeout, chat_id=chat_id, token=token)

    def send_voice(self, audio_path: str, caption: str | None = None, *,
                   chat_id: str | None = None, token: str | None = None, timeout: int = 120):
        """Envía un audio de voz. Abre y cierra el fichero; el llamador puede
        borrarlo después sin problemas de descriptores abiertos."""
        audio_path = Path(audio_path)
        body: dict = {}
        if caption is not None:
            body["caption"] = caption
        with audio_path.open("rb") as f:
            files = {"voice": (audio_path.name, f, "audio/mpeg")}
            return self._post("sendVoice", body, files=files, timeout=timeout, chat_id=chat_id, token=token)