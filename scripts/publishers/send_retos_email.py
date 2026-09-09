#!/usr/bin/env python3
"""
send_retos_email.py — Envía retos de programación por correo con plantilla dedicada.
Selecciona retos del blog, extrae código de ejemplo y genera email con soluciones.

Uso:
    python send_retos_email.py                             # Envía retos seleccionados
    python send_retos_email.py --dry-run                   # Muestra sin enviar
    python send_retos_email.py --max-retos 3               # Máx retos a enviar
    python send_retos_email.py --difficulty avanzado        # Filtra por dificultad
"""
import argparse
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from logging.handlers import RotatingFileHandler

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from utils.constants_downloadfile import CONFIG, LOGS_DIR, LOG_FILES
from utils.constants_templates import (
    RETOS_EMAIL_TEMPLATE, RETOS_EMAIL_ROW, RETOS_CODE_PREVIEW,
)

os.makedirs(LOGS_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        RotatingFileHandler(os.path.join(LOGS_DIR, LOG_FILES.get("email", "email.log")), maxBytes=1024*1024*5, backupCount=5, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger("retos_email")

# Ruta a los retos del blog (repo hermano)
_RETOS_BASE = Path(__file__).resolve().parent.parent.parent.parent / "blog" / "src" / "content" / "auto-challenges"
RETOS_DIR = _RETOS_BASE if _RETOS_BASE.exists() else Path("/home/jorge/dev/blog/src/content/auto-challenges")

# Estilos por dificultad
DIFFICULTY_STYLES = {
    "iniciacion": {
        "style": "background: #dcfce7; color: #166534; border: 1px solid #bbf7d0;",
        "icon": "🟢",
    },
    "intermedio": {
        "style": "background: #fef3c7; color: #92400e; border: 1px solid #fde68a;",
        "icon": "🟡",
    },
    "avanzado": {
        "style": "background: #fce7f3; color: #9d174d; border: 1px solid #fbcfe8;",
        "icon": "🔴",
    },
}

# Traducción de dificultad
DIFFICULTY_ES = {
    "iniciacion": "Iniciación",
    "intermedio": "Intermedio",
    "avanzado": "Avanzado",
}


def parse_mdx_frontmatter(content: str) -> dict:
    """Extrae el frontmatter YAML de un archivo MDX."""
    match = re.match(r'^---\s*\n(.*?)\n---\s*\n', content, re.DOTALL)
    if not match:
        return {}
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if val.startswith('['):
                val = [v.strip().strip('"').strip("'") for v in val.strip('[]').split(',')]
            fm[key] = val
    return fm


def extract_python_solution(content: str) -> str:
    """Extrae la primera solución en Python del contenido MDX."""
    # Buscar bloques de código Python
    pattern = r'```python\s*\n(.*?)```'
    matches = re.findall(pattern, content, re.DOTALL)
    if not matches:
        return ""
    # Tomar la primera solución (la más completa)
    solution = matches[0].strip()
    # Limitar a 15 líneas para el preview
    lines = solution.split('\n')
    if len(lines) > 15:
        lines = lines[:15]
        lines.append('    # ... (código truncado)')
    return '\n'.join(lines)


def extract_description(content: str) -> str:
    """Extrae la descripción del reto del contenido MDX."""
    # Buscar después del frontmatter, antes del primer heading
    parts = content.split('---', 2)
    if len(parts) < 3:
        return ""
    body = parts[2].strip()
    # Buscar la primera descripción (después de Challenge o del primer párrafo)
    lines = body.split('\n')
    desc_lines = []
    in_code = False
    for line in lines:
        if line.startswith('```'):
            in_code = not in_code
            continue
        if in_code:
            continue
        if line.startswith('#') or line.startswith('<'):
            break
        if line.strip() and not line.startswith('import'):
            desc_lines.append(line.strip())
        if len(desc_lines) >= 3:
            break
    return ' '.join(desc_lines)[:200]


def load_retos(max_retos: int = 3, difficulty: str = None) -> list:
    """Carga retos desde los archivos MDX del blog."""
    if not RETOS_DIR.exists():
        logger.warning(f"Directorio de retos no encontrado: {RETOS_DIR}")
        return []

    retos = []
    for mdx_file in RETOS_DIR.glob("*.mdx"):
        content = mdx_file.read_text(encoding='utf-8')
        fm = parse_mdx_frontmatter(content)

        # Filtrar por dificultad si se especifica
        reto_diff = (fm.get('difficulty', '') or '').lower()
        if difficulty and reto_diff != difficulty.lower():
            continue

        # Solo retos con soluciones (que tengan código Python)
        python_code = extract_python_solution(content)
        if not python_code:
            continue

        description = extract_description(content)
        languages = fm.get('languages', [])
        if isinstance(languages, str):
            languages = [languages]

        retos.append({
            'title': fm.get('title', mdx_file.stem),
            'description': description,
            'difficulty': reto_diff or 'iniciacion',
            'languages': languages,
            'slug': fm.get('slug', mdx_file.stem),
            'python_code': python_code,
            'file': mdx_file.name,
        })

    # Ordenar: primero avanzados, luego intermedios, luego iniciación
    order = {'avanzado': 0, 'intermedio': 1, 'iniciacion': 2}
    retos.sort(key=lambda r: order.get(r['difficulty'], 3))

    return retos[:max_retos]


def build_reto_row(reto: dict) -> str:
    """Genera HTML para un solo reto en el email."""
    diff = reto['difficulty']
    diff_info = DIFFICULTY_STYLES.get(diff, DIFFICULTY_STYLES['iniciacion'])
    diff_label = DIFFICULTY_ES.get(diff, diff.title())

    languages_str = ', '.join(reto['languages'][:4]) if reto['languages'] else 'Python'

    # Code preview
    code_html = ""
    if reto['python_code']:
        code_html = RETOS_CODE_PREVIEW.format(
            code_lang="Python",
            code_snippet=reto['python_code'][:500],  # Limitar tamaño
        )

    enlace = f"https://blog-jorbencas.vercel.app/retos/{reto['slug']}"

    return RETOS_EMAIL_ROW.format(
        difficulty_style=diff_info['style'],
        difficulty_icon=diff_info['icon'],
        difficulty=diff_label,
        languages=languages_str,
        titulo=reto['title'],
        descripcion=reto['description'][:200] if reto['description'] else 'Resuelve este desafío de programación.',
        code_preview_html=code_html,
        enlace=enlace,
    )


def build_email(retos: list) -> str:
    """Genera el HTML completo del email de retos."""
    now = datetime.now()
    fecha_hoy = now.strftime('%d de %B de %Y').replace('January', 'enero').replace('February', 'febrero').replace('March', 'marzo').replace('April', 'abril').replace('May', 'mayo').replace('June', 'junio').replace('July', 'julio').replace('August', 'agosto').replace('September', 'septiembre').replace('October', 'octubre').replace('November', 'noviembre').replace('December', 'diciembre')

    retos_html = '\n'.join(build_reto_row(r) for r in retos)

    difficulties = set(r['difficulty'] for r in retos)
    diff_str = '/'.join(DIFFICULTY_ES.get(d, d) for d in difficulties)

    all_langs = set()
    for r in retos:
        all_langs.update(r.get('languages', []))
    num_langs = max(len(all_langs), 1)

    return RETOS_EMAIL_TEMPLATE.format(
        fecha_hoy=fecha_hoy,
        total_retos=len(retos),
        dificultad=diff_str,
        num_lenguajes=num_langs,
        retos_html=retos_html,
        year=now.year,
    )


def send_email(html: str, subject: str, dry_run: bool = False) -> bool:
    """Envía el email por Mailgun."""
    if dry_run:
        logger.info("📧 DRY RUN — Email no enviado")
        logger.info(f"Subject: {subject}")
        # Guardar preview
        preview_path = Path(LOGS_DIR) / "retos_email_preview.html"
        preview_path.write_text(html, encoding='utf-8')
        logger.info(f"Preview guardado en: {preview_path}")
        return True

    mail_key = CONFIG.get("MAIL_KEY")
    mail_domain = CONFIG.get("MAIL_DOMAIN")
    email_to = CONFIG.get("EMAIL_TO")

    if not all([mail_key, mail_domain, email_to]):
        logger.warning("⚠️ Configuración de Mailgun incompleta.")
        return False

    try:
        response = requests.post(
            f"https://api.mailgun.net/v3/{mail_domain}/messages",
            auth=("api", mail_key),
            data={
                "from": f"Tech Pulse Retos <retos@{mail_domain}>",
                "to": email_to,
                "subject": subject,
                "html": html,
            },
            timeout=30,
        )
        if response.status_code == 200:
            logger.info(f"✅ Email enviado correctamente a {email_to}")
            return True
        else:
            logger.error(f"❌ Error sending email: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ Excepción enviando email: {e}")
        return False


async def run():
    parser = argparse.ArgumentParser(description="Send retos email with dedicated template")
    parser.add_argument("--dry-run", action="store_true", help="Preview without sending")
    parser.add_argument("--max-retos", type=int, default=3, help="Max retos to send (default 3)")
    parser.add_argument("--difficulty", type=str, default=None, help="Filter by difficulty: iniciacion, intermedio, avanzado")
    args = parser.parse_args()

    logger.info(f"🧩 Cargando retos (max: {args.max_retos}, difficulty: {args.difficulty or 'all'})")

    retos = load_retos(max_retos=args.max_retos, difficulty=args.difficulty)

    if not retos:
        logger.warning("⚠️ No se encontraron retos para enviar")
        return

    logger.info(f"📋 {len(retos)} retos seleccionados:")
    for r in retos:
        logger.info(f"   - [{r['difficulty']}] {r['title']}")

    html = build_email(retos)

    now = datetime.now()
    fecha = now.strftime('%d/%m/%Y')
    subject = f"🧩 Tech Pulse Retos — {fecha} ({len(retos)} desafíos)"

    success = send_email(html, subject, dry_run=args.dry_run)

    if success:
        logger.info("🎉 Proceso completado")
    else:
        logger.error("💥 Fallo en el envío")


if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
