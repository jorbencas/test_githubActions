# Contexto del proyecto — test_githubActions (Tech Pulse)

**Última actualización**: 2026-06-26 (dashboard: filtros por sección, fallback thumbnails YouTube, fix JSON-LD)
**Stack**: Python 3.11, asyncio, Gemini API, BeautifulSoup4, aiohttp, GitHub Actions
**Dashboard**: `http://jorbencasdownloaderdocument.surge.sh`
**Blog destino**: `jorbencas/blog` (PRs automáticos)
**Idioma**: Español (con traducción automática desde inglés)

## Contenido generado

### Weekly Tech Recaps
- Generados por `downloadFile.py` → `generar_blog_astro()`
- Archivos `.md` en `auto-news/` con frontmatter
- Secciones: introducción, noticias destacadas, herramienta, TL;DR, sneak peek, nota personal
- Template: `MD_TEMPLATE` en `constants_downloadfile.py`
- AI: `obtener_recap_semanal_ia()` en `utils.py` (Gemini 2.5 Flash/Pro)
- Frecuencia: sábados vía `scraper_workflow.yml`

### Coding Challenges
- Generados por `hunt_challenges.py` (scraping web + AI 3-tier fallback)
- Archivos `.mdx` en `auto-challenges/` con Big-O, test cases, `<Challenge>` component
- 12 lenguajes Codeember en rotación semanal determinista (seeded por ISO week)
- Template: `RETO_MD_TEMPLATE` en `constants_downloadfile.py`
- Frecuencia: dominical vía `hunt_challenges.yml`

### Dashboard HTML
- `public/index.html` con filtros por sección, grid, resumen AI
- Cada sección (noticias, vídeos) tiene su propio filtro de tiempo (`#news-week-filters`, `#video-week-filters`) + canal (`#news-channel-filters`, `#video-channel-filters`)
- Plantilla en `constants_downloadfile.py` (`HTML_TEMPLATE`) — escapado de llaves `{{`/`}}` en JSON-LD para compatibilidad con `str.format()`. Parámetros: `{fecha_hoy}`, `{resumen}`, `{api_url}`, `{api_token}`.
- Fallback visual en thumbnails de YouTube si la imagen no carga (gradiente `#0f172a`→`#1e293b` + nombre del canal)
- Mensaje de estado vacío para vídeos: `"No hay vídeos en este período."`
- SEO completo: meta author (Jorge Beneyto Castelló), OG tags, Twitter Cards, JSON-LD WebSite
- CSS móvil mejorado: `scrollbar-gutter: stable`, mejor disposición de chips, tipografía responsive, stat-cards apiladas
- Desplegado en Surge.sh tras cada ejecución del scraper

### Dashboard JS (`public/script.js`)
- Estado de filtros separado: `selSemanaNoticias` / `selSemanaVideos` (antes global `selSemana`)
- `generarSelectSemanas(items, prefix)` — genera select semanal reutilizable con optgroups por mes
- `renderNewsWeekFilters()` / `renderVideoWeekFilters()` — renderizan su propio chip "Últimas 2 Semanas" + selector de archivo
- Funciones de filtro independientes: `filtrarSemanaNoticias()`, `filtrarSemanaNoticiasDesdeSelector()`, `filtrarSemanaVideos()`, `filtrarSemanaVideosDesdeSelector()`
- `itemDentroSemana(itemTS, selector)` — recibe el selector de estado en lugar de usar variable global
- Cards de vídeo: quitado `aspect-ratio: 16/9` y `contain: layout style` del wrapper. Ahora el thumb tiene su propio contenedor con aspect-ratio por tipo. Imagen con `onerror` que oculta el img y muestra fallback con gradiente + nombre del canal.

### Dashboard CSS (`public/styles.css`)
- `.video-thumb-link` — contenedor del thumbnail, `aspect-ratio` por tipo (16/9 normal/live, 9/16 shorts)
- `.video-thumb` — wrapper relativo para img + fallback
- `.video-thumb-img` — imagen cover full-size
- `.video-thumb-img.errored` — `display: none` cuando falla la carga
- `.video-thumb-fallback` — gradiente oscuro, oculto por defecto; `.visible` lo muestra en flex centrado
- Grid: `minmax(220px, 1fr)` → `minmax(280px, 1fr)`

