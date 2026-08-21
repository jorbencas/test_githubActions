"""
Herramientas de IA — Envía herramientas de IA cada 3 horas por Telegram.
Gemini genera propuestas dinámicas: herramientas, cómo unirlas en workflows y
combinaciones entre categorías. DB estática de fallback. Nunca repite.

Uso:
    python scripts/ai_tools_generator.py            # envía herramientas
    python scripts/ai_tools_generator.py --dry-run  # solo muestra, no envía
    python scripts/ai_tools_generator.py --list-categories  # lista categorías
    python scripts/ai_tools_generator.py --stats    # estadísticas
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
CATS_PATH = SCRIPT_DIR / "utils" / "ai_categories.json"
DB_PATH = SCRIPT_DIR / "utils" / "ai_tools_database.json"
HISTORY_PATH = SCRIPT_DIR.parent / "ai_tools_history.json"
NEWS_PATH = SCRIPT_DIR.parent / "files" / "noticias_historico.json"
TOOLS_PATH = SCRIPT_DIR.parent / "files" / "herramientas.json"

BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
CHAT_ID = os.environ.get("AI_TOOLS_CHAT_ID", os.environ.get("TIPS_CHAT_ID", "-1004380905505"))
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

CATS = {"categorias": {}, "meta": {}}
CAT_EMOJI = {}
CAT_NAMES = {}


def load_categories():
    global CATS, CAT_EMOJI, CAT_NAMES, ALL_CATEGORIES
    if CATS_PATH.exists():
        with open(CATS_PATH, "r", encoding="utf-8") as f:
            CATS = json.load(f)
        CAT_EMOJI = {k: v["emoji"] for k, v in CATS["categorias"].items()}
        CAT_NAMES = {k: v["nombre"] for k, v in CATS["categorias"].items()}
    ALL_CATEGORIES = list(CAT_EMOJI.keys())
    return CATS["categorias"]


ALL_CATEGORIES = list(CAT_EMOJI.keys())


def load_database():
    if not DB_PATH.exists():
        return {"meta": {}, "tools": []}
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sent_titles": [], "last_run": None, "total_runs": 0, "db_exhausted": False}


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_recent_news(count=15):
    if not NEWS_PATH.exists():
        return []
    try:
        with open(NEWS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        recent = sorted(data, key=lambda x: x.get("ts", ""), reverse=True)[:count]
        result = []
        for item in recent:
            titulo = item.get("titulo", "")
            cat = item.get("categoria", "")
            fuente = item.get("fuente", "")
            if titulo:
                result.append(f"- {titulo} [{cat}] ({fuente})")
        return result
    except Exception:
        return []


def load_recent_tools(count=10):
    if not TOOLS_PATH.exists():
        return []
    try:
        with open(TOOLS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        recent = sorted(data, key=lambda x: x.get("ts", ""), reverse=True)[:count]
        result = []
        for item in recent:
            titulo = item.get("titulo", "")
            desc = item.get("descripcion", "")
            lang = item.get("lenguaje", "")
            stars = item.get("estrellas", "")
            if titulo:
                result.append(f"- {titulo} ({lang}, ⭐{stars}): {desc}")
        return result
    except Exception:
        return []


def select_random_categories(count=5):
    return random.sample(ALL_CATEGORIES, min(count, len(ALL_CATEGORIES)))


def select_tools_from_db(database, history, count=5):
    all_tools = database["tools"]
    sent_titles = set(history.get("sent_titles", []))
    available = [t for t in all_tools if t["tool"] not in sent_titles]
    if len(available) < count:
        available = all_tools
    random.shuffle(available)
    selected = []
    used_cats = set()
    for tool in available:
        if len(selected) >= count:
            break
        if tool["cat"] not in used_cats:
            selected.append(tool)
            used_cats.add(tool["cat"])
    if len(selected) < count:
        for tool in available:
            if len(selected) >= count:
                break
            if tool not in selected:
                selected.append(tool)
    return selected[:count]


def _cat_label(cat):
    emoji = CAT_EMOJI.get(cat, "🤖")
    nombre = CAT_NAMES.get(cat, cat)
    return f"{emoji} {nombre}"


def build_gemini_prompt(categories, sent_titles, news, tools):
    cats_str = "\n".join(f"- {c} ({CAT_NAMES.get(c, c)})" for c in categories)
    titles_str = "\n".join(sent_titles[:200]) if sent_titles else "(nunca se han enviado herramientas antes)"
    news_str = "\n".join(news[:15]) if news else "(no hay noticias recientes disponibles)"
    tools_str = "\n".join(tools[:10]) if tools else "(no hay herramientas trending disponibles)"

    return f"""Eres un curador experto en herramientas de Inteligencia Artificial. Propones herramientas de IA EN ESPAÑOL para contenido multimedia, unión de conceptos, automatizaciones, estudio y generación.

