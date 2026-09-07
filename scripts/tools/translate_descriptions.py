"""Traduce al castellano las descripciones en inglés de los ficheros de datos
que se envían por Telegram:

- files/agent_skills.json      (skills de agentes IA)
- files/recursos_blog.json     (recursos del blog)

La detección de idioma es heurística (scripts.utils.lang_es.looks_english)
y la traducción se hace por lotes con Gemini (requiere GEMINI_API_KEY).
Los items que ya estén en castellano o sean ambiguos no se tocan.
Los que ya tengan la propiedad interna "desc_en" se consideran traducidos.

Uso:
    python -m scripts.tools.translate_descriptions [--dry-run] [--batch-size 40]
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.lang_es import looks_english

SCRIPT_DIR = Path(__file__).resolve().parent
FILES_DIR = SCRIPT_DIR.parent.parent / "files"

TARGETS = {
    "agent_skills": FILES_DIR / "agent_skills.json",
    "recursos_blog": FILES_DIR / "recursos_blog.json",
}

BATCH_PROMPT = """Eres un traductor profesional. Traduce cada descripción a un castellano técnico correcto y natural. Conserva nombres propios, marcas, siglas y URLs tal cual. No uses markdown ni comillas. Responde SOLO con líneas en el formato "ID|texto_traducido", todo en una única respuesta, sin texto adicional.

=== INSTRUCCIONES ===
- Cada línea de entrada tiene el formato: ID|texto
- Traduce únicamente el texto (después del primer |)
- Devuelve exactamente el mismo número de líneas, mismas IDs, en el mismo orden
- Si una línea ya está en español o no se puede traducir, devuélvela tal cual

=== TEXTO ===
{block}
"""


def _translate_block(lines: list, client) -> dict:
    """Traduce un bloque de líneas "ID|texto" y devuelve {id: texto_traducido}."""
    payload = "\n".join(lines)
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=BATCH_PROMPT.format(block=payload),
        )
        raw = resp.text.strip() if resp.text else ""
    except Exception as e:
        print(f"    ⚠️ Error de Gemini en bloque: {e}")
        return {}

    out = {}
    for line in raw.splitlines():
        if "|" not in line:
            continue
        ident, _, text = line.partition("|")
        ident = ident.strip()
        text = text.strip()
        if ident.isdigit() and text:
            out[int(ident)] = text
    return out


def process_file(path: Path, dry_run: bool, batch_size: int, client) -> dict:
    """Traduce un fichero JSON de lista de items. Devuelve stats."""
    with open(path, "r", encoding="utf-8") as f:
        items = json.load(f)

    to_translate = [
        (i, item)
        for i, item in enumerate(items)
        if isinstance(item.get("descripcion", ""), str)
        and item["descripcion"].strip()
        and "desc_en" not in item
        and looks_english(item["descripcion"])
    ]
    print(f"  {path.name}: {len(items)} items, {len(to_translate)} en inglés")

    if dry_run:
        return {"total": len(items), "en": len(to_translate), "traducidas": 0}

    translated = 0
    for start in range(0, len(to_translate), batch_size):
        chunk = to_translate[start : start + batch_size]
        lines = [f"{pos}|{item['descripcion']}" for pos, item in chunk]
        result = _translate_block(lines, client)
        for pos, item in chunk:
            if pos in result and result[pos]:
                item["desc_en"] = item["descripcion"]
                item["descripcion"] = result[pos]
                translated += 1
        print(f"    → lote {start // batch_size + 1}: {len(result)}/{len(chunk)} traducidas")
        if translated and translated % (batch_size * 4) == 0:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(items, f, indent=2, ensure_ascii=False)
            print("    💾 guardado parcial")

    with open(path, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)
    return {"total": len(items), "en": len(to_translate), "traducidas": translated}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--batch-size", type=int, default=40)
    args = parser.parse_args()

    import os

    key = os.environ.get("GEMINI_API_KEY", "")
    if not key and not args.dry_run:
        print("❌ GEMINI_API_KEY no configurada. Nada que traducir.", file=sys.stderr)
        return 1

    client = None
    if key:
        try:
            from google import genai

            client = genai.Client(api_key=key)
        except ImportError:
            print("❌ google-genai no instalado.", file=sys.stderr)
            return 1

    total_stats = {"total": 0, "en": 0, "traducidas": 0}
    for name, path in TARGETS.items():
        print(f"📄 {name}: {path}")
        stats = process_file(path, args.dry_run, args.batch_size, client)
        for k in total_stats:
            total_stats[k] += stats[k]

    print(
        f"\n✅ Resumen: {total_stats['en']} en inglés de {total_stats['total']} items; "
        f"{'traducirías' if args.dry_run else 'traducidas'}: {total_stats['traducidas']}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())