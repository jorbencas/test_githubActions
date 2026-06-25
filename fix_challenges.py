"""
fix_challenges.py
=================
Reescribe archivos MDX de retos con soluciones de la BD local o IA.
Lenguajes del Codeember en rotación cíclica.

Uso:
  python fix_challenges.py                        # desde la BD local
  python fix_challenges.py --ai                   # con IA (Gemini)
  python fix_challenges.py --ai --limit 5         # solo 5 archivos
  python fix_challenges.py --ai --dry-run         # simular
  python fix_challenges.py --ai --force           # regenerar todo
"""
import os, re, json, sys, asyncio, argparse
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))
from constants_downloadfile import CONFIG, RETO_MD_TEMPLATE
from solutions_data import LANGS, GENERIC_SOLUTIONS, parse_frontmatter, slug_key, get_code, mdx_escape
from solutions_db import lookup as db_lookup

CHALLENGES_DIR = CONFIG.get("CHALLENGES_DIR", "auto-challenges")

# ─────────────────────────────────────────────
# MODO 1: DESDE LA BASE DE DATOS LOCAL
# ─────────────────────────────────────────────

def fix_all():
    folder = CHALLENGES_DIR
    files = sorted([
        f for f in os.listdir(folder)
        if f.endswith('.mdx') and (f.startswith('guia-plus-reto-') or f.startswith('guia-'))
    ])

    print(f"📂 {len(files)} archivos encontrados\n")
    fixed = 0
    lang_info = {lid: (lcode, lname) for lid, lcode, lname in LANGS}

    for idx, fname in enumerate(files):
        path = os.path.join(folder, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        fm = parse_frontmatter(content)
        if not fm.get('title'):
            print(f"⚠️  Sin título: {fname}")
            continue

        titulo = fm.get('title', '').strip()
        difficulty = fm.get('difficulty', 'Intermedio')
        pub_date = fm.get('pubDate', '2026-01-01')
        image = fm.get('image', '/img/default.jpg')
        slug = fm.get('slug', fname.replace('.mdx', ''))
        target_lang_id, _, _ = LANGS[idx % len(LANGS)]

        key = slug_key(slug)
        sol_data = None
        db_result = db_lookup(key.replace('-', ' '), target_lang_id)

        if db_result:
            sol_data = {
                "desc": db_result["descripcion"],
                "p1": db_result["paso1"],
                "p2": db_result["paso2"],
                "p3": db_result["paso3"],
            }
            codigo_raw = db_result["codigo"]
            lid_final = target_lang_id
            lcode_final, lname_final = lang_info[lid_final]
        else:
            from solutions_data import SOLUTIONS as EXT
            sol_data = EXT.get(key)
            if sol_data:
                codigo_raw, lid_final = get_code(sol_data, target_lang_id)
                lcode_final, lname_final = lang_info[lid_final]
            else:
                desc_generic = f"Resuelve el siguiente reto de programación: **{titulo}**."
                lid_final = target_lang_id
                lcode_final, lname_final = lang_info[lid_final]
                gen_fn = GENERIC_SOLUTIONS.get(lid_final, GENERIC_SOLUTIONS["python"])
                codigo_raw = gen_fn(titulo, desc_generic)

        desc_text = sol_data['desc'] if sol_data else desc_generic
        content_out = RETO_MD_TEMPLATE.format(
            titulo=titulo.replace('"', "'"),
            resumen_corto=desc_text[:140].replace('"', "'"),
            fecha_pub=pub_date,
            slug_name=slug,
            tags_seo=json.dumps([lid_final, 'retos', difficulty.lower(), 'guia-plus'], ensure_ascii=False),
            ruta_imagen=image,
            descripcion_ia=desc_text,
            dificultad=difficulty,
            paso_1=mdx_escape(sol_data['p1'] if sol_data else paso1),
            paso_2=mdx_escape(sol_data['p2'] if sol_data else paso2),
            paso_3=mdx_escape(sol_data['p3'] if sol_data else paso3),
            big_o_time=sol_data.get('big_o_time', 'O(n)') if sol_data else 'O(n)',
            big_o_space=sol_data.get('big_o_space', 'O(n)') if sol_data else 'O(n)',
            tabla_casos=sol_data.get('tabla_casos', '| `ejemplo` | `resultado` |') if sol_data else '| `ejemplo` | `resultado` |',
            lenguaje_lower=lcode_final,
            lenguaje_display=lname_final,
            codigo_solucion=codigo_raw
        )

        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content_out)
            print(f"✅ [{idx+1:03d}] {fname} → {lname_final}")
            fixed += 1
        except Exception as e:
            print(f"❌ Error en {fname}: {e}")

    print(f"\n🎉 {fixed}/{len(files)} archivos actualizados correctamente.")

    if not fixed:
        print("\n💡 ¿Primera vez? Prueba a ejecutar primero `python hunt_challenges.py` para generar retos nuevos.")


# ─────────────────────────────────────────────
# MODO 2: REGENERACIÓN CON IA
# ─────────────────────────────────────────────

def build_tags(lang: str, difficulty: str) -> str:
    lang_map = {lid: lname.lower() for lid, _, lname in LANGS}
    return json.dumps([lang_map.get(lang, lang), 'retos', difficulty.lower(), 'guia-plus'], ensure_ascii=False)


