# 🛰️ test_githubActions — Tech Automation Ecosystem

![Python](https://img.shields.io/badge/python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![License](https://img.shields.io/github/license/jorbencas/test_githubActions?style=flat-square&label=License)
![Repo size](https://img.shields.io/github/repo-size/jorbencas/test_githubActions?style=flat-square&label=Repo%20size&logo=git)
![Code size](https://img.shields.io/github/languages/code-size/jorbencas/test_githubActions?style=flat-square&label=Code%20size)
![Top language](https://img.shields.io/github/languages/top/jorbencas/test_githubActions?style=flat-square&label=Language)
![Last commit](https://img.shields.io/github/last-commit/jorbencas/test_githubActions?style=flat-square&logo=git&label=Last%20commit)
![Surge](https://img.shields.io/badge/Surge-Live-00ADD8?style=flat-square&logo=vercel&label=Dashboard)

![Scraper](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scraper_workflow.yml?branch=master&style=flat-square&label=Scraper&logo=github)
![Hourly](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_hourly_workflow.yml?branch=master&style=flat-square&label=Hourly&logo=github)
![6h](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_6h_workflow.yml?branch=master&style=flat-square&label=Every%206h&logo=github)
![Resources](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_resources.yml?branch=master&style=flat-square&label=Resources&logo=github)
![Email](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_email_workflow.yml?branch=master&style=flat-square&label=Email&logo=github)
![Telegram](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_telegram_workflow.yml?branch=master&style=flat-square&label=Telegram&logo=github)
![AI Tools](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_ai_tools.yml?branch=master&style=flat-square&label=AI%20Tools&logo=github)
![Tips](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_tips.yml?branch=master&style=flat-square&label=Tips&logo=github)
![Cleanup](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/clean_news.yml?branch=master&style=flat-square&label=Cleanup&logo=github)
![Challenges](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/hunt_challenges.yml?branch=master&style=flat-square&label=Challenges&logo=github)
![Optimize](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/optimize_images.yml?branch=master&style=flat-square&label=Optimize&logo=github)
![Dashboard](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/dashboard_update.yml?branch=master&style=flat-square&label=Dashboard&logo=github)
![Tests](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/tests.yml?branch=master&style=flat-square&label=Tests&logo=github)

Ecosistema de automatización tech que ejecuta **16 workflows de GitHub Actions** formando un pipeline de contenido completamente automatizado. Recolecta de **547 fuentes** (158 canales YouTube, 161 feeds RSS, 225 sitios de web scraping, 89 GitHub Topics, 5 GitHub Repos, 1 Product Hunt), procesa con **IA (Gemini)** y distribuye contenido a múltiples canales.

**Por qué existe:** Cada día aparecen decenas de noticias, vídeos y herramientas nuevas en el mundo tech. Seguir el ritmo manualmente es imposible. Este proyecto lo hace automáticamente: scrapear, procesar, traducir, generar contenido con IA y distribuirlo — todo sin intervención manual.

🚀 **[News Dashboard](http://jorbencasdownloaderdocument.surge.sh)**

---

## 📋 Overview

El ecosistema funciona como una fábrica de contenido tech con 6 etapas principales:

### 1. 🌐 Scraping — Recolección de datos de 547 fuentes

El scraping es la base de todo. Sin datos, no hay contenido que procesar. El sistema tiene **3 niveles de frecuencia**:

- **Cada hora** (`scrape_hourly`): Las fuentes más rápidas (161 RSS + 225 web scraping). Estas fuentes publican noticias cada pocos minutos y necesitan estar al día.
- **Cada 6 horas** (`scrape_6h`): Fuentes estándar que publican menos frecuentemente. Incluye auto-detección de herramientas IA.
- **Una vez al día** (`daily_resources`): GitHub Topics y repos. Estos cambian menos a menudo.

**Por qué 3 niveles:** No todas las fuentes publican a la misma velocidad. TechCrunch publica cada hora, pero GitHub Topics cambia una vez al día. Scrapear todo cada hora sería un desperdicio de recursos; scrapear todo una vez al día significaría perderte noticias importantes.

### 2. 🤖 IA — Procesamiento con Gemini

Una vez recolectados los datos, Gemini (Google AI) procesa:

- **Resúmenes automáticos** de cada noticia (en español)
- **Traducción inteligente** solo de elementos nuevos (flag `traducido`)
- **Generación de contenido** (tips, herramientas, saludos)
- **Deduplicación** por URL y título similar

**Por qué Gemini:** Es rápido, barato y maneja bien español. El fallback local (Ollama + Qwen) cubre cuando Gemini falla.

### 3. 📤 Publicación — Distribución multicanal

El contenido procesado se distribuye a:

- **Email newsletter** (Mailgun): Noticias agrupadas por fuente, con sección de vídeos
- **Telegram**: Noticias en tiempo real + resúmenes de voz (TTS)
- **Dashboard web** (Surge.sh): SSR con filtros, búsqueda y pestañas
- **Blog** (Vercel): Recaps semanales automáticos

### 4. 💡 Tips — Contenido generado con IA

Cada 3 horas se envían tips de IT por Telegram:

- **Tips mixtos** — Gemini genera tips frescos más 5 de la base de datos estática (708 tips)
- **Nunca repite** — tracking en `tips_history.json`
- **Mala/Buena práctica** — contrastes prácticos con código
- **80 categorías** — docker, git, linux, bases de datos, seguridad, programación...

### 5. 🛠️ Herramientas IA — Auto-detección y distribución

El sistema auto-detecta herramientas IA nuevas cada 6 horas:

- **Hugging Face API**: Modelos trending (por descargas) + espacios (por likes)
- **GitHub Search API**: Repos de IA con 200+ estrellas
- **Product Hunt**: Productos top del día

Luego Gemini genera herramientas frescas usando los candidatos auto-detectados como **ALTA PRIORIDAD**.

### 6. 🌅 Saludos — Imágenes generadas con IA

Cada 3 horas se envía una imagen de saludo (Buenos días / Buenas noches):

- **Gemini 3** genera la imagen con IA
- **Fallback**: Pollinations.ai → PIL local
- **11 estilos, 5 públicos, 6 emociones, 14 materias, 13 festivos**
- **Nunca repite**: tracking en `saludos_history.json`

---

## 📡 Sources — 547 Total

| Categoría | Cantidad | Ejemplos | Por qué |
|-----------|----------|----------|---------|
| YouTube channels | 158 | MoureDev, Fernando Herrera, The Engineer's Digest | Tutoriales y noticias en vídeo |
| RSS feeds | 161 | TechCrunch, The Verge, Wired, Ars Technica | Noticias tech de primera mano |
| Web scraping | 225 | Anthropic, Ollama, Mistral, LangChain, Mozilla Hacks | Blogs de empresas de IA |
| Dual (YT + Web) | 4 | MoureDev, Midudev, Carlos Azaustre, Xataka | Fuentes que publican en ambos canales |
| GitHub Topics | 89 | AI, LLM, Docker, Kubernetes, CSS, HTML | Repositorios trending |
| GitHub Repos | 5 | OpenWiki, Meetily, AutoPR, PR-Agent | Proyectos específicos |
| Product Hunt | 1 | Top products daily | Nuevos productos |

### Quick sources (hourly tier)

Las fuentes con `quick: True` se scrapean cada hora porque publican con frecuencia:

- **RSS (161)**: TechCrunch, The Verge, Wired, Ars Technica, Google Blog, Vercel, Docker, Kubernetes, HN, Stack Overflow, Dev.to, NVIDIA...
- **Web scraping (225)**: Anthropic Research, Ollama Blog, Mistral News, Cohere, LangChain, Google Developers, HuggingFace Papers, Mozilla Hacks...
- **Chinese AI**: QbitAI (量子位), 36氪 AI, Qwen, DeepSeek, 01.AI, THUDM/ChatGLM

---

## 📂 Project Structure

```
scripts/
├── scrapers/             🌐 Recolección de datos de 547 fuentes
│   ├── scraper_base.py         Extractores YouTube, Web, ScraperPro (soporte dual source)
│   ├── scrape_news.py          RSS + web + YouTube news (tier estándar incluye dual sources)
│   ├── scrape_tools.py         GitHub Trending + Product Hunt
│   ├── scrape_ai_tools.py      Auto-detección de herramientas IA (HF API + GitHub Search)
│   ├── scrape_agent_skills.py  Scraping skills de agentes IA
│   ├── scrape_concepts.py      Scraping conceptos de programación
│   ├── scrape_eixam.py         Scraping película "Eixam" → Telegram
│   ├── scrape_publicapis.py    Scraping APIs públicas
│   └── screenshot_helper.mjs   Helper de screenshots con Playwright
├── publishers/           📤 Generación y distribución de contenido
│   ├── generate_weekly.py      Recap semanal con IA + dashboard HTML (SSR)
│   ├── manage_resources.py     Paginación, limpieza, reorden de resources.mdx
│   ├── merge_freefordev.py     Merge de recursos free-for-dev
│   ├── send_email.py           Newsletter Mailgun (agrupada por fuente + vídeos, traducción inteligente)
│   └── send_telegram.py        Notificaciones Telegram (solo noticias, traducción inteligente + resúmenes)
├── tools/                🔧 Utilidades de mantenimiento
│   ├── clean_news.py           Validación de enlaces
│   ├── fix_images.py           Pipeline de imágenes (WebP/AVIF + portadas locales)
│   ├── hunt_challenges.py      Generación de retos con IA
│   ├── make_cover_collage.py   Collages de portadas
│   ├── optimize.py             Optimización de imágenes del dashboard
│   └── bump_updated_dates.py   Estampa updatedDate en frontmatter
├── utils/                🧰 Módulos compartidos
│   ├── constants_sources.py        Definición de FUENTES (547 fuentes)
│   ├── constants_downloadfile.py   Re-export de fuentes, templates, configuración
│   ├── constants_retos.py          Configuración de retos
│   ├── constants_templates.py      Templates HTML, email, markdown, prompts IA
│   ├── constants_mdtools.py        Constants para herramientas markdown
│   ├── common.py                   Helpers de JSON, URL, dedup, AI (soporte flag traducido)
│   ├── lang_es.py                  Detección de idioma castellano
│   ├── cache.py                    Cache pluggable (FileCache + CacheManager)
│   ├── ai_categories.json          166 categorías de herramientas IA
│   ├── ai_tools_database.json      DB de herramientas IA
│   ├── concepts_database.json      DB de conceptos de programación
│   ├── saludos_config.json         Configuración de saludos
│   └── tips_database.json          Base de datos de tips (708 tips)
├── tips_generator.py         💡 Tips diarios de IT (Gemini + fallback a DB, nunca repite)
├── ai_tools_generator.py     🛠️  Herramientas IA (Gemini + fallback a DB, 166 categorías)
├── saludo_imagen.py          🌅 Imagen de saludo diaria (Gemini → PIL fallback)
└── solutions/            💡 Base de datos de soluciones
    ├── solutions_db.py            Lookup + generación de soluciones
    └── solutions_data.py          107 soluciones curadas
tests/                    ✅ Suite de tests pytest (168 tests)
├── test_cache.py / test_constants_downloadfile.py
├── test_constants_retos.py / test_fix_images.py
├── test_manage_resources.py / test_solutions_db.py
├── test_ai_features.py / test_utils.py
├── test_bump_updated_dates.py / test_tips_generator.py
└── test_solutions_db.py
public/                   🕰️ Tech Timeline (Surge.sh)
├── index.html            Timeline interactiva 1970-2025
├── css/style.css         Estilos + 14 breakpoints responsive
├── js/app.js             Lógica: parallax, smoke, embers, IntersectionObserver
└── data/events.json      424 eventos con imágenes Wikipedia
```

---

## ⚡ Commands

Todos los scripts se ejecutan con `python -m` desde la raíz del proyecto:

### 🌐 Scraping

| Comando | Descripción | Cuándo usarlo |
|---------|-------------|---------------|
| `python -m scripts.scrapers.scrape_news --tier full` | Scraping completo (RSS + web + YouTube) | Cuando quieras todo el contenido |
| `python -m scripts.scrapers.scrape_news --tier light` | Scraping ligero (solo quick sources) | Para pruebas rápidas |
| `python -m scripts.scrapers.scrape_tools` | GitHub Trending + Product Hunt | Para descubrir herramientas nuevas |
| `python -m scripts.scrapers.scrape_ai_tools` | Auto-detección de herramientas IA | Para alimentar el generador de herramientas |

### 📤 Publicación

| Comando | Descripción | Cuándo usarlo |
|---------|-------------|---------------|
| `python -m scripts.publishers.generate_weekly --blog-path blog` | Generar recap semanal + dashboard (SSR) | Los sábados por la mañana |
| `python -m scripts.publishers.generate_weekly --dashboard-only` | Solo regenerar dashboard HTML (saltar recap IA) | Cuando solo cambias el diseño |
| `python -m scripts.publishers.send_email` | Enviar newsletter Mailgun | Para probar el email |
| `python -m scripts.publishers.send_email --dry-run` | Previsualizar email sin enviar | Siempre antes de enviar |
| `python -m scripts.publishers.send_telegram` | Enviar notificación Telegram con TTS | Para probar Telegram |
| `python -m scripts.publishers.send_telegram --dry-run` | Previsualizar Telegram sin enviar | Siempre antes de enviar |
| `python -m scripts.publishers.manage_resources --blog-path blog --max-cards 500 --clean --reorder --fix-spacing` | Gestionar resources.mdx | Cuando el blog tiene recursos desordenados |
| `python -m scripts.publishers.merge_freefordev --blog-path blog --free-dev-file /tmp/free-for-dev.md` | Merge de recursos free-for-dev | Para añadir nuevos recursos gratuitos |

### 🔧 Mantenimiento

| Comando | Descripción | Cuándo usarlo |
|---------|-------------|---------------|
| `python -m scripts.tools.fix_images --blog-path blog` | Pipeline de imágenes (portadas locales) | Cuando hay posts sin imágenes |
| `python -m scripts.tools.make_cover_collage --ci --blog-path blog` | Collages de portada | Para generar portadas compuestas |
| `python -m scripts.tools.hunt_challenges` | Generación de retos con IA | Cuando quieres nuevos retos |
| `python -m scripts.tools.clean_news` | Validación de enlaces | Para limpiar enlaces rotos |
| `python -m scripts.tools.optimize` | Optimización de imágenes del dashboard | Para reducir tamaño del dashboard |

### 💡 Tips de IT

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.tips_generator` | Envía 10 tips por Telegram |
| `python -m scripts.tips_generator --dry-run` | Previsualiza los tips sin enviar |
| `python -m scripts.tips_generator --list-categories` | Lista las categorías de tips |
| `python -m scripts.tips_generator --stats` | Estadísticas de la base de tips |

### 🛠️ AI Tools

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.ai_tools_generator` | Envía herramienta IA por Telegram |
| `python -m scripts.ai_tools_generator --dry-run` | Previsualiza sin enviar |
| `python -m scripts.ai_tools_generator --list-categories` | Lista las 166 categorías |
| `python -m scripts.ai_tools_generator --stats` | Estadísticas de la base |

### ✅ Testing

| Comando | Descripción |
|---------|-------------|
| `python -m pytest tests/ -v` | Ejecutar todos los tests (168 tests) |
| `python -m pytest tests/test_solutions_db.py -v` | Ejecutar un suite específico |

---

## 🤖 GitHub Actions — 16 Workflows

| Workflow | Horario | Qué hace | Por qué |
|----------|---------|----------|---------|
| **scraper_workflow** | Sáb 07:00 UTC | Generar recap semanal + portadas → PR al blog | Resumen semanal automático |
| **scrape_hourly** | Cada hora | Scraping ligero (RSS + quick sources) | Noticias que publican cada minuto |
| **scrape_6h** | Cada 6 horas | Scraping estándar + auto-detección IA | Fuentes que publican menos |
| **daily_resources** | Diario 06:00 UTC | Scraping herramientas + gestión resources.mdx | GitHub Topics cambian poco |
| **daily_ai_tools** | Cada 3 horas | Herramientas IA via Telegram (Gemini + DB) | Contenido fresco para el bot |
| **daily_tips** | Cada 3 horas | Tips IT via Telegram (Gemini + DB) | Tips prácticos diarios |
| **daily_saludo** | Cada 3 horas | Imágenes Buenos días/noches (Gemini → Telegram) | Saludos automatizados |
| **send_email** | Diario 09:00 UTC | Newsletter Mailgun (agrupada por fuente + vídeos) | Resumen diario por email |
| **send_telegram** | Cada 30 min | Telegram + TTS (cache para dedup) | Noticias en tiempo real |
| **clean_news** | Trimestral | Validación de enlaces | Mantener links vivos |
| **hunt_challenges** | Manual | Generación de retos con IA | Cuando hay cuota disponible |
| **optimize_images** | Dispatch desde blog | Optimización de imágenes | Para el blog |
| **dashboard_update** | Push (JS/CSS/Python/data) | Regenerar + deploy dashboard | Actualizaciones automáticas |
| **translate_descriptions** | Manual | Traducción de descripciones al castellano | Cuando hay descripciones sin traducir |
| **tests** | Push/PR a master | pytest (168 tests) | Calidad de código |
| **eixam_scrape** | Cada 6 horas | Scraping película "Eixam" → Telegram | Seguimiento de la película |

### Arquitectura de Workflows

```
┌─────────────────────────────────────────────────────────────────────┐
│                        RECOLECCIÓN DE DATOS                         │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_hourly   →  cada hora  →  quick sources (161 RSS + 225 web)│
│  scrape_6h       →  cada 6h    →  scraping estándar + auto IA      │
│  daily_resources →  diario     →  herramientas (89 GitHub Topics)   │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                    AUTO-DETECCIÓN DE HERRAMIENTAS IA                │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_ai_tools  →  cada 6h   →  HF Models + Spaces + GitHub     │
│  Output: files/ai_tools_candidates.json (50 herramientas, auto)    │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        PROCESAMIENTO SEMANAL                        │
├─────────────────────────────────────────────────────────────────────┤
│  scraper_workflow  →  Sáb 07:00 UTC                                │
│  ├── Generar recap semanal (IA + Gemini)                           │
│  ├── Generar portadas (Playwright)                                 │
│  └── Push al blog (auto-news + recursos)                           │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DISTRIBUCIÓN                                 │
├─────────────────────────────────────────────────────────────────────┤
│  send_email       →  diario    →  Newsletter Mailgun               │
│  send_telegram    →  cada 30m  →  Telegram + TTS                  │
│  dashboard_update →  en push   →  Deploy Surge.sh                 │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        MANTENIMIENTO                                │
├─────────────────────────────────────────────────────────────────────┤
│  clean_news       →  trimestral →  Validación de enlaces           │
│  hunt_challenges  →  manual    →  Retos con IA                    │
│  optimize_images  →  dispatch  →  Optimización de imágenes        │
│  daily_tips       →  cada 3h   →  Tips IT (Gemini + DB)           │
│  daily_ai_tools   →  cada 3h   →  Herramientas IA (auto + Gemini) │
│  daily_saludo     →  cada 3h   →  Imágenes saludo (Gemini)        │
│  tests            →  en push   →  168 tests pytest                │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Daily IT Tips

Tips diarios de IT enviados a Telegram cada 3 horas via `tips_generator.py`:

- **Generación mixta** — Gemini genera tips frescos más 5 de la base de datos estática, 10 total por ejecución
- **Fallback a DB estática** — 708 tips curados en 80 categorías (docker, git, linux, bases de datos, seguridad, programación...)
- **Nunca repite** — tracking de títulos enviados en `tips_history.json` (persistido via GitHub Actions Cache)
- **Mala/Buena práctica** — tips prácticos incluyen contraste estructurado `❌ Mala práctica / ✅ Buena práctica`
- **Recuperación por agotamiento** — cuando la DB se agota, Gemini genera el lote completo

---

## 🛠️ AI Tools

Herramientas IA enviadas a Telegram cada 3 horas via `ai_tools_generator.py`:

- **Auto-scraping** — `scrape_ai_tools.py` descubre herramientas nuevas cada 6h desde:
  - **Hugging Face API** — modelos trending (por descargas) + espacios (por likes)
  - **GitHub Search API** — repos de IA con 200+ estrellas, actualizados recientemente
  - **Product Hunt** — productos top del día
- **Generación con Gemini** — Gemini genera herramientas frescas usando candidatos auto-detectados como **ALTA PRIORIDAD**, con fallback a una base de datos estática de 107 herramientas curadas
- **166 categorías** — categorizadas en `ai_categories.json` para selección variada
- **Formato completo** — cada herramienta incluye: nombre claro, para qué sirve, enlace oficial (`url`), workflow, posibles integraciones (`combinaciones`), y restricciones/clave (`restricciones`)
- **Nunca repite** — tracking de herramientas enviadas en `ai_tools_history.json` (persistido via GitHub Actions Cache)
- **Prioridad multi-fuente** — herramientas encontradas en múltiples fuentes (HF + GitHub) obtienen máxima prioridad en el prompt de Gemini

### Flujo de auto-scraping

```
Cada 6h (scrape_6h_workflow):
  scrape_ai_tools.py → files/ai_tools_candidates.json
    ├── Hugging Face API (30 modelos + 20 espacios)
    ├── GitHub Search API (repos con 200+ estrellas)
    └── Product Hunt (productos top del día)

Cada 3h (daily_ai_tools):
  ai_tools_generator.py → Telegram
    ├── 1. Cargar ai_tools_candidates.json (ALTA PRIORIDAD)
    ├── 2. Cargar herramientas.json (inspiración)
    ├── 3. Cargar noticias_historico.json (inspiración)
    ├── 4. Prompt de Gemini con todas las fuentes → genera 5 herramientas
    └── 5. Enviar a Telegram
```

---

## 🌅 Saludos

Imágenes de saludo automatizadas (Buenos días / Buenas noches) enviadas a Telegram cada 3 horas via `saludo_imagen.py`:

- **Imagen generada con IA** — Gemini 3 (Nano Banana 2, `gemini-3.1-flash-image`) via la Interactions API
- **Conciencia horaria** — `SALUDOS_TZ_OFFSET` establece el desfase horario local para la ventana de "Buenos días" (5–12h) / "Buenas noches"
- **Variedad** — 11 estilos, 5 públicos, 6 emociones, 14 materias, 13 festivos, 12 temporadas desde `saludos_config.json`, nunca repite
- **Frases inspiradoras** — una frase diaria (día/noche) se dibuja DENTRO de la imagen, en el color dominante de la imagen, más el saludo debajo; nunca repite
- **Imágenes cuadradas** — ratio 1:1 para todas las fuentes (prompt Gemini, Pollinations `1024x1024`, PIL `1024x1024`), el overlay de texto preserva proporciones
- **Cadena de fallback** — si Gemini falla (cuota/429/error): intenta **Pollinations.ai** (imagen desde prompt, sin registro/API key), luego imagen **PIL local**
- **Envío** — `SALUDO_CHAT_ID` (fallback `TIPS_CHAT_ID`, default `-1004296712840`)

---

## 📧 Email Newsletter

La newsletter diaria se envía via Mailgun con:

- **Agrupada por fuente** — noticias organizadas por web (TechCrunch, The Verge, Xataka...)
- **Traducción inteligente** — solo traduce elementos nuevos (flag `traducido`), saltando los ya traducidos
- **Resúmenes persistidos** — resúmenes de IA guardados en JSON para evitar re-resumir
- **Sección de vídeos** — vídeos de YouTube con thumbnail, canal y duración
- **Diseño responsive** — funciona en móvil y escritorio

### Estilos de fuentes

Cada fuente tiene un color e icono personalizado:

| Fuente | Color | Icono |
|--------|-------|-------|
| TechCrunch | `#16a34a` | 📱 |
| The Verge | `#7c3aed` | 🔮 |
| Wired | `#000000` | ⚫ |
| Ars Technica | `#ff4400` | 🔬 |
| Hacker News | `#ff6600` | 🔶 |
| GitHub | `#24292e` | 🐙 |
| Google | `#4285f4` | 🔍 |
| Xataka | `#1d9bf0` | 📰 |
| OpenAI | `#10a37f` | 🤖 |

---

## 🤖 Telegram Notifications

- **Solo noticias** — solo envía elementos de noticias, no enlaces de vídeo
- **Deduplicación** — GitHub Actions Cache (`actions/cache@v4`) persiste `telegram_sent.json` entre ejecuciones
- **TTL** — 7 días de expiración para noticias, 24 horas para mensajes de voz
- **Filtro de tiempo** — solo envía noticias de las últimas 24 horas
- **Audio TTS** — resumen de voz diario a las 21:00 UTC con TODAS las noticias del día (no solo las 5 de la ejecución actual)
- **Traducción inteligente** — omite elementos ya traducidos (flag `traducido`)
- **Resúmenes persistidos** — resúmenes de IA guardados en `noticias_historico.json` para evitar re-resumir

---

## 🕰️ Tech Timeline

Timeline interactiva de la historia de la tecnología (1970-2025), desplegada en Surge.sh.

**Características:**
- **424 eventos** en 9 categorías (languages, frameworks, tools, AI, hardware, internet, companies, opensource, news)
- **168 noticias** cubriendo todos los años desde 1970
- **Imágenes reales** de Unsplash como fondos por era (circuitos, PCs retro, internet, smartphones, IA)
- **6 eras temáticas** con colores, humo y partículas únicas por década
- **Efecto teatro** — parallax de 3 capas que se mueven al hacer scroll
- **Elementos SVG** por era (circuitos, floppys, globos, teléfonos, cerebros)
- **Scroll animations** — tarjetas y años aparecen al hacer scroll (IntersectionObserver)
- **Música ambient** — dron profundo + crujido de fuego (Web Audio API)
- **Responsive** — funciona en todas las resoluciones (320px → ultra-wide)

### Estructura

```
public/
├── index.html          HTML principal
├── css/style.css       Estilos + 14 breakpoints responsive
├── js/app.js           Lógica: parallax, smoke, embers, IntersectionObserver
└── data/events.json    424 eventos con imágenes Wikipedia
```

### Despliegue

Se despliega automáticamente via GitHub Actions en Surge.sh cuando se push-a `public/`.

---

## 📊 Dashboard

Desplegado en Surge.sh. Completamente **server-side rendered (SSR)** — Python genera un único `index.html` con todo el contenido pre-renderizado (noticias, vídeos de YouTube, ranking de GitHub). JavaScript es mínimo y solo maneja filtros interactivos, pestañas y búsqueda.

**Mejoras recientes de UI:**
- **ResourceCard mejorado** — nuevas props `headline`, `features`, `platform` para descripciones estructuradas (retrocompatible)
- **Chips de fuente dual** — fuentes con YouTube y web (MoureDev, Midudev, Carlos Azaustre, Xataka) muestran chips de filtro en ambas secciones
- **Filtros de canal separados** — filtro de noticias usa `news_items` (sin YouTube), filtro de vídeo usa `video_items` (sin web)
- **Badges de tipo** — `📄 Noticia`, `📡 RSS`, `🔧 Herramienta` en tarjetas de noticias; `🎬 Video`, `🩳 Short`, `🔴 Directo` en tarjetas de vídeo
- **Footer** — "Creado con ❤️ y sin ánimo de lucro por @jorbencas" + disclaimer (sin contenido alojado)
- **Dark theme** — gradiente de título de noticias usa `#60a5fa → #3b82f6` en modo oscuro
- **Traducción** — solo nuevos elementos traducidos, flag `traducido` previene re-traducción

Los recaps semanales archivan automáticamente posts viejos (>2 semanas) y fuerzan un-post-por-semana para SEO. Las noticias se agrupan por fuente con deduplicación antes de renderizar.

---

## 🔐 GitHub Secrets

| Secret | Descripción |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del chat/grupo |
| `GEMINI_API_KEY` | API key de Google AI Studio |
| `MAILGUN_API_KEY` | API key de Mailgun |
| `MAILGUN_DOMAIN` | Dominio de Mailgun |
| `EMAIL_USER` | Email de destino |
| `BLOG_TOKEN` | Token de checkout del blog |
| `SALUDO_CHAT_ID` | Chat/grupo para saludos (fallback: `TELEGRAM_CHAT_ID`) |
| `AI_TOOLS_CHAT_ID` | Chat/grupo para herramientas IA (fallback: `TELEGRAM_CHAT_ID`) |
| `TIPS_CHAT_ID` | Chat/grupo para tips IT (fallback: `TELEGRAM_CHAT_ID`) |
| `TOKEN_API_ID` | API ID para Telethon (scraper) |
| `SURGE_TOKEN` | Token de Surge.sh para deploy |
| `DOWNLOADER_API_TOKEN` | Token para el scraper de YouTube |

Variables del repositorio:

| Variable | Descripción |
|----------|-------------|
| `SALUDOS_TZ_OFFSET` | Desfase horario en horas para el saludo (ej. `2` = CEST). Vacío/ausente → UTC |

---

## 🧪 Test Coverage

168 tests pytest cubriendo:
- **Cache** — FileCache, CacheManager, expiración, TTL, limpieza de flush
- **Constants** — configuraciones de fuentes (547 fuentes), templates de email, templates de retos
- **Dual sources** — extracción YouTube + web scraping, renderizado de chips en ambas secciones
- **Email templates** — placeholders, headers de fuente, secciones de vídeo, estilos de botones
- **Pipeline de imágenes** — generación de portadas locales, conversión WebP/AVIF
- **AI features** — 166 categorías, DB tools, generador de herramientas IA, saludo por hora/festivos
- **Resources** — paginación, limpieza, reorden, gestión de tarjetas, dedup cross-file, fix de cards malformados
- **Solutions** — lookup en base de datos, generación multi-lenguaje, edge cases
- **Utilities** — helpers de JSON, validación de URLs, deduplicación, integración AI, soporte flag `traducido`
- **Tips** — generador de tips, base de datos, categorías
- **Bump dates** — actualización de fechas en frontmatter

---

## 🦙 IA Local (Ollama + Qwen 2.5)

Los workflows instalan **Ollama con Qwen 2.5 1.5B** en el propio runner de Actions, con el modelo cacheado (`actions/cache`, clave compartida `ollama-qwen2.5-1.5b`):

- **Fallback de traducción** (`scrape_hourly`, `scrape_6h`) — si Gemini falla (cuota/404), los títulos de noticias se traducen con Qwen local; si Ollama tampoco está disponible, se omite silenciosamente

---

## 🎬 Eixam — Película (Scraping + Noticias)

Workflow `eixam_scrape` que recopila toda la información sobre la película **"Eixam"** (Enjambre, 2026), thriller rural dirigido por Óscar Bernàcer.

### Fuentes de búsqueda

- **Google News RSS** — 14 queries generales (título original + español, director, actores, localizaciones)
- **YouTube** — 5 queries orientadas a tráilers y clips
- **Contraste.info** — RSS de WordPress (revista de cine)
- **Bing News RSS** — búsquedas complementarias
- **Medios de reseñas** — 9 sitios domain-scoped (decine21, fotogramas, cinemaldito, etc.)
- **Redes sociales** — Instagram y Twitter/X de @acontracorrientefilms y @atlantidamallorca

### Sistema anti-falsos positivos

"Filtrado de relevancia con señales fuertes (director, actores, localizaciones) y negativas (abejas, Swarm, Donald Glover, ciencia). Requiere mínimo 2 señales positivas y cero negativas."

### Envío a Telegram

- Cada noticia se envía con foto (si disponible) + título + enlace
- Clasificación automática por tipo: trailer, foto, poster, entrevista, crítica, noticia, video
- Deduplicación por URL normalizada (resuelve redirecciones de Bing/MSN)
- Acumulación en `files/eixam_pelicula.json` con flag `enviada` para no reenviar

### Uso

```bash
# Recopilar y archivar (sin enviar)
python -m scripts.scrapers.scrape_eixam

# Dry-run (mostrar sin guardar)
python -m scripts.scrapers.scrape_eixam --dry-run

# Enviar a Telegram
python -m scripts.scrapers.scrape_eixam --enviar
```

---

*Maintained by **[Jorge (@jorbencas)](https://github.com/jorbencas)***
