#!/usr/bin/env python3
"""
disponibilidad.py — Verificación de fuentes (al scrapear) y enlaces (al enviar).

Dos niveles:
  1. Fuente viva: `scraper_base` avisa con HTTP != 200 / excepción.
  2. Enlace vivo: antes de enviar, cada URL de noticia se comprueba con
     HEAD (fallback GET si 405) — timeout corto y concurrencia.

Código OK: 2xx/3xx y también 403/429 (anti-bot: el enlace vive para el
usuario). Muerto: 404/410/5xx, error de conexión o SSL.
"""
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Iterable, List, Optional, Tuple

import requests

logger = logging.getLogger(__name__)

TIMEOUT = 10
MAX_WORKERS = 8
_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}
# 401/403/419/429/999: paywall o protección anti-bot → el enlace vive para
# el lector (Reuters, WSJ, LinkedIn, rate-limit… devuelven estos códigos)
_OK_STATUS = set(range(200, 400)) | {401, 403, 419, 429, 999}


def verificar_url(url: str, timeout: int = TIMEOUT) -> Tuple[bool, str]:
    """Comprueba que `url` responde. → (vivo, detalle).

    HEAD primero; si el servidor lo rechaza (405/501) reintenta con GET.
    """
    if not url or not isinstance(url, str):
        return False, "sin enlace"
    if not url.startswith(("http://", "https://")):
        return False, "esquema no soportado"
    try:
        resp = requests.head(
            url, timeout=timeout, headers=_HEADERS, allow_redirects=True
        )
        if resp.status_code in (405, 501):
            resp = requests.get(
                url, timeout=timeout, headers=_HEADERS,
                allow_redirects=True, stream=True,
            )
            resp.close()
        code = resp.status_code
        if code in _OK_STATUS:
            return True, str(code)
        return False, f"HTTP {code}"
    except requests.exceptions.SSLError:
        return False, "SSL"
    except requests.exceptions.Timeout:
        return False, "timeout"
    except requests.exceptions.RequestException as e:
        return False, type(e).__name__ or "conexión"


def filtrar_disponibles(
    items: Iterable[dict],
    campo: str = "enlace",
    max_workers: int = MAX_WORKERS,
) -> Tuple[List[dict], List[Tuple[dict, str]]]:
    """Parte `items` en (vivos, muertos).

    - `vivos`: items cuyo enlace responde (o sin enlace → se conservan).
    - `muertos`: lista de (item, motivo) descartados.
    """
    vivos: List[dict] = []
    muertos: List[Tuple[dict, str]] = []
    pendientes = []
    sin_enlace = []

    for it in items:
        url = it.get(campo) if isinstance(it, dict) else None
        if not url:
            sin_enlace.append(it)
        else:
            pendientes.append(it)

    if pendientes:
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futs = {
                pool.submit(verificar_url, it.get(campo, "")): it
                for it in pendientes
            }
            for fut in as_completed(futs):
                it = futs[fut]
                try:
                    ok, motivo = fut.result()
                except Exception as e:  # defensa: nunca tumbar el envío
                    ok, motivo = False, type(e).__name__
                if ok:
                    vivos.append(it)
                else:
                    muertos.append((it, motivo))

    # Conservar el orden original
    orden = {id(it): i for i, it in enumerate(items)}
    vivos += sin_enlace
    vivos.sort(key=lambda x: orden.get(id(x), 0))
    muertos.sort(key=lambda x: orden.get(id(x[0]), 0))
    return vivos, muertos


def log_descartes(muertos: List[Tuple[dict, str]], contexto: str = "noticias") -> None:
    """Log estándar para descartes por enlace caído."""
    if not muertos:
        return
    motivos = {}
    for _, motivo in muertos:
        motivos[motivo] = motivos.get(motivo, 0) + 1
    resumen = ", ".join(f"{m}×{n}" for m, n in sorted(motivos.items()))
    logger.warning(
        "🔗 %d %s descartadas: enlace caído (%s)",
        len(muertos), contexto, resumen,
    )
    for it, motivo in muertos[:10]:
        enlace = (it.get("enlace") or it.get("url") or "")[:80]
        logger.warning("   ❌ %s — %s", motivo, enlace)
