# test_githubActions — Agent Guide

## Git restrictions
- NEVER run `git push`, `git pull`, or `git fetch`. These operations must be done manually by the user.

## Commands
- `python downloadFile.py` — run main scraper (news collection + publishing)
- `python hunt_challenges.py` — hunt for coding challenges + generate solutions
- `python clean_news.py` — validate links, prune dead entries
- `python optimize.py` — image optimization pipeline

## Stack
- Python 3.11+, async (asyncio + aiohttp)
- Gemini API (`google-genai`) for summaries, translations, solutions, images
- BeautifulSoup4 + Playwright for web scraping
- Pillow + pillow-avif-plugin for image optimization
- edge-tts for Telegram voice messages (Spanish voice)
- Mailgun API for email newsletters
- Surge.sh for static dashboard deployment
- GitHub Actions for automation (3 workflows)

## Repository
- `jorbencas/test_githubActions` (branch: master)
- Deployed dashboard: `http://jorbencasdownloaderdocument.surge.sh`
- Blog target: `jorbencas/blog` (auto-news + challenges via PR)

## Architecture

### Core scripts
| Script | Purpose |
|--------|---------|
| `downloadFile.py` | Orchestrator: scrapes 30+ sources, dedup, AI summary, generates recap MD + dashboard + email + Telegram |
| `hunt_challenges.py` | Scrapes challenge websites, generates solution MDX with AI/DB/generic fallback |

| `clean_news.py` | Quarterly link health check + dead entry removal |
| `optimize.py` | Image conversion (WebP/AVIF/MP4) with SSIM-guided compression |
| `utils.py` | Shared AI helpers (solutions, recaps, images, translations) |
| `solutions_db.py` | Hardcoded solutions database (5 challenges × 12 languages) + generic generators |
| `constants_downloadfile.py` | All config: sources, API keys, templates, prompts |

### Data files
- `files/noticias_historico.json` — full history (max 900 entries)
- `files/all_news.json` — alternative history (max 600, pruned quarterly)
- `files/avatars_cache.json` — YouTube channel avatar cache
- `optimized_cache.json` — image opt results (hash-based dedup)

### Output directories
- `auto-news/` — weekly recap `.md` files (copied to blog via workflow)
- `auto-challenges/` — challenge `.mdx` files
- `public/` — static dashboard (`index.html` + styles + scripts + images)
- `public/optimizado/` — optimized WebP/AVIF/WebM images
- `images/` — raw downloaded images

### Content pipeline
- **Weekly recaps** → `downloadFile.py` → `auto-news/YYYY-W{week}-tech-recap.md`
- **Challenges** → `hunt_challenges.py` → `auto-challenges/guia-{slug}.mdx`
- **Dashboard** → `downloadFile.py` → `public/index.html` → deployed to Surge.sh

### GitHub Actions workflows
| Workflow | Trigger | Action |
|----------|---------|--------|
| `scraper_workflow.yml` | Saturday 07:00 UTC | Optimize images → scrape → generate recap → PR to blog → deploy Surge |
| `hunt_challenges.yml` | Sunday 23:00 UTC | Hunt challenges → generate solutions → PR to blog |
| `clean_news.yml` | Quarterly (Jan/Apr/Jul/Oct) | Validate links → prune dead entries |

### 3-tier challenge solution fallback
1. **Local DB** (`solutions_db.lookup`) — 5 complete solutions in 12 languages
2. **Gemini AI** (`obtener_solucion_ia`) — dynamic generation
3. **Generic generator** (`generate_generic`) — stub code with explanation templates

### Language rotation (Codeember)
12 languages cycled per challenge file: Python, JavaScript, TypeScript, Go, Rust, Java, C#, Kotlin, Swift, PHP, Ruby, Dart.

## Subagentes

### `migrate-challenges-to-blog`
Migra scripts de retos/soluciones/guías de `test_githubActions` al blog (`jorbencas/blog`), dejando solo el pipeline de news/weekly aquí.

Uso: invocar el subagente `migrate-challenges-to-blog` desde cualquier sesión en este proyecto.

## Secrets (GitHub)
`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`, `GEMINI_API_KEY`, `MAILGUN_API_KEY`, `MAILGUN_DOMAIN`, `EMAIL_USER`, `BLOG_TOKEN`

## Workflow
1. Always run scripts from repo root (auto-chdir not needed).
2. After modifying `constants_downloadfile.py` (templates/prompts), verify with a dry-run if possible.
3. If adding a new source, add to `FUENTES` in `constants_downloadfile.py`.
4. If adding a challenge language, update `LANGS` in `solutions_data.py` and `solutions_db.py`.
5. Changes affecting blog output must be tested locally first.
6. **Always update `docs/contexto.md` after any significant change** — keep "Última actualización" date fresh, update source list, architecture notes, and file references.
## Notes
- `optimized_cache.json` is auto-generated cache; safe to delete.
- Weekly recaps are NOT regenerated if the `.md` file already exists.
- The blog repo is checked out as `./blog` in the GitHub Actions runner.
- Python venv: `.venv/` (local dev), dependencies in `requirements.txt`.
- Log files (`*.log`, `logs/`) y `prompt.txt` se pueden eliminar — no son necesarios.
