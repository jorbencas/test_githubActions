# Project Generator — Secrets y Variables

Toda la automatización vive en **este repositorio** (`jorbencas/test_githubActions`).
El proyecto se migró desde `devjobs`; ya no hay referencias cruzadas entre repos.

Workflow: `.github/workflows/generate-projects.yml` (cron `0 */4 * * *` + `workflow_dispatch`).

## Secrets (obligatorios)

**Settings → Secrets and variables → Actions → New repository secret**

| Secret | Descripción |
|--------|-------------|
| `TELEGRAM_BOT_TOKEN` | Token del bot de @BotFather. Debe ser **admin** del canal. |
| `TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID` | ID del canal destino (empieza por `-100`). |
| `GEMINI_API_KEY` | Key de Google AI Studio. Sin ella el workflow falla. |

## Variables (opcionales)

**Settings → Variables and secrets → Actions → New repository variable**

| Variable | Default | Descripción |
|----------|---------|-------------|
| `AI_MODEL` | `gemini-2.5-flash` | Debe ser un modelo **2.x** (usa `system_instruction`). |
| `PROJECTS_PER_RUN` | `3` | Proyectos por ejecución (en `workflow_dispatch` gana el input `count`). |
| `SCRAPE_TUWEB_DEV` | `true` | Scraping de ideas en tuweb.dev. |

## Obtener el Channel ID

```bash
cd project_generator
python -m src.main test-telegram                      # envía mensaje de prueba
python -m src.get_channel_id                          # lista chats recientes
python -m src.get_channel_id "reportes proyectos"     # filtra por nombre
```

## Fallo de Gemini

`ALLOW_DETERMINISTIC_FALLBACK` está fijado a `false` en el workflow a propósito: si Gemini
falla, la ejecución **falla** en lugar de generar siempre las mismas plantillas fijas.
Para depurar en local, ponlo a `true` en tu `.env`.
