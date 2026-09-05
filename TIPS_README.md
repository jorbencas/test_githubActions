# Tips de IT — Gemini + DB Local

Bot de Telegram que envia **10 tips cada 3 horas**. Gemini genera tips dinamicos usando noticias y herramientas trending como fuente. DB estatica como fallback. **Nunca repite tips.**

## Como funciona

```
Cada 3 horas (00:00, 03:00, 06:00, ..., 21:00 UTC)
    |
    +---> Selecciona 5-6 categorias al azar (de 266)
    |
    +---> Gemini genera 5 tips nuevos
    |      - Usa noticias de tech como inspiracion
    |      - Usa herramientas trending de GitHub
    |      - Respeta historial para NUNCA repetir
    |
    +---> DB estatica: 5 tips no enviados
    |      - Si DB agotada -> solo Gemini (10 tips)
    |
    +---> Mezcla = 10 tips unicos
    |
    +---> Enviar a Telegram
    |
    +---> Guarda titulos en historial (PERMANENTE)
```

## Formato de los tips

Los tips se envian limpios, sin emojis, en formato breadcrumb:

```
Buenos dias
Miercoles 12 de Agosto 2026 -- 11:40
-----------------------------------------

xclip -selection clipboard < archivo.txt copia el contenido al portapapeles en Linux. En macOS: cat archivo.txt | pbcopy.

-----------------------------------------

git bisect start, git bisect bad (commit actual), git bisect good v1.0 (ultima version que funcionaba). Git prueba commits y te dice cual rompio todo.

-----------------------------------------

self es la referencia al objeto actual. En una clase, self.nombre = 'Juan' guarda 'Juan' en la instancia. Es como 'this' en Java/JS pero explicito.
```

### Reglas de formato

- Sin emojis en titulos ni bodies
- Sin "Tip 1:", "Tip 2:", etc.
- Sin "Categoria / Nivel / Fuente"
- Sin footer
- Cada tip = 1 idea clara y concreta
- Codigo SOLO cuando es necesario (comandos, SQL, bash, scripts, config)
- Sin codigo para conceptos, principios, consejos
- **TODO en castellano (espanol)**: titulos y bodies siempre en espanol
- Terminos tecnicos: se traducen al castellano y se pone la forma inglesa entre parentesis la primera vez (p. ej. "arranque en frio (cold start)", "equilibrador de carga (load balancer)", "cola de mensajes (message queue)")
- Siglas/acronimos: expandir entre parentesis la primera vez (VPN = Virtual Private Network) + una frase breve que la explique en contexto
- Los conceptos ("type": "concepto") deben tener una explicacion DIDACTICA y extensa: 3-5 parrafos con analogia o ejemplo cotidiano, como funciona por dentro, cuando usarlo y cuando evitarlo, y errores o malentendidos comunes

## Fuentes de datos

| Fuente | Archivo | Que usa |
|--------|---------|---------|
| Noticias scraping | `files/noticias_historico.json` | 10-15 noticias recientes como inspiracion |
| GitHub trending | `files/herramientas.json` | 5-10 tools trending como inspiracion |
| DB estatica | `scripts/utils/tips_database.json` | 708 tips + `scripts/utils/concepts_database.json` 283 conceptos como fallback |
| Historial | `tips_history.json` | Todos los titulos enviados (nunca repetir) |

## Categorias (266)

### Sistemas Operativos
`linux`, `windows`, `ubuntu`, `macos`, `android`, `android_studio`, `ios`, `vim`, `vscode`

### Lenguajes de Programacion
`python`, `javascript`, `typescript`, `rust`, `go`, `java`, `kotlin`, `cpp`, `c`, `csharp`, `swift`, `php`, `ruby`

### Frameworks y Librerias
`react`, `vue`, `angular`, `svelte`, `astro`, `nextjs`, `nuxt`, `nodejs`, `fastapi`, `django`, `flask`, `express`, `spring`, `dotnet`, `flutter`, `react_native`

