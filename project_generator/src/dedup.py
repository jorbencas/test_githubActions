"""dedup.py — Anti-duplicados de proyectos: hash normalizado + similitud.

Dos capas, porque el hash exacto solo cubre el caso literal:

1. `hash_unicidad`: MD5 de título normalizado (minúsculas, sin acentos) +
   lenguaje + descripción. Se recalcula SIEMPRE en servidor; el hash que
   manda la IA se ignora.
2. `titulo_mas_similar`: Jaccard sobre tokens del título (sin stopwords)
   contra el historial y el propio lote. «Gestor de tareas con FastAPI» y
   «Gestor de tareas FastAPI» no colisionan por hash, pero superan el
   umbral de similitud.
"""
from __future__ import annotations

import hashlib
import re
import unicodedata
from typing import Iterable, List, Optional, Sequence, Tuple

UMBRAL_SIMILITUD = 0.55

_STOPWORDS = {
    # español
    "de", "del", "la", "el", "los", "las", "un", "una", "unos", "unas",
    "y", "o", "u", "a", "e", "en", "con", "por", "para", "sin", "sobre", "que",
    "al", "se", "su", "sus", "lo", "como", "mas", "muy", "este", "esta",
    "estos", "estas", "cuyo", "cuales", "cuando", "donde", "quien",
    # english
    "the", "of", "and", "or", "for", "with", "on", "in", "to", "an", "at",
    "by", "from", "as", "is", "are", "be", "my", "your", "app", "using",
}

_RE_TOKEN = re.compile(r"[a-z0-9]+")


def normalizar_texto(texto: str) -> str:
    """Minúsculas, sin acentos, espacios colapsados."""
    if not texto:
        return ""
    t = unicodedata.normalize("NFKD", str(texto))
    t = "".join(c for c in t if not unicodedata.combining(c))
    return re.sub(r"\s+", " ", t).strip().casefold()


def hash_unicidad(titulo: str, lenguaje: str, descripcion_corta: str) -> str:
    """MD5 (16 chars) sobre el título normalizado + lenguaje + descripción."""
    contenido = (
        f"{normalizar_texto(titulo)}|{normalizar_texto(lenguaje)}|"
        f"{normalizar_texto(descripcion_corta)}"
    )
    return hashlib.md5(contenido.encode("utf-8")).hexdigest()[:16]


def tokens_titulo(titulo: str) -> frozenset:
    """Tokens del título normalizado, sin stopwords.

    Los dígitos se conservan aunque tengan 1 carácter («Proyecto 0» ≠
    «Proyecto 1»); las letras sueltas se descartan.
    """
    return frozenset(
        tok for tok in _RE_TOKEN.findall(normalizar_texto(titulo))
        if tok not in _STOPWORDS and (len(tok) > 1 or tok.isdigit())
    )


def similitud_jaccard(a: frozenset, b: frozenset) -> float:
    """|A∩B| / |A∪B|; 0 si alguno de los conjuntos está vacío."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def titulo_mas_similar(
    titulo: str,
    existentes: Iterable[str],
    umbral: float = UMBRAL_SIMILITUD,
) -> Optional[str]:
    """El título de `existentes` más similar a `titulo`, si supera `umbral`.

    → el título ganador, o None si ninguno llega al umbral.
    """
    propios = tokens_titulo(titulo)
    if not propios:
        return None
    mejor: Optional[str] = None
    mejor_score = 0.0
    for otro in existentes:
        score = similitud_jaccard(propios, tokens_titulo(otro))
        if score > mejor_score:
            mejor, mejor_score = otro, score
    if mejor is not None and mejor_score >= umbral:
        return mejor
    return None


def filtrar_nuevos(
    proyectos: Sequence[dict],
    hashes_existentes: Iterable[str],
    titulos_existentes: Iterable[str],
    umbral: float = UMBRAL_SIMILITUD,
) -> Tuple[List[dict], List[Tuple[dict, str]]]:
    """Aplica hash exacto + similitud de título, también dentro del lote.

    → (aceptados, descartados[(proyecto, motivo)]).
    """
    hashes = set(hashes_existentes)
    titulos: List[str] = list(titulos_existentes)
    aceptados: List[dict] = []
    descartados: List[Tuple[dict, str]] = []

    for p in proyectos:
        h = p.get("hash_unicidad", "")
        if h and h in hashes:
            descartados.append((p, "hash duplicado"))
            continue
        titulo = p.get("titulo", "")
        dup = titulo_mas_similar(titulo, titulos, umbral=umbral)
        if dup is not None:
            descartados.append((p, f"similar a «{dup}»"))
            continue
        aceptados.append(p)
        if h:
            hashes.add(h)
        if titulo:
            titulos.append(titulo)

    return aceptados, descartados
