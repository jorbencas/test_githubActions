#!/usr/bin/env python3
"""
backfill_traducido.py — Marca todos los items existentes como traducidos.
Ejecutar una vez para evitar re-traducciones innecesarias.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.utils.constants_downloadfile import CONFIG, FUENTES_INGLES, NOTICIAS_FILENAME


def main():
    path_json = os.path.join(CONFIG["FOLDER"], NOTICIAS_FILENAME)
    if not os.path.exists(path_json):
        print(f"❌ No se encontró {path_json}")
        return

    with open(path_json, "r", encoding="utf-8") as f:
        historial = json.load(f)

    print(f"📂 Cargados {len(historial)} items")

    # Marcar items de fuentes en inglés como traducidos
    marcados = 0
    for item in historial:
        fuente = item.get("fuente", "").lower()
        if any(x in fuente for x in FUENTES_INGLES):
            if not item.get("traducido"):
                item["traducido"] = True
                marcados += 1

    print(f"✅ {marcados} items marcados como traducidos")

    with open(path_json, "w", encoding="utf-8") as f:
        json.dump(historial, f, ensure_ascii=False, indent=2)

    print(f"💾 Guardado en {path_json}")


if __name__ == "__main__":
    main()
