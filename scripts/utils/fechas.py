#!/usr/bin/env python3
"""
fechas.py — Parseo de fechas de publicación y control de recencia (≤24 h).

Regla única para TODOS los scrapers y envíos de noticias:
  una noticia solo es válida si su fecha de publicación es la fecha de envío
  o, como mucho, las últimas 24 horas. Si la fuente no da fecha, no hay
  información de antigüedad (cada llamada decide si la acepta).

Formatos soportados por `parsear_fecha`:
  - RFC822/RSS : "Wed, 11 Apr 2026 20:32:00 +0200"
  - ISO        : "2026-04-11T20:32:00", "2026-04-11 20:32:00Z", "2026-04-11"
  - Español    : "11 abril 2026, 20:32", "11 de abril de 2026", "11/04/2026 20:32"
  - Relativo   : "hace 2 horas", "hace 3 días" (se resuelve contra `ref`)

Las fechas sin hora se interpretan a las 00:00 (Europe/Madrid), de modo que
una noticia "de ayer" queda fuera de la ventana de 24 h.
"""
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")
VENTANA_HORAS = 24

_MESES = {
    "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
    "julio": 7, "agosto": 8, "septiembre": 9, "setiembre": 9, "octubre": 10,
    "noviembre": 11, "diciembre": 12,
    "ene": 1, "feb": 2, "mar": 3, "abr": 4, "may": 5, "jun": 6,
    "jul": 7, "ago": 8, "sep": 9, "oct": 10, "nov": 11, "dic": 12,
}
_MESES_RE = "|".join(sorted(_MESES, key=len, reverse=True))

_RE_RFC822 = re.compile(r"^[a-z]{3},\s+\d{1,2}\s+[a-z]{3}\s+\d{4}", re.I)
_RE_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:[T\s](\d{1,2}):(\d{2})(?::(\d{2}))?)?")
_RE_BARRAS = re.compile(r"\b(\d{1,2})/(\d{1,2})/(\d{4})\b")
_RE_ES = re.compile(rf"\b(\d{{1,2}})(?:\s+de\s+|\s+)({_MESES_RE})\.?(?:\s+de\s+(\d{{4}}))?\b", re.I)
_RE_HORA = re.compile(r"(?:\bat\b|a\s+las\s+)?\s*(\d{1,2}):(\d{2})(?::(\d{2}))?", re.I)
_RE_REL = re.compile(
    r"\bhace\s+(\d+)\s+(horas?|h|minutos?|min|d[ií]as?|d|semanas?|sem|meses?|mes|a[nñ]os?|a[nñ]o)\b",
    re.I,
)


def _a_madrid(dt: datetime) -> datetime:
    """Convierte a Europe/Madrid (asume Madrid si no trae zona horaria)."""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=MADRID)
    return dt.astimezone(MADRID)


def _hora_en(texto: str, desde: int = 0):
    """Extrae HH:MM[:SS] de `texto` a partir de la posición `desde`."""
    m = _RE_HORA.search(texto, desde)
    if not m:
        return 0, 0, 0
    return int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)


def parsear_fecha(texto, ref: datetime = None):
    """Parsea una fecha de publicación → datetime (Madrid) o None si no hay.

    `ref` es el instante de referencia para los formatos relativos
    ("hace 3 días"); por defecto, ahora.
    """
    if not texto:
        return None
    t = str(texto).strip()
    if not t:
        return None
    ref = _a_madrid(ref) if ref else datetime.now(MADRID)

    # Relativo: "hace 2 horas" / "hace 3 días"
    m = _RE_REL.search(t)
    if m:
        n = int(m.group(1))
        u = m.group(2).lower()
        if u.startswith("h"):
            delta = timedelta(hours=n)
        elif u.startswith("min"):
            delta = timedelta(minutes=n)
        elif u.startswith("sem"):
            delta = timedelta(weeks=n)
        elif u.startswith("mes"):
            delta = timedelta(days=30 * n)
        elif u.startswith("a"):
            delta = timedelta(days=365 * n)
        else:
            delta = timedelta(days=n)
        return ref - delta

    # RFC822 (RSS/pubDate): "Wed, 11 Apr 2026 20:32:00 +0200"
    if _RE_RFC822.match(t):
        try:
            return _a_madrid(parsedate_to_datetime(t))
        except Exception:
            pass

    # ISO: "2026-04-11T20:32:00" / "2026-04-11"
    m = _RE_ISO.search(t)
    if m:
        try:
            hh, mm, ss = _hora_en(t, m.end())
            if m.group(4) is not None:
                hh, mm, ss = int(m.group(4)), int(m.group(5)), int(m.group(6) or 0)
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)),
                            hh, mm, ss, tzinfo=MADRID)
        except ValueError:
            pass

    # Español con barra: "11/04/2026 20:32"
    m = _RE_BARRAS.search(t)
    if m:
        try:
            hh, mm, ss = _hora_en(t, m.end())
            return datetime(int(m.group(3)), int(m.group(2)), int(m.group(1)),
                            hh, mm, ss, tzinfo=MADRID)
        except ValueError:
            pass

    # Español: "11 abril 2026, 20:32" / "11 de abril de 2026" / "11 abr."
    m = _RE_ES.search(t)
    if m:
        try:
            anio = int(m.group(3)) if m.group(3) else ref.year
            hh, mm, ss = _hora_en(t, m.end())
            return datetime(anio, _MESES[m.group(2).lower()], int(m.group(1)),
                            hh, mm, ss, tzinfo=MADRID)
        except (ValueError, KeyError):
            pass

    return None


def es_reciente(fecha: datetime, ref: datetime = None, horas: int = VENTANA_HORAS) -> bool:
    """True si `fecha` no es anterior a `ref - horas`.

    Las fechas futuras se aceptan (no son «antiguas»): suelen ser ruidos de
    zona horaria o anuncios de estrenos próximos.
    """
    if fecha is None:
        return False
    ref = _a_madrid(ref) if ref else datetime.now(MADRID)
    fecha = _a_madrid(fecha)
    return fecha >= ref - timedelta(hours=horas)


def texto_es_reciente(texto, ref: datetime = None, horas: int = VENTANA_HORAS):
    """True/False si se pudo parsear `texto`; None si no contiene fecha.

    `None` = sin información de antigüedad (el llamante decide).
    """
    fecha = parsear_fecha(texto, ref=ref)
    if fecha is None:
        return None
    return es_reciente(fecha, ref=ref, horas=horas)


def extraer_fecha_de_texto(texto, ref: datetime = None):
    """Busca una fecha absoluta dentro de un título/texto libre → datetime|None.

    No interpreta años sueltos ("El nido (2026)"): hace falta día + mes
    (y opcionalmente año u hora).
    """
    if not texto:
        return None
    t = str(texto)
    m = _RE_BARRAS.search(t) or _RE_ISO.search(t) or _RE_ES.search(t)
    if not m:
        return None
    # Reutiliza el parseo desde la fecha encontrada (conserva la hora si la hay)
    return parsear_fecha(t[m.start():], ref=ref)