### Patrones y Arquitecturas
`oop`, `design_patterns`, `rust_patterns`, `csharp_patterns`, `go_patterns`, `python_patterns`, `javascript_patterns`, `typescript_patterns`
`arch_hexagonal`, `arch_clean`, `arch_mvc`, `arch_cqrs`, `arch_event_sourcing`, `solid`, `func_prog`, `reactive_prog`, `concurrent_prog`, `async_prog`

### Testing
`testing`, `testing_python`, `testing_javascript`, `testing_rust`, `testing_go`, `testing_csharp`, `testing_java`
`testing_unit`, `testing_integration`, `testing_e2e`, `testing_load`, `testing_security`, `testing_visual`, `testing_performance`
`mocking`, `test_containers`

### DevOps y Cloud
`devops`, `docker`, `kubernetes`, `ci_cd`, `terraform`, `ansible`, `serverless`
`cloud`, `aws`, `azure`, `gcp`, `aws_deploy`, `vercel`, `netlify`

### Bases de Datos
`databases`, `sql`, `sql_server`, `postgresql`, `mysql`, `mariadb`, `oracle_db`
`mongodb`, `couchdb`, `cassandra`, `elasticsearch`, `influxdb`, `timescaledb`, `cockroachdb`
`redis`, `memcached`

### Redes y Seguridad
`redes`, `seguridad`, `cybersecurity`, `devsecops`, `ssl_tls`, `domain_dns`
`oauth2`, `jwt`, `rate_limiting`

### Servicios y Messaging
`backend`, `frontend`, `api_rest`, `api_graphql`, `api_design`, `graphql`, `grpc`, `websockets`
`message_queue`, `rabbitmq`, `kafka`, `webhooks`, `microservices`

### Monitoreo y Observabilidad
`monitoring`, `observability`, `monitoring_tools`, `prometheus`, `grafana`, `datadog`, `new_relic`, `sentry`, `uptime_kuma`
`log_analysis`, `alerts`, `apm`, `logging`

### Administracion
`admin_sistemas`, `linux_admin`, `windows_server`, `active_directory`, `user_admin`, `user_management`
`rbac`, `group_policy`, `dns_server`, `dhcp`, `sudo_config`, `pam`, `ssh_keys`, `certificates_admin`

### Servidores y Storage
`nginx`, `nginx_deploy`, `file_server`, `samba`, `ldap`, `storage`, `backup_tools`
`file_system`, `ext4`, `ntfs`, `btrfs`, `zfs`, `raid`, `lvm`, `nfs`, `smb_cifs`
`proxmox`, `esxi`, `hyper_v`

### Concurrencia
`concurrency`, `parallelism`, `goroutines`, `asyncio`, `threading`, `multiprocessing`
`locks`, `semaphores`, `channels`, `event_loop`

### Organizacion y Deploy
`folder_organization`, `project_structure`, `monorepo_setup`, `polyrepo`
`deployment`, `docker_deploy`, `k8s_deploy`, `fallback_deploy`, `rollback`
`deploy_blue_green`, `deploy_canary`, `feature_flags`, `dark_launch`

### Automatizacion
`n8n`, `n8n_workflows`, `make`, `zapier`, `power_automate`
`cron_jobs`, `cron_tasks`, `pm2`, `systemd`, `env_config`

### Gestion de Proyectos
`project_management`, `trello`, `jira`, `notion`, `linear`, `asana`, `todoist`, `obsidian`

### Leyendas de Programacion
`legend_friday`, `legend_99bugs`, `legend_it_works`, `legend_coment`
`legend_stackoverflow`, `legend_10x`, `legend_premature_opt`, `legend_no_docs`, `legend_resume_driven`

### IA y Data
`ai`, `llms`, `ai_agents`, `prompt_engineering`, `machine_learning`
`data_engineering`, `big_data`, `blockchain`, `iot`

