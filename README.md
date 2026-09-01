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
![Saludos](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_saludo.yml?branch=master&style=flat-square&label=Saludos&logo=github)
![AI Tools](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_ai_tools.yml?branch=master&style=flat-square&label=AI%20Tools&logo=github)
![Cleanup](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/clean_news.yml?branch=master&style=flat-square&label=Cleanup&logo=github)
![Challenges](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/hunt_challenges.yml?branch=master&style=flat-square&label=Challenges&logo=github)
![Optimize](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/optimize_images.yml?branch=master&style=flat-square&label=Optimize&logo=github)
![Dashboard](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/dashboard_update.yml?branch=master&style=flat-square&label=Dashboard&logo=github)
![Tests](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/tests.yml?branch=master&style=flat-square&label=Tests&logo=github)

Automated tech news ecosystem. Collects from **515 sources** (158 YouTube channels, 151 RSS feeds, 107 web scraping sites, 89 GitHub Topics, 8 GitHub Repos, 1 Product Hunt, 1 GitHub Collection), processes with **AI (Gemini)**, and distributes content across multiple channels. 4 dual sources (MoureDev, Midudev, Carlos Azaustre, Xataka) extract from both YouTube AND web scraping. Also manages images, resources, programming challenges, a daily IT tips system, and the blog dashboard for [jorbencas/blog](https://blog-jorbencas.vercel.app/).

🚀 **[News Dashboard](http://jorbencasdownloaderdocument.surge.sh)**

---

## 📋 Overview

This project runs **15 GitHub Actions workflows** that form a fully automated content pipeline:

1. **Scrape** — news and tools from 515 sources (158 YouTube channels, 151 RSS feeds, 107 web scraping, 89 GitHub Topics); 4 dual sources extract from both YouTube AND web scraping
2. **Process** — AI summarization with Gemini, news grouped by source, automatic translation (only new items), image generation, deduplication, summaries persisted in JSON
3. **Publish** — weekly recaps with source grouping, dashboard (SSR), email newsletter with video section, Telegram notifications (news only, no videos)
4. **Manage** — resource lists, challenges, image optimization, link validation, SEO dedup
5. **Tips** — daily IT tips sent via Telegram, mixing Gemini-generated tips with a static database (399 tips) never repeated
6. **Saludos** — hourly image greetings (Buenos días / Buenas noches) sent via Telegram with AI-generated image and fallback chain (Gemini → Unsplash → PIL)

---

## 📡 Sources — 515 Total

| Category | Count | Examples |
|----------|-------|---------|
| YouTube channels | 154 | MoureDev, Fernando Herrera, The Engineer's Digest |
| RSS feeds | 151 | TechCrunch, The Verge, Wired, Ars Technica, Google Blog, Vercel Blog, OpenCode Releases |
| Web scraping | 107 | Anthropic, Ollama, Mistral, LangChain, Mozilla Hacks, OpenCode Docs, Claude Help Center |
| Dual (YT + Web) | 4 | MoureDev, Midudev, Carlos Azaustre, Xataka |
| GitHub Topics | 89 | AI, LLM, Docker, Kubernetes, CSS, HTML, algorithms |
| GitHub Collections | 1 | AI Tools |
| GitHub Repos | 8 | OpenWiki, Meetily, AutoPR, PR-Agent, Code-to-Road |
| Product Hunt | 1 | Top products daily |

### Quick sources (hourly tier)

RSS and web scraping sources with `quick: True` are scraped every hour:

- **RSS (150)**: TechCrunch, The Verge, Wired, Ars Technica, Google Blog, Google AI, Vercel, Astro Releases, Docker, Kubernetes, Krebs, HN, Stack Overflow, Dev.to, NVIDIA, Machine Learning Mastery, etc.
- **Web scraping (43)**: Anthropic Research, Ollama Blog, Mistral News, Cohere, LangChain, Google Developers, HuggingFace Papers, Mozilla Hacks, Qwen Blog, DeepSeek, 01.AI, Claude Help Center
- **Chinese AI**: QbitAI (量子位), 36氪 AI, Qwen, DeepSeek, 01.AI, THUDM/ChatGLM

---

## 📂 Project Structure

```
scripts/
├── scrapers/             🌐 Data collection from 515 sources
│   ├── scraper_base.py         YouTube, Web, ScraperPro extractors (dual source support)
│   ├── scrape_news.py          RSS + web + YouTube news (standard tier includes dual sources)
│   ├── scrape_tools.py         GitHub Trending + Product Hunt
│   ├── scrape_ai_tools.py      Auto-detect AI tools (HF API + GitHub Search)
│   └── screenshot_helper.mjs   Playwright screenshot helper
├── publishers/           📤 Content generation & distribution
│   ├── generate_weekly.py      AI recap + dashboard HTML (SSR)
│   ├── manage_resources.py     Pagination, cleanup, reorder resources.mdx
│   ├── merge_freefordev.py     Merge free-for-dev resources
│   ├── send_email.py           Mailgun newsletter (grouped by source + videos, smart translation)
│   └── send_telegram.py        Telegram notifications (news only, smart translation + summaries)
├── tools/                🔧 Maintenance utilities
│   ├── clean_news.py           Link validation
│   ├── fix_images.py           Image pipeline (Unsplash + Gemini + WebP/AVIF)
│   ├── hunt_challenges.py      AI challenge generation
│   ├── make_cover_collage.py   Cover image collages
│   ├── optimize.py             Dashboard image optimization
│   ├── update_resource_format.py  Batch update ResourceCard to new format (headline, features, platform)
│   └── downloadFile.py         (legacy) Original monolith
├── utils/                🧰 Shared modules
│   ├── constants_downloadfile.py   Sources, templates, config
│   ├── constants_retos.py          Challenge configuration
│   ├── common.py                   JSON, URL, dedup, AI helpers (traducido flag support)
│   ├── utils_retos.py              Challenge utilities
│   └── cache.py                    Pluggable cache (FileCache + CacheManager)
├── backfill_traducido.py    🔄 One-time migration (mark 6,612 items as translated)
└── solutions/            💡 Challenge solutions database
    ├── solutions_db.py            Lookup + solution generation
    └── solutions_data.py          105+ curated solutions in 12 languages
├── tips_generator.py         💡 Daily IT tips (Gemini + DB fallback, nunca repite)
├── ai_tools_generator.py     🛠️  AI tools (Gemini + DB fallback, 150 categorías)
├── saludo_imagen.py          🌅 Imagen de saludo diario (Gemini → Unsplash → PIL fallback)
├── backfill_traducido.py    🔄 One-time migration (mark 6,612 items as translated)
└── utils/
    ├── tips_database.json         399 tips (con estructura ❌/✅ mala/buena práctica)
    ├── ai_categories.json         150 categorías de herramientas IA
    ├── ai_tools_database.json     20 herramientas IA con combinaciones
    ├── saludos_config.json        Estilos/públicos/emociones/materias/festivos
    └── constants_sources.py       Fuentes de scraping (+ OpenCode, Claude Help Center)
tests/                    ✅ pytest test suite (134 tests)
├── test_cache.py / test_constants_downloadfile.py
├── test_constants_retos.py / test_fix_images.py
├── test_manage_resources.py / test_solutions_db.py
├── test_ai_features.py / test_utils.py
└── test_solutions_db.py
```

---

## ⚡ Commands

All scripts run with `python -m` from the project root:

### 🌐 Scraping

| Command | Description |
|---------|-------------|
| `python -m scripts.scrapers.scrape_news --tier full` | Full news scrape (RSS + web + YouTube) |
| `python -m scripts.scrapers.scrape_news --tier light` | Light scrape (quick sources only) |
| `python -m scripts.scrapers.scrape_tools` | GitHub Trending + Product Hunt |
| `python -m scripts.scrapers.scrape_ai_tools` | Auto-detect AI tools (HF API + GitHub Search) |

### 📤 Publishing

| Command | Description |
|---------|-------------|
| `python -m scripts.publishers.generate_weekly --blog-path blog` | Generate weekly recap + dashboard (SSR) |
| `python -m scripts.publishers.generate_weekly --dashboard-only` | Only regenerate dashboard HTML (skip AI recap) |
| `python -m scripts.publishers.send_email` | Send Mailgun newsletter |
| `python -m scripts.publishers.send_email --dry-run` | Preview email without sending |
| `python -m scripts.publishers.send_telegram` | Send Telegram notification with TTS |
| `python -m scripts.publishers.send_telegram --dry-run` | Preview Telegram without sending |
| `python -m scripts.publishers.manage_resources --blog-path blog --max-cards 500 --clean --reorder --fix-spacing` | Manage resources.mdx |
| `python -m scripts.publishers.merge_freefordev --blog-path blog --free-dev-file /tmp/free-for-dev.md` | Merge free-for-dev resources |

### 🔧 Maintenance

| Command | Description |
|---------|-------------|
| `python -m scripts.tools.fix_images --blog-path blog` | Unsplash + Gemini image pipeline |
| `python -m scripts.tools.make_cover_collage --ci --blog-path blog` | Cover collages |
| `python -m scripts.tools.hunt_challenges` | AI challenge generation |
| `python -m scripts.tools.clean_news` | Link validation |
| `python -m scripts.tools.optimize` | Dashboard image optimization |
| `python scripts/backfill_traducido.py` | One-time: mark existing items as translated |

### 💡 Tips de IT

| Command | Description |
|---------|-------------|
| `python scripts/tips_generator.py` | Envía 10 tips por Telegram |
| `python scripts/tips_generator.py --dry-run` | Previsualiza los tips sin enviar |
| `python scripts/tips_generator.py --list-categories` | Lista las categorías de tips |
| `python scripts/tips_generator.py --stats` | Estadísticas de la base de tips |

### 🛠️ AI Tools

| Command | Description |
|---------|-------------|
| `python scripts/ai_tools_generator.py` | Envía herramienta IA por Telegram |
| `python scripts/ai_tools_generator.py --dry-run` | Previsualiza sin enviar |
| `python scripts/ai_tools_generator.py --list-categories` | Lista las 150 categorías |
| `python scripts/ai_tools_generator.py --stats` | Estadísticas de la base |

### 🌅 Saludos

| Command | Description |
|---------|-------------|
| `python scripts/saludo_imagen.py` | Genera y envía imagen de saludo |
| `python scripts/saludo_imagen.py --dry-run` | Solo genera, no envía |
| `python scripts/saludo_imagen.py --list-config` | Muestra la configuración disponible |

### ✅ Testing

| Command | Description |
|---------|-------------|
| `python -m pytest tests/ -v` | Run all tests (134 tests) |
| `python -m pytest tests/test_solutions_db.py -v` | Run specific test suite |

---

## 🤖 GitHub Actions — 15 Workflows

| Workflow | Schedule / Trigger | Pipeline |
|----------|-------------------|----------|
| **scraper_workflow** | Sat 07:00 UTC | Generate weekly recap + portadas → PR to blog |
| **scrape_hourly** | Every hour | Light scrape (RSS + quick sources) |
| **scrape_6h** | Every 6 hours | Standard scrape |
| **daily_resources** | Daily 06:00 UTC | Tools scrape + resources.mdx management |
| **daily_tips** | Every 3 hours | IT tips via Telegram (Gemini + DB, nunca repite) |
| **daily_ai_tools** | Every 3 hours | Herramientas IA via Telegram (Gemini + DB, 150 categorías) |
| **daily_saludo** | Every 3 hours | Imagen de saludo (Gemini → Unsplash → PIL fallback) |
| **send_email** | Daily 09:00 UTC | Mailgun newsletter (grouped by source + videos) |
| **send_telegram** | Every 30 min | Telegram + TTS (GitHub Actions Cache for dedup) |
| **telegram_ai_bot** | Every 15 min | Bot IA local en Telegram: responde menciones/respuestas/`/ai` con Qwen 2.5 vía Ollama (`/help` para ver uso) |
| **clean_news** | Quarterly | Link health check |
| **hunt_challenges** | Dispatch manual | AI challenge generation (schedule off: cuota Gemini) |
| **optimize_images** | Dispatch from blog | Image optimization for blog |
| **dashboard_update** | Push (JS/CSS/Python/data) | Regenerate + deploy dashboard |
| **tests** | Push/PR to master | pytest (134 tests) |

### Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION                              │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_hourly   →  every hour  →  quick sources (150 RSS + 43 web) │
│  scrape_6h       →  every 6h    →  standard scrape + AI tools auto  │
│  daily_resources →  daily       →  tools (89 GitHub Topics + repos) │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        AI TOOLS AUTO-SCRAPE                         │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_ai_tools  →  every 6h   →  HF Models + Spaces + GitHub     │
│  Output: files/ai_tools_candidates.json (50 tools, auto-detected)  │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        WEEKLY PROCESSING                            │
├─────────────────────────────────────────────────────────────────────┤
│  scraper_workflow  →  Sat 07:00 UTC                                │
│  ├── Generate weekly recap (AI + Gemini)                           │
│  ├── Generate portadas (Playwright)                                │
│  └── Push to blog (auto-news + resources)                          │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DISTRIBUTION                                 │
├─────────────────────────────────────────────────────────────────────┤
│  send_email       →  daily       →  Mailgun newsletter             │
│  send_telegram    →  every 30min →  Telegram + TTS                 │
│  dashboard_update →  on push     →  Surge.sh deploy                │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        MAINTENANCE                                  │
├─────────────────────────────────────────────────────────────────────┤
│  clean_news       →  quarterly   →  link validation                │
│  hunt_challenges  →  weekly      →  AI challenges                  │
│  optimize_images  →  dispatch    →  image optimization             │
│  daily_tips      →  every 3h   →  tips IT (Gemini + DB)           │
│  daily_ai_tools  →  every 3h   →  herramientas IA (auto + Gemini) │
│  daily_saludo    →  every 3h   →  imagen saludo + fallback        │
│  tests            →  on push     →  134 pytest tests               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 💡 Daily IT Tips

Automated daily IT tips sent to Telegram every 3 hours via `tips_generator.py`:

- **Mixed generation** — Gemini generates fresh tips (5) plus 5 from the static database, 10 total per run
- **Static DB fallback** — 399 curated tips across 22 categories (docker, git, linux, databases, security, programming...)
- **Never repeats** — tracks sent titles in `tips_history.json` (persisted via GitHub Actions Cache)
- **Mala/Buena práctica** — practical tips include a structured `❌ Mala práctica / ✅ Buena práctica` contrast
- **Exhaustion recovery** — when the DB is exhausted, Gemini generates the full batch

---

## 🛠️ AI Tools

Automated AI tools sent to Telegram every 3 hours via `ai_tools_generator.py`:

- **Auto-scraping** — `scrape_ai_tools.py` discovers new tools every 6h from:
  - **Hugging Face API** — trending models (by downloads) + spaces (by likes)
  - **GitHub Search API** — AI repos with 200+ stars, recently updated
  - **Product Hunt** — daily top products
- **Gemini generation** — Gemini generates fresh tools using auto-detected candidates as HIGH PRIORITY input, falling back to a static database of 107 curated tools
- **150 categories** — categorized in `ai_categories.json` for varied selection
- **Complete format** — each tool includes: clear name, what it's for, official website link (`url`), workflow, possible integrations (`combinaciones`), and key restrictions/caveats (`restricciones`)
- **Never repeats** — tracks sent tools in `ai_tools_history.json` (persisted via GitHub Actions Cache)
- **Multi-source priority** — tools found in multiple sources (HF + GitHub) get maximum priority in Gemini prompt

### Auto-scraping data flow

```
Cada 6h (scrape_6h_workflow):
  scrape_ai_tools.py → files/ai_tools_candidates.json
    ├── Hugging Face API (30 models + 20 spaces)
    ├── GitHub Search API (repos with 200+ stars)
    └── Product Hunt (daily top products)

Cada 3h (daily_ai_tools):
  ai_tools_generator.py → Telegram
    ├── 1. Load ai_tools_candidates.json (HIGH PRIORITY)
    ├── 2. Load herramientas.json (inspiration)
    ├── 3. Load noticias_historico.json (inspiration)
    ├── 4. Gemini prompt with all sources → generates 5 tools
    └── 5. Send to Telegram
```

---

## 🌅 Saludos

Automated image greetings (Buenos días / Buenas noches) sent to Telegram every 3 hours via `saludo_imagen.py`:

- **AI-generated image** — Gemini 3 (Nano Banana 2, `gemini-3.1-flash-image`) via the Interactions API
- **Time aware** — `SALUDOS_TZ_OFFSET` sets the local timezone offset for the "Buenos días" (5–12h) / "Buenas noches" window
- **Variety** — 11 styles, 5 públicos, 6 emociones, 14 materias, 13 festivos, 12 temporadas from `saludos_config.json`, never repeats
- **Inspiring phrases** — a daily motivational frase (día/noche) is drawn INSIDE the image, in the image's dominant color, plus the saludo below it; never repeats
- **Square images** — 1:1 ratio for all sources (Gemini prompt, Pollinations `1024x1024`, PIL `1024x1024`), text overlay preserves proportions
- **Fallback chain** — if Gemini fails (quota/429/error): tries **Pollinations.ai** (image from prompt, no registration/API key needed), then a **local PIL** image
- **Send** — `SALUDO_CHAT_ID` (fallback `TIPS_CHAT_ID`, default `-1004296712840`)

---

## 📧 Email Newsletter

The daily email newsletter is sent via Mailgun with:

- **Grouped by source** — news organized by website (TechCrunch, The Verge, Xataka, etc.)
- **Smart translation** — only translates new items (`traducido` flag), skips already-translated
- **Persisted summaries** — AI summaries saved in JSON to avoid re-summarization
- **Video section** — YouTube videos with thumbnail, channel, and duration
- **Responsive design** — works on mobile and desktop

### Source styles

Each source has a custom color and icon:

| Source | Color | Icon |
|--------|-------|------|
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

- **News only** — only sends news items, no video links
- **Deduplication** — GitHub Actions Cache (`actions/cache@v4`) persists `telegram_sent.json` between runs
- **TTL** — 7-day expiration for news items, 24-hour for voice messages
- **Time filter** — only sends news from the last 24 hours
- **TTS audio** — daily voice summary at 21:00 UTC with ALL news from the day (not just the 5 from current run)
- **Smart translation** — skips already-translated items (`traducido` flag)
- **Persisted summaries** — AI summaries saved in `noticias_historico.json` to avoid re-summarization

---

## 📊 Dashboard

Deployed on Surge.sh. Fully **server-side rendered (SSR)** — Python generates a single `index.html` with all content pre-rendered (news, YouTube videos, GitHub ranking). JavaScript is minimal and only handles interactive filters, tabs, and search.

**Recent UI improvements:**
- **ResourceCard enhanced** — new `headline`, `features`, `platform` props for structured descriptions (backward compatible)
- **Dual source chips** — sources with both YouTube and web (MoureDev, Midudev, Carlos Azaustre, Xataka) show filter chips in both News and Multimedia sections
- **Separated channel filters** — news filter uses `news_items` (no YouTube), video filter uses `video_items` (no web links)
- **Type badges** — `📄 Noticia`, `📡 RSS`, `🔧 Herramienta` in news cards; `🎬 Video`, `🩳 Short`, `🔴 Directo` in video cards
- **Footer** — "Creado con ❤️ y sin ánimo de lucro por @jorbencas" + disclaimer (no hosted content)
- **Dark theme** — news title gradient uses `#60a5fa → #3b82f6` in dark mode
- **Translation** — only new items translated, `traducido` flag prevents re-translation

Weekly recaps auto-archive old posts (>2 weeks) and enforce one-post-per-week SEO. News is grouped by source with deduplication before rendering.

---

## 🔐 GitHub Secrets

| Secret | Description |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Chat/group ID |
| `GEMINI_API_KEY` | Google AI Studio API key |
| `MAILGUN_API_KEY` | Mailgun API key |
| `MAILGUN_DOMAIN` | Mailgun domain |
| `EMAIL_USER` | Destination email |
| `BLOG_TOKEN` | Blog checkout token |
| `UNSPLASH_ACCESS_KEY` | Unsplash API key (fix_images) |
| `SALUDO_CHAT_ID` | Chat/group ID para saludos (fallback: `TELEGRAM_CHAT_ID`) |
| `AI_TOOLS_CHAT_ID` | Chat/group ID para herramientas IA (fallback: `TELEGRAM_CHAT_ID`) |

Repository variables:

| Variable | Description |
|----------|-------------|
| `SALUDOS_TZ_OFFSET` | Desfase horario en horas para el saludo (ej. `2` = CEST). Vacío/ausente → UTC |

---

## 🧪 Test Coverage

134 pytest tests covering:
- **Cache** — FileCache, CacheManager, expiration, TTL, flush cleanup
- **Constants** — source configurations (515 sources), email templates, challenge templates
- **Dual sources** — YouTube + web scraping extraction, chip rendering in both sections
- **Email templates** — placeholders, source headers, video sections, button styles
- **Image pipeline** — Unsplash fetching, Gemini banner gen, WebP/AVIF conversion
- **AI features** — 150 categorías, DB tools, generador de herramientas IA, saludo por hora/festivos
- **Resources** — pagination, cleanup, reordering, card management, cross-file dedup, malformed card fix
- **Solutions** — database lookup, multi-language generation, edge cases
- **Utilities** — JSON helpers, URL validation, deduplication, AI integration, `traducido` flag support

---

## 🦙 IA Local (Ollama + Qwen 2.5)

Los workflows instalan **Ollama con Qwen 2.5 1.5B** en el propio runner de Actions, con el modelo cacheado (`actions/cache`, clave compartida `ollama-qwen2.5-1.5b`):

- **`telegram_ai_bot`** — bot conversacional en Telegram 100% local:
  - Menciona al bot: `@bot ¿qué es un closure?`
  - Comando directo: `/ai explícame async/await`
  - Responde a un mensaje del bot citándolo → usa el texto citado como contexto
  - `/help` → muestra la ayuda de uso en el chat
  - Sin estado en git: confirma los updates en el servidor de Telegram y filtra mensajes >15 min, así no interfiere con otros workflows
- **Fallback de traducción** (`scrape_hourly`, `scrape_6h`) — si Gemini falla (cuota/404), los títulos de noticias se traducen con Qwen local; si Ollama tampoco está disponible, se omite silenciosamente

---

*Maintained by **[Jorge (@jorbencas)](https://github.com/jorbencas)***
