"""
Migra la DB de conceptos a 100% castellano y mejora las explicaciones con Gemini.

Convierte title/summary/explanation/interview_question/interview_answer al español
(si el término técnico es estándar en inglés se añade entre paréntesis la primera vez)
y reescribe explicaciones cortas a 3-5 párrafos didácticos.

Uso:
    GEMINI_API_KEY=xxx python -m scripts.tools.migrate_concepts_es
    GEMINI_API_KEY=xxx python -m scripts.tools.migrate_concepts_es --dry-run
    GEMINI_API_KEY=xxx python -m scripts.tools.migrate_concepts_es --limit 10 --batch 5
    GEMINI_API_KEY=xxx python -m scripts.tools.migrate_concepts_es --only-language
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent.parent  # scripts/
CONCEPTS_PATH = SCRIPT_DIR / "utils" / "concepts_database.json"
MODEL = "gemini-2.5-flash"
MIN_EXPLANATION_CHARS = 600
EXPLANATION_RULES = (
    "(1) qué es, con una analogía o ejemplo cotidiano; "
    "(2) cómo funciona por dentro, paso a paso; "
    "(3) cuándo usarlo y cuándo evitarlo; "
    "(4) errores o malentendidos comunes; "
    "(5) relación con otros conceptos si aplica"
)
COPY_FIELDS = ["title", "summary", "explanation", "code_example", "use_cases",
               "difficulty", "language", "interview_relevant", "interview_question",
               "interview_answer"]
OPTIONAL_FIELDS = {"use_cases", "difficulty", "language", "interview_relevant",
                   "interview_question", "interview_answer"}


def build_migrate_prompt(concepts, only_language):
    concepts_json = json.dumps(concepts, ensure_ascii=False, indent=2)
    if only_language:
        core = ("Traduce al castellano SOLO title, summary, interview_question e "
                "interview_answer y los comentarios del code_example. La explanation "
                "se conserva tal cual si ya es correcta y en español.")
    else:
        core = (
            "Mejora la explanation para que sea DIDÁCTICA y extensa: 3-5 párrafos bien "
            f"estructurados: {EXPLANATION_RULES}. NUNCA una definición de una sola frase "
            "ni un párrafo genérico."
        )
    return f"""Eres un profesor experto en programación. Convierte los siguientes conceptos a CASTELLANO de calidad.

=== INSTRUCCIONES ===
1. TODO el texto de salida en castellano (español): title, summary, explanation, interview_question, interview_answer y los COMENTARIOS del code_example.
2. Los títulos van en español. Si el término técnico es estándar en inglés, escribe la forma castellana y añade el término inglés entre paréntesis la primera vez (p. ej. "Búsqueda binaria (Binary Search)", "Cola de mensajes (message queue)").
3. {core}
4. Mantén todo lo demás (id, cat, type, tags, source) exactamente igual.
5. El code_example: mantenlo funcional y REAL; traduce solo los comentarios y strings de ejemplo.
6. use_cases: 2-3 casos de uso reales en español. Si faltan, complétalos.
7. Si falta language o interview_question/interview_answer, complétalos en castellano.
8. Devuelve SOLO el JSON array, sin markdown ni texto adicional.

=== CONCEPTOS ORIGINALES (JSON) ===
{concepts_json}

