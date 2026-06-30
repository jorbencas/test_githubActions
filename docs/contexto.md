# Contexto del proyecto — test_githubActions (Tech Pulse)

**Última actualización**: 2026-06-30 (modular scripts, 20 RSS feeds, dedup, Telegram 30min, chip favicons, badge CSS)
**Stack**: Python 3.11, asyncio, Gemini API, BeautifulSoup4, aiohttp, Playwright, GitHub Actions
**Dashboard**: `http://jorbencasdownloaderdocument.surge.sh`
**Blog destino**: `jorbencas/blog` (PRs automáticos)
**Idioma**: Español (con traducción automática desde inglés)

## Contenido generado

### Weekly Tech Recaps
- Generados por `generate_weekly.py`
- Archivos `.md` en `auto-news/` con frontmatter
- Secciones: introducción, noticias destacadas, herramienta, TL;DR, sneak peek, nota personal
- Template: `MD_TEMPLATE` en `constants_downloadfile.py`
- AI: `obtener_recap_semanal_ia()` en `utils.py` (Gemini 2.5 Flash/Pro)
- Frecuencia: sábados vía `scraper_workflow.yml`

### Dashboard HTML
- `public/index.html` generado desde `HTML_TEMPLATE` en `constants_downloadfile.py`
- Filtros: categoría (`#news-category-filters`), tipo Tech/Beca/RSS (`#news-badge-filters`), fuente RSS (`#news-rss-filters`), tiempo (`#news-week-filters`), canal (`#news-channel-filters`)
- Vídeos: filtros de tiempo (`#video-week-filters`) + canal (`#video-channel-filters`)
- Ranking GitHub Stars: top 20 repos ordenados por estrellas, con filtro por nombre/lenguaje
- Stats bar con conteos de noticias Tech/Beca, vídeos, herramientas
- Desplegado en Surge.sh tras cada ejecución del scraper

### Dashboard JS (`public/script.js`)
- `DATA_URL` apunta a `data.json`
- Filtros combinables: semana, categoría, badge, origen RSS, canal
- Chips con favicon fallback via Google favicon service (`//www.google.com/s2/favicons?domain=...`)
- `chipWithImage()` reutilizable para todos los chips de canal/fuente
- `renderGithubRanking()` + `initGithubFilter()` para ranking interactivo

### Dashboard CSS (`public/styles.css`)
- Badges definidos como clases: `.badge-tech` (azul), `.badge-beca` (verde), `.badge-rss` (celeste), `.badge-cat` (púrpura)
- Fallback visual en thumbnails de YouTube con gradiente oscuro
- Grid responsive: `minmax(280px, 1fr)`
- Chips redondeados con `.chip-img` para avatares/favicons

## Fuentes de datos

### YouTube (canales tech)
MoureDev, Midudev, Pelado Nerd, HolaMundo, FreeCodeCamp, DotCSV, DeBug, Víctor Robles, Fazt, Clipset, CodelyTV, EDteam, Programa Con Arnau, El Pingüino de Mario, Carlos Azaustre, Código Facilito, Applesfera, Ringa Tech, Nethermind, LinkTV, Programador X + varios más.

### Web (60+ fuentes HTML)
TechCrunch, The Verge, Wired, Ars Technica, Hacker News, Slashdot, GitHub Blog, OpenAI, Google AI, NVIDIA Blog, Dev.to, Xataka, Genbeta, ADSL Zone, MuyComputer, ComputerHoy, Hipertextual, El País Tecnología, HobbyConsolas, Mixx.io, Hugging Face Blog, Anthropic, Meta AI, DeepMind, MIT Tech Review, VentureBeat AI, Becas, Fundación Carolina, Levante-EMV, HackTheBox, etc.

### RSS (20 fuentes)
OpenAI Blog, Anthropic Blog, Google DeepMind, Meta AI Blog, Mistral AI News, GitHub Engineering, Stack Overflow Blog, Hacker News, LangChain Blog, Google AI Blog, MIT Tech Review AI, Google Search Central, Google Developers, Moz Blog SEO, Search Engine Journal, Wired AI, The Verge AI, TechCrunch AI, Ars Technica AI, Dev.to

### Herramientas (descubrimiento automático)
- **GitHub Trending** (`github.com/trending`) — con subtipos `github`, `github-topic`, `github-collection`
- **Product Hunt** (`producthunt.com`) — best-effort, JS-heavy

## Arquitectura

