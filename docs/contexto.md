# Contexto del proyecto — test_githubActions (Tech Pulse)

**Última actualización**: 2026-07-01 (fix cache.py + input fondo blanco + cambios menores)
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
- Filtros: tipo de fuente, categoría, tipo Tech/RSS (`#news-badge-filters`), fuente RSS (`#news-rss-filters`), tiempo (`#news-week-filters`), canal (`#news-channel-filters`)
- Multimedia con tabs: YouTube/TikTok/Instagram (`#multimedia-tabs`), filtros de tiempo (`#video-week-filters`) + canal (`#video-channel-filters`), contenido en `#multimedia-content`
- Ranking GitHub Stars: top 20 repos ordenados por estrellas, con filtro por nombre/lenguaje
- Sección de Tendencias: Google Trends + TikTok, filtrable por tipo (`#trend-type-filters`)
- Stats bar con conteos de noticias Tech, Multimedia
- Desplegado en Surge.sh tras cada ejecución del scraper

### Reference data (data.json)
- `skills`: 5 categorías (Programación, IA/ML, Cloud/DevOps, Seguridad, Datos)
- `llms`: Propietarios, Open Source, Especializados, Multi-modal
- `lenguajes`: Web, Sistema, Datos/IA, Mobile, Empresarial
- `frameworks`: Frontend, Backend, Mobile/Desktop, CSS/UI
- `librerias`: IA/ML, Testing, DevOps, Utilidades
- Se renderiza en dashboard como sección colapsable "📚 Referencia"

### Dashboard JS (`public/script.js`)
- **Store pattern**: `const store = {...}` centraliza 10+ variables de estado global (semana, categoría, badge, canal, tipoFuente, tab, trendType, etc.)
- **Generic chip factory**: `renderChips()` única función para todos los filtros de chips. `renderCanalChips()` para canales con imagen.
- **Helpers puros**: `limpiarFuente()`, `tipoFuente()`, `tipoMultimedia()`, `dominioUrl()`, `itemEnSemana()`, `faviconSrc()`, `chipImg()` — sin side effects.
- **Filtros unificados**: `aplicarFiltrosNoticias()` y `aplicarFiltrosVideos()` leen del store, sin duplicación de lógica.
- `DATA_URL` apunta a `data.json`. Filtros combinables: tipo de fuente, semana, categoría, badge, origen RSS, canal.
- **Sección de tendencias**: `renderTrends()` renderiza Google Trends + TikTok, filtrable por tipo vía `store.trendType`.
- Multimedia separada en tabs: YouTube / TikTok / Instagram con `store.tabMultimedia` y `tipoMultimedia(item)`.
- `ALL_YT_CHANNELS` (22 canales) siempre aparecen en chips aunque tengan 0 items en el período.
- Chips con favicon via Google favicon service + `onerror` fallback.

### Dashboard CSS (`public/styles.css`)
- Badges definidos como clases: `.badge-tech` (azul), `.badge-rss` (celeste), `.badge-cat` (púrpura)
- Fallback visual en thumbnails de YouTube con gradiente oscuro
- Grid responsive: `minmax(280px, 1fr)`
- Chips redondeados con `.chip-img` para avatares/favicons

## Fuentes de datos

### YouTube (canales tech)
MoureDev, Midudev, Pelado Nerd, HolaMundo, FreeCodeCamp, DotCSV, DeBug, Víctor Robles, Fazt, Clipset, CodelyTV, EDteam, Programa Con Arnau, El Pingüino de Mario, Carlos Azaustre, Código Facilito, Applesfera, Ringa Tech, Nethermind, LinkTV, Programador X + varios más.

### Web (60+ fuentes HTML)
TechCrunch, The Verge, Wired, Ars Technica, Hacker News, Slashdot, GitHub Blog, OpenAI, Google AI, NVIDIA Blog, Dev.to, Xataka, Genbeta, ADSL Zone, MuyComputer, ComputerHoy, Hipertextual, El País Tecnología, HobbyConsolas, Mixx.io, Hugging Face Blog, Anthropic, Meta AI, DeepMind, MIT Tech Review, VentureBeat AI, Fundación Carolina, Levante-EMV, HackTheBox, etc.

### RSS (22 fuentes, quick=True para tier light)
OpenAI Blog, Anthropic Blog, Google DeepMind, Meta AI Blog, Mistral AI News, GitHub Engineering, Stack Overflow Blog, Hacker News, LangChain Blog, Google AI Blog, MIT Tech Review AI, Google Search Central, Google Developers, Moz Blog SEO, Search Engine Journal, Wired AI, The Verge AI, TechCrunch AI, Ars Technica AI, Dev.to, Cohere RSS, Hugging Face Daily Papers

### Instagram (web scraping best-effort)
This Week in React, Python Hub (nueva)

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
| `scrape_trends.py` | Playwright: Google Trends + TikTok (solo a `trends.json`, no contamina `noticias_historico.json`) | `files/trends.json` |
| `generate_weekly.py` | AI recap + dashboard HTML + data.json → `auto-news/` + `public/` | `public/index.html`, `public/data.json` |
| `send_email.py` | Mailgun newsletter con resúmenes por noticia + párrafo introductorio IA del lote (solo news, sin multimedia) | — |
| `send_telegram.py` | Telegram con TTS por noticia, dedup vía `telegram_sent.json` | — |
| `clean_news.py` | Validación trimestral de enlaces, poda de muertos | `noticias_historico.json` |
| `optimize.py` | Conversión de imágenes a WebP/AVIF/MP4 | `public/optimizado/` |