=== CATEGORÍAS DE ESTE BATCH ===
{cats_str}

=== HERRAMIENTAS YA ENVIADAS (NUNCA REPETIR) ===
{titles_str}

=== NOTICIAS TECH DE HOY (inspiración) ===
{news_str}

=== HERRAMIENTAS/REPOS TRENDING DE HOY (inspiración) ===
{tools_str}

=== REGLAS ESTRICTAS ===
1. Genera EXACTAMENTE 5 herramientas
2. Cada herramienta = UNA categoría DIFERENTE del batch
3. NUNCA repitas nombre, herramienta ni idea de la lista de enviados
4. Cada herramienta debe tener UNA sola idea clara y concreta
5. Incluye SIEMPRE el campo "workflow": una cadena que muestre cómo se aplica (ej. "Transcripción -> LLM resumen -> Obsidian")
6. Incluye SIEMPRE el campo "combinaciones": array de 2-5 categorías del listado total con las que encaja
7. Incluye SIEMPRE el campo "url": enlace web OFICIAL de la herramienta (https://...)
8. Incluye SIEMPRE el campo "restricciones": una frase corta con las limitaciones o requisitos clave (plan gratuito, hardware, coste, curva de aprendizaje)
9. Todo en ESPAÑOL correcto
10. NUNCA uses emojis en los campos "tool" ni "body"
11. Usa nombres de herramientas reales y conocidas (respeta la clave exacta de categoría)
12. Varía dificultad: 1=básico, 2=intermedio, 3=avanzado

=== LISTADO TOTAL DE CATEGORÍAS (usa estas claves exactas en "cat" y en "combinaciones") ===
{', '.join(sorted(ALL_CATEGORIES))}

=== EJEMPLO ===
{{
  "cat": "transcripcion",
  "tool": "OpenAI Whisper",
  "body": "Transcribe audio y vídeo a texto con alta precisión. Es la base de los pipelines de contenido audiovisual.",
  "workflow": "Whisper -> LLM resumen -> Obsidian",
  "combinaciones": ["second_brain", "video_edit", "llm_workflow"],
  "url": "https://openai.com/whisper",
  "restricciones": "Modelo abierto; necesita GPU o cola de API para timings largos.",
  "dific": 1
}}

=== RESPUESTA ===
SOLO el JSON array, sin markdown, sin texto adicional:
[{{"cat": "...", "tool": "...", "body": "...", "workflow": "...", "combinaciones": [...], "url": "https://...", "restricciones": "...", "dific": 1}}, ...]"""


def generate_tools_gemini(count, categories, sent_titles):
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY no configurada. Solo se usarán tools de la DB.")
        return None

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except ImportError:
        print("⚠️  google-genai no instalado. Solo se usarán tools de la DB.")
        return None
    except Exception as e:
        print(f"⚠️  Error al inicializar Gemini: {e}")
        return None

    news = load_recent_news(15)
    tools = load_recent_tools(10)
    prompt = build_gemini_prompt(categories, sent_titles, news, tools)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        generated = json.loads(text)
        if isinstance(generated, list) and len(generated) > 0:
            valid = []
            for t in generated:
                if all(k in t for k in ("cat", "tool", "body")):
                    if t["cat"] in CAT_EMOJI:
                        t.setdefault("workflow", "")
                        t.setdefault("combinaciones", [])
                        t.setdefault("url", "")
                        t.setdefault("restricciones", "")
                        t.setdefault("dific", 1)
                        valid.append(t)
            if valid:
                print(f"✅ Gemini generó {len(valid)} herramientas nuevas")
                return valid[:count]
        print("⚠️  Respuesta de Gemini no tiene formato válido")
        return None
    except json.JSONDecodeError:
        print("⚠️  Gemini respondió con JSON inválido")
        return None
    except Exception as e:
        print(f"⚠️  Error al llamar a Gemini: {e}")
        return None


def mix_tools(gemini_tools, db_tools, total=5):
    mixed = []
    g = gemini_tools or []
    d = db_tools or []
    random.shuffle(g)
    random.shuffle(d)
    i_g, i_d = 0, 0
    while len(mixed) < total:
        added = False
        if i_g < len(g) and len(mixed) < total:
            mixed.append(g[i_g])
            i_g += 1
            added = True
        if i_d < len(d) and len(mixed) < total:
            mixed.append(d[i_d])
            i_d += 1
            added = True
        if not added:
            break
    return mixed[:total]


DIFFICULTY_BAR = {1: "●○○", 2: "●●○", 3: "●●●"}


def format_tool_message(tool, index):
    cat = tool.get("cat", "")
    tool_name = tool.get("tool", "")
    body = tool.get("body", "")
    workflow = tool.get("workflow", "")
    combos = tool.get("combinaciones", [])
    url = tool.get("url", "")
    restricciones = tool.get("restricciones", "")
    dific = tool.get("dific", 1)
    bar = DIFFICULTY_BAR.get(dific, "●○○")
    emoji = CAT_EMOJI.get(cat, "🤖")
    nombre = CAT_NAMES.get(cat, cat)

    lines = [f"{index}. {emoji} *{nombre}* — *{tool_name}*"]
    lines.append(f"   {bar} {'Básico' if dific == 1 else 'Intermedio' if dific == 2 else 'Avanzado'}")
    if body:
        lines.append(f"   {body}")
    if url:
        lines.append(f"   🔗 {url}")
    if workflow:
        lines.append(f"   ⚙️ _Workflow:_ {workflow}")
    if combos:
        labels = ", ".join(CAT_NAMES.get(c, c) for c in combos if c in CAT_EMOJI)
        if labels:
            lines.append(f"   🔗 _Combina con:_ {labels}")
    if restricciones:
        lines.append(f"   ⚠️ _Limitaciones:_ {restricciones}")
    return "\n".join(lines)


def build_daily_message(tools):
    greeting = _get_time_greeting(datetime.now())
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    header = f"{greeting} — {date_str}\n{'─' * 28}\n🧰 *Herramientas de IA para tu día*"

    grouped = {}
    for i, tool in enumerate(tools, 1):
        cat = tool.get("cat", "")
        grouped.setdefault(cat, []).append((i, tool))

    body_parts = []
    for cat, cat_tools in grouped.items():
        emoji = CAT_EMOJI.get(cat, "🤖")
        nombre = CAT_NAMES.get(cat, cat)
        body_parts.append(f"\n{emoji} *{nombre}* ({len(cat_tools)} herramienta{'s' if len(cat_tools) > 1 else ''})")
        for idx, tool in cat_tools:
            body_parts.append("")
            body_parts.append(format_tool_message(tool, idx))
        body_parts.append(f"\n{'─' * 28}")

    body = "\n".join(body_parts)
    footer = f"💡 {len(tools)} herramientas de {len(grouped)} categorías\n\n_Combina herramientas entre sí para crear workflows potentes._"

    return header + "\n" + body + "\n" + footer


def _get_time_greeting(now):
    hour = now.hour
    if 5 <= hour < 12:
        return "*Buenos días*"
    elif 12 <= hour < 19:
        return "*Buenas tardes*"
    else:
        return "*Buenas noches*"


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  TIPS_BOT_TOKEN o TIPS_CHAT_ID no configurados.")
        print("   Configura las variables de entorno o usa --dry-run.")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=30)
        if resp.status_code == 200:
            print("✅ Mensaje enviado a Telegram.")
            return True
        else:
            print(f"❌ Error Telegram ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def main():
    load_categories()

    dry_run = "--dry-run" in sys.argv
    list_cats = "--list-categories" in sys.argv
    show_stats = "--stats" in sys.argv

    if list_cats:
        print("📂 Categorías disponibles:")
        for cat in sorted(ALL_CATEGORIES):
            print(f"   {CAT_EMOJI.get(cat, '?')} {cat}: {CAT_NAMES.get(cat, cat)}")
        print(f"\n   Total: {len(ALL_CATEGORIES)} categorías")
        return

    database = load_database()
    history = load_history()
    sent_titles = history.get("sent_titles", [])

    if show_stats:
        print("📊 Estadísticas del sistema de herramientas IA:")
        print(f"   Tools en DB: {len(database['tools'])}")
        print(f"   Tools enviados (total): {len(sent_titles)}")
        print(f"   DB agotada: {'Sí' if history.get('db_exhausted') else 'No'}")
        print(f"   Última ejecución: {history.get('last_run', 'Nunca')}")
        print(f"   Total ejecuciones: {history.get('total_runs', 0)}")
        print(f"   Categorías disponibles: {len(ALL_CATEGORIES)}")
        return

    if len(database.get("tools", [])) == 0 and not GEMINI_API_KEY:
        print(f"❌ No hay DB ({DB_PATH}) ni GEMINI_API_KEY. Nada que enviar.")
        sys.exit(1)

    categories = select_random_categories(5)
    print(f"📂 Categorías de este batch: {', '.join(categories)}")

    db_exhausted = history.get("db_exhausted", False)

    if db_exhausted:
        print("🔄 DB agotada. Generando 5 herramientas con Gemini...")
        gemini_tools = generate_tools_gemini(5, categories, sent_titles)
        if gemini_tools:
            for t in gemini_tools:
                t["source"] = "gemini"
            tools = gemini_tools
        else:
            print("⚠️  Gemini no disponible. Reintentando con DB (puede repetir)...")
            tools = select_tools_from_db(database, history, 5)
    else:
        print("🔄 Generando herramientas (Gemini + DB)...")
        gemini_tools = generate_tools_gemini(3, categories, sent_titles)
        if gemini_tools:
            for t in gemini_tools:
                t["source"] = "gemini"
            db_tools = select_tools_from_db(database, history, 2)
        else:
            print("⚠️  Gemini no disponible. Usando solo DB...")
            db_tools = select_tools_from_db(database, history, 5)
        tools = mix_tools(gemini_tools, db_tools, total=5)

    message = build_daily_message(tools)

    print(f"\n🧰 Herramientas seleccionadas ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        emoji = CAT_EMOJI.get(tool.get("cat", ""), "?")
        src = tool.get("source", "db")
        print(f"   {i}. {emoji} [{tool.get('cat')}] {tool.get('tool')} ({src})")

    if dry_run:
        print("\n--- VISTA PREVIA (dry-run) ---\n")
        print(message)
        print("\n--- FIN VISTA PREVIA ---")
        return

    if send_telegram(message):
        for tool in tools:
            name = tool.get("tool", "")
            if name and name not in sent_titles:
                history["sent_titles"].append(name)
        history["last_run"] = datetime.now().isoformat()
        history["total_runs"] = history.get("total_runs", 0) + 1
        if not db_exhausted and len(database.get("tools", [])) > 0:
            db_sent = sum(1 for t in tools if t.get("source") != "gemini")
            if db_sent > 0:
                remaining = len([t for t in database["tools"]
                                 if t["tool"] not in set(history["sent_titles"])])
                if remaining == 0:
                    history["db_exhausted"] = True
                    print("🔄 DB estática agotada. A partir de ahora solo Gemini.")
        save_history(history)
        print(f"📊 Total tools enviados: {len(history['sent_titles'])}")


if __name__ == "__main__":
    main()