=== RESPUESTA ===
[{{"id": "identificador_original", "title": "...", "summary": "...", "explanation": "...", "code_example": "...", "use_cases": [...], "difficulty": 1, "language": "python", "interview_relevant": true, "interview_question": "...", "interview_answer": "..."}}, ...]"""


def parse_json(text):
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
    return json.loads(text)


def migrate_batch(client, concepts, only_language):
    prompt = build_migrate_prompt(concepts, only_language)
    for attempt in range(3):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            migrated = parse_json(response.text)
            if isinstance(migrated, list):
                return migrated
        except json.JSONDecodeError:
            pass
        except Exception as e:
            print(f"   ⚠️  Reintento por error de Gemini: {e}")
        time.sleep(2)
    return None


def apply_migration(concept, result):
    for field in COPY_FIELDS:
        value = result.get(field)
        if value is None or (isinstance(value, str) and not value.strip()):
            continue
        if field in concept and isinstance(concept[field], bool) and not isinstance(value, bool):
            continue
        concept[field] = value
    return concept


def main():
    parser = argparse.ArgumentParser(description="Migra la DB de conceptos a castellano con Gemini.")
    parser.add_argument("--dry-run", action="store_true", help="solo muestra lo que se va a procesar")
    parser.add_argument("--limit", type=int, default=0, help="procesa solo los primeros N conceptos")
    parser.add_argument("--batch", type=int, default=5, help="conceptos por llamada a Gemini")
    parser.add_argument("--only-language", action="store_true",
                        help="solo traduce, no mejora las explicaciones")
    parser.add_argument("--force", action="store_true", help="procesa todos aunque ya cumplan")
    args = parser.parse_args()

    if not CONCEPTS_PATH.exists():
        print(f"❌ No existe la DB de conceptos: {CONCEPTS_PATH}")
        sys.exit(1)

    with open(CONCEPTS_PATH, "r", encoding="utf-8") as f:
        db = json.load(f)
    concepts = db.get("concepts", [])
    if not concepts:
        print("❌ La DB de conceptos está vacía.")
        sys.exit(1)

    if args.only_language:
        candidates = concepts
    elif args.force:
        candidates = concepts
    else:
        candidates = [c for c in concepts
                      if len(c.get("explanation", "")) < MIN_EXPLANATION_CHARS
                      or not c.get("language")
                      or not c.get("interview_question")]
    if args.limit > 0:
        candidates = candidates[:args.limit]

    print(f"📚 Total conceptos: {len(concepts)}")
    print(f"🔄 Para procesar: {len(candidates)}")
    if not candidates:
        print("✅ Todo cumple el objetivo. Usa --force para re-verificar todo.")
        return

    if args.dry_run:
        print("\n--- CONCEPTOS QUE SE PROCESARÁN (dry-run) ---")
        for c in candidates:
            title = c.get("title", "")
            expl = len(c.get("explanation", ""))
            print(f"   {c.get('id', '?')} | {title} | explanation: {expl} chars")
        return

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("❌ GEMINI_API_KEY no configurada.")
        print("   Ejecuta con tu clave, por ejemplo:")
        print("   GEMINI_API_KEY=tu_clave python -m scripts.tools.migrate_concepts_es")
        sys.exit(1)

    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except ImportError:
        print("❌ google-genai no instalado. Instálalo: pip install google-genai")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error al inicializar Gemini: {e}")
        sys.exit(1)

    backup = CONCEPTS_PATH.with_suffix(".json.bak")
    backup.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Backup guardado en: {backup}\n")

    by_id = {c.get("id"): c for c in concepts}
    done = 0
    for i in range(0, len(candidates), args.batch):
        chunk = candidates[i:i + args.batch]
        print(f"⏳ Procesando {i + 1}-{i + len(chunk)} de {len(candidates)}...")
        results = migrate_batch(client, chunk, args.only_language)
        if results is None:
            print("   ⚠️  No se pudo procesar este lote; se conserva el original.")
            continue
        by_result = {r.get("id"): r for r in results if r.get("id")}
        for c in chunk:
            r = by_result.get(c.get("id"))
            if r:
                apply_migration(c, r)
                done += 1
        with open(CONCEPTS_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        time.sleep(2)

    db["meta"] = {
        **(db.get("meta") or {}),
        "castellano": True,
        "migrated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with open(CONCEPTS_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    print(f"\n✅ Migración completada: {done}/{len(candidates)} conceptos actualizados.")
    print(f"   Guardado en: {CONCEPTS_PATH}")


if __name__ == "__main__":
    main()