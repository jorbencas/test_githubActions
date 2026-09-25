# Secrets requeridos en devjobs para Project Generator

Configurar en: **Settings → Secrets and variables → Actions → New repository secret**

## Obligatorios

| Secret | Valor | Origen |
|--------|-------|--------|
| `TELEGRAM_BOT_TOKEN` | `123456789:ABCdef...` | Copiar de test_githubActions |
| `TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID` | `-1004497081221` | Ya obtenido |
| `GEMINI_API_KEY` | `AIza...` | Copiar de test_githubActions |

## Opcionales (para otros providers)

| Secret | Valor | Origen |
|--------|-------|--------|
| `OPENAI_API_KEY` | `sk-...` | Si usas OpenAI |
| `ANTHROPIC_API_KEY` | `sk-ant-...` | Si usas Anthropic |

## Variables opcionales (Settings → Variables → Actions)

| Variable | Default | Descripción |
|----------|---------|-------------|
| `AI_PROVIDER` | `gemini` | `openai`, `anthropic`, `gemini`, `deterministic` |
| `AI_MODEL` | `gemini-1.5-flash` | Modelo específico |
| `SCRAPE_TUWEB_DEV` | `true` | Activar scraper |
| `PROJECTS_PER_RUN` | `5` | Proyectos por ejecución |

## Flujo actual (sin PAT)

```
devjobs (cron lunes 9am / manual)
  │
  ▼ workflow_call (usa github.token nativo)
generate-projects-internal.yml
  │
  ├── checkout devjobs (github.token)
  ├── pip install
  ├── python -m src.main generate --send-telegram
  ├── Sends to Telegram (secrets: TELEGRAM_*, GEMINI_API_KEY)
  ├── Commits history to devjobs (github.token)
  ▼
```

## Ventajas

- ✅ **Sin GH_PAT** — usa `github.token` nativo
- ✅ **Un solo repo** — todo en devjobs
- ✅ **Menos permisos** — solo `contents: write` en workflow interno
- ✅ **Mismo resultado** — proyectos en Telegram + historial en devjobs

## Para probar manualmente

Actions → **[PROJECTS] Generate Projects** → Run workflow → elegir parámetros → Run