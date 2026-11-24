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
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from utils.lang_es import looks_english
from utils.telegram_client import TelegramClient

SCRIPT_DIR = Path(__file__).resolve().parent
CATS_PATH = SCRIPT_DIR / "utils" / "ai_categories.json"
DB_PATH = SCRIPT_DIR / "utils" / "ai_tools_database.json"
HISTORY_PATH = SCRIPT_DIR.parent / "ai_tools_history.json"
NEWS_PATH = SCRIPT_DIR.parent / "files" / "noticias_historico.json"
TOOLS_PATH = SCRIPT_DIR.parent / "files" / "herramientas.json"
BLOG_RESOURCES_PATH = SCRIPT_DIR.parent / "files" / "recursos_blog.json"
CANDIDATES_PATH = SCRIPT_DIR.parent / "files" / "ai_tools_candidates.json"
AGENT_SKILLS_PATH = SCRIPT_DIR.parent / "files" / "agent_skills.json"
POOL_PATH = SCRIPT_DIR.parent / "files" / "ai_tools_pool.json"
MERGED_TOOLS_PATH = SCRIPT_DIR.parent / "files" / "herramientas_merged.json"
PUBLICAPIS_PATH = SCRIPT_DIR.parent / "files" / "publicapis_apis.json"

MAX_PROMOTE_PER_RUN = 10
MAX_POOL_SIZE = 1500
MAX_SENT_IN_PROMPT = 2000

BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
CHAT_ID = os.environ.get("AI_TOOLS_CHAT_ID", os.environ.get("TIPS_CHAT_ID", "-1004380905505"))
_client = TelegramClient(bot_token=BOT_TOKEN, chat_id=CHAT_ID)
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


def _history_default():
    return {
        "sent_titles": [],
        "sent_urls": [],
        "sent_skills": [],
        "sent_resources": [],
        "last_run": None,
        "total_runs": 0,
        "db_exhausted": False,
    }


def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        for key, default in _history_default().items():
            data.setdefault(key, default)
        return data
    return _history_default()


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


# ── Normalización / anti-duplicados ──────────────────────────────────────────

def _norm_name(value):
    """Normaliza un nombre de herramienta/skill para comparar sin falsos positivos."""
    text = (value or "").strip().lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return " ".join(text.split())


def _norm_url(value):
    """Normaliza una URL para comparar (sin www, query, fragmento ni slash final)."""
    text = (value or "").strip().lower()
    text = re.sub(r"^https?://(www\.)?", "", text)
    text = text.split("#", 1)[0].split("?", 1)[0]
    return text.rstrip("/")


def sent_sets(history):
    """Devuelve (nombres, urls) normalizados ya enviados como herramientas."""
    names = {_norm_name(t) for t in history.get("sent_titles", []) if _norm_name(t)}
    urls = {_norm_url(u) for u in history.get("sent_urls", []) if _norm_url(u)}
    return names, urls


def es_duplicado(item, sent_names, sent_urls, k_name="tool", k_url="url"):
    """True si el item ya se envió (por nombre o URL) o es inválido."""
    name = _norm_name(item.get(k_name, ""))
    if not name:
        return True
    if name in sent_names:
        return True
    url = _norm_url(item.get(k_url, ""))
    if url and url in sent_urls:
        return True
    return False


def filtrar_nuevos(items, sent_names, sent_urls, k_name="tool", k_url="url"):
    """Filtra items ya enviados y duplicados DENTRO del propio lote."""
    result = []
    seen_names, seen_urls = set(), set()
    for item in items:
        if es_duplicado(item, sent_names, sent_urls, k_name, k_url):
            continue
        name = _norm_name(item.get(k_name, ""))
        url = _norm_url(item.get(k_url, ""))
        if name in seen_names:
            continue
        if url and url in seen_urls:
            continue
        seen_names.add(name)
        if url:
            seen_urls.add(url)
        result.append(item)
    return result


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


