"""
regenerate_challenges.py
========================
Regenera todos los archivos MDX de retos con:
  - Soluciones reales generadas por Gemini AI
  - Lenguajes rotativos del Codeember (no siempre Python)
  - Pasos explicativos reales (no texto genérico)
  - Código completo y funcional

Uso:
  python regenerate_challenges.py                 # procesa todos los retos
  python regenerate_challenges.py --limit 10      # solo los primeros N
  python regenerate_challenges.py --dry-run       # muestra qué haría sin escribir
"""

import os
import re
import sys
import json
import asyncio
import argparse
from datetime import datetime
from google import genai

# ─────────────────────────────────────────────
# CONFIGURACIÓN
# ─────────────────────────────────────────────
CHALLENGES_DIR = "../blog/src/content/auto-challenges"
GEMINI_KEY = os.getenv("GEMINI_API_KEY")

# Lenguajes del Codeember — rotación cíclica según el índice del archivo
# El orden importa: se asigna cíclicamente al procesar los archivos
CODEEMBER_LANGS = [
    "python",
    "javascript",
    "typescript",
    "go",
    "rust",
    "java",
    "csharp",     # C#
    "kotlin",
    "swift",
    "php",
    "ruby",
    "dart",
]

# Mapeo de nombre de lenguaje → identificador markdown (para el bloque de código)
LANG_CODE_ID = {
    "python":     "python",
    "javascript": "javascript",
    "typescript": "typescript",
    "go":         "go",
    "rust":       "rust",
    "java":       "java",
    "csharp":     "csharp",
    "kotlin":     "kotlin",
    "swift":      "swift",
    "php":        "php",
    "ruby":       "ruby",
    "dart":       "dart",
}

# Nombre legible del lenguaje (para usarlo en el prompt)
LANG_DISPLAY = {
    "python":     "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go":         "Go",
    "rust":       "Rust",
    "java":       "Java",
    "csharp":     "C#",
    "kotlin":     "Kotlin",
    "swift":      "Swift",
    "php":        "PHP",
    "ruby":       "Ruby",
    "dart":       "Dart",
}

# ─────────────────────────────────────────────
# TEMPLATE MDX CORREGIDO
# ─────────────────────────────────────────────
RETO_MDX_TEMPLATE = """\
---
draft: false
title: "{title}"
description: "{description}"
pubDate: "{pub_date}"
tags: {tags}
slug: "{slug}"
image: "{image}"
author: "Jorge Beneyto Castelló"
difficulty: "{difficulty}"
---

import Challenge from '../../components/Challenge.astro';

# 🎯 Desafío: {titulo_limpio}

### 📝 Descripción del Reto

{descripcion}

<Challenge 
  nivel="{difficulty}" 
  mision="{mision_corta}" 
/>

---

## 💡 Guía de Solución Paso a Paso

<details>
<summary><b>Ver explicación y código 🛠️ (¡No hagas spoiler!)</b></summary>
<div class="details-content">

### 🏗️ Paso 1: Análisis de la lógica

{paso1}

### ⚙️ Paso 2: Implementación en {lang_display}

{paso2}

### 🚀 Paso 3: Complejidad y Optimización

{paso3}

### 💻 Código de la Solución ({lang_display})

```{lang_code}
{codigo}
```

</div>
</details>
"""

# ─────────────────────────────────────────────
# FUNCIONES DE PARSEO
# ─────────────────────────────────────────────

def parse_frontmatter(content: str) -> dict:
    """Extrae el frontmatter YAML del MDX."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    raw = match.group(1)
    data = {}
    for line in raw.split('\n'):
        if ':' in line:
            key, _, val = line.partition(':')
            data[key.strip()] = val.strip().strip('"')
    return data

def extract_challenge_info(filepath: str) -> dict | None:
    """Lee un MDX y extrae título, dificultad, fecha, imagen, slug, tags."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return None

    fm = parse_frontmatter(content)
    if not fm.get('title'):
        return None

    # Limpiar título (quitar emojis y prefijos)
    titulo = fm.get('title', '').replace('🏆', '').strip()
    titulo_limpio = re.sub(r'^RETO:\s*', '', titulo).strip()

    # Detectar si ya tiene solución real (código no vacío / no TODO)
    has_real_solution = (
        '# TODO' not in content
        and 'solution_plus' not in content
        and 'Desafío ' not in content  # template genérico
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
        'tags_raw': fm.get('tags', '["python", "retos"]'),
        'has_real_solution': has_real_solution,
    }