### Scraping tiers
El scraping se divide en 3 tiers para balancear frescura vs. carga:
- `--tier light` (cada hora): ~22 fuentes con `"quick": True` (RSS + web rápida)
- `--tier standard` (cada 6h): ~80 fuentes web (sin YouTube)
- `--tier full` (cada 12h / sábados): ~150 fuentes (todo, incluyendo YouTube)

### Módulos compartidos
- `utils.py` (AI helpers + `resumir_lote_noticias` para newsletter + `load_json`/`save_json`)
- `cache.py` (sistema de caché SOLID: `ICacheBackend` ABC, `FileCache` escritura atómica + TTL, `N8nCache` esqueleto webhook, `CacheManager` con `key_fn` inyectable y `flush()`)
- `constants_downloadfile.py` (config central: API keys, 150 fuentes, templates, prompts, CATEGORIAS)

### Content pipeline
1. `scrape_news.py` → `files/noticias_historico.json` (máx 900, dedup automático)
2. `scrape_tools.py` → `files/herramientas.json` (máx 200)
3. `scrape_trends.py` → `files/trends.json`
4. `generate_weekly.py` → `auto-news/YYYY-W{week}-tech-recap.md` + `public/` → Surge
5. `send_email.py` → Mailgun (diario 09:00 UTC)
6. `send_telegram.py` → Telegram con audio TTS (cada 30 min, solo noticias nuevas + YT, filtrados trends/social)
7. Tendencias de `trends.json` se muestran en dashboard (sección 📊 Tendencias) y en email (al final de la newsletter)

### Sistema de caché (cache.py)
- `ICacheBackend` (ABC): interfaz con `load()` y `save()`
- `FileCache`: persistencia en JSON plano, escritura atómica via `os.replace()`
- `N8nCache`: esqueleto para migración a n8n (usa webhook en vez de archivo)
- `CacheManager`: orquesta con TTL opcional y estrategia de clave (`key_fn`)
- Usado por `send_telegram.py` para evitar re-envíos. `telegram_sent.json` se persiste entre ejecuciones vía git push.
- Diseñado para n8n: cambiar `FileCache` → `N8nCache` sin tocar la lógica de negocio.

### Migración a n8n
Ver `docs/n8n_migration.md` para el plan detallado por fases:
1. Fase 1: Caché híbrido (FileCache + N8nCache esqueleto) ← actual
2. Fase 2: Webhook intermedio (N8nCache funcional)
3. Fase 3: Flujos completos en n8n
4. Fase 4: Desactivar GH Actions

### Sistema de templates (constants_downloadfile.py)
- **HTML_TEMPLATE**: genera `public/index.html`. Placeholders: `{fecha_hoy}`, `{resumen}`. Dead code (`api_url`, `api_token`, `api_salud`) eliminado.
- **EMAIL_TEMPLATE**: newsletter Mailgun con estadísticas en preview, bloque de resumen IA (`{contenido_html}` ahora poblado con párrafo generado por `resumir_lote_noticias()`), lista de noticias con resúmenes individuales.
- **MD_TEMPLATE**: weekly recap para blog, 15+ placeholders, bien aprovechado.
- **PROMPT_IMAGEN_TEMPLATE**: prompt para generación de imágenes con `{titulo_post}`.

### Fixes recientes
- **cache.py**: `FileCache.load()` ahora detecta si `telegram_sent.json` es una lista (corrupto) y lo convierte a dict automáticamente, evitando `AttributeError: 'list' object has no attribute 'get'`
- **styles.css / HTML_TEMPLATE**: input `#github-filter` con `background: #fff` explícito para evitar fondo negro en temas oscuros del navegador

### Deduplicación
- `deduplicar_items()` en `utils.py`:
  - URL normalizada (sin `?utm_*`, `#fragment`, trailing `/`, `http`→`https`)
  - Prefijo de título al 85% del más corto
- Se ejecuta en `scrape_news.py` (al scrapear) y `generate_weekly.py` (al generar dashboard)
- Telegram mantiene `telegram_sent.json` para no reenviar

### Workflows (GitHub Actions)
| Workflow | Trigger | Acción |
|----------|---------|--------|
| `scrape_hourly_workflow.yml` | Cada hora | `scrape_news.py --tier light` (RSS + fuentes rápidas) |
| `scrape_6h_workflow.yml` | Cada 6h | `scrape_news.py --tier standard` (fuentes web) |
| `scraper_workflow.yml` | Sábado 07:00 UTC | `--tier full` + tools → weekly → email+Telegram → PR blog → Surge |
| `trends_workflow.yml` | Martes+viernes 08:00 UTC | Playwright: Google Trends + TikTok |
| `send_email_workflow.yml` | Diario 09:00 UTC | Mailgun newsletter (solo noticias, sin multimedia) |
| `send_telegram_workflow.yml` | Cada 30 min | Telegram con TTS (solo noticias + YT, filtrando trends/social) + persistencia `telegram_sent.json` vía git push |
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
  "badge": "Tech",
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
- `downloadFile.py` es un wrapper que delega en los scripts modulares. No contiene lógica propia.
