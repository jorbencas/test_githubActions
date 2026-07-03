# 🛰️ test_githubActions — Automatización Tech

![Python](https://img.shields.io/badge/python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)
![Playwright](https://img.shields.io/badge/playwright-✓-45ba4b?style=flat-square&logo=playwright)
![License](https://img.shields.io/github/license/jorbencas/test_githubActions?style=flat-square&label=Licencia)
![Repo size](https://img.shields.io/github/repo-size/jorbencas/test_githubActions?style=flat-square&label=Tamaño&logo=git)
![Code size](https://img.shields.io/github/languages/code-size/jorbencas/test_githubActions?style=flat-square&label=Código)
![Top language](https://img.shields.io/github/languages/top/jorbencas/test_githubActions?style=flat-square&label=Lenguaje)
![Last commit](https://img.shields.io/github/last-commit/jorbencas/test_githubActions?style=flat-square&logo=git&label=Último%20cambio)
![Surge](https://img.shields.io/badge/Surge-Live-00ADD8?style=flat-square&logo=vercel&label=Dashboard)

![Scraper](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scraper_workflow.yml?branch=master&style=flat-square&label=Scraper&logo=github)
![Hourly](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_hourly_workflow.yml?branch=master&style=flat-square&label=Cada%20hora&logo=github)
![6h](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_6h_workflow.yml?branch=master&style=flat-square&label=Cada%206h&logo=github)
![Trends](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/trends_workflow.yml?branch=master&style=flat-square&label=Tendencias&logo=github)
![Resources](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_resources.yml?branch=master&style=flat-square&label=Recursos&logo=github)
![Email](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_email_workflow.yml?branch=master&style=flat-square&label=Email&logo=github)
![Telegram](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_telegram_workflow.yml?branch=master&style=flat-square&label=Telegram&logo=github)
![Clean](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/clean_news.yml?branch=master&style=flat-square&label=Limpieza&logo=github)
![Challenges](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/hunt_challenges.yml?branch=master&style=flat-square&label=Retos&logo=github)
![Optimize](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/optimize_images.yml?branch=master&style=flat-square&label=Optimizar&logo=github)
![Tests](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/tests.yml?branch=master&style=flat-square&label=Tests&logo=github)

Ecosistema automatizado de noticias tech. Recopila, procesa con **IA (Gemini)** y distribuye contenido multicanal. También gestiona imágenes, recursos, retos de programación y el dashboard del blog [jorbencas/blog](https://blog-jorbencas.vercel.app/).

🚀 **[Dashboard de Noticias](http://jorbencasdownloaderdocument.surge.sh)**

---

## Estructura

```
scripts/
├── scrapers/           # Scraping de noticias, redes sociales, tools, trends
│   ├── scraper_base.py       # Extractores compartidos (YouTube, Web, ScraperPro)
│   ├── scrape_news.py        # Noticias (RSS + web + YouTube)
│   ├── scrape_social.py      # Redes sociales (Playwright)
│   ├── scrape_tools.py       # GitHub Trending + Product Hunt
│   ├── scrape_trends.py      # Google Trends + TikTok
│   └── screenshot_helper.mjs # Helper para capturas
├── publishers/         # Generación y distribución de contenido
│   ├── generate_weekly.py    # Recap semanal + dashboard HTML
│   ├── manage_resources.py   # Paginación, limpieza y reorden de resources.mdx
│   ├── merge_freefordev.py   # Merge de free-for-dev resources
│   ├── send_email.py         # Newsletter Mailgun
│   └── send_telegram.py      # Notificaciones Telegram con TTS
├── tools/              # Utilidades de mantenimiento
│   ├── clean_news.py         # Verificación de enlaces
│   ├── fix_images.py         # Pipeline de imágenes (Unsplash + Gemini + WebP/AVIF)
│   ├── hunt_challenges.py    # Generación IA de retos de programación
│   ├── make_cover_collage.py # Collages de portada
│   ├── optimize.py           # Optimización de imágenes (dashboard)
│   └── downloadFile.py       # (legacy) Versión monolítica original
├── utils/              # Módulos compartidos
│   ├── constants_downloadfile.py  # Fuentes, templates, configuración
│   ├── constants_retos.py         # Configuración de retos
│   ├── common.py                  # Utilidades (JSON, URLs, dedup, IA)
│   ├── utils_retos.py             # Utilidades para retos
│   └── cache.py                   # Caché pluggable (FileCache + CacheManager)
└── solutions/          # Base de datos de soluciones de retos
    ├── solutions_db.py           # Lookup + generación de soluciones
    └── solutions_data.py         # 105+ soluciones curadas en 12 lenguajes
tests/                  # Tests pytest (90+ tests)
├── test_cache.py
├── test_constants_downloadfile.py
├── test_constants_retos.py
├── test_fix_images.py
├── test_manage_resources.py
├── test_solutions_db.py
└── test_utils.py
```

---

## Comandos

Todos los scripts se ejecutan con `python -m` desde la raíz del proyecto:

```bash
# Scraping
python -m scripts.scrapers.scrape_news --tier full
python -m scripts.scrapers.scrape_social --source all
python -m scripts.scrapers.scrape_tools
python -m scripts.scrapers.scrape_trends

# Publicación
python -m scripts.publishers.generate_weekly --blog-path blog
python -m scripts.publishers.send_email
python -m scripts.publishers.send_telegram
python -m scripts.publishers.manage_resources --blog-path blog --max-cards 500 --clean --reorder
python -m scripts.publishers.merge_freefordev --blog-path blog --free-dev-file /tmp/free-for-dev.md

# Mantenimiento
python -m scripts.tools.fix_images --blog-path blog
python -m scripts.tools.make_cover_collage --ci --blog-path blog
python -m scripts.tools.hunt_challenges
python -m scripts.tools.clean_news
python -m scripts.tools.optimize

# Tests
python -m pytest tests/ -v
```

---

## GitHub Actions (11 workflows)

| Workflow | Trigger | Acción |
|----------|---------|--------|
| `scraper_workflow.yml` | Sábado 07:00 UTC | Scraping completo → weekly → PR blog → Surge |
| `scrape_hourly_workflow.yml` | Cada hora | Scraping tier light (RSS + rápidas) |
| `scrape_6h_workflow.yml` | Cada 6h | Scraping tier standard |
| `trends_workflow.yml` | Mar+Vie 08:00 UTC | Google Trends + TikTok |
| `daily_resources.yml` | Diario 06:00 UTC | Tools + gestión resources.mdx |
| `send_email_workflow.yml` | Diario 09:00 UTC | Newsletter Mailgun |
| `send_telegram_workflow.yml` | Cada 30 min | Telegram con TTS |
| `clean_news.yml` | Trimestral | Verificación de enlaces |
| `hunt_challenges.yml` | Semanal (domingo) | Generación de retos IA |
| `optimize_images.yml` | Dispatch desde blog | Optimización imágenes del blog |
| `tests.yml` | Push/PR a master | pytest |

---

## Secrets de GitHub

| Secret | Descripción |
| :--- | :--- |
| `TELEGRAM_BOT_TOKEN` | Token del bot de Telegram |
| `TELEGRAM_CHAT_ID` | ID del chat/grupo |
| `GEMINI_API_KEY` | API Key de Google AI Studio |
| `MAILGUN_API_KEY` | API Key de Mailgun |
| `MAILGUN_DOMAIN` | Dominio Mailgun |
| `EMAIL_USER` | Correo destino |
| `BLOG_TOKEN` | Token para checkout del blog |
| `UNSPLASH_ACCESS_KEY` | API Key de Unsplash |

---

## Dashboard

El dashboard se despliega en Surge.sh. Es un HTML estático (~6.5KB) con data.json (~530KB, 1400+ registros) renderizado vía JavaScript (Observable Store). Incluye noticias, vídeos de YouTube, Instagram, X/Twitter, Threads y TikTok.

---

*Mantenido por **[Jorge (@jorbencas)](https://github.com/jorbencas)***