async def regenerate_with_ai(limit: int = None, dry_run: bool = False, force: bool = False):
    from utils import obtener_solucion_ia
    from google import genai

    api_key = CONFIG.get("GEMINI_KEY")
    if not api_key:
        print("❌ GEMINI_API_KEY no encontrada. Usa --ai solo si tienes configurada la API key.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)
    folder = CHALLENGES_DIR

    if not os.path.exists(folder):
        print(f"❌ Carpeta no encontrada: {folder}")
        sys.exit(1)

    archivos = sorted([
        os.path.join(folder, f) for f in os.listdir(folder)
        if f.endswith('.mdx') and f.startswith('guia-plus-')
    ])

    print(f"📂 Encontrados {len(archivos)} retos en {folder}")
    if limit:
        archivos = archivos[:limit]
        print(f"🔢 Limitado a los primeros {limit} archivos.")

    ok = skipped = errores = 0
    total = len(archivos)
    lang_info = {lid: (lcode, lname) for lid, lcode, lname in LANGS}

    for i, filepath in enumerate(archivos):
        info = extract_challenge_info(filepath)
        if not info:
            print(f"⚠️ [{i+1}/{total}] No se pudo leer: {os.path.basename(filepath)}")
            errores += 1
            continue

        if info['has_real_solution'] and not force:
            print(f"✅ [{i+1}/{total}] Ya resuelto: {info['titulo_limpio']}")
            skipped += 1
            continue

        lang_id, lcode, lname = LANGS[i % len(LANGS)]
        print(f"🎯 [{i+1}/{total}] Generando: {info['titulo_limpio']} → {lname}")

        if dry_run:
            print(f"   [DRY-RUN] Escribiría: {info['filepath']} ({lname})")
            ok += 1
            continue

        sol = await obtener_solucion_ia(info['titulo_limpio'], "fix_challenges", client, lang=lname)
        if not sol:
            print(f"   ⚠️ No se pudo generar solución para: {info['titulo_limpio']}")
            errores += 1
            continue

        test_cases = sol.get('test_cases', 'entrada_ejemplo | salida_ejemplo')
        tabla_casos = '\n'.join(
            f'| `{c.split("|")[0].strip()}` | `{c.split("|")[1].strip()}` |'
            for c in test_cases.split(';') if '|' in c
        ) or '| `ejemplo` | `resultado` |'

        content = RETO_MD_TEMPLATE.format(
            titulo=info['titulo'].replace('"', "'"),
            resumen_corto=sol.get('descripcion', '')[:140].replace('"', "'"),
            fecha_pub=info['pub_date'],
            slug_name=info['slug'],
            tags_seo=build_tags(lang_id, info['difficulty']),
            ruta_imagen=info['image'],
            descripcion_ia=sol.get('descripcion', ''),
            dificultad=info['difficulty'],
            paso_1=sol.get('paso1', ''),
            paso_2=sol.get('paso2', ''),
            paso_3=sol.get('paso3', ''),
            big_o_time=sol.get('big_o_time', 'O(n)'),
            big_o_space=sol.get('big_o_space', 'O(n)'),
            tabla_casos=tabla_casos,
            lenguaje_lower=lcode,
            lenguaje_display=lname,
            codigo_solucion=sol.get('codigo', '')
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"   ✅ Guardado con {lname}")
            ok += 1
        except Exception as e:
            print(f"   ❌ Error escribiendo {os.path.basename(filepath)}: {e}")
            errores += 1

        await asyncio.sleep(3)

    print(f"\n{'='*50}")
    print(f"📊 Resumen: {ok} generados | {skipped} ya resueltos | {errores} errores")
    print(f"{'='*50}")


def extract_challenge_info(filepath: str) -> dict | None:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None

    fm = parse_frontmatter(content)
    if not fm.get('title'):
        return None

    titulo = fm.get('title', '').replace('🏆', '').strip()
    titulo_limpio = re.sub(r'^RETO:\s*', '', titulo).strip()

    has_real_solution = (
        '# TODO' not in content
        and 'solution_plus' not in content
        and 'Desafío ' not in content
        and len(content) > 2000
    )

    return {
        'filepath': filepath,
        'filename': os.path.basename(filepath),
        'slug': fm.get('slug', os.path.basename(filepath).replace('.mdx', '')),
        'titulo': titulo,
        'titulo_limpio': titulo_limpio,
        'difficulty': fm.get('difficulty', 'Intermedio'),
        'pub_date': fm.get('pubDate', datetime.now().strftime('%Y-%m-%d')),
        'image': fm.get('image', 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-4.0.3&auto=format&fit=crop&w=1170&q=80'),
        'has_real_solution': has_real_solution,
    }


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reescribe retos con soluciones (BD local o IA)")
    parser.add_argument('--ai', action='store_true', help='Usar IA (Gemini) en vez de BD local')
    parser.add_argument('--limit', type=int, default=None, help='Procesar solo los primeros N archivos')
    parser.add_argument('--dry-run', action='store_true', help='Solo simular, no escribir archivos')
    parser.add_argument('--force', action='store_true', help='Regenerar incluso los que ya tienen solución')
    args = parser.parse_args()

    if args.ai:
        asyncio.run(regenerate_with_ai(limit=args.limit, dry_run=args.dry_run, force=args.force))
    else:
        fix_all()
