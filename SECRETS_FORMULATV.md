# GitHub Secrets requeridos para FormulaTV Calendar Scraper

Configura estos secrets en: **Settings → Secrets and variables → Actions → New repository secret**

## Google OAuth Credentials (para Google Calendar API)

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `GOOGLE_CLIENT_ID` | Client ID de Google Cloud Console | `123456789-abc.apps.googleusercontent.com` |
| `GOOGLE_CLIENT_SECRET` | Client Secret de Google Cloud Console | `GOCSPX-xxxxxxxxxxxx` |
| `GOOGLE_CALLBACK_URL` | Redirect URI autorizada | `http://localhost/api/auth/google/callback` |

## Google Calendar Token (pre-autenticado)

| Secret | Descripción | Cómo obtener |
|--------|-------------|--------------|
| `GOOGLE_CREDENTIALS_JSON` | Contenido completo de `google_credentials.json` | Copia el archivo completo |
| `GOOGLE_TOKEN_JSON` | Contenido completo de `google_token.json` (token OAuth ya autenticado) | Ejecuta `python scripts/scrape_formulatv_espana.py --crear-eventos` en local, copia `config/google_token.json` |

---

## Configuración paso a paso

### 1. Google Cloud Console
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Selecciona tu proyecto → **APIs y servicios** → **Biblioteca**
3. Busca **"Google Calendar API"** → **Habilitar**
4. **APIs y servicios** → **Credenciales** → **Crear credenciales** → **ID de cliente OAuth**
   - Tipo: **Aplicación de escritorio** (o "Web application" si usas callback HTTP)
   - Nombre: "FormulaTV Calendar Scraper"
   - **URIs de redirección autorizados**: `http://localhost/api/auth/google/callback`
5. Copia **Client ID** y **Client Secret** → añade como secrets `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`

### 2. Generar token OAuth local (una sola vez)
```bash
# En tu máquina local
cd test_githubActions
cp config/google_credentials.json.example config/google_credentials.json
# Edita google_credentials.json con tu Client ID/Secret

# Ejecuta el script para autenticar (abrirá navegador)
python scripts/scrape_formulatv_espana.py --crear-eventos --guardar-json
# Se abrirá navegador → autoriza acceso a Google Calendar
# Se generará config/google_token.json
```

### 3. Añadir secrets en GitHub
- `GOOGLE_CREDENTIALS_JSON`: Contenido completo de `config/google_credentials.json`
- `GOOGLE_TOKEN_JSON`: Contenido completo de `config/google_token.json` (generado en paso 2)
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `GOOGLE_CALLBACK_URL`: Del paso 1

### 4. Verificar
El workflow se ejecuta automáticamente cada 2 días (06:00 UTC) o manualmente desde **Actions → FormulaTV Calendar Scraper → Run workflow**.

---

## Qué hace el scraper

1. **Descarga** `https://www.formulatv.com/calendario/series/` (mes actual)
2. **Parsea** atributos `data-tip-*` de las píldoras del calendario (HTML)
3. **Extrae** 28+ series con: título, fecha, cadena/plataforma, género, temporadas, capítulos
4. **Crea eventos** en Google Calendar:
   - 🕐 **09:00** hora local (Europe/Madrid)
   - ⏰ **Recordatorio 30 min** antes (popup)
   - 🔄 **Deduplicación** por título + fecha
   - 📝 Descripción con género, cadena, temporadas, capítulos, enlace FormulaTV
5. **Guarda** JSON en `files/formulatv_espana_series.json` (artifact de 30 días)
5. **Sube** JSON como artifact (30 días retención)

---

## Ejecución manual

```bash
# Local (dry-run)
python scripts/scrape_formulatv_espana.py --dry-run

# Local (crear eventos + guardar JSON)
python scripts/scrape_formulatv_espana.py --crear-eventos --guardar-json
```

---

## Notas

- **Solo mes actual**: FormulaTV solo expone el mes actual en `/calendario/series/`. El workflow corre cada 2 días, así que siempre captura estrenos del mes en curso.
- **Sin API key**: No requiere TMDB, TVMaze, ni keys de API. Solo HTML público de FormulaTV.
- **Sin navegador**: Usa requests + BeautifulSoup, funciona en GitHub Actions sin Playwright/Selenium.
- **Deduplicación**: Evita eventos duplicados comprobando título + fecha en Google Calendar antes de crear.