### Documentacion
`documentation`, `api_docs`, `readme`, `swagger`, `technical_writing`

### Carrera Tech
`conferences`, `podcasts_tech`, `roadmap_dev`, `salary_tech`, `interview_prep`, `cv_tech`, `freelance`, `remote_work`

### Otros
`hardware`, `gadgets`, `virtualizacion`, `open_source`, `sdd`, `soft_skills`, `game_dev`, `unity`, `scraping`, `diseno_web`, `terminal`, `bash`, `bash_scripting`, `python_auto`

## Setup completo

### 1. Crear bot de Telegram

1. Abre Telegram -> [@BotFather](https://t.me/BotFather)
2. `/newbot` -> nombre + username
3. Copia el **TOKEN**

### 2. Obtener Chat ID

1. Envia un mensaje a tu bot
2. Abre: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Busca `"chat":{"id": NUMERO}`

### 3. Crear API key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API key**
3. Copia la key

### 4. Configurar Secrets en GitHub

En tu repo -> Settings -> Secrets and variables -> Actions:

| Secret | Descripcion |
|--------|-------------|
| `TIPS_BOT_TOKEN` | Token del bot de Telegram |
| `TIPS_CHAT_ID` | ID del chat/grupo/canal |
| `GEMINI_API_KEY` | API key de Google Gemini |

### 5. Activar el workflow

1. Ve a **Actions** en tu repo
2. Busca **"Tips de IT (cada 6h)"**
3. Click **Enable workflow**

## Uso local

```bash
# Vista previa (no envia nada)
python scripts/tips_generator.py --dry-run

# Enviar a Telegram
TIPS_BOT_TOKEN=xxx TIPS_CHAT_ID=xxx GEMINI_API_KEY=xxx python scripts/tips_generator.py

# Ver categorias
python scripts/tips_generator.py --list-categories

# Estadisticas
python scripts/tips_generator.py --stats
```

## Estructura

```
scripts/
├── tips_generator.py              # script principal (Gemini + DB)
├── tools/
│   └── migrate_concepts_es.py     # traduce y mejora la DB de conceptos con Gemini
└── utils/
    ├── tips_database.json         # 708 tips estaticos (fallback)
    └── concepts_database.json     # 283 conceptos estaticos (fallback)
files/
├── noticias_historico.json        # noticias scraping (inspiracion)
└── herramientas.json              # GitHub trending (inspiracion)
tips_history.json                  # historial PERMANENTE (auto)
.github/workflows/
└── daily_tips.yml                 # workflow cada 6h
```

## Nunca se repiten

El sistema garantiza cero repeticiones:

1. **Historial permanente**: `tips_history.json` guarda el titulo de CADA tip enviado
2. **Gemini recibe el historial**: El prompt incluye los ultimos 200 titulos enviados
3. **Noticias cambian**: Cada batch usa noticias diferentes del dia
4. **Tools trending cambian**: Cada batch usa tools diferentes de GitHub
5. **DB se agota**: Cuando se usan los tips y conceptos de la DB, solo Gemini genera (con fuente infinita)

## Troubleshooting

| Problema | Solucion |
|----------|----------|
| No llegan mensajes | Verifica secrets: TIPS_BOT_TOKEN y TIPS_CHAT_ID |
| Gemini no responde | Verifica GEMINI_API_KEY en GitHub secrets |
| Tips repetidos | Revisa tips_history.json, borra si es necesario |
| Error 403 Forbidden | Anade el bot como administrador del grupo |
| Error de Gemini | El script cae back a DB estatica automaticamente |

## Anadir tips a la DB

Edita `scripts/utils/tips_database.json`:

```json
{
  "id": 151,
  "cat": "python",
  "title": "Tu tip nuevo",
  "body": "Explicacion concisa del tip.",
  "difficulty": 1
}
```

Niveles: `1` = Basico, `2` = Intermedio, `3` = Avanzado
