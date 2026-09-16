"""
imdb_parental.py — SRP: vigila las fichas de Guía Parental de IMDb y notifica
si el texto scrapeado cambia entre ejecuciones.

Separado como módulo independiente para reutilizarse
en cualquier scraper que necesite monitorizar páginas de parental de IMDb.

Uso:
    from imdb_parental import IMDBParentalMonitor

    monitor = IMDBParentalMonitor(urls=..., path=..., headers=HEADERS)
    monitor.comprobar(dry_run=False)

El envío a Telegram usa un `TelegramClient` inyectado (DIP); por defecto lee
BOT_TOKEN/CHAT_ID de las variables de entorno al construir.
"""
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.telegram_client import TelegramClient

import movie_scraper_base as base


_IMDB_PARENTAL_ANCHORES = {
    "sex": "Sex & Nudity",
    "violence": "Violence & Gore",
    "profanity": "Profanity",
    "alcohol": "Alcohol, Drugs & Smoking",
    "intense": "Frightening & Intense Scenes",
    "frightening": "Frightening & Intense Scenes",
    "certificate": "Certificate",
    "certificates": "Certificaciones",
}
_IMDB_PARENTAL_BOILER = {
    "añadir un producto", "no data", "no voting data votar", "votar", "editar", "",
}


class IMDBParentalMonitor:
    """Vigila N fichas de Guía Parental de IMDb. Por cada una, si el texto
    scrapeado cambia respecto al último snapshot (almacenado en `path`),
    envía 1 mensaje a Telegram. La primera ejecución solo fija la línea base."""

    def __init__(self, urls: list, path: Path, headers: dict = None,
                 bot_token: str = "", chat_id: str = "", client: TelegramClient = None):
        self.urls = urls
        self.path = path
        self.headers = headers or base.HEADERS
        self.bot_token = bot_token or os.environ.get("TIPS_BOT_TOKEN", "")
        self.chat_id = chat_id or os.environ.get("SALUDO_CHAT_ID", os.environ.get("TIPS_CHAT_ID", ""))
        self.client = client or TelegramClient(bot_token=self.bot_token, chat_id=self.chat_id)

    def _fetch(self, url: str):
        """Devuelve (titulo, texto) o None si no se pudo leer."""
        def _obtener():
            try:
                r = requests.get(url, timeout=20, headers={
                    **self.headers,
                    "Accept-Language": "es-ES,es;q=0.9",
                })
                if r.status_code == 200 and len(r.text) > 3000:
                    return r.text
            except Exception:
                pass
            try:
                # jina devuelve la página como texto; usa headers por defecto porque
                # con nuestros headers de navegador responde 403.
                r = requests.get(f"https://r.jina.ai/{url}", timeout=40)
                if r.status_code == 200 and len(r.text) > 1000:
                    return r.text
            except Exception:
                pass
            return None

        body = _obtener()
        if not body:
            return None

        titulo = ""
        m = re.search(r"Title:\s*(.+?)(?:\s*-\s*Guía|$)", body)
        if m:
            titulo = m.group(1).strip()

        texto = self._extraer_parental(body)
        return titulo, texto

    @staticmethod
    def _extraer_parental(body: str) -> str:
        i = body.find("Markdown Content:")
        if i != -1:
            body = body[i + len("Markdown Content:"):]
        patron = re.compile(
            r"## \[([^\]]+)\]\((?:[^)]*#([a-z]+).*?)\)\n\n(.*?)(?=\n\n## |\Z)",
            re.S,
        )
        secciones = []
        for m in patron.finditer(body):
            titulo, anchor, contenido = m.group(1), m.group(2), m.group(3)
            if anchor not in _IMDB_PARENTAL_ANCHORES:
                continue
            lineas = [
                ln.strip()
                for ln in contenido.split("\n")
                if ln.strip().lower() not in _IMDB_PARENTAL_BOILER
            ]
            texto = "\n".join(lineas).strip()
            if texto:
                secciones.append(f"{_IMDB_PARENTAL_ANCHORES[anchor]}:\n{texto}")
        return "\n\n".join(secciones).strip()

    def _send_telegram_plain(self, mensaje: str) -> bool:
        if not self.client.bot_token or not self.client.chat_id:
            print("⚠️  TIPS_BOT_TOKEN / SALUDO_CHAT_ID no configurados; no se envía.")
            return False
        try:
            r = self.client.send_message(mensaje, parse_mode=None, timeout=60)
            return r is not None and r.status_code == 200
        except Exception:
            return False

    def comprobar(self, dry_run: bool = False):
        """Escanea todas las URLs vigiladas, guarda el snapshot, y envía a
        Telegram solo si el texto ha cambiado respecto a la ejecución anterior."""
        estado = {}
        if self.path.exists():
            try:
                estado = json.loads(self.path.read_text(encoding="utf-8"))
            except Exception:
                estado = {}

        cambios = []
        for url in self.urls:
            anterior = estado.get(url)
            obtenido = self._fetch(url)
            if not obtenido:
                print(f"  ⚠️  IMDb Parental sin leer ({url}) — se conserva el snapshot previo.")
                continue
            titulo, texto = obtenido
            if not texto:
                continue
            if anterior is not None and texto != anterior.get("texto", ""):
                cambios.append((url, titulo, texto))
            estado[url] = {"texto": texto, "actualizado": datetime.now().isoformat()}

        if not dry_run:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps(estado, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        if dry_run:
            if cambios:
                print(f"  🔎 dry-run: {len(cambios)} cambio(s) detectado(s) — no se envía.")
            return

        for url, titulo, texto in cambios:
            mensaje = (
                f"🆕 CAMBIO en la ficha IMDb (Guía Parental)\n"
                f"{titulo or url}\n{url}\n\n{texto[:3500]}"
            )
            if len(texto) > 3500:
                mensaje += "\n\n_(texto truncado)_"
            if self._send_telegram_plain(mensaje):
                print(f"✅ Enviado a Telegram el cambio de {url}")
            else:
                print(f"❌ Telegram: falló el envío del cambio de {url}")
        if not cambios:
            print("✅ Guía Parental IMDb: sin cambios en las 2 fichas.")