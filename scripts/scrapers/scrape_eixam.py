#!/usr/bin/env python3
"""
scrape_eixam.py — Recopila TODA la información disponible sobre la película
"Eixam" (Enjambre, 2026), thriller rural dirigido por Óscar Bernàcer.

Reúne y va archivando a lo largo del tiempo: trailers, fotos, artículos,
noticias, críticas, reviews, primeras impresiones, pósters, primeras imágenes,
críticas de todos los medios y entrevistas a actores.

La salida se acumula (deduplicada por URL) en:
    files/eixam_pelicula.json

Cada entrada se clasifica por tipo (trailer, foto, poster, entrevista, critica,
noticia, video, fotograma, otro) y se guarda con su fecha, medio y enlace.

Uso:
    python scripts/scrapers/scrape_eixam.py                 # recopila y archiva
    python scripts/scrapers/scrape_eixam.py --dry-run       # muestra sin guardar
    python scripts/scrapers/scrape_eixam.py --enviar        # además envía resumen a Telegram
"""
import argparse
import asyncio
import html
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_DIR = SCRIPT_DIR.parent.parent
sys.path.insert(0, str(REPO_DIR))

PELICULA = "Eixam"
PELICULA_ES = "Enjambre"
OUTPUT_PATH = Path(REPO_DIR) / "files" / "eixam_pelicula.json"

# Términos de búsqueda con variantes (título original + título español)
QUERIES = [
    "Eixam Óscar Bernàcer",
    "Eixam película",
    "Eixam Enjambre 2026",
    "Enjambre película Óscar Bernàcer",
    "Enjambre 2026 película",
    "Enjambre óscar bernacer estreno",
    "Eixam crítica",
    "Enjambre crítica reseña",
    "Eixam tráiler trailer",
    "Enjambre tráiler oficial",
    "Eixam Pablo Molinero",
    "eixam Cristina Fernández Pintado",
    "eixam Malpàs",
    "eixam Bejís rodaje",
]

# Términos para vídeos de YouTube (más cortos y orientados a tráilers/clips)
YT_QUERIES = [
    "eixam película",
    "eixam enjambre tráiler",
    "eixam óscar bernàcer",
    "enjambre eixam estreno 2026",
    "eixam thriller rural",
]

# Búsquedas en Contraste (revista de cine, WordPress RSS)
CONTRASTE_QUERIES = [
    "eixam enjambre",
    "enjambre eixam",
    "eixam bernàcer",
]

