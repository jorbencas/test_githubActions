#!/usr/bin/env python3
"""
cache.py — Sistema de caché reutilizable con backend pluggable (SOLID).

Interfaces:
  ICacheBackend   — abstracción de persistencia (archivo, Redis, n8n webhook)
  CacheManager    — orquestador con TTL opcional y estrategia de clave

Backends concretos:
  FileCache       — JSON plano en disco
  N8nCache        — esqueleto para migración a n8n (vía webhook)

Uso:
  from cache import CacheManager, FileCache
  cache = CacheManager(FileCache("telegram_sent.json"), ttl_hours=48)
  if cache.is_new(item[ENLACE_KEY]):
      cache.mark_sent(item[ENLACE_KEY])
  cache.flush()
"""

import json
import logging
import os
from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Any

from scripts.utils.constants_downloadfile import ENLACE_KEY, TS_KEY

logger = logging.getLogger(__name__)


class ICacheBackend(ABC):
    """Backend de persistencia para el caché."""

    @abstractmethod
    def load(self) -> dict[str, Any]:
        """Carga todo el caché desde el backend."""

    @abstractmethod
    def save(self, data: dict[str, Any]):
        """Persiste el caché completo en el backend."""


class FileCache(ICacheBackend):
    """Backend que persiste en un archivo JSON."""

    def __init__(self, path: str):
        self.path = path
        self._data: dict[str, Any] | None = None
        self._dirty = False

    def load(self) -> dict[str, Any]:
        if self._data is not None:
            return self._data
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    raw = json.load(f)
                if isinstance(raw, list):
                    logger.warning("⚠️ Caché %s es una lista, convirtiendo a dict", self.path)
                    self._data = {}
                    for item in raw:
                        if isinstance(item, dict):
                            key = item.get(ENLACE_KEY) or item.get("enlace", "")
                            if key:
                                self._data[key] = item
                        elif isinstance(item, str):
                            self._data[item] = {"ts": 0}
                elif isinstance(raw, dict):
                    self._data = raw
                else:
                    self._data = {}
            except (json.JSONDecodeError, OSError) as e:
                logger.warning("⚠️ Error leyendo caché %s: %s", self.path, e)
                self._data = {}
        else:
            self._data = {}
        return self._data

    def save(self, data: dict[str, Any]):
        basedir = os.path.dirname(self.path) or "."
        os.makedirs(basedir, exist_ok=True)
        tmp = self.path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, self.path)
        except OSError as e:
            logger.error("❌ Error escribiendo caché %s: %s", self.path, e)
            raise
        self._data = data
        self._dirty = False


class N8nCache(ICacheBackend):
    """
    Backend para n8n — delega persistencia a un webhook.

    Esqueleto listo para migración. Cuando se active, hará:
      GET  {webhook_url}   → carga el estado
      POST {webhook_url}   → persiste el estado
    """

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        self._data: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        # TODO: requests.get(self.webhook_url) → response.json()
        return self._data

    def save(self, data: dict[str, Any]):
        # TODO: requests.post(self.webhook_url, json=data)
        self._data = data


def _default_key(item: dict) -> str:
    """Estrategia de clave por defecto: enlace normalizado."""
    return (item.get(ENLACE_KEY) or "").strip().rstrip("/").lower()


class CacheManager:
    """
    Orquestador de caché con TTL opcional.

    Args:
        backend: Implementación de ICacheBackend.
        ttl_hours: Si se pasa, una clave se considera "vieja" tras N horas.
                   Si no se pasa, las claves son permanentes.
        key_fn: Función que extrae la clave de un item dict.
                Por defecto usa el enlace normalizado.
    """

    def __init__(
        self,
        backend: ICacheBackend,
        ttl_hours: int | None = None,
        key_fn=_default_key,
    ):
        self.backend = backend
        self.ttl = timedelta(hours=ttl_hours) if ttl_hours else None
        self.key_fn = key_fn
        self._data: dict[str, Any] | None = None

    def _ensure_loaded(self):
        if self._data is None:
            self._data = self.backend.load()

    def _get_key(self, item_or_key: dict | str) -> str:
        if isinstance(item_or_key, dict):
            return self.key_fn(item_or_key)
        return item_or_key.strip().lower()

    def is_new(self, item_or_key: dict | str) -> bool:
        """True si el item/clave no está en caché o ha expirado."""
        self._ensure_loaded()
        key = self._get_key(item_or_key)
        entry = self._data.get(key)
        if entry is None:
            return True
        if self.ttl:
            ts = entry.get(TS_KEY) if isinstance(entry, dict) else entry
            if isinstance(ts, (int, float)):
                if datetime.now() - datetime.fromtimestamp(ts) > self.ttl:
                    return True
        return False

    def mark_sent(self, item_or_key: dict | str):
        """Marca un item/clave como ya procesado."""
        self._ensure_loaded()
        key = self._get_key(item_or_key)
        self._data[key] = {"ts": datetime.now().timestamp()}

    def flush(self):
        """Persiste el estado actual en el backend."""
        if self._data is not None:
            self.backend.save(self._data)

    def size(self) -> int:
        """Cantidad de entradas en caché."""
        self._ensure_loaded()
        return len(self._data)

    def clear(self):
        """Limpia todo el caché en memoria (no persiste hasta flush)."""
        self._data = {}
