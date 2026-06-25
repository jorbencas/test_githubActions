# Contexto del proyecto — test_githubActions (Tech Pulse)

**Última actualización**: 2026-06-25 (herramientas + actualizar_recursos.py)
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

### Language Guides
- Generados por `gen_lang_guides.py` (independiente, no referenciado por workflows)

### Dashboard HTML
- `public/index.html` con filtros por canal/semana, grid, resumen AI
- Desplegado en Surge.sh tras cada ejecución del scraper

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
5. `fix_challenges.py` → reescribe MDX desde BD local (`--ai` para regenerar con Gemini)
6. `clean_news.py` → mantiene `all_news.json` desde `noticias_historico.json`

### Base de datos de soluciones
- `solutions_data.py` → 105 entradas básicas (py/js) extraídas de `fix_challenges.py`
- `solutions_db.py` → 5 entradas curadas (12 lenguajes + Big-O + test cases) + merge con extended
- `lookup()` → soporta claves completas (python) y cortas (py/js)

## Archivos

### Scripts activos
- `downloadFile.py` (orcestrador principal)
- `hunt_challenges.py` (cacería de retos)
- `fix_challenges.py` (reescritura BD local + `--ai`)
- `clean_news.py` (limpieza trimestral)
- `optimize.py` (optimización de imágenes)
- `gen_lang_guides.py` (guías de lenguaje, independiente)
- `actualizar_recursos.py` (fusión de herramientas → resources.mdx del blog)
- `local_run.py` (dev runner)

### Módulos compartidos
- `utils.py` (AI helpers: solución, recap, imagen, traducción)
- `solutions_db.py` (lookup unificado)
- `solutions_data.py` (105 soluciones extendidas + generadores)
- `constants_downloadfile.py` (config central: API keys, fuentes, templates, prompts)

### Tests
- `tests/test_solutions_db.py` (13 tests)
- `tests/test_content_filter.py` (20 tests)
- Comando: `.venv/bin/python -m unittest discover tests/ -v`

### Workflows
- `.github/workflows/scraper_workflow.yml` (sábados) — incluye paso `Actualizar resources.mdx con nuevas herramientas`
- `.github/workflows/hunt_challenges.yml` (domingos + manual)
- `.github/workflows/clean_news.yml` (trimestral + manual)
- `.github/workflows/tests.yml` (manual + tras scraper/hunt)

## Reglas importantes
- Siempre ejecutar tests tras cambios: `.venv/bin/python -m unittest discover tests/ -v`
- Al modificar `constants_downloadfile.py`, verificar con dry-run si es posible
- Si se añade fuente, agregar a `FUENTES` en `constants_downloadfile.py` y actualizar este documento
- Para sitios JS complejos (MIT Tech Review, DeepMind), intentar con Playwright o RSS feed como fallback
- Los retos semanales NO se regeneran si el `.mdx` ya existe
- Todas las rutas de salida se leen de `CONFIG` en `constants_downloadfile.py`
