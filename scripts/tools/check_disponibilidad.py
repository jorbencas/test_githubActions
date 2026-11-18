#!/usr/bin/env python3
"""
check_disponibilidad.py — Verificación de disponibilidad (job de CI).

1. Fuentes: comprueba que cada fuente de noticias de FUENTES responde
   (RSS/URL) y lista las caídas.
2. Enlaces: comprueba que los enlaces de las noticias recientes (≤24 h)
   de `files/noticias_historico.json` siguen vivos y los elimina del
   histórico si están caídos (404/410/5xx/conexión).

Uso:
    python -m scripts.tools.check_disponibilidad            # fuentes + enlaces
    python -m scripts.tools.check_disponibilidad --solo-fuentes
    python -m scripts.tools.check_disponibilidad --solo-enlaces
    python -m scripts.tools.check_disponibilidad --sin-poda  # solo informe
"""
import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from utils.constants_downloadfile import (  # noqa: E402
    CONFIG, FUENTES, ENLACE_KEY, FECHA_PUB_KEY, ID_VIDEO_KEY,
    NOTICIAS_FILENAME, TIPO_KEY, TIPO_VAL_HERRAMIENTA, URL_KEY, YT_KEY,
)
from utils.disponibilidad import verificar_url  # noqa: E402
from utils.fechas import texto_es_reciente  # noqa: E402

UA = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
    )
}


def fuentes_noticias() -> dict:
    """Solo fuentes que produce noticias (no herramientas)."""
    return {
        k: v for k, v in FUENTES.items()
        if v.get(TIPO_KEY) != TIPO_VAL_HERRAMIENTA and (URL_KEY in v or "rss" in v or YT_KEY in v)
    }


async def comprobar_fuentes(sem: asyncio.Semaphore, session, nombre, info) -> tuple:
    target = info.get("rss") or info.get(URL_KEY) or info.get(YT_KEY)
    if not target:
        return nombre, None
    async with sem:
        try:
            async with session.get(target, timeout=20, headers=UA, allow_redirects=True) as r:
                if r.status == 200:
                    return nombre, None
                # Algunos servidores rechazan GET a bots pero viven → HEAD
                if r.status in (403, 405, 429, 501):
                    return nombre, None
                return nombre, f"HTTP {r.status}"
        except Exception as e:
            return nombre, type(e).__name__


async def run_fuentes() -> list:
    """→ lista de (nombre, motivo) de fuentes caídas."""
    import aiohttp  # import perezoso: solo hace falta para comprobar fuentes

    fuentes = fuentes_noticias()
    print(f"🌐 Comprobando {len(fuentes)} fuentes de noticias…")
    fallos = []
    sem = asyncio.Semaphore(20)
    connector = aiohttp.TCPConnector(ssl=False, limit=20)
    async with aiohttp.ClientSession(connector=connector, headers=UA) as session:
        tareas = [
            comprobar_fuentes(sem, session, nombre, info)
            for nombre, info in fuentes.items()
        ]
        for coro in asyncio.as_completed(tareas):
            nombre, motivo = await coro
            if motivo:
                fallos.append((nombre, motivo))
                print(f"  ❌ {nombre}: {motivo}")
    if fallos:
        print(f"⚠️ {len(fallos)} fuentes no disponibles de {len(fuentes)}")
    else:
        print(f"✅ Todas las fuentes responden ({len(fuentes)})")
    return fallos


def run_enlaces(poda: bool = True) -> list:
    """Comprueba enlaces de noticias ≤24 h; opcionalmente las elimina.

    → lista de (titulo, motivo) con los enlaces caídos.
    """
    path = os.path.join(CONFIG["FOLDER"], NOTICIAS_FILENAME)
    if not os.path.exists(path):
        print(f"📭 No existe {path}")
        return []
    with open(path, encoding="utf-8") as f:
        historial = json.load(f)

    recientes = [
        n for n in historial
        if not n.get(ID_VIDEO_KEY)
        and texto_es_reciente(n.get(FECHA_PUB_KEY, "")) is not False
        and n.get(ENLACE_KEY)
    ]
    print(f"🔗 Comprobando {len(recientes)} enlaces de noticias ≤24 h…")

    caidos = []
    from concurrent.futures import ThreadPoolExecutor, as_completed
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {
            pool.submit(verificar_url, n[ENLACE_KEY]): n for n in recientes
        }
        for fut in as_completed(futs):
            n = futs[fut]
            ok, motivo = fut.result()
            if not ok:
                caidos.append((n.get("titulo", ""), motivo, n.get(ENLACE_KEY, "")))
                print(f"  ❌ {motivo} — {n.get(ENLACE_KEY, '')[:80]}")

    if caidos:
        print(f"⚠️ {len(caidos)} enlaces caídos de {len(recientes)}")
        if poda:
            urls_caidas = {url for _, _, url in caidos}
            nuevos_hist = [
                n for n in historial
                if not (n.get(ENLACE_KEY) in urls_caidas and not n.get(ID_VIDEO_KEY))
            ]
            eliminados = len(historial) - len(nuevos_hist)
            if eliminados:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(nuevos_hist, f, ensure_ascii=False, indent=2)
                print(f"🗑️ {eliminados} noticias con enlace caído eliminadas del histórico")
    else:
        print(f"✅ Todos los enlaces responden ({len(recientes)})")
    return caidos


def main():
    parser = argparse.ArgumentParser(description="Verifica fuentes y enlaces de noticias")
    parser.add_argument("--solo-fuentes", action="store_true", help="Solo comprobar fuentes")
    parser.add_argument("--solo-enlaces", action="store_true", help="Solo comprobar enlaces")
    parser.add_argument("--sin-poda", action="store_true", help="No eliminar enlaces caídos")
    args = parser.parse_args()

    hacer_fuentes = not args.solo_enlaces
    hacer_enlaces = not args.solo_fuentes

    exit_code = 0
    if hacer_fuentes:
        fallos = asyncio.run(run_fuentes())
        # Informe, no bloquea el pipeline: las fuentes caídas se reintentan
        # en la siguiente ejecución horaria.
        if fallos:
            print(f"📋 Informe fuentes caídas: {[n for n, _ in fallos]}")

    if hacer_enlaces:
        caidos = run_enlaces(poda=not args.sin_poda)
        if caidos:
            print(f"📋 Informe enlaces caídos: {len(caidos)}")

    print("✅ check_disponibilidad completado")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