### Scripts modulares (cada uno independiente)

| Script | Función | Salida |
|--------|---------|--------|
| `scraper_base.py` | Clases base: YouTubeExtractor, WebExtractor (incl. `extraer_rss`), ScraperPro, AvatarRepository, ContentFilter | — (módulo) |
| `scrape_news.py` | Scrapea noticias web + YouTube + RSS → `noticias_historico.json` | `files/noticias_historico.json` |
| `scrape_tools.py` | Scrapea GitHub Trending + Product Hunt → `herramientas.json` | `files/herramientas.json` |
| `scrape_trends.py` | Playwright: Google Trends + TikTok → `trends.json` | `files/trends.json` |
| `generate_weekly.py` | AI recap + dashboard HTML + data.json → `auto-news/` + `public/` | `public/index.html`, `public/data.json` |
| `send_email.py` | Mailgun newsletter con resúmenes por noticia | — |
| `send_telegram.py` | Telegram con TTS por noticia, dedup vía `telegram_sent.json` | — |
| `clean_news.py` | Validación trimestral de enlaces, poda de muertos | `noticias_historico.json` |
| `optimize.py` | Conversión de imágenes a WebP/AVIF/MP4 | `public/optimizado/` |

### Módulos compartidos
- `utils.py` (AI helpers: resumen, recap, imagen, traducción, dedup)
- `constants_downloadfile.py` (config central: API keys, 139 fuentes, templates, prompts, CATEGORIAS)

### Content pipeline
1. `scrape_news.py` → `files/noticias_historico.json` (máx 900, dedup automático)
2. `scrape_tools.py` → `files/herramientas.json` (máx 200)
3. `scrape_trends.py` → `files/trends.json`
4. `generate_weekly.py` → `auto-news/YYYY-W{week}-tech-recap.md` + `public/` → Surge
5. `send_email.py` → Mailgun (diario 09:00 UTC)
6. `send_telegram.py` → Telegram con audio TTS (cada 30 min, solo noticias nuevas)

### Deduplicación
- `deduplicar_items()` en `utils.py`:
  - URL normalizada (sin `?utm_*`, `#fragment`, trailing `/`, `http`→`https`)
  - Prefijo de título al 85% del más corto
- Se ejecuta en `scrape_news.py` (al scrapear) y `generate_weekly.py` (al generar dashboard)
- Telegram mantiene `telegram_sent.json` para no reenviar

### Workflows (GitHub Actions)
| Workflow | Trigger | Acción |
|----------|---------|--------|
| `scraper_workflow.yml` | Sábado 07:00 UTC | scrape news+tools → generate weekly → email+Telegram → PR blog → Surge |
| `trends_workflow.yml` | Martes+viernes 08:00 UTC | Playwright: Google Trends + TikTok |
| `send_email_workflow.yml` | Diario 09:00 UTC | Mailgun newsletter |
| `send_telegram_workflow.yml` | Cada 30 min | Telegram con TTS (noticias nuevas) |
| `clean_news.yml` | Trimestral | Validar enlaces → podar muertos |

### Noticias: estructura de item
```json
{
  "titulo": "...",
  "enlace": "...",
  "fuente": "Fuente X",
  "tipo": "noticia|video|shorts|live|herramienta",
  "f": "dd/mm",
  "fecha_publicacion": "...",
  "fecha_real": "dd/mm/aaaa",
  "ts": "ISO datetime",
  "badge": "Tech|Beca",
  "categoria": "🤖 IA|...",
  "origen": "web|rss",
  "id_video": "(solo YouTube)"
}
```

## Reglas importantes
- Al modificar `constants_downloadfile.py`, verificar con `py_compile`. El `HTML_TEMPLATE` usa `str.format()`, escapar llaves literales como `{{`/`}}`.
- Si se añade fuente, agregar a `FUENTES` en `constants_downloadfile.py` y actualizar este documento.
- Fuentes RSS: usar clave `"rss": "URL"` en FUENTES. El scraper detecta automáticamente `"rss"` y parsea XML (RSS 2.0 o Atom).
- Los weekly recaps NO se regeneran si el `.md` ya existe.
- **Git restrictions**: NEVER hacer `git push`, `git pull`, o `git fetch`. Solo commit local.
- Todas las rutas de salida se leen de `CONFIG` en `constants_downloadfile.py`.
- `downloadFile.py` se mantiene por retrocompatibilidad pero los scripts modulares son los activos.
