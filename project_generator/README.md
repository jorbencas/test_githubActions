# Project Generator 🚀

Generador automático de ideas de proyectos de software funcionales, útiles y variados. Se ejecuta vía GitHub Actions (cron) y envía los resultados a un canal privado de Telegram.

## Características

- **Niveles**: Junior / Semisenior / Senior
- **Scopes**: Miniproyecto (1-2 sem) / Proyecto (3-6 sem) / Multiproyecto (6+ sem)
- **Lenguajes**: Python, JavaScript, TypeScript, C#, Go, Rust
- **Tipos**: Web, API, CLI, Mobile, Desktop, Fullstack, Microservicio, Bot, IA/ML, Datos, DevOps, Testing, Seguridad
- **Tech Stack detallado**: Frameworks, librerías, BD, infra, IA/ML, testing con justificación por herramienta
- **IA integrada**: Especifica cuándo y por qué usar IA (OpenAI, Anthropic, Gemini, local)
- **Anti-duplicados**: Sistema de hashes para no repetir proyectos
- **Fuentes de inspiración**: Tips de Telegram, tuweb.dev (scraper), plantillas determinísticas
- **Persistencia**: Historial JSON local + artefacto en GitHub Actions
- **Notificaciones**: Envío formateado a canal Telegram (Markdown + JSON adjunto)

## Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                    GITHUB ACTIONS (CRON)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Checkout   │→ │  Install    │→ │  Generate Projects      │  │
│  │  Repo       │  │  Deps       │  │  (Python + AI)          │  │
│  └─────────────┘  └─────────────┘  └───────────┬─────────────┘  │
│                                                │                │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────▼─────────────┐  │
│  │  Commit     │← │  Upload     │← │  Send to Telegram       │  │
│  │  History    │  │  Artifact   │  │  (Bot API)              │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      CANAL TELEGRAM                             │
│  📋 Resumen + 📋 Proyecto 1 + 📋 Proyecto 2 + ... + 📦 JSON    │
└─────────────────────────────────────────────────────────────────┘
```

## Instalación Rápida

```bash
# 1. Clonar y entrar
cd project_generator

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables
cp .env.example .env
# Editar .env con tus valores (ver sección Configuración)

# 5. Probar conexión Telegram
python -m src.main test-telegram

# 6. Generar primeros proyectos
python -m src.main generate --count 3 --send-telegram
```

## Configuración

### Secrets de GitHub (OBLIGATORIOS)

Ve a **Settings → Secrets and variables → Actions → New repository secret**:

| Secret | Descripción | Ejemplo |
|--------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Token de @BotFather | `123456789:ABCdef...` |
| `TELEGRAM_REPORTS_PROYECTOS_CHANNEL_ID` | ID del canal privado | `-1001234567890` |
| `OPENAI_API_KEY` | Key de OpenAI | `sk-...` |
| `ANTHROPIC_API_KEY` | Key de Anthropic (opcional) | `sk-ant-...` |
| `GEMINI_API_KEY` | Key de Google Gemini (opcional) | `...` |

### Variables de GitHub (OPCIONALES)

**Settings → Variables → Actions → New variable**:

| Variable | Default | Descripción |
|----------|---------|-------------|
| `AI_PROVIDER` | `openai` | `openai`, `anthropic`, `gemini`, `deterministic` |
| `AI_MODEL` | `gpt-4o-mini` | Modelo específico del proveedor |
| `PROJECTS_PER_RUN` | `5` | Proyectos por ejecución |
| `SCRAPE_TUWEB_DEV` | `true` | Activar scraper de tuweb.dev |

### Obtener Channel ID de Telegram

```bash
# Opción 1: Usando el script del proyecto
cd /home/jorge/dev/devjobs/downloader_telegram/app
python get_channel_id.py "reportes proyectos"

# Opción 2: Usando el generador
python -m src.main test-telegram
# El bot enviará un mensaje de prueba y mostrará el channel_id
```

## Uso CLI

```bash
# Generar proyectos
python -m src.main generate --count 10
python -m src.main generate --count 5 --nivel senior --scope multiproyecto --lenguaje python --send-telegram

# Ver historial
python -m src.main history --list 20 --stats --verbose

# Enviar últimos proyectos a Telegram
python -m src.main send --count 5

# Probar Telegram
python -m src.main test-telegram

