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

Automated tech news ecosystem. Collects, processes with **AI (Gemini)**, and distributes content across multiple channels. Also manages images, resources, programming challenges, and the blog dashboard for [jorbencas/blog](https://blog-jorbencas.vercel.app/).

🚀 **[News Dashboard](http://jorbencasdownloaderdocument.surge.sh)**

---

## 📋 Overview

This project runs **11 GitHub Actions workflows** that form a fully automated content pipeline:

1. **Scrape** — news and tools from 50+ sources (RSS, web, YouTube)
2. **Process** — AI summarization with Gemini, news grouped by category, translation, image generation
3. **Publish** — weekly recaps with auto-archive, dashboard (SSR), email newsletter, Telegram notifications
4. **Manage** — resource lists, challenges, image optimization, link validation, SEO dedup

---

## 📂 Project Structure

```
scripts/
├── scrapers/             🌐 Data collection from 50+ sources
│   ├── scraper_base.py         YouTube, Web, ScraperPro extractors
│   ├── scrape_news.py          RSS + web + YouTube news
│   ├── scrape_tools.py         GitHub Trending + Product Hunt
│   └── screenshot_helper.mjs   Playwright screenshot helper
├── publishers/           📤 Content generation & distribution
│   ├── generate_weekly.py      AI recap + dashboard HTML (SSR)
│   ├── manage_resources.py     Pagination, cleanup, reorder resources.mdx
│   ├── merge_freefordev.py     Merge free-for-dev resources
│   ├── send_email.py           Mailgun newsletter
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
tests/                    ✅ pytest test suite (89 tests)
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
| `python -m scripts.scrapers.scrape_tools` | GitHub Trending + Product Hunt |

### 📤 Publishing

| Command | Description |
|---------|-------------|
| `python -m scripts.publishers.generate_weekly --blog-path blog` | Generate weekly recap + dashboard (SSR) |
| `python -m scripts.publishers.send_email` | Send Mailgun newsletter |
| `python -m scripts.publishers.send_telegram` | Send Telegram notification with TTS |
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
| `python -m pytest tests/ -v` | Run all tests (89 tests) |
| `python -m pytest tests/test_solutions_db.py -v` | Run specific test suite |

---

## 🤖 GitHub Actions — 11 Workflows

| Workflow | Schedule / Trigger | Pipeline |
|----------|-------------------|----------|
| **scraper_workflow** | Sat 07:00 UTC | Generate weekly recap + portadas → PR to blog |
| **scrape_hourly** | Every hour | Light scrape (RSS + quick sources) |
| **scrape_6h** | Every 6 hours | Standard scrape |
| **daily_resources** | Daily 06:00 UTC | Tools scrape + resources.mdx management |
| **send_email** | Daily 09:00 UTC | Mailgun newsletter |
| **send_telegram** | Every 30 min | Telegram with TTS audio |
| **clean_news** | Quarterly | Link health check |
| **hunt_challenges** | Weekly (Sun) | AI challenge generation |
| **optimize_images** | Dispatch from blog | Image optimization for blog |
| **dashboard_update** | Push (JS/CSS/Python) | Regenerate + deploy dashboard |
| **tests** | Push/PR to master | pytest (89 tests) |

### Workflow Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA COLLECTION                              │
├─────────────────────────────────────────────────────────────────────┤
│  scrape_hourly  →  every hour  →  RSS + quick sources              │
│  scrape_6h      →  every 6h    →  standard scrape                  │
│  daily_resources →  daily       →  tools + resources.mdx           │
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
│  tests            →  on push     →  89 pytest tests                │
└─────────────────────────────────────────────────────────────────────┘
```

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

## 📊 Dashboard

Deployed on Surge.sh. Fully **server-side rendered (SSR)** — Python generates a single `index.html` with all content pre-rendered (news, YouTube videos, GitHub ranking). JavaScript is minimal (~135 lines) and only handles interactive filters, tabs, and search.

Weekly recaps auto-archive old posts (>2 weeks) and enforce one-post-per-week SEO. News is grouped by category before AI processing for better context.

---

## 🧪 Test Coverage

89 pytest tests covering:
- **Cache** — FileCache, CacheManager, expiration, TTL
- **Constants** — source configurations, challenge templates
- **Image pipeline** — Unsplash fetching, Gemini banner gen, WebP/AVIF conversion
- **Resources** — pagination, cleanup, reordering, card management
- **Solutions** — database lookup, multi-language generation, edge cases
- **Utilities** — JSON helpers, URL validation, deduplication, AI integration

---

*Maintained by **[Jorge (@jorbencas)](https://github.com/jorbencas)***
