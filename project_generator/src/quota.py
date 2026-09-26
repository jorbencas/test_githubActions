"""Sondeo del límite real de cuota de cada modelo.

El free tier no publica sus cifras y las que circulan por internet no cuadran
con lo que devuelve la API en cada proyecto, así que la única fuente fiable es
el propio `429` y las cabeceras `x-ratelimit-*` de la respuesta.

Se llama a la REST directamente en vez de pasar por el SDK porque
`google-genai` no expone las cabeceras de la respuesta.

OJO: cada sondeo consume 1 petición del cupo diario del modelo sondeado.
"""
import json
import re
from typing import Any, Dict, List, Optional

import httpx

ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

# Modelos que se suelen sondear, además de los que ya tenía la cadena.
MODELOS_SUGERIDOS = [
    "gemini-2.5-flash",
    "gemini-2.5-pro",
    "gemini-2.5-flash-lite",
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-3-flash",
    "gemini-3.1-flash-lite",
]

_RE_QUOTA_VALUE = re.compile(r"quotaValue[\"']?\s*:\s*[\"']?(\d+)")
_RE_QUOTA_ID = re.compile(r"quotaId[\"']?\s*:\s*[\"']?([A-Za-z0-9_-]+)")
_RE_MODELO = re.compile(r"model:\s*([\w.-]+)")


def _extraer_ratelimit(headers) -> Dict[str, str]:
    """Se queda con las cabeceras x-ratelimit-* (el nombre ha cambiado con el tiempo)."""
    return {k.lower(): v for k, v in headers.items() if k.lower().startswith("x-ratelimit")}


async def sondear_modelo(
    client: httpx.AsyncClient, api_key: str, model: str
) -> Dict[str, Any]:
    """Una petición mínima a `model` y devuelve su estado de cuota."""
    info: Dict[str, Any] = {"modelo": model}
    try:
        respuesta = await client.post(
            ENDPOINT.format(model=model),
            json={"contents": [{"parts": [{"text": "ping"}]}]},
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
        )
    except Exception as e:  # red, DNS, TLS...
        return {**info, "estado": "error de red", "detalle": str(e)[:100]}

    info["http"] = respuesta.status_code
    info.update(_extraer_ratelimit(respuesta.headers))

    if respuesta.status_code == 200:
        info["estado"] = "disponible"
        return info

    if respuesta.status_code == 429:
        info["estado"] = "429 sin cuota"
        try:
            cuerpo = json.dumps(respuesta.json())
        except Exception:
            cuerpo = respuesta.text
        limite = _RE_QUOTA_VALUE.search(cuerpo)
        cuota = _RE_QUOTA_ID.search(cuerpo)
        modelo = _RE_MODELO.search(cuerpo)
        if limite:
            info["limite_diario"] = limite.group(1)
        if cuota:
            info["cuota"] = cuota.group(1)
        if modelo:
            info["modelo_en_el_error"] = modelo.group(1)
        return info

    if respuesta.status_code == 404:
        info["estado"] = "404 no existe"
        return info

    info["estado"] = f"http {respuesta.status_code}"
    info["detalle"] = respuesta.text[:150]
    return info


async def sondear_todos(
    api_key: str, modelos: Optional[List[str]] = None, timeout: float = 30.0
) -> List[Dict[str, Any]]:
    """Sondea varios modelos en serie (en paralelo gastarían cuota a la vez)."""
    objetivos = modelos or MODELOS_SUGERIDOS
    resultados = []
    async with httpx.AsyncClient(timeout=timeout) as client:
        for model in objetivos:
            resultados.append(await sondear_modelo(client, api_key, model))
    return resultados


def formatear(resultados: List[Dict[str, Any]]) -> str:
    """Tabla legible con lo que importa: si existe y cuánto le queda."""
    lineas = [
        f"{'modelo':28s} {'estado':18s} {'límite/día':>11s}  {'restante':>9s}",
        "-" * 72,
    ]
    for r in resultados:
        limite = r.get("limite_diario") or r.get("x-ratelimit-limit-requests", "-")
        restante = r.get("x-ratelimit-remaining-requests", "-")
        lineas.append(
            f"{r['modelo']:28s} {r.get('estado', '?'):18s} {str(limite):>11s}  {str(restante):>9s}"
        )
        if r.get("cuota"):
            lineas.append(f"{'':28s} └ {r['cuota']}")
        if r.get("detalle"):
            lineas.append(f"{'':28s} └ {r['detalle']}")
    return "\n".join(lineas)