# Probar scrapers
python -m src.main scrape
```

## Ejemplo de Proyecto Generado

```json
{
  "titulo": "Sistema de Gestión de Ensayos para Bandas de Música",
  "descripcion_corta": "App móvil + panel web para gestionar ensayos, convocatorias y asistencia de músicos",
  "nivel": "semisenior",
  "scope": "proyecto",
  "tipo": ["mobile", "web", "api"],
  "tech_stack": {
    "lenguaje_principal": "typescript",
    "frameworks": [
      {"nombre": "React Native (Expo)", "categoria": "framework", "por_que": "Cross-platform iOS/Android, hot reload, ecosistema maduro"},
      {"nombre": "Next.js", "categoria": "framework", "por_que": "Panel web SSR, API routes, optimizado para SEO"}
    ],
    "librerias": [
      {"nombre": "Zustand", "categoria": "state", "por_que": "Simple, sin boilerplate, TypeScript nativo"},
      {"nombre": "React Query", "categoria": "data", "por_que": "Cache, sync, optimistic updates para API"}
    ],
    "bases_datos": [
      {"nombre": "PostgreSQL", "categoria": "db", "por_que": "Relacional, JSONB para metadata flexible, multi-tenant nativo"}
    ],
    "infraestructura": [
      {"nombre": "Docker Compose", "categoria": "infra", "por_que": "Dev/prod parity, multi-servicio local"}
    ],
    "ia_ml": [
      {"nombre": "OpenAI Embeddings", "categoria": "ia", "por_que": "Búsqueda semántica de repertorios, clustering de músicos"}
    ],
    "testing": [
      {"nombre": "Jest + React Testing Library", "categoria": "testing", "por_que": "Unit + integration, coverage, snapshot"}
    ]
  },
  "funcionalidades_clave": [
    "CRUD ensayos/actuaciones con repertorio",
    "Convocatoria por cuerda/instrumento/individuo",
    "Respuesta asistencia con estados (pendiente/confirmado/rechazado)",
    "Notificaciones push (FCM/APNs) + email transaccional",
    "Panel junta: calendario, lista, transporte, uniformes",
    "App músico: agenda personal, chat interno, encuestas anónimas"
  ],
  "por_que_ia": "Clasificación automática de disponibilidad por patrones históricos + generación de resúmenes de actas con LLM",
  "cliente_ia_sugerido": "openai",
  "complejidad_estimada": "media",
  "tiempo_estimado_semanas": 4,
  "fuente_inspiracion": "tips_telegram"
}
```

## Estructura del Proyecto

```
project_generator/
├── .github/workflows/
│   └── generate-projects.yml      # GitHub Action cron
├── src/
│   ├── config.py                  # Settings (pydantic-settings)
│   ├── models.py                  # Modelos Pydantic (Proyecto, TechStack, etc.)
│   ├── ai_providers.py            # Abstracción IA (OpenAI, Anthropic, Gemini, Deterministic)
│   ├── prompts.py                 # System prompt + user prompt builder + validación
│   ├── scrapers.py                # Scrapers tuweb.dev + tips Telegram
│   ├── generator.py               # Orquestador principal
│   ├── telegram_sender.py         # Envío formateado a Telegram Bot API
│   └── main.py                    # CLI entry point
├── requirements.txt
├── .env.example
└── README.md
```

## Personalización

### Añadir nuevo proveedor IA

1. Crear clase en `ai_providers.py` heredando de `AIProvider`
2. Implementar `generate()` y `get_model_name()`
3. Registrar en `get_provider()`

### Añadir nueva fuente de inspiración

1. Crear scraper en `scrapers.py` 
2. Retornar `List[Dict]` con claves: `titulo`, `descripcion`, `fuente`, `url` (opcional)
3. Integrar en `generator._get_external_inspiration()`

### Modificar plantillas determinísticas

Editar `DeterministicProvider._load_templates()` en `ai_providers.py`

## Reglas de Generación (Hardcoded en System Prompt)

1. ✅ Proyectos funcionales y útiles en mundo real
2. ✅ Tech stack coherente con nivel/scope
3. ✅ Justificación por herramienta (`por_que`)
4. ✅ IA solo si aporta valor real (clasificación, generación, análisis, embeddings)
5. ✅ Mobile permitido (Flutter, React Native, MAUI) — **NO solo iOS nativo**
6. ✅ Anti-duplicados vía hash MD5(titulo+lenguaje+descripcion)
7. ✅ Variedad forzada en niveles, scopes, lenguajes, tipos

## Troubleshooting

| Problema | Solución |
|----------|----------|
| `TELEGRAM_BOT_TOKEN` inválido | Verificar en @BotFather, regenerar si necesario |
| `CHANNEL_ID` no encontrado | Bot debe ser admin en el canal. Usar `get_channel_id.py` |
| Rate limit Telegram | Action espera 0.5s entre mensajes. Reducir `PROJECTS_PER_RUN` |
| IA devuelve JSON inválido | Reintenta automáticamente (3x). Revisa `AI_MODEL` válido |
| Duplicados constantes | Limpia `data/generated_projects.json` o aumenta `temperature` |

## Licencia

MIT - Úsalo libremente para generar ideas de proyectos reales.