# GitHub Secrets para FormulaTV Daily Premieres → Telegram

Configura en: **Settings → Secrets and variables → Actions → New repository secret**

## Telegram Bot (requerido)

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token del bot (de @BotFather) | `123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ` |
| `SALUDO_CHAT_ID` | ID del chat/grupo/canal destino (el mismo que usan los saludos/greetings) | `-1001234567890` o `@canal` |
| `TELEGRAM_REPORT_IMG_TOPIC_ID` | Topic ID del foro "report img" (opcional) | `123` |

---

## Configuración paso a paso

### 1. Crear bot de Telegram
1. Habla con **@BotFather** en Telegram
2. `/newbot` → nombre → username (debe terminar en `bot`)
3. Copia el **token** → añade como secret `TELEGRAM_BOT_TOKEN`

### 2. Obtener Chat ID (usa SALUDO_CHAT_ID)
**El mismo ID que usan los saludos/greetings diarios**

Si ya tienes configurados los saludos automáticos, **usa ese mismo chat ID**:

1. **Grupo/Canal público**: username (ej: `@mi_canal`) o ID numérico
2. **Grupo privado**: ve a `https://api.telegram.org/bot<TOKEN>/getUpdates`, busca `"chat":{"id":-1001234567890,...}`

Añade como secret `SALUDO_CHAT_ID` (mismo valor que usas para los saludos diarios).

### 3. Topic ID (foro "report img") - Opcional
Si el chat es un **grupo con temas (foro)**:
1. En el grupo, ve al tema "report img"
2. La URL tiene `#topic/123` o usa `@RawDataBot` para ver el `message_thread_id`
3. Añade como secret `TELEGRAM_REPORT_IMG_TOPIC_ID`

---

## Qué hace el workflow

1. **Ejecuta cada día a las 07:00 UTC (09:00 Madrid)**
2. **Scrapea** `https://www.formulatv.com/calendario/series/` (mes actual)
3. **Filtra** SOLO estrenos DE HOY (no días anteriores)
3. **Filtra** plataformas españolas (Movistar+, RTVE, Atresmedia, Mediaset, Filmin, Netflix, Prime Video, Disney+, HBO Max, Paramount+, autonómicas)
4. **Evita duplicados** usando `files/formulatv_sent.json` (persistente entre runs)
5. **Envía a Telegram** como mensaje HTML formateado:
   - Header: "🎬 Estrenos de HOY — 8 de octubre de 2026"
   - Agrupado por plataforma
   - Cada serie: título, género, tipo (película/serie), enlace FormulaTV
6. **Guarda log** de enviados para no repetir

---

## Ejecución local

```bash
# Dry-run (ver mensaje sin enviar)
python scripts/scrape_formulatv_telegram.py --dry-run

# Con filtro español (default)
python scripts/scrape_formulatv_telegram.py

# Sin filtro (todas las plataformas)
python scripts/scrape_formulatv_telegram.py --todas

# Variables de entorno necesarias:
export TELEGRAM_BOT_TOKEN="123:ABC"
export TELEGRAM_CHAT_ID="-1001234567890"
export TELEGRAM_REPORT_IMG_TOPIC_ID="123"  # opcional
```

---

## Variables de entorno

| Variable | Requerida | Descripción |
|----------|-----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Sí | Token de @BotFather |
| `TELEGRAM_CHAT_ID` | Sí | ID del chat/grupo/canal |
| `TELEGRAM_REPORT_IMG_TOPIC_ID` | No | Topic ID del foro "report img" |

---

## Formato del mensaje Telegram

```
🎬 <b>Estrenos de HOY</b> — 8 de octubre de 2026

📺 <b>Series y películas que se estrenan hoy en plataformas españolas:</b>

📍 <b>Movistar+</b>
  🎬 <b>El Castillo</b> (Crimen)
     🔗 <a href="...">Ver en FormulaTV</a>

📍 <b>Netflix</b>
  🎬 <b>Bajo la superficie</b> (Drama) 🎬 Película
     🔗 <a href="...">Ver en FormulaTV</a>

📡 <i>Fuente: FormulaTV calendario</i>
🤖 <i>Bot automático — 14:04</i>
```

---

## Persistencia anti-duplicados

- Archivo: `files/formulatv_sent.json` (subido como artifact 30 días)
- Clave: `titulo|fecha` (ej: `El Castillo|2026-10-08`)
- Máximo 1000 entradas (rotación automática)
- Si el workflow falla y re-ejecuta, NO re-envía lo ya enviado