# ─────────────────────────────────────────────
# GENERACIÓN IA
# ─────────────────────────────────────────────

async def obtener_solucion_real(titulo: str, dificultad: str, lang: str, client) -> dict | None:
    """
    Usa Gemini para generar una solución real y completa para el reto.
    Devuelve un dict con: descripcion, paso1, paso2, paso3, codigo
    """
    lang_display = LANG_DISPLAY.get(lang, lang)
    
    prompt = f"""
Resuelve el siguiente reto de programación de forma COMPLETA y REAL.
Reto: "{titulo}"
Dificultad: {dificultad}
Lenguaje: {lang_display}

RESPONDE EXCLUSIVAMENTE con un objeto JSON válido con este esquema exacto:
{{
  "descripcion": "Descripción clara del problema con ejemplos de entrada/salida. Mínimo 80 palabras.",
  "paso1": "Análisis detallado del problema: qué necesitamos calcular, restricciones, casos borde. Mínimo 60 palabras.",
  "paso2": "Explicación de la implementación: algoritmo elegido, estructuras de datos, por qué este enfoque. Mínimo 60 palabras.",
  "paso3": "Análisis de complejidad temporal O(?) y espacial O(?). Posibles optimizaciones. Mínimo 40 palabras.",
  "codigo": "CÓDIGO COMPLETO Y FUNCIONAL en {lang_display} con comentarios explicativos. Debe incluir ejemplos de uso con datos reales. NO uses placeholders ni TODOs. Mínimo 20 líneas."
}}

IMPORTANTE:
- El código debe ser 100% funcional, no pseudocódigo
- Usa el lenguaje {lang_display} con su sintaxis correcta
- Incluye imports necesarios
- Añade un main/ejemplo de ejecución al final del código
- Los textos descriptivos escríbelos en español
"""

    for intento in range(3):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt
            )
            text = response.text.strip()
            # Extraer JSON
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                # Validar que tiene código real
                if (data.get('codigo')
                        and len(data['codigo']) > 100
                        and 'TODO' not in data['codigo']
                        and 'placeholder' not in data['codigo'].lower()):
                    return data
        except json.JSONDecodeError:
            pass
        except Exception as e:
            err_str = str(e)
            if '429' in err_str or 'QUOTA' in err_str.upper() or 'RESOURCE_EXHAUSTED' in err_str.upper():
                wait = 60 * (intento + 1)
                print(f"   ⏳ Rate limit, esperando {wait}s...")
                await asyncio.sleep(wait)
            else:
                print(f"   ⚠️ Error Gemini: {e}")
                break
    return None

# ─────────────────────────────────────────────
# ESCRITURA DE ARCHIVO
# ─────────────────────────────────────────────

def build_tags(tags_raw: str, lang: str, difficulty: str) -> str:
    """Construye la lista de tags con el lenguaje correcto."""
    lang_display = LANG_DISPLAY.get(lang, lang)
    diff_lower = difficulty.lower()
    return json.dumps([lang_display.lower(), 'retos', diff_lower, 'guia-plus'], ensure_ascii=False)

def write_challenge_mdx(info: dict, sol: dict, lang: str, dry_run: bool = False) -> bool:
    """Escribe el archivo MDX con la solución real."""
    lang_display = LANG_DISPLAY.get(lang, lang)
    lang_code = LANG_CODE_ID.get(lang, lang)
    
    # Descripción corta para mision (máx 160 chars)
    descripcion_corta = sol['descripcion'][:155].rstrip() + ('...' if len(sol['descripcion']) > 155 else '')
    
    # Tags actualizados con el lenguaje real  
    tags = build_tags(info['tags_raw'], lang, info['difficulty'])
    
    content = RETO_MDX_TEMPLATE.format(
        title=info['titulo'].replace('"', "'"),
        description=descripcion_corta.replace('"', "'"),
        pub_date=info['pub_date'],
        tags=tags,
        slug=info['slug'],
        image=info['image'],
        difficulty=info['difficulty'],
        titulo_limpio=info['titulo_limpio'].replace('"', "'"),
        descripcion=sol['descripcion'],
        mision_corta=descripcion_corta.replace('"', "'"),
        paso1=sol['paso1'],
        paso2=sol['paso2'],
        paso3=sol['paso3'],
        lang_display=lang_display,
        lang_code=lang_code,
        codigo=sol['codigo'],
    )
    
    if dry_run:
        print(f"   [DRY-RUN] Escribiría: {info['filepath']} ({lang_display})")
        return True
    
    try:
        with open(info['filepath'], 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"   ❌ Error escribiendo {info['filename']}: {e}")
        return False

