"""Utilidades para garantizar contenido en castellano en mensajes de Telegram.

Detección heurística de descripciones en inglés y helper de traducción on-the-fly.
"""

import re

# Palabras-función con alta frecuencia; sirven para discernir idioma incluso
# cuando apenas hay vocabulario técnico (nombres propios, repos, marcas).
EN_STOP = {
    "the", "and", "with", "for", "a", "an", "to", "of", "in", "is", "are",
    "you", "your", "this", "that", "from", "on", "tool", "tools", "using",
    "use", "based", "built", "allows", "create", "helps", "users", "their",
    "into", "its", "can", "be", "as", "by", "or", "at", "we", "our", "who",
    "which", "not", "no", "will", "when", "then", "than", "how", "more",
    "these", "those", "there", "they", "them", "has", "have", "had", "been",
    "each", "other", "also", "may", "very", "much", "just", "all", "one",
    "if", "but", "so", "do", "does", "did", "what", "most", "some", "such",
    "their", "about", "over", "after", "before", "up", "out", "now",
}

ES_STOP = {
    "el", "la", "los", "las", "de", "del", "y", "con", "para", "una", "un",
    "en", "es", "son", "tu", "tus", "este", "esta", "estos", "estas", "que",
    "por", "sobre", "crea", "crear", "permite", "usuarios", "su", "sus",
    "hacer", "basado", "se", "o", "a", "desde", "como", "puedes", "puede",
    "utiliza", "interfaz", "también", "tambien", "más", "mas", "ser", "al",
    "lo", "hay", "puede", "disponible", "gratis", "gratuita", "completo",
    "tiene", "ofrece", "incluye", "ideales", "ideal", "soporta", "apoya",
    "usar", "gestión", "gestion", "fácil", "facil", "rápido", "rapido",
    "rápida", "rapida", "simplemente", "además", "ademas", "todas", "todos",
    "cada", "otro", "otra", "otros", "otras", "este", "esta", "esto",
}

_WORD_RE = re.compile(r"[a-záéíóúüñ]+")
_ACCENT_RE = re.compile(r"[áéíóúüñÁÉÍÓÚÜñ]")


def detect_es(text: str) -> str:
    """Devuelve 'es' | 'en' | 'ambig'. Heurística con en/ES stopwords + acentos.

    Reglas:
    - Texto vacío → 'empty'
    - Acentos/marcas propias del español (ñ, á, é, í, ó, ú, ü) presentes y sin
      clara mayoría de stopwords inglesas → 'es' (señal muy fuerte).
    - Más stopwords inglesas que españolas → 'en'.
    - Más stopwords españolas → 'es'.
    - Empate (o sin stopwords en ninguno de los dos idiomas) → 'en', porque la
      inmensa mayoría de descripciones cortas de estos catálogos vienen en inglés.
    """
    if not text or not text.strip():
        return "empty"
    words = _WORD_RE.findall(text.lower())
    if not words:
        return "ambig"
    en = sum(1 for w in words if w in EN_STOP)
    es = sum(1 for w in words if w in ES_STOP)
    if _ACCENT_RE.search(text):
        return "es" if es >= en - 1 else "en"
    if en > es:
        return "en"
    if es > en:
        return "es"
    return "en"


def looks_english(text: str) -> bool:
    """True si la descripción parece escrita en inglés."""
    return detect_es(text) == "en"


TRANSLATE_PROMPT = """Eres un traductor profesional EN → ES. Traduce SOLO la descripción al castellano correcto y natural. Conserva nombres propios, marcas y URLs tal cual. No uses comillas ni markdown. No añadas texto ni explicaciones.

TEXTO:
{text}
"""


def translate_description_async(text: str, client) -> str:
    """Traduce una descripción en inglés a castellano usando el cliente Gemini ya inicializado."""
    if not text or not text.strip():
        return text
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=TRANSLATE_PROMPT.format(text=text),
        )
        out = response.text.strip() if response.text else ""
        if out and len(out) > 10:
            return out[:500]
    except Exception:
        pass
    return text