def load_agent_skills():
    """Carga las skills de agentes IA desde agent_skills.json."""
    if not AGENT_SKILLS_PATH.exists():
        return []
    try:
        with open(AGENT_SKILLS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except Exception:
        return []


def select_skills_from_db(skills, sent_titles, count=2):
    """Selecciona skills que NO hayan sido enviadas. Nunca recicla: devuelve menos si hace falta."""
    sent = {_norm_name(s) for s in sent_titles if _norm_name(s)}
    available = [s for s in skills if _norm_name(s.get("titulo", "")) not in sent]
    random.shuffle(available)
    return available[:count]


def format_skill_message(skill, index):
    """Formatea un skill para el mensaje de Telegram."""
    titulo = skill.get("titulo", "Skill")
    desc = skill.get("descripcion", "")
    fuente = skill.get("fuente", "")
    enlace = skill.get("enlace", "")
    plataformas = skill.get("_platforms", [])
    category = skill.get("_category", "")

    lines = [f"{index}. 🎯 *{titulo}*"]
    if desc:
        lines.append(f"   {desc[:150]}")
    if enlace:
        lines.append(f"   🔗 {enlace}")
    if plataformas:
        platforms_str = ", ".join(plataformas[:5])
        lines.append(f"   ⚙️ Plataformas: {platforms_str}")
    if category:
        lines.append(f"   📂 {category}")
    return "\n".join(lines)


PRICING_ES = {
    "free": "💰 Gratuito",
    "freemium": "⚠️ Versión gratuita con funciones limitadas",
    "paid": "💰 De pago",
    "subscription": "💰 Suscripción mensual/anual",
    "open source": "🔓 Código abierto",
    "open-source": "🔓 Código abierto",
}


def format_blog_resource_message(res, index):
    """Formatea un recurso del blog para el mensaje de Telegram."""
    titulo = res.get("titulo", "Recurso")
    desc = res.get("descripcion", "")
    enlace = res.get("enlace", "")
    cat = res.get("categoria", "")
    pricing = res.get("pricing", "")
    repo = res.get("repo", "")
    blog_category = res.get("blog_category", "")

    lines = [f"{index}. 📚 *{titulo}*"]
    if desc:
        lines.append(f"   {desc[:150]}")
    if enlace:
        lines.append(f"   🔗 {enlace}")
    if repo:
        lines.append(f"   📦 Repo: {repo}")
    if cat:
        lines.append(f"   📂 {cat}")
    if blog_category and blog_category.lower() not in ("nuevas-herramientas", "nuevas herramientas descubiertas"):
        lines.append(f"   🏷️ {blog_category}")
    if pricing:
        pricing_lower = pricing.lower().strip()
        pricing_text = PRICING_ES.get(pricing_lower, f"💰 {pricing}")
        lines.append(f"   {pricing_text}")
    return "\n".join(lines)


def load_recent_tools(count=25):
    path = MERGED_TOOLS_PATH if MERGED_TOOLS_PATH.exists() else TOOLS_PATH
    if not path.exists():
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
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


def load_blog_resources(count=20):
    """Load resources from blog's resources.json (migrated to test_githubActions)."""
    if not BLOG_RESOURCES_PATH.exists():
        return []
    try:
        with open(BLOG_RESOURCES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        # Shuffle to get random selection
        import random
        random.shuffle(data)
        result = []
        for item in data[:count]:
            titulo = item.get("titulo", "")
            enlace = item.get("enlace", "")
            desc = item.get("descripcion", "")
            cat = item.get("categoria", "")
            if titulo:
                result.append(f"- {titulo} ({cat}): {desc} → {enlace}")
        return result
    except Exception:
        return []


def load_blog_resources_for_message(count=5, sent_titles=None):
    """Load random blog resources for daily message (formatted for Telegram).

    Nunca recicla: si solo quedan N nuevas, devuelve N (0 si no queda ninguna).
    """
    if not BLOG_RESOURCES_PATH.exists():
        return []
    try:
        with open(BLOG_RESOURCES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        if sent_titles:
            sent_names = {_norm_name(t) for t in sent_titles if _norm_name(t)}
            data = [r for r in data if _norm_name(r.get("titulo", "")) not in sent_names]
        import random
        random.shuffle(data)
        result = []
        for item in data[:count]:
            titulo = item.get("titulo", "")
            enlace = item.get("enlace", "")
            desc = item.get("descripcion", "")
            cat = item.get("categoria", "")
            pricing = item.get("pricing", "")
            repo = item.get("repo", "")
            blog_category = item.get("blog_category", "")
            if titulo:
                result.append({
                    "titulo": titulo,
                    "enlace": enlace,
                    "descripcion": desc,
                    "categoria": cat,
                    "pricing": pricing,
                    "repo": repo,
                    "blog_category": blog_category,
                })
        return result
    except Exception:
        return []


def _translate_descriptions_batch(items):
    """Traduce por lotes las 'descripcion' que estén en inglés a castellano.

    Fallback: Gemini → Telegram translate → original.
    """
    if not items:
        return items

    to_translate = [
        (i, item.get("descripcion", ""))
        for i, item in enumerate(items)
        if item.get("descripcion") and looks_english(item["descripcion"])
    ]
    if not to_translate:
        return items

    # Fallback 1: Gemini
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)

            numbered = "\n".join(f"{pos}|{desc}" for pos, (_, desc) in enumerate(to_translate))
            prompt = (
                "Traduce cada línea del siguiente listado al castellano. "
                "El formato es ID|texto. Devuelve EXACTAMENTE el mismo formato "
                "ID|texto_traducido, una línea por item, sin añadir nada más. "
                "Conserva nombres propios, marcas, URLs tal cual.\n\n"
                + numbered
            )
            response = client.models.generate_content(
                model="gemini-2.5-flash", contents=prompt,
            )
            text = response.text.strip() if response.text else ""

            translations = {}
            for line in text.splitlines():
                if "|" in line:
                    parts = line.split("|", 1)
                    try:
                        idx = int(parts[0].strip())
                        translations[idx] = parts[1].strip()
                    except ValueError:
                        continue

            for local_pos, (orig_idx, _) in enumerate(to_translate):
                if local_pos in translations and translations[local_pos]:
                    items[orig_idx]["descripcion"] = translations[local_pos]

            if translations:
                print(f"🌐 Traducidas {len(translations)}/{len(to_translate)} descripciones en → es (Gemini)")
                return items
        except Exception as e:
            print(f"⚠️ Gemini falló, intentando Telegram translate: {e}")

    # Fallback 2: Telegram translate
    try:
        import asyncio
        from utils.telegram_translate import translate_batch
        texts = [desc for _, desc in to_translate]
        loop = asyncio.new_event_loop()
        translated = loop.run_until_complete(translate_batch(texts))
        loop.close()
        for (orig_idx, _), new_text in zip(to_translate, translated):
            if new_text:
                items[orig_idx]["descripcion"] = new_text
        print(f"🌐 Traducidas {len(to_translate)} descripciones en → es (Telegram)")
    except Exception as e:
        print(f"⚠️ Telegram translate falló, manteniendo inglés: {e}")

    return items


def load_ai_candidates(count=15):
    if not CANDIDATES_PATH.exists():
        return []
    try:
        with open(CANDIDATES_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        result = []
        for item in data[:count]:
            titulo = item.get("titulo", "")
            desc = item.get("descripcion", "")
            lang = item.get("lenguaje", "")
            stars = item.get("estrellas", "")
            source = item.get("fuente", "")
            if titulo:
                result.append(f"- {titulo} ({source}, {lang}, ⭐{stars}): {desc}")
        return result
    except Exception:
        return []


def select_random_categories(count=5):
    return random.sample(ALL_CATEGORIES, min(count, len(ALL_CATEGORIES)))


def select_tools_from_db(database, history, count=5):
    """Selección de la DB curada sin reciclar: si queda poco, devuelve menos."""
    all_tools = database.get("tools", [])
    sent_names, sent_urls = sent_sets(history)
    available = [t for t in all_tools if not es_duplicado(t, sent_names, sent_urls)]
    random.shuffle(available)
    return _diversify_by_cat(available, count)


def _diversify_by_cat(available, count):
    """Prioriza categorías distintas, sin repetir dentro del lote."""
    selected = []
    used_cats = set()
    for tool in available:
        if len(selected) >= count:
            break
        if tool.get("cat") not in used_cats:
            selected.append(tool)
            used_cats.add(tool.get("cat"))
    if len(selected) < count:
        for tool in available:
            if len(selected) >= count:
                break
            if tool not in selected:
                selected.append(tool)
    return selected[:count]


def select_from_pool(pool_tools, history, count=5, prefer_cats=None):
    """Selecciona del pool (DB + promocionadas) lo que NO esté ya enviado."""
    sent_names, sent_urls = sent_sets(history)
    available = [t for t in pool_tools if not es_duplicado(t, sent_names, sent_urls)]
    if prefer_cats:
        preferred = [t for t in available if t.get("cat") in set(prefer_cats)]
        rest = [t for t in available if t.get("cat") not in set(prefer_cats)]
        random.shuffle(preferred)
        random.shuffle(rest)
        ordered = _diversify_by_cat(preferred, count) + rest
    else:
        random.shuffle(available)
        ordered = _diversify_by_cat(available, count)
    result, used = [], set()
    for tool in ordered:
        if len(result) >= count:
            break
        key = _norm_name(tool.get("tool", ""))
        if key and key not in used:
            used.add(key)
            result.append(tool)
    return result


# ── Pool ampliado (DB curada + fuentes promocionadas) ───────────────────────

def load_pool(database=None):
    """Carga files/ai_tools_pool.json; si no existe, lo siembra con la DB curada."""
    if POOL_PATH.exists():
        try:
            with open(POOL_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list) and data:
                return data
        except Exception:
            pass
    if database is None:
        database = load_database()
    return list(database.get("tools", []))


def save_pool(pool):
    POOL_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(POOL_PATH, "w", encoding="utf-8") as f:
        json.dump(pool[:MAX_POOL_SIZE], f, indent=2, ensure_ascii=False)


def load_promotion_candidates(history, pool, limit=MAX_PROMOTE_PER_RUN):
    """Candidatos reales (HF/GitHub + herramientas + public APIs) aún no en el pool
    ni ya enviados, con descripción suficiente para promoverlos."""
    sent_names, sent_urls = sent_sets(history)
    pool_urls = {_norm_url(t.get("url", "")) for t in pool if _norm_url(t.get("url", ""))}
    pool_names = {_norm_name(t.get("tool", "")) for t in pool if _norm_name(t.get("tool", ""))}

    sources = []
    for path in (CANDIDATES_PATH, MERGED_TOOLS_PATH, PUBLICAPIS_PATH):
        if not path.exists():
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                sources.extend(data)
        except Exception:
            continue

    candidates, seen = [], set()
    for item in sources:
        if not isinstance(item, dict):
            continue
        titulo = item.get("titulo", "") or item.get("tool", "")
        enlace = item.get("enlace", "") or item.get("url", "")
        desc = item.get("descripcion", "") or item.get("body", "")
        if not titulo or not enlace or len(desc) < 40:
            continue
        name_key, url_key = _norm_name(titulo), _norm_url(enlace)
        if not name_key or name_key in pool_names or name_key in sent_names:
            continue
        if url_key in pool_urls or url_key in sent_urls:
            continue
        if name_key in seen:
            continue
        seen.add(name_key)
        candidates.append({
            "titulo": titulo,
            "enlace": enlace,
            "descripcion": desc[:400],
            "lenguaje": item.get("lenguaje", ""),
            "fuente": item.get("fuente", ""),
        })
        if len(candidates) >= limit:
            break
    return candidates


def _validate_promoted(entry, source_item):
    """Valida una ficha devuelta por Gemini para promoverla al pool."""
    if not isinstance(entry, dict):
        return None
    cat = entry.get("cat", "")
    tool = (entry.get("tool", "") or "").strip()
    body = (entry.get("body", "") or "").strip()
    restricciones = (entry.get("restricciones", "") or "").strip()
    if cat not in CAT_EMOJI or not tool or not body or not restricciones:
        return None
    combos = [c for c in entry.get("combinaciones", []) if c in CAT_EMOJI][:5]
    url = entry.get("url", "") or source_item.get("enlace", "")
    if not url.startswith("http"):
        return None
    return {
        "cat": cat,
        "tool": tool,
        "body": body[:300],
        "workflow": (entry.get("workflow", "") or "").strip()[:200],
        "combinaciones": combos,
        "url": url,
        "restricciones": restricciones[:200],
        "dific": int(entry.get("dific", 1) or 1) if str(entry.get("dific", 1)) in ("1", "2", "3") else 1,
        "source": "promoted",
        "fuente_raw": source_item.get("fuente", ""),
    }


def promote_to_pool(pool, history, categories=None, max_promote=MAX_PROMOTE_PER_RUN):
    """Convierte candidatos reales en fichas de herramienta (Gemini) y las añade al pool."""
    if not GEMINI_API_KEY:
        print("⚠️  Sin GEMINI_API_KEY: no se promueven candidatos al pool.")
        return pool, 0
    candidates = load_promotion_candidates(history, pool, limit=max_promote)
    if not candidates:
        print("📭 Sin candidatos nuevos para promover.")
        return pool, 0
    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"⚠️  Gemini no disponible para promoción: {e}")
        return pool, 0

    cats_str = ", ".join(sorted(ALL_CATEGORIES))
    numbered = "\n".join(
        f"{i}|{c['titulo']}|{c['descripcion']}|{c['enlace']}" for i, c in enumerate(candidates)
    )
    prompt = f"""Eres un curador de herramientas de IA. Convierte cada candidato del listado en una ficha
de herramienta en español. Formato por línea: ID|titulo|descripcion|url

=== CATEGORÍAS VÁLIDAS (usa EXACTAMENTE una de estas claves en "cat") ===
{cats_str}

=== REGLAS ===
1. Asigna la categoría más adecuada de la lista (clave exacta).
2. "tool": nombre real y conocido de la herramienta (sin emojis).
3. "body": una frase clara en español de qué hace.
4. "workflow": ejemplo corto de uso (ej. "Descarga -> Resumen -> Obsidian").
5. "combinaciones": 2-3 categorías válidas de la lista con las que encaja.
6. "url": la URL oficial tal cual aparece en el candidato.
7. "restricciones": requisito o limitación clave (plan gratis, GPU, API de pago, etc.).
8. "dific": 1, 2 o 3.
9. Si el candidato no es una herramienta real de IA o no encaja en ninguna categoría, omídelo.

=== CANDIDATOS ===
{numbered}

=== RESPUESTA ===
SOLO el JSON array, sin markdown:
[{{"id": 0, "cat": "...", "tool": "...", "body": "...", "workflow": "...", "combinaciones": [...], "url": "https://...", "restricciones": "...", "dific": 1}}, ...]"""

    try:
        response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        text = (response.text or "").strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        generated = json.loads(text)
    except Exception as e:
        print(f"⚠️  Promoción fallida (Gemini): {e}")
        return pool, 0

    if not isinstance(generated, list):
        return pool, 0

    by_id = {i: c for i, c in enumerate(candidates)}
    existing_names = {_norm_name(t.get("tool", "")) for t in pool}
    added = 0
    for entry in generated:
        if added >= max_promote:
            break
        src = by_id.get(entry.get("id") if isinstance(entry.get("id"), int) else -1)
        if src is None:
            continue
        valid = _validate_promoted(entry, src)
        if not valid:
            continue
        key = _norm_name(valid["tool"])
        if key in existing_names:
            continue
        existing_names.add(key)
        pool.append(valid)
        added += 1

    if added:
        print(f"➕ Promovidas {added} candidatos reales al pool de herramientas.")
    else:
        print("📭 Ningún candidato superó la validación de promoción.")
    return pool, added


def _cat_label(cat):
    emoji = CAT_EMOJI.get(cat, "🤖")
    nombre = CAT_NAMES.get(cat, cat)
    return f"{emoji} {nombre}"


def build_gemini_prompt(categories, sent_titles, news, tools, candidates=None, blog_resources=None):
    cats_str = "\n".join(f"- {c} ({CAT_NAMES.get(c, c)})" for c in categories)
    titles_str = "\n".join(sent_titles[:MAX_SENT_IN_PROMPT]) if sent_titles else "(nunca se han enviado herramientas antes)"
    news_str = "\n".join(news[:15]) if news else "(no hay noticias recientes disponibles)"
    tools_str = "\n".join(tools[:10]) if tools else "(no hay herramientas trending disponibles)"
    candidates_str = "\n".join(candidates[:15]) if candidates else "(no hay candidatos auto-detectados)"
    blog_str = "\n".join(blog_resources[:15]) if blog_resources else "(no hay recursos del blog disponibles)"

    return f"""Eres un curador experto en herramientas de Inteligencia Artificial. Propones herramientas de IA EN ESPAÑOL para contenido multimedia, unión de conceptos, automatizaciones, estudio y generación.

=== CATEGORÍAS DE ESTE BATCH ===
{cats_str}

=== HERRAMIENTAS YA ENVIADAS (NUNCA REPETIR) ===
{titles_str}

=== CANDIDATOS AUTO-DETECTADOS (ALTA PRIORIDAD: usa estos si encajan) ===
{candidates_str}

=== NOTICIAS TECH DE HOY (inspiración) ===
{news_str}

=== HERRAMIENTAS/REPOS TRENDING DE HOY (inspiración) ===
{tools_str}

=== RECURSOS DEL BLOG (2108 recursos migrados) ===
{blog_str}

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
13. PRIORIZA herramientas de la sección CANDIDATOS AUTO-DETECTADOS si son relevantes
14. Si un candidato aparece en múltiples fuentes (HF + GitHub), dale MÁXIMA prioridad

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


def generate_tools_gemini(count, categories, sent_titles, sent_names=None, sent_urls=None):
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

    if sent_names is None or sent_urls is None:
        sent_names, sent_urls = sent_sets({"sent_titles": sent_titles})

    news = load_recent_news(15)
    tools = load_recent_tools(10)
    candidates = load_ai_candidates(30)
    blog_resources = load_blog_resources(15)
    prompt = build_gemini_prompt(categories, sent_titles, news, tools, candidates, blog_resources)

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
            # FILTRO OBLIGATORIO: nunca reenviar nada ya enviado ni repetir en el lote
            valid = filtrar_nuevos(valid, sent_names, sent_urls)
            if valid:
                print(f"✅ Gemini generó {len(valid)} herramientas nuevas")
                return valid[:count]
        print("⚠️  Respuesta de Gemini no tiene formato válido o todo era duplicado")
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
    # Sin duplicados intra-lote (nombre o URL normalizados)
    return filtrar_nuevos(mixed[:total], set(), set())


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


def build_daily_message(tools, skills=None, blog_resources=None):
    greeting = _get_time_greeting(datetime.now())
    now = datetime.now()
    date_str = now.strftime("%d/%m/%Y")
    header = f"{greeting} — {date_str}\n{'─' * 28}\n🧰 *Herramientas de IA para tu día*"

    body_parts = []
    for i, tool in enumerate(tools, 1):
        body_parts.append("")
        body_parts.append(format_tool_message(tool, i))

    if skills:
        body_parts.append("")
        body_parts.append("━" * 28)
        body_parts.append("🎯 *AI AGENT SKILLS*")
        body_parts.append("━" * 28)
        for i, skill in enumerate(skills, 1):
            body_parts.append("")
            body_parts.append(format_skill_message(skill, i))

    if blog_resources:
        body_parts.append("")
        body_parts.append("━" * 28)
        body_parts.append("📚 *RECURSOS DEL BLOG*")
        body_parts.append("━" * 28)
        for i, res in enumerate(blog_resources, 1):
            body_parts.append("")
            body_parts.append(format_blog_resource_message(res, i))

    body = "\n".join(body_parts)
    cats = set(t.get("cat", "") for t in tools)
    footer_parts = [f"💡 {len(tools)} herramientas"]
    if skills:
        footer_parts.append(f"🎯 {len(skills)} skills")
    if blog_resources:
        footer_parts.append(f"📚 {len(blog_resources)} recursos")
    footer_parts.append(f"de {len(cats)} categorías")
    footer = " · ".join(footer_parts)

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

    try:
        resp = _client.send_message(text, parse_mode="Markdown", disable_web_page_preview=True, timeout=30)
        if resp is None:
            return False
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
    sent_names, sent_urls = sent_sets(history)

    if show_stats:
        pool = load_pool(database)
        remaining = [t for t in pool if not es_duplicado(t, sent_names, sent_urls)]
        print("📊 Estadísticas del sistema de herramientas IA:")
        print(f"   Tools en DB curada: {len(database['tools'])}")
        print(f"   Tools en pool (DB + promocionadas): {len(pool)}")
        print(f"   Pool sin enviar: {len(remaining)}")
        print(f"   Tools enviados (total): {len(sent_titles)} ({len(sent_urls)} con URL)")
        print(f"   Skills enviadas: {len(history.get('sent_skills', []))}")
        print(f"   Recursos enviados: {len(history.get('sent_resources', []))}")
        print(f"   Pool agotado: {'Sí' if history.get('db_exhausted') else 'No'}")
        print(f"   Última ejecución: {history.get('last_run', 'Nunca')}")
        print(f"   Total ejecuciones: {history.get('total_runs', 0)}")
        print(f"   Categorías disponibles: {len(ALL_CATEGORIES)}")
        return

    if len(database.get("tools", [])) == 0 and not GEMINI_API_KEY:
        print(f"❌ No hay DB ({DB_PATH}) ni GEMINI_API_KEY. Nada que enviar.")
        sys.exit(1)

    categories = select_random_categories(5)
    print(f"📂 Categorías de este batch: {', '.join(categories)}")

    # ── Pool ampliado: DB curada + candidatos reales promocionados ──
    pool = load_pool(database)
    if not dry_run:
        pool, promoted = promote_to_pool(pool, history, categories)
        if promoted:
            save_pool(pool)
    remaining = [t for t in pool if not es_duplicado(t, sent_names, sent_urls)]
    print(f"🧰 Pool: {len(pool)} tools · {len(remaining)} sin enviar")

    # ── Herramientas: Gemini (post-filtrado) + pool, nunca reciclando ──
    gemini_tools = None
    if GEMINI_API_KEY:
        gemini_count = 5 if len(remaining) < 2 else 3
        gemini_tools = generate_tools_gemini(
            gemini_count, categories, sent_titles, sent_names, sent_urls
        )
        if gemini_tools:
            for t in gemini_tools:
                t["source"] = "gemini"
    if not gemini_tools:
        if not GEMINI_API_KEY:
            print("⚠️  Sin GEMINI_API_KEY. Usando solo pool local...")
        else:
            print("⚠️  Gemini sin resultados nuevos. Usando solo pool local...")

    pool_needed = 5 - len(gemini_tools or [])
    pool_tools = select_from_pool(pool, history, count=pool_needed, prefer_cats=categories)
    if gemini_tools:
        tools = mix_tools(gemini_tools, pool_tools, total=5)
    else:
        tools = pool_tools[:5]
    # Red de seguridad final: jamás enviar nada ya enviado ni repetir en el lote
    tools = filtrar_nuevos(tools, sent_names, sent_urls)
    if len(tools) < 5:
        print(f"⚠️  Solo {len(tools)} herramientas nuevas disponibles (pool sin reciclado).")

    # Cargar y seleccionar agent skills (sin reciclar)
    all_skills = load_agent_skills()
    skills = select_skills_from_db(all_skills, history.get("sent_skills", []), count=2)
    skills = _translate_descriptions_batch(skills)
    print(f"🎯 Skills seleccionadas: {len(skills)}")

    # Recursos del blog (sin reciclar)
    blog_resources = load_blog_resources_for_message(
        5, history.get("sent_resources", [])
    )
    blog_resources = _translate_descriptions_batch(blog_resources)
    print(f"📚 Recursos del blog: {len(blog_resources)}")

    if not tools and not skills and not blog_resources:
        print("🛑 Nada nuevo que enviar: pool, skills y recursos agotados.")
        print("   Se ampliarán fuentes en la próxima ejecución (promoción de candidatos).")
        history["last_run"] = datetime.now().isoformat()
        history["total_runs"] = history.get("total_runs", 0) + 1
        history["db_exhausted"] = True
        save_history(history)
        return

    message = build_daily_message(tools, skills, blog_resources)

    print(f"\n🧰 Herramientas seleccionadas ({len(tools)}):")
    for i, tool in enumerate(tools, 1):
        emoji = CAT_EMOJI.get(tool.get("cat", ""), "?")
        src = tool.get("source", "db")
        print(f"   {i}. {emoji} [{tool.get('cat')}] {tool.get('tool')} ({src})")
    for i, skill in enumerate(skills, 1):
        print(f"   🎯 {skill.get('titulo', 'Skill')} ({skill.get('fuente', '')})")

    if dry_run:
        print("\n--- VISTA PREVIA (dry-run) ---\n")
        print(message)
        print("\n--- FIN VISTA PREVIA ---")
        return

    if send_telegram(message):
        for tool in tools:
            name = tool.get("tool", "")
            url = tool.get("url", "")
            if name and _norm_name(name) not in sent_names:
                history["sent_titles"].append(name)
                sent_names.add(_norm_name(name))
            if url and _norm_url(url) not in sent_urls:
                history["sent_urls"].append(url)
                sent_urls.add(_norm_url(url))
        for skill in skills:
            key = _norm_name(skill.get("titulo", ""))
            if key and key not in history["sent_skills"]:
                history["sent_skills"].append(key)
        for res in blog_resources:
            key = _norm_name(res.get("titulo", ""))
            if key and key not in history["sent_resources"]:
                history["sent_resources"].append(key)
        history["last_run"] = datetime.now().isoformat()
        history["total_runs"] = history.get("total_runs", 0) + 1
        remaining_after = [t for t in pool if not es_duplicado(t, sent_names, sent_urls)]
        history["db_exhausted"] = len(remaining_after) == 0
        if history["db_exhausted"]:
            print("🔄 Pool local agotado: solo Gemini + promoción de candidatos a partir de ahora.")
        save_history(history)
        print(f"📊 Total tools enviados: {len(history['sent_titles'])}")


if __name__ == "__main__":
    main()