# ─────────────────────────────────────────────
# PROCESO PRINCIPAL
# ─────────────────────────────────────────────

async def regenerate_all(limit: int = None, dry_run: bool = False, force: bool = False):
    """Regenera todos los retos con soluciones reales."""
    
    if not GEMINI_KEY:
        print("❌ GEMINI_API_KEY no encontrada en variables de entorno.")
        sys.exit(1)
    
    client = genai.Client(api_key=GEMINI_KEY)
    folder = CHALLENGES_DIR
    
    if not os.path.exists(folder):
        print(f"❌ Carpeta no encontrada: {folder}")
        sys.exit(1)
    
    # Recopilar todos los MDX
    archivos = sorted([
        os.path.join(folder, f)
        for f in os.listdir(folder)
        if f.endswith('.mdx') and f.startswith('guia-plus-')
    ])
    
    print(f"📂 Encontrados {len(archivos)} retos 'guia-plus-' en {folder}")
    
    if limit:
        archivos = archivos[:limit]
        print(f"🔢 Limitado a los primeros {limit} archivos.")
    
    ok = 0
    skipped = 0
    errores = 0
    total = len(archivos)
    
    for i, filepath in enumerate(archivos):
        info = extract_challenge_info(filepath)
        if not info:
            print(f"⚠️ [{i+1}/{total}] No se pudo leer: {os.path.basename(filepath)}")
            errores += 1
            continue
        
        # Si ya tiene solución real y no se fuerza, saltar
        if info['has_real_solution'] and not force:
            print(f"✅ [{i+1}/{total}] Ya resuelto: {info['titulo_limpio']}")
            skipped += 1
            continue
        
        # Asignar lenguaje cíclicamente
        lang = CODEEMBER_LANGS[i % len(CODEEMBER_LANGS)]
        lang_display = LANG_DISPLAY[lang]
        
        print(f"🎯 [{i+1}/{total}] Generando: {info['titulo_limpio']} → {lang_display}")
        
        if dry_run:
            write_challenge_mdx(info, {
                'descripcion': 'DRY RUN - descripción real',
                'paso1': 'DRY RUN - paso 1',
                'paso2': 'DRY RUN - paso 2',
                'paso3': 'DRY RUN - paso 3',
                'codigo': f'# DRY RUN {lang_display} code here',
            }, lang, dry_run=True)
            ok += 1
            continue
        
        # Obtener solución de IA
        sol = await obtener_solucion_real(info['titulo_limpio'], info['difficulty'], lang, client)
        
        if not sol:
            print(f"   ⚠️ No se pudo generar solución para: {info['titulo_limpio']}")
            errores += 1
            continue
        
        if write_challenge_mdx(info, sol, lang):
            print(f"   ✅ Guardado con {lang_display}")
            ok += 1
        else:
            errores += 1
        
        # Pausa entre peticiones para respetar rate limits
        await asyncio.sleep(3)
    
    print(f"\n{'='*50}")
    print(f"📊 Resumen: {ok} generados | {skipped} ya resueltos | {errores} errores")
    print(f"{'='*50}")

# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Regenera los retos con soluciones reales y lenguajes del Codeember")
    parser.add_argument('--limit', type=int, default=None, help='Procesar solo los primeros N archivos')
    parser.add_argument('--dry-run', action='store_true', help='Solo simular, no escribir archivos')
    parser.add_argument('--force', action='store_true', help='Regenerar incluso los que ya tienen solución')
    args = parser.parse_args()
    
    asyncio.run(regenerate_all(
        limit=args.limit,
        dry_run=args.dry_run,
        force=args.force,
    ))
