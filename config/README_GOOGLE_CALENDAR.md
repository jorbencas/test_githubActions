# Google Calendar Integration para Filmaffinity/Filmaffinity

Este documento explica cómo configurar la integración con Google Calendar para crear automáticamente eventos de estrenos de series en Filmaffinity.

## 📋 Requisitos previos

1. **Cuenta de Google** con acceso a Google Calendar
2. **Proyecto en Google Cloud Console** con Calendar API habilitada
3. **Credenciales OAuth 2.0** (tipo "Aplicación de escritorio")

## 🔧 Configuración paso a paso

### 1. Crear proyecto en Google Cloud Console

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el **Project ID**

### 2. Habilitar Google Calendar API

1. En el menú lateral: **APIs y servicios** → **Biblioteca**
2. Busca "Google Calendar API"
3. Haz clic en **Habilitar**

### 3. Crear credenciales OAuth 2.0

1. En el menú lateral: **APIs y servicios** → **Credenciales**
2. **Crear credenciales** → **ID de cliente OAuth**
3. Tipo de aplicación: **Aplicación de escritorio** (Desktop app)
4. Nombre: `Filmaffinity-Filmaffinity Calendar Bot`
4. Copia el **Client ID** y **Client Secret**

### 4. Configurar archivo de credenciales

Copia el archivo de ejemplo y edítalo con tus credenciales:

```bash
cp config/google_credentials.json.example config/google_credentials.json
```

Edita `config/google_credentials.json` con tus datos:

```json
{
  "installed": {
    "client_id": "TU_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "tu-proyecto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "TU_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

### 3. Configurar secrets en GitHub

Ve a tu repositorio en GitHub → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**:

| Nombre | Valor |
|--------|-------|
| `GOOGLE_CREDENTIALS` | Contenido completo del JSON de credenciales (todo el JSON en una línea) |
| `GOOGLE_TOKEN` | *(Se genera automáticamente en la primera ejecución, déjalo vacío inicialmente)* |

**Para obtener GOOGLE_CREDENTIALS en una línea:**
```bash
cat config/google_credentials.json | tr -d '\n' | pbcopy
# O en Linux:
cat config/google_credentials.json | tr -d '\n' | xclip -selection clipboard
```

### 4. Primera ejecución (generar token)

La primera vez que se ejecute el workflow, se abrirá un flujo de autorización OAuth. Como GitHub Actions no puede hacer OAuth interactivo, necesitas:

1. **Ejecuta localmente una vez** para generar el token:
   ```bash
   cd test_githubActions
   python scripts/google_calendar_filmin.py --test
   ```
   Se abrirá el navegador → Autoriza el acceso → Se guardará `config/google_token.json`

2. Sube el token a GitHub Secrets:
   ```bash
   cat config/google_token.json | tr -d '\n' | pbcopy
   # Pega en GitHub Secrets como GOOGLE_TOKEN
   ```

### 5. Uso en GitHub Actions

El workflow se ejecuta automáticamente:
- **Cada lunes a las 06:00 UTC** (programado)
- **Manual** via `workflow_dispatch` con opciones:
  - `dry_run`: Solo mostrar qué haría
  - `crear_todos`: Crear todos los eventos en Calendar

### Uso local

```bash
# Test de conexión
python scripts/google_calendar_filmin.py --test

# Dry run (ver qué eventos crearía)
python scripts/google_calendar_filmin.py --dry-run

# Crear todos los eventos
python scripts/google_calendar_filmin.py --crear-todos

# Listar próximos 30 días
python scripts/google_calendar_filmin.py --listar 30

# Limpiar eventos > 30 días
python scripts/google_calendar_filmin.py --limpiar 30
```

## 📅 Series configuradas

El script incluye 10 series españolas programadas para 2026 en Filmaffinity:

| Serie | Estreno | Género |
|-------|---------|--------|
| El tiempo que te doy | 2026-01-15 | Drama romántico |
| El cuerpo en llamas | 2026-02-01 | True crime / Thriller |
| Reina Roja | 2026-02-29 | Thriller policial |
| La chica de nieve | 2026-03-01 | Thriller |
| El fotógrafo de Mauthausen | 2026-03-15 | Drama histórico |
| El caso Asunta | 2026-04-15 | True crime |
| El caso Alcásser | 2026-05-01 | True crime / Documental |
| El corazón del océano | 2026-05-01 | Drama de época |
| Entre tierras | 2026-06-01 | Drama romántico / Época |
| Los ilusos 13+13 | 2026-09-03 | Drama / Metacine |

## 🔧 Personalización

Para añadir/quitar series, edita la lista `SERIES_FILMIN_2026` en:
- `scripts/scrapers/scrape_filmaffinity_filmin.py`
- `scripts/google_calendar_filmin.py`

Cada serie requiere:
```python
{
    "nombre": "Nombre de la serie",
    "director": "Director/a",
    "protagonistas": ["Actor 1", "Actor 2"],
    "estreno_filmin": "2026-MM-DD",  # Formato YYYY-MM-DD
    "temporadas": 1,
    "capitulos": 8,
    "genero": "Género"
}
```

## 🔒 Seguridad

- **Nunca** subas `google_credentials.json` ni `google_token.json` al repositorio
- Usa **GitHub Secrets** para almacenar credenciales
- El archivo `config/google_token.json` se genera automáticamente y contiene tokens de acceso
- Los tokens expiran y se renuevan automáticamente

## 🐛 Solución de problemas

| Error | Solución |
|-------|----------|
| `invalid_grant` | El token expiró. Borra `config/google_token.json` y vuelve a autorizar |
| `redirect_uri_mismatch` | Verifica que `http://localhost` esté en URIs de redirección autorizadas en Google Cloud |
| `access_denied` | Verifica que el usuario tenga acceso al calendario |
| `quota_exceeded` | Límite de cuota de API superado. Espera o solicita aumento de cuota |

## 📚 Referencias

- [Google Calendar API](https://developers.google.com/calendar/api)
- [OAuth 2.0 para aplicaciones de escritorio](https://developers.google.com/identity/protocols/oauth2/native-app)
- [Python Quickstart](https://developers.google.com/calendar/api/quickstart/python)