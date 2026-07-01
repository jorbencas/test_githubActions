# Migración a n8n — Tech Pulse

## Objetivo

Reemplazar los workflows de GitHub Actions por flujos en n8n, ganando:
- Scheduler preciso (cron real, no el best-effort de GH Actions)
- GUI visual para monitorizar ejecuciones
- Backend de caché vía webhook (elimina dependencia de git push)
- Escalado horizontal (cada fuente puede ser un nodo independiente)

## Arquitectura target

```
[n8n Scheduler] ──→ [HTTP Request: scrape fuente X] ──→ [N8nCache: check] ──→ [Telegram/Email]
                        │
                        └──→ [Write JSON a repositorio / S3 / webhook]
```

## Componentes y su equivalente n8n

### Scraping

| Componente actual | Nodo n8n equivalente | Notas |
|---|---|---|
| `scrape_news.py --tier light` | `Schedule (cada 1h)` → `HTTP Request (cada RSS)` | Cada fuente RSS es un nodo HTTP independiente |
| `scrape_news.py --tier standard` | `Schedule (cada 6h)` → `HTTP Request (cada fuente web)` | Las fuentes web pueden compartir un sub-workflow "HTML Extractor" |
| `scrape_news.py --tier full` | `Schedule (cada 12h)` → `HTTP Request (YouTube + resto)` | YouTube requiere sub-workflow con lógica de extracción de JSON embebido |
| `scraper_base.py` (lógica) | `Function` node o `n8n-n8n-nodes-base.code` | La lógica de clasificación (`clasificar_noticia()`) y extracción se transpila a JS |
| `scrape_trends.py` | `Schedule` → `Playwright` (n8n node) | n8n tiene soporte nativo para Puppeteer/Playwright |

### Caché (CacheManager + backends)

| Backend actual | Backend n8n | Cómo funciona |
|---|---|---|
| `FileCache("telegram_sent.json")` | `N8nCache(webhook_url)` | n8n expone un webhook que recibe `GET` (load) y `POST` (save). El estado se guarda en una tabla de n8n o en Redis via nodo. |
| `ICacheBackend` | Interface → n8n `Webhook` node | El `CacheManager` en Python se reemplaza por la lógica de "verificar si ya se envió" dentro del flujo n8n |

### Notificaciones

| Componente actual | Nodo n8n equivalente |
|---|---|
| `send_telegram.py` | `Telegram` node (n8n tiene nodo nativo) |
| `send_email.py` | `Email` (SMTP) o `Mailgun` node |
| TTS audio (`edge-tts`) | No hay equivalente directo; se puede llamar a un webhook que ejecute un script Python |

## Estrategia de migración (fases)

### Fase 1 — Caché híbrido (ahora)
- `CacheManager` con `FileCache` para GH Actions
- `N8nCache` implementado como clase funcional que habla con webhook
- Ambos backends implementan `ICacheBackend` → sin cambios en `send_telegram.py`

### Fase 2 — Webhook intermedio
- Desplegar un endpoint n8n que reciba `POST /cache` y `GET /cache`
- Cambiar `FileCache("telegram_sent.json")` → `N8nCache("https://n8n.instance/cache")`
- El caché ahora vive en n8n, no en el repo

### Fase 3 — Flujos en n8n
1. Crear flujo "Hourly RSS Scraper" en n8n (schedule cada 1h)
2. Crear flujo "Web Scraper" (cada 6h)
3. Crear flujo "YouTube Scraper" (cada 12h)
4. Crear flujo "Telegram Dispatcher" (cada 30 min, consume del caché)
5. Crear flujo "Daily Email" (cada 24h)

### Fase 4 — Desactivar GH Actions
- Una vez que n8n cubra todos los flujos, desactivar los workflows de GH Actions
- Mantener `scraper_workflow.yml` solo para la generación semanal + deploy a Surge

## Requisitos n8n

- n8n self-hosted (Docker) o n8n.cloud
- Nodos necesarios:
  - `Schedule Trigger`
  - `HTTP Request` (para scraping)
  - `HTML Extract` (para parsear HTML)
  - `Function` / `Code` (para lógica Python→JS)
  - `Telegram`
  - `Email` (SMTP)
  - `Webhook` (para caché)
  - `Playwright` (para TikTok/Instagram/Google Trends)
- Redis o SQLite para persistencia del caché

## Flujo n8n example (RSS → Telegram)

```
[Schedule: cada 1h]
    │
    ▼
[HTTP Request: GET https://openai.com/news/feed.xml]
    │
    ▼
[HTML Extract: parsear items del XML]
    │
    ▼
[Code: clasificar noticia + asignar badge/categoría]
    │
    ▼
[Webhook: GET /cache?key={url}] ← N8nCache
    │
    ├── si existe → [NoOp] (descartar)
    │
    └── si nueva → [Webhook: POST /cache {key, ts}]
                      │
                      ▼
                    [Telegram: sendMessage]
                      │
                      ▼
                    [Code: generar audio TTS] ← edge-tts vía sub-workflow
```

## Scripts Python que se mantienen (sin migrar a n8n)

- `generate_weekly.py` — muy complejo para migrar (Gemini + templates + múltiples salidas). Se mantiene como script llamado por n8n vía `Execute Command` o por GH Actions.
- `optimize.py` — procesamiento de imágenes, no necesita scheduling.
- `downloadFile.py` — wrapper legacy, eliminar tras migración completa.
