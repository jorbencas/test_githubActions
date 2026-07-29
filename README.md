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
![Cleanup](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/clean_news.yml?branch=master&style=flat-square&label=Cleanup&logo=github)
![Challenges](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/hunt_challenges.yml?branch=master&style=flat-square&label=Challenges&logo=github)
![Optimize](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/optimize_images.yml?branch=master&style=flat-square&label=Optimize&logo=github)
![Dashboard](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/dashboard_update.yml?branch=master&style=flat-square&label=Dashboard&logo=github)
![Tests](https://img.shields.io/github/actions/workflow/status/jorbencas/test_githubActions/tests.yml?branch=master&style=flat-square&label=Tests&logo=github)

Automated tech news ecosystem. Collects from **350+ sources** (158 YouTube channels, 55 RSS feeds, 11 web scraping sites, 82 HTML pages, 52 GitHub Topics, 5 GitHub Repos, 1 Product Hunt, 1 GitHub Collection), processes with **AI (Gemini)**, and distributes content across multiple channels. Also manages images, resources, programming challenges, and the blog dashboard for [jorbencas/blog](https://blog-jorbencas.vercel.app/).

🚀 **[News Dashboard](http://jorbencasdownloaderdocument.surge.sh)**

---

## 📋 Overview

This project runs **11 GitHub Actions workflows** that form a fully automated content pipeline:

1. **Scrape** — news and tools from 350+ sources (158 YouTube channels, 55 RSS feeds, 11 web scraping, 82 HTML pages, 52 GitHub Topics)
2. **Process** — AI summarization with Gemini, news grouped by source, automatic translation (web + YT), image generation, deduplication
3. **Publish** — weekly recaps with source grouping, dashboard (SSR), email newsletter with video section, Telegram notifications with TTS
4. **Manage** — resource lists, challenges, image optimization, link validation, SEO dedup

---

## 📡 Sources — 350+ Total

| Category | Count | Examples |
|----------|-------|---------|
| YouTube channels | 158 | MoureDev, Fernando Herrera, The Engineer's Digest |
| RSS feeds (quick) | 55 | TechCrunch, The Verge, Wired, Ars Technica, Google Blog, Vercel Blog |
| Web scraping (quick) | 11 | Xataka, Anthropic, Ollama, Mistral, LangChain, Mozilla Hacks |
| HTML scraping | 82 | Genbeta, Slashdot, Applesfera, El País Tecnología |
| GitHub Topics | 52 | AI, LLM, Docker, Kubernetes, CSS, HTML, algorithms |
| GitHub Collections | 1 | AI Tools |
| GitHub Repos | 5 | OpenWiki, Meetily, AutoPR, PR-Agent, Code-to-Road |
| Product Hunt | 1 | Top products daily |

### Quick sources (hourly tier)

RSS and web scraping sources with `quick: True` are scraped every hour:

- **RSS (55)**: TechCrunch, The Verge, Wired, Ars Technica, Google Blog, Google AI, Vercel, Astro Releases, Docker, Kubernetes, Krebs, HN, Stack Overflow, Dev.to, NVIDIA, Machine Learning Mastery, etc.
- **Web scraping (11)**: Anthropic Research, Ollama Blog, Mistral News, Cohere, LangChain, Google Developers, HuggingFace Papers, Mozilla Hacks, Qwen Blog, DeepSeek, 01.AI
- **Chinese AI**: QbitAI (量子位), 36氪 AI, Qwen, DeepSeek, 01.AI, THUDM/ChatGLM

---

## 📂 Project Structure

```
scripts/
├── scrapers/             🌐 Data collection from 350+ sources
│   ├── scraper_base.py         YouTube, Web, ScraperPro extractors
│   ├── scrape_news.py          RSS + web + YouTube news
│   ├── scrape_tools.py         GitHub Trending + Product Hunt
│   └── screenshot_helper.mjs   Playwright screenshot helper
├── publishers/           📤 Content generation & distribution
│   ├── generate_weekly.py      AI recap + dashboard HTML (SSR)
│   ├── manage_resources.py     Pagination, cleanup, reorder resources.mdx
│   ├── merge_freefordev.py     Merge free-for-dev resources
│   ├── send_email.py           Mailgun newsletter (grouped by source + videos)
│   └── send_telegram.py        Telegram notifications with TTS
├── tools/                🔧 Maintenance utilities
│   ├── clean_news.py           Link validation
│   ├── fix_images.py           Image pipeline (Unsplash + Gemini + WebP/AVIF)
│   ├── hunt_challenges.py      AI challenge generation
│   ├── make_cover_collage.py   Cover image collages
│   ├── optimize.py             Dashboard image optimization
│   └── downloadFile.py         (legacy) Original monolith
├── utils/                🧰 Shared modules
│   ├── constants_downloadfile.py   Sources, templates, config
│   ├── constants_retos.py          Challenge configuration
│   ├── common.py                   JSON, URL, dedup, AI helpers
│   ├── utils_retos.py              Challenge utilities
│   └── cache.py                    Pluggable cache (FileCache + CacheManager)
└── solutions/            💡 Challenge solutions database
    ├── solutions_db.py            Lookup + solution generation
    └── solutions_data.py          105+ curated solutions in 12 languages
tests/                    ✅ pytest test suite (101 tests)
├── test_cache.py / test_constants_downloadfile.py
├── test_constants_retos.py / test_fix_images.py
├── test_manage_resources.py / test_solutions_db.py
└── test_utils.py
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

### ✅ Testing

| Command | Description |
|---------|-------------|
| `python -m pytest tests/ -v` | Run all tests (117 tests) |
| `python -m pytest tests/test_solutions_db.py -v` | Run specific test suite |

---

## 🤖 GitHub Actions — 11 Workflows

| Workflow | Schedule / Trigger | Pipeline |
|----------|-------------------|----------|
| **scraper_workflow** | Sat 07:00 UTC | Generate weekly recap + portadas → PR to blog |
| **scrape_hourly** | Every hour | Light scrape (RSS + quick sources) |
| **scrape_6h** | Every 6 hours | Standard scrape |
| **daily_resources** | Daily 06:00 UTC | Tools scrape + resources.mdx management |
| **send_email** | Daily 09:00 UTC | Mailgun newsletter (grouped by source + videos) |
| **send_telegram** | Every 30 min | Telegram + TTS (GitHub Actions Cache for dedup) |
| **clean_news** | Quarterly | Link health check |
| **hunt_challenges** | Weekly (Sun) | AI challenge generation |
| **optimize_images** | Dispatch from blog | Image optimization for blog |
| **dashboard_update** | Push (JS/CSS/Python/data) | Regenerate + deploy dashboard |
| **tests** | Push/PR to master | pytest (117 tests) |

### Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION                              │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_hourly   →  every hour  →  quick sources (55 RSS + 11 web) │
│  scrape_6h       →  every 6h    →  standard scrape (82 HTML pages) │
│  daily_resources →  daily       →  tools (52 GitHub Topics + repos) │
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
│  tests            →  on push     →  117 pytest tests               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📧 Email Newsletter

The daily email newsletter is sent via Mailgun with:

- **Grouped by source** — news organized by website (TechCrunch, The Verge, Xataka, etc.)
- **Translated titles** — English titles auto-translated to Spanish via Gemini
- **AI summaries** — each news item has a 3-4 line summary in Spanish
- **Video section** — YouTube videos with thumbnail, channel, and duration
- **SVG social icons** — GitHub, X/Twitter, GitLab, Email
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

- **Deduplication** — GitHub Actions Cache (`actions/cache@v4`) persists `telegram_sent.json` between runs
- **TTL** — 7-day expiration for news items, 24-hour for voice messages
- **Time filter** — only sends news from the last 24 hours
- **TTS audio** — daily voice summary via Edge TTS (es-ES-AlvaroNeural)
- **Translated titles** — Gemini translates English titles to Spanish

---

## 📊 Dashboard

Deployed on Surge.sh. Fully **server-side rendered (SSR)** — Python generates a single `index.html` with all content pre-rendered (news, YouTube videos, GitHub ranking). JavaScript is minimal and only handles interactive filters, tabs, and search.

**Recent UI improvements:**
- **Separated channel filters** — news filter uses `news_items` (no YouTube), video filter uses `video_items` (no web links)
- **Type badges** — `📄 Noticia`, `📡 RSS`, `🔧 Herramienta` in news cards; `🎬 Video`, `🩳 Short`, `🔴 Directo` in video cards
- **Footer** — "Creado con ❤️ y sin ánimo de lucro por @jorbencas" + disclaimer (no hosted content)
- **Dark theme** — news title gradient uses `#60a5fa → #3b82f6` in dark mode
- **Translation** — English YouTube channel titles (`FUENTES_INGLES`) auto-translated via Gemini during weekly recap generation

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
| `UNSPLASH_ACCESS_KEY` | Unsplash API key |

---

## 🧪 Test Coverage

117 pytest tests covering:
- **Cache** — FileCache, CacheManager, expiration, TTL, flush cleanup
- **Constants** — source configurations, email templates, challenge templates
- **Email templates** — placeholders, source headers, video sections, button styles
- **Image pipeline** — Unsplash fetching, Gemini banner gen, WebP/AVIF conversion
- **Resources** — pagination, cleanup, reordering, card management, cross-file dedup, malformed card fix
- **Solutions** — database lookup, multi-language generation, edge cases
- **Utilities** — JSON helpers, URL validation, deduplication, AI integration

---

*Maintained by **[Jorge (@jorbencas)](https://github.com/jorbencas)***
