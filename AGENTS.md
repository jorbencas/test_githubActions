# test_githubActions — Agent Guide

## Git restrictions
- NEVER run `git push`, `git pull`, or `git fetch`. These operations must be done manually by the user.

## Commands
- `python downloadFile.py` — (legacy) monolithic orchestrator
- `python scrape_news.py` — scrape news sources (YouTube + web)
- `python scrape_tools.py` — scrape tools (GitHub Trending + Product Hunt)
- `python generate_weekly.py` — generate weekly recap MD + dashboard HTML
- `python send_email.py` — send Mailgun newsletter
- `python send_telegram.py` — send Telegram notification with TTS audio
- `python clean_news.py` — validate links, prune dead entries
- `python optimize.py` — image optimization pipeline

## Stack
- Python 3.11+, async (asyncio + aiohttp)
- Gemini API (`google-genai`) for summaries, translations, solutions, images
- BeautifulSoup4 for web scraping
- Pillow + pillow-avif-plugin for image optimization
- edge-tts for Telegram voice messages (Spanish voice)
- Mailgun API for email newsletters
- Surge.sh for static dashboard deployment
- GitHub Actions for automation (11 workflows)

## Repository
- `jorbencas/test_githubActions` (branch: master)
- Deployed dashboard: `http://jorbencasdownloaderdocument.surge.sh`
- Blog target: `jorbencas/blog` (auto-news + challenges via PR)

## Architecture

### Core scripts
| Script | Purpose | Dependencies |
|--------|---------|-------------|
| `scraper_base.py` | Shared extractors (YouTube, Web, ScraperPro) | constants_downloadfile |
| `scrape_news.py` | Scrape news + YouTube sources | scraper_base, utils |
| `scrape_tools.py` | Scrape GitHub Trending + Product Hunt | scraper_base |
| `generate_weekly.py` | AI recap + dashboard HTML | constants_downloadfile, utils, scraper_base |
| `send_email.py` | Mailgun newsletter | constants_downloadfile |
| `send_telegram.py` | Telegram with TTS audio | constants_downloadfile, edge-tts |
| `downloadFile.py` | (legacy) old monolithic version | — |
| `clean_news.py` | Quarterly link health check | — |
| `optimize.py` | Image conversion (WebP/AVIF/MP4) | Pillow |

### Data files
- `files/noticias_historico.json` — full news history (max 900 entries)
- `files/herramientas.json` — discovered tools from GitHub + Product Hunt (max 200)
- `files/avatars_cache.json` — YouTube channel avatar cache
- `optimized_cache.json` — image opt results (hash-based dedup)

### Output directories
- `auto-news/` — weekly recap `.md` files (copied to blog via PR)
- `public/` — static dashboard (`index.html` + JS + CSS + images)
- `public/optimizado/` — optimized WebP/AVIF/WebM images

### Content pipeline
- **News** → `scrape_news.py` → `files/noticias_historico.json`
- **Tools** → `scrape_tools.py` → `files/herramientas.json`
- **Weekly recap** → `generate_weekly.py` → `auto-news/YYYY-W{week}-tech-recap.md`
  - Auto-archives recaps >2 weeks old to `auto-news/archive/`
  - SEO: one post per week max (dedup by week slug)
  - News grouped by category before AI processing
- **Dashboard** → `generate_weekly.py` → `public/` → Surge.sh
- **PR to blog** → `scraper_workflow.yml` (copia auto-news + recursos + imágenes)

### GitHub Actions workflows
| Workflow | Trigger | Action |
|----------|---------|--------|
| `scraper_workflow.yml` | Saturday 07:00 UTC | Generate weekly recap + portadas → PR to blog |
| `scrape_hourly_workflow.yml` | Every hour | Light scrape (RSS + quick sources) |
| `scrape_6h_workflow.yml` | Every 6 hours | Standard scrape |
| `daily_resources.yml` | Daily 06:00 UTC | Tools scrape + resources.mdx management |
| `send_email_workflow.yml` | Daily 09:00 UTC | Send Mailgun newsletter |
| `send_telegram_workflow.yml` | Every 30 min | Send Telegram with TTS audio |
| `clean_news.yml` | Quarterly (Jan/Apr/Jul/Oct) | Validate links → prune dead entries |
| `hunt_challenges.yml` | Weekly (Sun) | AI challenge generation |
| `optimize_images.yml` | Dispatch from blog | Image optimization for blog |
| `tests.yml` | Push/PR to master | pytest (89 tests) |
| `dashboard_update.yml` | Push (JS/CSS/Python) | Regenerate + deploy dashboard |

### Modular pipeline (each script is independent)

1. **News scraping** (`scrape_news.py`): YouTube + web sources → `noticias_historico.json`
2. **Tools scraping** (`scrape_tools.py`): GitHub Trending + Product Hunt → `herramientas.json`
3. **Weekly generation** (`generate_weekly.py`): AI recap (grouped by category) + dashboard → `auto-news/` + `public/`
   - Auto-archives old recaps, enforces one-post-per-week SEO
4. **Email** (`send_email.py`): Mailgun newsletter
5. **Telegram** (`send_telegram.py`): Telegram with edge-tts audio

## Secrets (GitHub)
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`, `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `EMAIL_USER`, `BLOG_TOKEN`, `UNSPLASH_ACCESS_KEY`

## Workflow
1. Always run scripts from repo root (auto-chdir not needed).
2. After modifying `constants_downloadfile.py` (templates/prompts), verify with a dry-run if possible.
3. If adding a new source, add to `FUENTES` in `constants_downloadfile.py`.
4. Each script is standalone — can be run independently or in sequence.
5. Changes affecting blog output must be tested locally first.
6. **Always update `docs/contexto.md` after any significant change**.

## Notes
- `optimized_cache.json` is auto-generated cache; safe to delete.
- Weekly recaps are NOT regenerated if the `.md` file already exists.
- Old recaps (>2 weeks) are auto-archived to `auto-news/archive/`.
- The blog repo is checked out as `./blog` in the GitHub Actions runner.
- Python venv: `.venv/` (local dev), dependencies in `requirements.txt`.
- Log files (`*.log`, `logs/`) y `prompt.txt` se pueden eliminar.
- `downloadFile.py` is kept for backward compatibility; prefer the new modular scripts.
