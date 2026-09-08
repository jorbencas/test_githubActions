<div align="center">

# 🛰️ test_githubActions

**Tech Automation Ecosystem**

![Python](https://img.shields.io/badge/python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/github/license/jorbencas/test_githubActions?style=for-the-badge)
![Tests](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/tests.yml?branch=master&style=for-the-badge&label=Tests&logo=github)
![Surge](https://img.shields.io/badge/Surge-Live-00ADD8?style=for-the-badge&logo=vercel&label=Dashboard)

[![Scraper](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scraper_workflow.yml?branch=master&style=flat-square&label=Scraper&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![Hourly](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_hourly_workflow.yml?branch=master&style=flat-square&label=Hourly&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![6h](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/scrape_6h_workflow.yml?branch=master&style=flat-square&label=Every%206h&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![Resources](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_resources.yml?branch=master&style=flat-square&label=Resources&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![Email](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_email_workflow.yml?branch=master&style=flat-square&label=Email&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![Telegram](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/send_telegram_workflow.yml?branch=master&style=flat-square&label=Telegram&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![AI Tools](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_ai_tools.yml?branch=master&style=flat-square&label=AI%20Tools&logo=github)](https://github.com/jorbencas/test_githubActions/actions)
[![Tips](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/daily_tips.yml?branch=master&style=flat-square&label=Tips&logo=github)](https://github.com/jorbencas/test_githubActions/actions)

Ecosistema de automatización tech que ejecuta **16 workflows de GitHub Actions** formando un pipeline de contenido completamente automatizado. Recolecta de **547 fuentes** (158 canales YouTube, 161 feeds RSS, 225 sitios de web scraping, 89 GitHub Topics, 5 GitHub Repos, 1 Product Hunt), procesa con **IA (Gemini)** y distribuye contenido a múltiples canales.

**[🚀 News Dashboard](http://jorbencasdownloaderdocument.surge.sh)** · **[📖 Blog: Tech Pulse](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard)** · **[🔧 Instalación](https://blog-jorbencas.vercel.app/posts/instalacion-tech-pulse)**

</div>

---

## 📋 Overview

> **[📖 Leer más en el blog](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard)** — Explicación detallada de la arquitectura y decisiones de diseño.

| Fase | Descripción | Frecuencia | Blog |
|------|-------------|------------|------|
| 🌐 **Scraping** | Recolección de datos de 547 fuentes | Cada hora / 6h / diario | [📖](https://blog-jorbencas.vercel.app/posts/instalacion-tech-pulse) |
| 🤖 **IA** | Procesamiento con Gemini (resúmenes, traducción) | En cada scraping | [📖](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) |
| 📤 **Publicación** | Distribución multicanal (Email, Telegram, Dashboard) | Diario / cada 30min | [📖](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) |
| 💡 **Tips** | Contenido generado con IA (708 tips, 80 categorías) | Cada 3 horas | [📖](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) |
| 🛠️ **Herramientas** | Auto-detección de herramientas IA (166 categorías) | Cada 3 horas | [📖](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) |
| 🌅 **Saludos** | Imágenes generadas con IA | Cada 3 horas | [📖](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) |

---

## 📡 Sources

| Categoría | Cantidad | Ejemplos |
|-----------|----------|----------|
| YouTube channels | 158 | MoureDev, Fernando Herrera, The Engineer's Digest |
| RSS feeds | 161 | TechCrunch, The Verge, Wired, Ars Technica |
| Web scraping | 225 | Anthropic, Ollama, Mistral, LangChain, Mozilla Hacks |
| GitHub Topics | 89 | AI, LLM, Docker, Kubernetes, CSS, HTML |
| GitHub Repos | 5 | OpenWiki, Meetily, AutoPR, PR-Agent |
| Product Hunt | 1 | Top products daily |

---

## 📂 Project Structure

```
scripts/
├── scrapers/                 🌐 Recolección de datos
│   ├── scraper_base.py           Extractores YouTube, Web, ScraperPro
│   ├── scrape_news.py            RSS + web + YouTube news
│   ├── scrape_tools.py           GitHub Trending + Product Hunt
│   ├── scrape_ai_tools.py        Auto-detección de herramientas IA
│   ├── scrape_agent_skills.py    Scraping skills de agentes IA
│   ├── scrape_concepts.py        Scraping conceptos de programación
│   └── scrape_publicapis.py      Scraping APIs públicas (con detección pricing)
├── publishers/               📤 Generación y distribución
│   ├── generate_weekly.py        Recap semanal + dashboard HTML
│   ├── manage_resources.py       Gestión de resources.mdx
│   ├── merge_freefordev.py       Merge de recursos free-for-dev
│   ├── send_email.py             Newsletter Mailgun
│   └── send_telegram.py          Notificaciones Telegram + TTS
├── tools/                    🔧 Utilidades de mantenimiento
│   ├── clean_news.py             Validación de enlaces
│   ├── fix_images.py             Pipeline de imágenes
│   ├── hunt_challenges.py        Generación de retos con IA
│   ├── make_cover_collage.py     Collages de portadas
│   └── optimize.py               Optimización de imágenes
├── utils/                    🧰 Módulos compartidos
│   ├── common.py                 Helpers de JSON, URL, dedup, AI
│   ├── lang_es.py                Detección de idioma
│   ├── cache.py                  Cache pluggable
│   └── ai_categories.json        166 categorías de herramientas IA
├── tips_generator.py         💡 Tips diarios de IT
├── ai_tools_generator.py     🛠️ Herramientas IA
├── saludo_imagen.py          🌅 Imagen de saludo diaria
└── solutions/                💡 Base de datos de soluciones
    ├── solutions_db.py            Lookup + generación
    └── solutions_data.py          107 soluciones curadas
tests/                        ✅ Suite de tests pytest (168 tests)
public/                       🕰️ Tech Timeline (Surge.sh)
```

---

## ⚡ Commands

### 🌐 Scraping

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.scrapers.scrape_news --tier full` | Scraping completo (RSS + web + YouTube) |
| `python -m scripts.scrapers.scrape_news --tier light` | Scraping ligero (solo quick sources) |
| `python -m scripts.scrapers.scrape_tools` | GitHub Trending + Product Hunt |
| `python -m scripts.scrapers.scrape_ai_tools` | Auto-detección de herramientas IA |

### 📤 Publicación

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.publishers.generate_weekly --blog-path blog` | Generar recap semanal + dashboard |
| `python -m scripts.publishers.send_email` | Enviar newsletter Mailgun |
| `python -m scripts.publishers.send_email --dry-run` | Previsualizar email sin enviar |
| `python -m scripts.publishers.send_telegram` | Enviar notificación Telegram con TTS |
| `python -m scripts.publishers.send_telegram --dry-run` | Previsualizar Telegram sin enviar |

### 💡 Tips de IT

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.tips_generator` | Envía 10 tips por Telegram |
| `python -m scripts.tips_generator --dry-run` | Previsualiza los tips sin enviar |
| `python -m scripts.tips_generator --list-categories` | Lista las categorías de tips |

### 🛠️ AI Tools

| Comando | Descripción |
|---------|-------------|
| `python -m scripts.ai_tools_generator` | Envía herramienta IA por Telegram |
| `python -m scripts.ai_tools_generator --dry-run` | Previsualiza sin enviar |
| `python -m scripts.ai_tools_generator --list-categories` | Lista las 166 categorías |

### ✅ Testing

| Comando | Descripción |
|---------|-------------|
| `python -m pytest tests/ -v` | Ejecutar todos los tests (168 tests) |
| `python -m pytest tests/test_solutions_db.py -v` | Ejecutar un suite específico |

---

## 🤖 GitHub Actions — 16 Workflows

| Workflow | Horario | Descripción |
|----------|---------|-------------|
| `scraper_workflow` | Sáb 07:00 UTC | Recap semanal + portadas → PR al blog |
| `scrape_hourly` | Cada hora | Scraping ligero (RSS + quick sources) |
| `scrape_6h` | Cada 6 horas | Scraping estándar + auto-detección IA |
| `daily_resources` | Diario 06:00 UTC | Scraping herramientas + gestión resources.mdx |
| `daily_ai_tools` | Cada 3 horas | Herramientas IA via Telegram |
| `daily_tips` | Cada 3 horas | Tips IT via Telegram |
| `daily_saludo` | Cada 3 horas | Imágenes Buenos días/noches |
| `send_email` | Diario 09:00 UTC | Newsletter Mailgun |
| `send_telegram` | Cada 30 min | Telegram + TTS |
| `clean_news` | Trimestral | Validación de enlaces |
| `hunt_challenges` | Manual | Generación de retos con IA |
| `optimize_images` | Dispatch | Optimización de imágenes |
| `dashboard_update` | Push (JS/CSS/Python) | Regenerar + deploy dashboard |
| `tests` | Push/PR a master | pytest (168 tests) |
| `translate_descriptions` | Manual | Traducción de descripciones |

---

## 🕰️ Tech Timeline

Timeline interactiva de la historia de la tecnología (1970-2025), desplegada en Surge.sh.

- **424 eventos** en 9 categorías
- **Imágenes reales** de Unsplash como fondos por era
- **6 eras temáticas** con colores, humo y partículas únicas
- **Efecto teatro** — parallax de 3 capas
- **Scroll animations** — IntersectionObserver
- **Música ambient** — Web Audio API
- **Responsive** — 320px → ultra-wide

---

## 📊 Dashboard — Tech Timeline

Desplegado en Surge.sh. Experiencia inmersiva de scroll horizontal 2D que recorre la historia de la tecnología (1970-2025).

**Características:**
- **6 eras temáticas** con imágenes reales de Unsplash (Mainframes, PC, Internet, Web 2.0, Móvil, IA)
- **Parallax 3 capas** (back, mid, front) con efecto teatro
- **Partículas canvas** (humo + brasas) con colores por era
- **Música ambiente** (Web Audio API, generada proceduralmente)
- **Animaciones scroll** (IntersectionObserver) con efecto fade-in
- **Año dinámico** que cambia al hacer scroll
- **Línea temporal** con puntos de eventos interactivos
- **Responsive** (320px → ultra-wide, landscape, touch, reduced motion)
- **424 eventos** de historia tech (1970-2025)

**Estructura:**
```
public/
├── index.html          ← HTML principal
├── css/style.css       ← Dark theme + 14 breakpoints responsive
├── js/app.js           ← Lógica: eras, parallax, partículas, audio, scroll
└── data/events.json    ← 424 eventos de historia tech
```

---

## 🧪 Test Coverage

168 tests pytest cubriendo:

| Módulo | Tests |
|--------|-------|
| Cache | FileCache, CacheManager, expiración, TTL |
| Constants | 547 fuentes, templates email, retos |
| Dual sources | YouTube + web scraping |
| Email templates | Placeholders, headers, secciones vídeo |
| Pipeline imágenes | Portadas locales, WebP/AVIF |
| AI features | 166 categorías, DB tools, saludo |
| Resources | Paginación, limpieza, dedup |
| Solutions | Lookup, generación multi-lenguaje |
| Utilities | JSON, URLs, dedup, AI, traducción |
| Tips | Generador, base de datos, categorías |

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
| `SALUDO_CHAT_ID` | Chat/grupo para saludos |
| `AI_TOOLS_CHAT_ID` | Chat/grupo para herramientas IA |
| `TIPS_CHAT_ID` | Chat/grupo para tips IT |
| `SURGE_TOKEN` | Token de Surge.sh |

---

## 📧 Email Newsletter

- **Agrupada por fuente** — noticias organizadas por web
- **Traducción inteligente** — solo traduce elementos nuevos
- **Resúmenes persistidos** — guardados en JSON
- **Sección de vídeos** — YouTube con thumbnail y duración
- **Diseño responsive** — móvil y escritorio

---

## 🤖 Telegram Notifications

- **Solo noticias** — no envía enlaces de vídeo
- **Deduplicación** — GitHub Actions Cache
- **TTL** — 7 días noticias, 24 horas audio
- **Filtro de tiempo** — últimas 24 horas
- **Audio TTS** — resumen de voz diario
- **Traducción inteligente** — omite ya traducidos

---

## 🦙 IA Local (Ollama + Qwen 2.5)

Fallback de traducción en workflows:
- **Ollama + Qwen 2.5 1.5B** en runner de Actions
- **Modelo cacheado** (`actions/cache`)
- **Fallback de Gemini** — si falla, usa Qwen local

---

## 📚 Blog Posts

Artículos relacionados en [blog-jorbencas.vercel.app](https://blog-jorbencas.vercel.app):

| Post | Descripción |
|------|-------------|
| [Tech Pulse: Dashboard Automatizado](https://blog-jorbencas.vercel.app/proyectos/tech-pulse-dashboard) | Arquitectura completa del ecosistema |
| [Instalación de Tech Pulse](https://blog-jorbencas.vercel.app/posts/instalacion-tech-pulse) | Guía paso a paso de configuración |
| [Devjobs Automation Suite](https://blog-jorbencas.vercel.app/proyectos/devjobs-automation-suite) | Pipeline de video, bots IA y scrapers |

---

<div align="center">

**Made with ❤️ by [Jorge (@jorbencas)](https://github.com/jorbencas)**

</div>