# Directorios / medios de reseñas específicos consultados vía Google News.
# SOLO se busca el título original "eixam" (referencia inequívoca de esta película),
# porque "enjambre" mezclaría fichas de otras películas homónimas (2020, 2003...).
SITIOS_RESENIAS = [
    ("decine21.com", "eixam"),
    ("contraste.info", "eixam"),
    ("butacaancha", "eixam"),
    ("fotogramas.es", "eixam"),
    ("cinemaldito.com", "eixam"),
    ("aullidos.com", "eixam"),
    ("ecartelera", "eixam"),
    ("sensa cine", "eixam"),
    ("filmaffinity", "eixam"),
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Accept": "application/xml,application/json,text/html,*/*;q=0.8",
    "Accept-Language": "es-ES,es;q=0.9,en;q=0.8",
}

BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
# Se envía al mismo canal/secret que usa el envío de imágenes de buenos días (SALUDO_CHAT_ID)
CHAT_ID = os.environ.get("SALUDO_CHAT_ID", os.environ.get("TIPS_CHAT_ID", ""))

# =============================================================================
# Sistema de relevancia: señales positivas y negativas para evitar falsos positivos
# "Enjambre" aparece en muchas obras y contextos (serie Donald Glover/Swarm,
# películas homónimas, abejas/apicultura, aviación, iOS, ciencia, etc.).
# Solo aceptamos resultados con suficientes señales positivas y ninguna negativa.
# =============================================================================

# Señales fuertes y específicas de ESTA película (la vuelven inequívoca)
SENALES_FUERTES = [
    "óscar bernàcer", "oscar bernacer", "bernàcer", "pablo molinero",
    "cristina fernández pintado", "cristina fernandez pintado",
    "maría maroto", "maria maroto", "pablo derqui", "marta belenguer",
    "jordi aguilar", "glòria march", "gloria march", "àngel fígols",
    "àngel fígols", "malpàs", "bejís", "bejis", "a contracorriente",
    "nadal", "lluc", "silvia", "alba", "comunidad valenciana",
    "atlàntida mallorca", "atlantida mallorca", "corte y confección",
    "nakamura films", "primer largometraje de ficción",
]

# Señales positivas genéricas de cine/película (refuerzan pero no bastan solas)
SENALES_CINE = [
    "película", "pelicula", "cine", "film", "estreno", "largometraje",
    "tráiler", "trailer", "reparto", "director", "dirección", "direccion",
    "crítica", "critica", "reseña", "resena", "review", "cartel", "póster",
    "poster", "fotograma", "rodaje", "taquilla", "pantalla", "cineasta",
    "industria del cine", "actores", "actriz", "guion", "banda sonora",
]

# Contextos de "enjambre" que NO son esta película (se descartan siempre)
SENALES_NEGATIVAS = [
    "abeja", "abejas", "apicultura", "colmena", "drones", "apiario",
    "miel", "polinización", "polinizacion",
    "donald glover", "swarm", "prime video series", "serie de prime video",
    "hipnotic", "laurent bouzereau", "el exterminador", "exterminador",
    "battle fish", "thor", "marvel", "avengers", "avispas", "machos enjambre",
    "avispa", "jugador", "torneo", "ciencia", "investigación", "investigacion",
    "genética", "genetica", "ordenador", "computadora", "apple", "ios",
    "teléfono", "telefono", "avión", "avion", "helicóptero", "helicoptero",
    "la nueva serie", "serie de la semana", "recomendada", "recomienda",
]

# Años de estrenos de otras películas/series homónimas "Enjambre" que NO son la nuestra:
# si el título menciona un año distinto de 2026, es otra obra (fichas de decine21, etc.).
ANIOS_OTROS = ["2020", "2003", "2005", "2014", "2021", "2019", "2022", "2013", "2025"]

# Umbral de puntuación: mínimo de señales positivas para aceptar
UMBRAL_POSITIVAS = 2


def _relevancia(titulo: str) -> int:
    """Devuelve el nº de señales positivas (fuertes + cine) de un título,
    o -1 si contiene una señal negativa inequívoca."""
    texto = titulo.lower()
    if any(neg in texto for neg in SENALES_NEGATIVAS):
        return -1
    puntuacion = 0
    for s in SENALES_FUERTES:
        if s in texto:
            puntuacion += 1
    for s in SENALES_CINE:
        if s in texto:
            puntuacion += 1
    return puntuacion


def _es_relevante(titulo: str) -> bool:
    """Acepta solo lo claramente relacionado con la película Eixam (Enjambre)."""
    texto = titulo.lower()
    punt = _relevancia(texto)
    if punt < 0:
        return False
    # Fichas de otras películas/series homónimas: si el título indica un año
    # distinto de 2026, no es la nuestra.
    if any(a in texto for a in ANIOS_OTROS):
        return False
    # Requiere que aparezca el título de la peli o el director
    if not any(k in texto for k in ("eixam", "enjambre", "bernàcer", "oscar bernacer", "óscar bernàcer")):
        return False
    # Si el título menciona AMBOS títulos (Enjambre y Eixam), es la misma película:
    # señal muy fuerte que basta con un solo refuerzo de cine.
    if "eixam" in texto and "enjambre" in texto:
        return punt >= 1
    # Filtrar el grupo "eixam" suelto en nombre propio (ciencia: enjambre de Eixam)
    if "eixam" in texto and punt == 0 and not any(c in texto for c in SENALES_CINE):
        return False
    return punt >= UMBRAL_POSITIVAS


def _url_real(url: str) -> str:
    """Extrae la URL destino real de servidores de redirección (Bing apiclick)."""
    from urllib.parse import unquote
    m = re.search(r"[?&]url=", url)
    if m:
        real = unquote(url.split(m.group(0), 1)[1].split("&")[0])
        if real.startswith(("http://", "https://")):
            url = real
    m = re.search(r"https?://[^\s\"<>]+", url)
    url = m.group(0) if m else url
    # Normaliza los espejos regionales de MSN (es-us/es-ve/es-mx → mismo artículo)
    if "msn.com/" in url:
        url = re.sub(r"https?://[^/]+/[a-z]{2}-[a-z]{2}/", "https://www.msn.com/", url)
        # Une variantes de categoría (other/cine/entretenimiento/noticias...) del mismo
        # contenido: conserva solo dominio + slug del artículo (vi-... o id-...).
        slug = re.search(r"/(?:vi-|id-?|AA)[A-Za-z0-9_-]+", url)
        if slug:
            url = "https://www.msn.com" + slug.group(0)
    return url

# Palabras que orientan la clasificación por tipo de contenido
CLASIFICADOR = [
    ("trailer", ["tráiler", "trailer", "trailer oficial", "teaser"]),
    ("poster", ["póster", "poster", "cartel"]),
    ("entrevista", ["entrevista", "interview"]),
    ("critica", ["crítica", "critica", "reseña", "review", "críticas"]),
    ("forograma", ["fotograma", "frame"]),
    ("foto", ["foto", "fotograf", "imágenes", "imagenes", "imagen", "imágenes"]),
    ("video", ["vídeo", "video", "clip"]),
    ("noticia", ["estreno", "primeras imágenes", "primera imagen", "rodaje", "se anuncia"]),
]


def clasificar(texto: str) -> str:
    t = texto.lower()
    for tipo, palabras in CLASIFICADOR:
        for p in palabras:
            if p in t:
                return tipo
    return "noticia"


def _rss_google(termino: str, ventana: str = "3h") -> list:
    url = f"https://news.google.com/rss/search?q={quote_plus(termino)}+when:{ventana}&hl=es&gl=ES&ceid=ES:es"
    items = []
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code != 200:
            return []
        texto = r.text
        regex = re.compile(
            r"<item>.*?<title>(.*?)</title>.*?<link>(.*?)</link>.*?<pubDate>(.*?)</pubDate>.*?</item>",
            re.S,
        )
        for m in regex.finditer(texto):
            titulo = html.unescape(m.group(1)).strip()
            enlace = html.unescape(m.group(2)).strip()
            enlace = re.sub(r"^<\!\[CDATA\[|\]\]>$", "", enlace)
            fecha = m.group(3).strip()
            img_url = ""
            im = re.search(r"<img.*?src=\"(.*?)\"", m.group(0))
            if im:
                img_url = html.unescape(im.group(1))
            items.append({
                "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                "medio": "Google News", "imagen": img_url,
            })
    except Exception as e:
        print(f"  ⚠️  Google RSS error ({termino}): {e}")
    return items


def _rss_youtube(termino: str) -> list:
    """Busca vídeos en YouTube (resultados del buscador) extrayendo 'ytInitialData'
    del HTML, ya que el RSS oficial está deshabilitado (400)."""
    url = f"https://www.youtube.com/results?search_query={quote_plus(termino)}"
    items = []
    try:
        r = requests.get(url, timeout=25, headers=HEADERS)
        if r.status_code != 200:
            print(f"  ⚠️  YouTube status {r.status_code} ({termino})")
            return []
        import json
        m = re.search(r"var ytInitialData = (\{.*?\});</script>", r.text, re.S)
        if not m:
            return []
        data = json.loads(m.group(1))
        vistos = set()

        def _caminar(o):
            if isinstance(o, dict):
                v = o.get("videoRenderer")
                if v:
                    vid = v.get("videoId", "")
                    ti = (v.get("title", {}).get("runs", [{}])[0].get("text", "")
                          or v.get("title", {}).get("simpleText", ""))
                    canal = v.get("ownerText", {}).get("runs", [{}])[0].get("text", "")
                    if vid and vid not in vistos:
                        vistos.add(vid)
                        items.append({
                            "titulo": ti, "url": f"https://www.youtube.com/watch?v={vid}",
                            "fecha_pub": "", "fecha_ts": datetime.now().isoformat(),
                            "medio": canal or "YouTube", "imagen": f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
                        })
                for val in o.values():
                    _caminar(val)
            elif isinstance(o, list):
                for x in o:
                    _caminar(x)

        _caminar(data)
    except Exception as e:
        print(f"  ⚠️  YouTube error ({termino}): {e}")
    return items


def _rss_contraste(termino: str) -> list:
    """Busca en Contraste.info (revista de cine) usando su feed RSS de búsqueda
    de WordPress (los directorios de reseñas a menudo salen tarde)."""
    url = f"https://contraste.info/search/{quote_plus(termino)}/feed/rss2/"
    items = []
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code != 200:
            return []
        texto = r.text
        regex = re.compile(r"<item>(.*?)</item>", re.S)
        for m in regex.finditer(texto):
            item = m.group(0)
            titulo = html.unescape(re.search(r"<title>(.*?)</title>", item, re.S).group(1)).strip() if re.search(r"<title>(.*?)</title>", item, re.S) else ""
            enlace = html.unescape(re.search(r"<link>(.*?)</link>", item, re.S).group(1)).strip() if re.search(r"<link>(.*?)</link>", item, re.S) else ""
            fecha = html.unescape(re.search(r"<pubDate>(.*?)</pubDate>", item, re.S).group(1)).strip() if re.search(r"<pubDate>(.*?)</pubDate>", item, re.S) else ""
            if titulo and enlace:
                items.append({
                    "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                    "medio": "Contraste", "imagen": "",
                })
    except Exception as e:
        print(f"  ⚠️  Contraste error ({termino}): {e}")
    return items


def _rss_bing(termino: str) -> list:
    url = f"https://www.bing.com/news/search?q={quote_plus(termino)}&format=rss"
    items = []
    try:
        r = requests.get(url, timeout=20, headers=HEADERS)
        if r.status_code != 200:
            return []
        texto = r.text
        regex = re.compile(r"<item>.*?</item>", re.S)
        for m in regex.finditer(texto):
            item = m.group(0)
            titulo = html.unescape(re.search(r"<title>(.*?)</title>", item, re.S).group(1)).strip() if re.search(r"<title>(.*?)</title>", item, re.S) else ""
            enlace = html.unescape(re.search(r"<link>(.*?)</link>", item, re.S).group(1)).strip() if re.search(r"<link>(.*?)</link>", item, re.S) else ""
            fecha = html.unescape(re.search(r"<pubDate>(.*?)</pubDate>", item, re.S).group(1)).strip() if re.search(r"<pubDate>(.*?)</pubDate>", item, re.S) else ""
            fuente = html.unescape(re.search(r"<News:Source>(.*?)</News:Source>", item, re.S).group(1)).strip() if re.search(r"<News:Source>(.*?)</News:Source>", item, re.S) else ""
            img_url = ""
            im = re.search(r"<News:Image.*?<News:Url>(.*?)</News:Url>", item, re.S) or re.search(r"<Image.*?<Url>(.*?)</Url>", item, re.S)
            if im:
                img_url = html.unescape(im.group(1))
            if titulo and enlace:
                items.append({
                    "titulo": titulo, "url": enlace, "fecha_pub": fecha, "fecha_ts": datetime.now().isoformat(),
                    "medio": fuente or "Bing News", "imagen": img_url,
                })
    except Exception as e:
        print(f"  ⚠️  Bing RSS error ({termino}): {e}")
    return items


def _anexar(items, resultados, vistos):
    """Añade a resultados los items relevantes y no duplicados."""
    for it in items:
        if not _es_relevante(it["titulo"]):
            continue
        url = _url_real(it["url"])
        if not url or url in vistos:
            continue
        vistos.add(url)
        it["url"] = url
        it["tipo"] = clasificar(it["titulo"])
        it["relevancia"] = _relevancia(it["titulo"])
        it["pelicula"] = PELICULA
        resultados.append(it)


def recopilar() -> list:
    resultados = []
    vistos = set()
    # Buscar tanto lo reciente (3h) como lo de la última semana (7d) para no perder
    # artículos que salieron fuera de la última ventana horaria.
    for termino in QUERIES:
        grupos_google = [_rss_google(termino, "3h"), _rss_google(termino, "7d")]
        for items in grupos_google:
            _anexar(items, resultados, vistos)
    for termino in QUERIES:
        _anexar(_rss_bing(termino), resultados, vistos)
    for termino in YT_QUERIES:
        _anexar(_rss_youtube(termino), resultados, vistos)
    for termino in CONTRASTE_QUERIES:
        _anexar(_rss_contraste(termino), resultados, vistos)
    # Medios de reseñas específicos, vía Google News acotado al dominio del sitio.
    # Se busca solo el título original "eixam" para evitar fichas de películas
    # homónimas de otros años.
    for dominio, termino in SITIOS_RESENIAS:
        for it in _rss_google(f"site:{dominio} {termino}", "7d"):
            _anexar([it], resultados, vistos)
    return resultados


def cargar_existente():
    if OUTPUT_PATH.exists():
        try:
            return json.loads(OUTPUT_PATH.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


# =============================================================================
# Validación opcional con IA (Gemini). Se usa cuando hay GEMINI_API_KEY para
# descartar falsos positivos difíciles de identificar solo con reglas.
# =============================================================================
def _validar_ia(items) -> list:
    """Usa Gemini para confirmar si cada título pertenece a la película
    Eixam (Enjambre) de Óscar Bernàcer. Devuelve los items confirmados."""
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        return items
    if not items:
        return items
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
        numerados = "\n".join(f"{i+1}. {it['titulo']} — {it['url']}" for i, it in enumerate(items))
        prompt = (
            "Eres un experto en cine. Determina cuáles de los siguientes titulares se refieren "
            "EXCLUSIVAMENTE a la película española 'Eixam' (Enjambre, 2026), un thriller rural "
            "dirigido por Óscar Bernàcer con Pablo Molinero y Cristina Fernández Pintado, cuya "
            "historia transcurre en la aldea de Malpàs.\n"
            "NO cuentan: otras películas/series llamadas 'Enjambre' (ej. Swarm de Donald Glover, "
            "Hypnotic, series de abejas/apicultura, ciencia, aviación).\n"
            "Responde SOLO con la lista de números de los titulares que SÍ son sobre esta película, "
            "separados por comas, sin texto adicional. Ejemplo: 1,3,5\n\n"
            f"{numerados}"
        )
        resp = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
        texto = (resp.text or "").strip()
        aceptados = set()
        for part in re.findall(r"\d+", texto):
            idx = int(part)
            if 1 <= idx <= len(items):
                aceptados.add(idx - 1)
        if not aceptados and texto:
            # Si la IA no devuelve nada pero hay texto, no filtramos (fail-open parcial):
            return items
        return [it for i, it in enumerate(items) if i in aceptados]
    except Exception as e:
        print(f"  ⚠️  Validación IA opcional no disponible ({e}) — sigo con filtros locales.")
        return items


def main():
    parser = argparse.ArgumentParser(description="Recopila info sobre la película Eixam (Enjambre)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra resultados sin guardar")
    parser.add_argument("--enviar", action="store_true", help="Envía resumen a Telegram")
    args = parser.parse_args()

    print(f"🎬 Recopilando información sobre '{PELICULA}' ({PELICULA_ES})...")

    nuevos = recopilar()
    # Filtrado adicional con IA (solo si hay GEMINI_API_KEY) para reducir falsos positivos
    nuevos = _validar_ia(nuevos)
    existentes = cargar_existente()
    urls_existentes = {e["url"] for e in existentes}

    realmente_nuevos = [n for n in nuevos if n["url"] not in urls_existentes]

    # Conteo por tipo de lo que hay acumulado + lo nuevo
    todos = existentes + realmente_nuevos
    por_tipo = {}
    for t in todos:
        tipo = t.get("tipo", "noticia")
        por_tipo[tipo] = por_tipo.get(tipo, 0) + 1

    print(f"\n📚 Previamente archivados: {len(existentes)}")
    print(f"✨ Nuevos encontrados ahora: {len(realmente_nuevos)}")
    print(f"📊 Total archivo: {len(todos)}")
    print("\nDistribución por tipo:")
    for tipo, n in sorted(por_tipo.items(), key=lambda x: -x[1]):
        print(f"   • {tipo}: {n}")

    if realmente_nuevos:
        print("\n🆕 Nuevos elementos:")
        for n in realmente_nuevos[:30]:
            print(f"   [{n['tipo']}] {n['titulo'][:80]}")
            print(f"        {n['url']}")

    if args.dry_run:
        print("\n--- DRY RUN: no se guarda nada ---")
        return

    if realmente_nuevos:
        OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT_PATH.write_text(json.dumps(todos, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n💾 Guardado: {len(todos)} entradas en {OUTPUT_PATH}")
    else:
        print("\n✅ Sin novedades: no hay contenido nuevo que archivar.")

    if args.enviar:
        _enviar_telegram(realmente_nuevos, por_tipo, len(todos))


def _enviar_telegram(nuevos, por_tipo, total):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  TIPS_BOT_TOKEN / SALUDO_CHAT_ID no configurados; no se envía.")
        return
    try:
        msg_parts = [f"🎬 *Eixam (Enjambre)* — Novedades recopiladas\n"
                     f"Nuevos: {len(nuevos)} · Total archivo: {total}"]
        tipos = " · ".join(f"{k}: {v}" for k, v in sorted(por_tipo.items()))
        msg_parts.append(tipos)
        for n in nuevos[:10]:
            msg_parts.append(f"▫️ [{n['tipo']}] {n['titulo'].replace('*', '')}\n{n['url']}")
        msg = "\n".join(msg_parts)[:4000]
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        r = requests.post(url, data={"chat_id": CHAT_ID, "text": msg, "parse_mode": "Markdown"}, timeout=60)
        print("✅ Resumen enviado a Telegram." if r.status_code == 200 else f"❌ Telegram error {r.status_code}")
    except Exception as e:
        print(f"❌ Error enviando Telegram: {e}")


if __name__ == "__main__":
    main()