## Fuentes de datos

### YouTube (canales tech)
MoureDev, Midudev, Pelado Nerd, HolaMundo, FreeCodeCamp, DotCSV, DeBug, Víctor Robles, Fazt, Clipset, CodelyTV, EDteam, Programa Con Arnau, El Pingüino de Mario, Carlos Azaustre, Código Facilito, Applesfera, etc.

### Web (45+ fuentes)
TechCrunch (IA), The Verge, Wired, Ars Technica, Hacker News, Slashdot, GitHub Blog, OpenAI, Google AI, NVIDIA Blog, Dev.to, Xataka, Genbeta, ADSL Zone, MuyComputer, ComputerHoy, Hipertextual, El País Tecnología, HobbyConsolas, Mixx.io, Hugging Face Blog, Anthropic, Meta AI (engineering.fb.com), DeepMind, MIT Technology Review (JS-rendered), VentureBeat AI, Becas, Fundación Carolina, Levante-EMV, HackTheBox, etc.

### Herramientas (fuentes de descubrimiento automático)
- **GitHub Trending** (`https://github.com/trending`) — repos destacados con descripción, lenguaje y estrellas
- **Product Hunt** (`https://www.producthunt.com/`) — lanzamientos de productos tech (best-effort, JS-heavy)

## Arquitectura

### Pipeline principal
1. `optimize.py` → optimiza imágenes
2. `downloadFile.py` → scrapea 35+ fuentes, AI summary, genera recap + dashboard + email + Telegram
   - Separa herramientas (tipo: "herramienta") del flujo de noticias
   - Guarda herramientas descubiertas en `files/herramientas.json` (acumulativo, máx 200)
3. `actualizar_recursos.py` → fusiona herramientas nuevas en `resources.mdx` del blog (ejecutado en workflow tras checkout del blog)
4. `hunt_challenges.py` → scrapea retos, genera soluciones (DB→AI→generic)
5. `clean_news.py` → mantiene `all_news.json` desde `noticias_historico.json`

### Base de datos de soluciones
- `solutions_data.py` → 105 entradas básicas (py/js) extraídas de `fix_challenges.py`
- `solutions_db.py` → 5 entradas curadas (12 lenguajes + Big-O + test cases) + merge con extended
- `lookup()` → soporta claves completas (python) y cortas (py/js)

## Archivos

### Scripts activos
- `downloadFile.py` (orcestrador principal)
- `hunt_challenges.py` (cacería de retos)
- `clean_news.py` (limpieza trimestral)
- `optimize.py` (optimización de imágenes)
- `actualizar_recursos.py` (fusión de herramientas → resources.mdx del blog)

### Módulos compartidos
- `utils.py` (AI helpers: solución, recap, imagen, traducción)
- `solutions_db.py` (lookup unificado)
- `solutions_data.py` (105 soluciones extendidas + generadores)
- `constants_downloadfile.py` (config central: API keys, fuentes, templates, prompts)

### Workflows
- `.github/workflows/scraper_workflow.yml` (sábados) — incluye paso `Actualizar resources.mdx con nuevas herramientas`
- `.github/workflows/hunt_challenges.yml` (domingos + manual)
- `.github/workflows/clean_news.yml` (trimestral + manual)

## Reglas importantes
- Al modificar `constants_downloadfile.py`, verificar con dry-run si es posible. El `HTML_TEMPLATE` usa `str.format()`, escapar llaves literales como `{{`/`}}`.
- Si se añade fuente, agregar a `FUENTES` en `constants_downloadfile.py` y actualizar este documento
- Para sitios JS complejos (MIT Tech Review, DeepMind), intentar con Playwright o RSS feed como fallback
- Los retos semanales NO se regeneran si el `.mdx` ya existe
- Todas las rutas de salida se leen de `CONFIG` en `constants_downloadfile.py`
- **Git restrictions**: NEVER hacer `git push`, `git pull`, o `git fetch`. Solo commit local.
