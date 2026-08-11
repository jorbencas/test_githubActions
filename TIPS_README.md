# 💡 Tips de IT — Gemini + DB Local

Bot de Telegram que envía **10 tips cada 6 horas**. Gemini genera tips dinámicos usando noticias y herramientas trending como fuente. DB estática como fallback. **Nunca repite tips.**

## Cómo funciona

```
Cada 6 horas (00:00, 06:00, 12:00, 18:00 UTC)
    │
    ├─→ Selecciona 5-6 categorías al azar (de 35+)
    │
    ├─→ Gemini genera 5 tips nuevos
    │      - Usa noticias de tech como inspiración
    │      - Usa herramientas trending de GitHub
    │      - Respeta historial para NUNCA repetir
    │
    ├─→ DB estática: 5 tips no enviados
    │      - Si DB agotada → solo Gemini (10 tips)
    │
    ├─→ Mezcla = 10 tips únicos
    │
    ├─→ Enviar a Telegram
    │
    └─→ Guarda títulos en historial (PERMANENTE)
```

## Fuentes de datos

| Fuente | Archivo | Qué usa |
|--------|---------|---------|
| Noticias scraping | `files/noticias_historico.json` | 10-15 noticias recientes como inspiración |
| GitHub trending | `files/herramientas.json` | 5-10 tools trending como inspiración |
| DB estática | `scripts/utils/tips_database.json` | 150 tips como fallback |
| Historial | `tips_history.json` | Todos los títulos enviados (nunca repetir) |

## Categorías (35+)

| Emoji | ID | Nombre |
|-------|-----|--------|
| 🐧 | `linux` | Linux |
| 🪟 | `windows` | Windows |
| 🟠 | `ubuntu` | Ubuntu |
| 🍎 | `macos` | macOS |
| 📱 | `android` | Android |
| 🤖 | `android_studio` | Android Studio |
| 🍎 | `ios` | iOS/Swift |
| 🌐 | `redes` | Redes |
| 🔒 | `seguridad` | Seguridad |
| ⚙️ | `devops` | DevOps |
| 🔀 | `git` | Git |
| 🐳 | `docker` | Docker |
| ☸️ | `kubernetes` | Kubernetes |
| 🗄️ | `databases` | Bases de datos |
| 🤖 | `ai` | Inteligencia Artificial |
| 🧠 | `llms` | LLMs/Modelos |
| 🦾 | `ai_agents` | AI Agents/Skills |
| 💬 | `prompt_engineering` | Prompt Engineering |
| 📊 | `machine_learning` | Machine Learning |
| 💻 | `programming` | Programación |
| 🐍 | `python` | Python |
| 📜 | `javascript` | JavaScript |
| 🟦 | `typescript` | TypeScript |
| 🦀 | `rust` | Rust |
| 🐹 | `go` | Go |
| ☕ | `java` | Java |
| 🟣 | `kotlin` | Kotlin |
| ⚡ | `cpp` | C/C++ |
| 🔧 | `c` | C |
| 🎮 | `csharp` | C# |
| 🦅 | `swift` | Swift |
| 🐘 | `php` | PHP |
| 💎 | `ruby` | Ruby |
| 🔍 | `sql` | SQL |
| 🎨 | `html_css` | HTML/CSS |
| ⚛️ | `react` | React |
| 💚 | `vue` | Vue.js |
| 🔴 | `angular` | Angular |
| 🟠 | `svelte` | Svelte |
| 🚀 | `astro` | Astro |
| ▲ | `nextjs` | Next.js |
| 💚 | `nuxt` | Nuxt.js |
| 🟢 | `nodejs` | Node.js |
| ⚡ | `fastapi` | FastAPI |
| 🎸 | `django` | Django |
| 🧪 | `flask` | Flask |
| 🚂 | `express` | Express.js |
| 🌱 | `spring` | Spring Boot |
| 🟣 | `dotnet` | .NET/C# |
| 🏗️ | `oop` | OOP/POO |
| 🧩 | `design_patterns` | Patrones de diseño |
| 🦀 | `rust_patterns` | Patrones en Rust |
| 🎮 | `csharp_patterns` | Patrones en C# |
| 🐹 | `go_patterns` | Patrones en Go |
| 🐍 | `python_patterns` | Patrones en Python |
| 📜 | `javascript_patterns` | Patrones en JavaScript |
| 🟦 | `typescript_patterns` | Patrones en TypeScript |
| ⬡ | `arch_hexagonal` | Arquitectura Hexagonal |
| ✨ | `arch_clean` | Clean Architecture |
| 📐 | `arch_mvc` | MVC/MVVM |
| 📋 | `arch_cqrs` | CQRS |
| 📡 | `arch_event_sourcing` | Event Sourcing |
| 💪 | `solid` | Principios SOLID |
| λ | `func_prog` | Programación Funcional |
| 🔄 | `reactive_prog` | Programación Reactiva |
| ⚡ | `concurrent_prog` | Concurrency |
| ⏳ | `async_prog` | Programación Asíncrona |
| ✨ | `clean_code` | Clean Code |
| 🧪 | `testing` | Testing/TDD |
| 🐍 | `testing_python` | Testing en Python |
| 📜 | `testing_javascript` | Testing en JavaScript |
| 🦀 | `testing_rust` | Testing en Rust |
| 🐹 | `testing_go` | Testing en Go |
| 🎮 | `testing_csharp` | Testing en C# |
| ☕ | `testing_java` | Testing en Java |
| 🔌 | `api_design` | Diseño de APIs |
| 🔗 | `microservices` | Microservicios |
| 📡 | `graphql` | GraphQL |
| ⌨️ | `bash` | Bash/Shell |
| 📜 | `bash_scripting` | Bash Scripting |
| 🐍 | `python_auto` | Python Automation |
| ☁️ | `cloud` | Cloud |
| ☁️ | `aws` | AWS |
| ☁️ | `azure` | Azure |
| ☁️ | `gcp` | Google Cloud |
| ⚡ | `serverless` | Serverless |
| 🏗️ | `terraform` | Terraform |
| 🔧 | `ansible` | Ansible |
| 🔄 | `ci_cd` | CI/CD |
| 🛡️ | `cybersecurity` | Ciberseguridad |
| 🔒 | `devsecops` | DevSecOps |
| 🔧 | `hardware` | Hardware |
| 📲 | `gadgets` | Gadgets/Tech |
| 📦 | `virtualizacion` | Virtualización |
| 💖 | `open_source` | Open Source |
| 📦 | `sdd` | Desarrollo/CI/CD |
| 🗣️ | `soft_skills` | Soft Skills |
| 🐦 | `flutter` | Flutter/Dart |
| 📱 | `react_native` | React Native |
| 🕷️ | `scraping` | Scraping/Web Scraping |
| 🎨 | `diseno_web` | Diseño Web |
| 💻 | `terminal` | Terminal/CLI |
| 📝 | `vim` | Vim/Neovim |
| 💙 | `vscode` | VS Code |
| 🖥️ | `admin_sistemas` | Administración de Sistemas |
| 🐧 | `linux_admin` | Linux Admin |
| 🌐 | `nginx` | Nginx |
| 👁️ | `observability` | Observabilidad |
| 📊 | `monitoring` | Monitoreo |
| 📡 | `iot` | IoT |
| 🎮 | `game_dev` | Game Development |
| 🎯 | `unity` | Unity |
| 📈 | `data_engineering` | Data Engineering |
| 🗃️ | `big_data` | Big Data |
| ⛓️ | `blockchain` | Blockchain |
| 📖 | `documentation` | Documentación |
| 📘 | `api_docs` | Documentación de APIs |
| 📄 | `readme` | README/Guias |
| 📋 | `swagger` | Swagger/OpenAPI |
| ✍️ | `technical_writing` | Escritura Técnica |
| 🚀 | `deployment` | Despliegue/Deploy |
| 🐳 | `docker_deploy` | Deploy con Docker |
| ☸️ | `k8s_deploy` | Deploy con Kubernetes |
| ▲ | `vercel` | Vercel |
| 🟢 | `netlify` | Netlify |
| ☁️ | `aws_deploy` | Deploy en AWS |
| 🌐 | `nginx_deploy` | Deploy con Nginx |
| 🔒 | `ssl_tls` | SSL/TLS/Certificados |
| 🌍 | `domain_dns` | Dominios/DNS |
| 🏠 | `hosting` | Hosting |
| 🌐 | `cdn` | CDN |
| 📝 | `logging` | Logging |
| 💾 | `backup` | Backup/Respaldos |
| 📈 | `scaling` | Escalabilidad |
| ⚖️ | `load_balancing` | Load Balancing |
| 🔄 | `reverse_proxy` | Reverse Proxy |
| 🟢 | `pm2` | PM2 |
| ⚙️ | `systemd` | Systemd |
| ⏰ | `cron_jobs` | Cron Jobs |
| 🔐 | `env_config` | Variables de Entorno |
| 📊 | `monitoring_tools` | Herramientas Monitoreo |
| 🔥 | `prometheus` | Prometheus |
| 📊 | `grafana` | Grafana |
| 🐕 | `datadog` | Datadog |
| 🟢 | `new_relic` | New Relic |
| 🔴 | `sentry` | Sentry |
| 📡 | `uptime_kuma` | Uptime Kuma |
| 📝 | `log_analysis` | Análisis de Logs |
| 🔔 | `alerts` | Alertas |
| 📈 | `apm` | APM |
| ⚙️ | `backend` | Backend |
| 🎨 | `frontend` | Frontend |
| 🔌 | `api_rest` | API REST |
| 📡 | `api_graphql` | API GraphQL |
| ⚡ | `grpc` | gRPC |
| 🔗 | `websockets` | WebSockets |
| 📮 | `message_queue` | Colas de Mensajes |
| 🐰 | `rabbitmq` | RabbitMQ |
| 📨 | `kafka` | Kafka |
| 🔴 | `redis` | Redis |
| ⚡ | `memcached` | Memcached |
| ⏰ | `cron_tasks` | Tareas Programadas |
| 🪝 | `webhooks` | Webhooks |
| 🔐 | `oauth2` | OAuth2 |
| 🎫 | `jwt` | JWT |
| 🚦 | `rate_limiting` | Rate Limiting |
| ⚡ | `concurrency` | Concurrencia |
| 🔀 | `parallelism` | Paralelismo |
| 🐹 | `goroutines` | Goroutines |
| ⏳ | `asyncio` | Asyncio |
| 🧵 | `threading` | Threading |
| 💻 | `multiprocessing` | Multiprocessing |
| 🔒 | `locks` | Locks/Mutex |
| 🚦 | `semaphores` | Semáforos |
| 📡 | `channels` | Channels |
| 🔄 | `event_loop` | Event Loop |
| 📋 | `project_management` | Gestión de Proyectos |
| 📋 | `trello` | Trello |
| 📋 | `jira` | Jira |
| 📝 | `notion` | Notion |
| 📐 | `linear` | Linear |
| ✅ | `asana` | Asana |
| ☑️ | `todoist` | Todoist |
| 💎 | `obsidian` | Obsidian |
| ⚡ | `n8n` | n8n |
| 🔄 | `n8n_workflows` | Workflows n8n |
| 🔧 | `make` | Make/Integromat |
| ⚡ | `zapier` | Zapier |
| ⚙️ | `power_automate` | Power Automate |
| 🪟 | `windows_server` | Windows Server |
| 🏢 | `active_directory` | Active Directory |
| 👤 | `user_admin` | Administración Usuarios |
| 🔐 | `rbac` | RBAC/Permisos |
| 📜 | `group_policy` | Group Policy |
| 🌐 | `dns_server` | DNS Server |
| 📡 | `dhcp` | DHCP |
| 📁 | `file_server` | Servidor de Archivos |
| 🐾 | `samba` | Samba |
| 🏢 | `ldap` | LDAP |
| 🗄️ | `sql_server` | SQL Server |
| 🐘 | `postgresql` | PostgreSQL |
| 🐬 | `mysql` | MySQL |
| 🐬 | `mariadb` | MariaDB |
| 🔴 | `oracle_db` | Oracle DB |
| 🍃 | `mongodb` | MongoDB |
| 🛋️ | `couchdb` | CouchDB |
| 👁️ | `cassandra` | Cassandra |
| 🔍 | `elasticsearch` | Elasticsearch |
| 📈 | `influxdb` | InfluxDB |
| ⏰ | `timescaledb` | TimescaleDB |
| 🪳 | `cockroachdb` | CockroachDB |
| 📁 | `file_system` | Sistemas de Archivos |
| 🐧 | `ext4` | EXT4 |
| 🪟 | `ntfs` | NTFS |
| 🌳 | `btrfs` | BTRFS |
| 🐟 | `zfs` | ZFS |
| 💾 | `raid` | RAID |
| 📦 | `lvm` | LVM |
| 🌐 | `nfs` | NFS |
| 🔗 | `smb_cifs` | SMB/CIFS |
| 💾 | `storage` | Almacenamiento |
| 💾 | `backup_tools` | Herramientas Backup |
| 📦 | `proxmox` | Proxmox |
| ☁️ | `esxi` | ESXi |
| 🪟 | `hyper_v` | Hyper-V |
| 👥 | `user_management` | Gestión de Usuarios |
| 🔑 | `sudo_config` | Configuración Sudo |
| 🔐 | `pam` | PAM/Auth |
| 🔑 | `ssh_keys` | SSH Keys |
| 📜 | `certificates_admin` | Certificados |
| 📁 | `folder_organization` | Organización Carpetas |
| 🏗️ | `project_structure` | Estructura de Proyectos |
| 📦 | `monorepo_setup` | Monorepo |
| 📦 | `polyrepo` | Polyrepo |
| 🧪 | `testing_unit` | Testing Unitario |
| 🔗 | `testing_integration` | Testing Integración |
| 🌐 | `testing_e2e` | Testing E2E |
| 📊 | `testing_load` | Testing Carga |
| 🔒 | `testing_security` | Testing Seguridad |
| 👁️ | `testing_visual` | Testing Visual |
| ⚡ | `testing_performance` | Testing Rendimiento |
| 🎭 | `mocking` | Mocking/Stubbing |
| 🐳 | `test_containers` | TestContainers |
| 🔄 | `fallback_deploy` | Fallback Deploy |
| ⏪ | `rollback` | Rollback |
| 🔵🟢 | `deploy_blue_green` | Deploy Blue-Green |
| 🐦 | `deploy_canary` | Deploy Canary |
| 🚩 | `feature_flags` | Feature Flags |
| 🌑 | `dark_launch` | Dark Launch |
| 😱 | `legend_friday` | Leyenda: Viernes no Deploy |
| 🐛 | `legend_99bugs` | Leyenda: 99 bugs |
| 🤷 | `legend_it_works` | Leyenda: Funciona no toques |
| 💬 | `legend_coment` | Leyenda: El comentario |
| 📋 | `legend_stackoverflow` | Leyenda: Copiar de StackOverflow |
| ⚡ | `legend_10x` | Leyenda: Programador 10x |
| 🐌 | `legend_premature_opt` | Leyenda: Optimización prematura |
| 📝 | `legend_no_docs` | Leyenda: No documentar |
| 📄 | `legend_resume_driven` | Leyenda: Resume-driven dev |
| 🎤 | `conferences` | Conferencias Tech |
| 🎧 | `podcasts_tech` | Podcasts Tech |
| 🗺️ | `roadmap_dev` | Roadmaps de Dev |
| 💰 | `salary_tech` | Salarios Tech |
| 🎯 | `interview_prep` | Preparación Entrevistas |
| 📄 | `cv_tech` | CV/Currículum Tech |
| 💼 | `freelance` | Freelance |
| 🏠 | `remote_work` | Trabajo Remoto |

## Setup completo

### 1. Crear bot de Telegram

1. Abre Telegram → [@BotFather](https://t.me/BotFather)
2. `/newbot` → nombre + username
3. Copia el **TOKEN**

### 2. Obtener Chat ID

1. Envía un mensaje a tu bot
2. Abre: `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Busca `"chat":{"id": NUMERO}`

### 3. Crear API key de Gemini

1. Ve a [Google AI Studio](https://aistudio.google.com/apikey)
2. Click **Create API key**
3. Copia la key

### 4. Configurar Secrets en GitHub

En tu repo → Settings → Secrets and variables → Actions:

| Secret | Descripción |
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
# Vista previa (no envía nada)
python scripts/tips_generator.py --dry-run

# Enviar a Telegram
TIPS_BOT_TOKEN=xxx TIPS_CHAT_ID=xxx GEMINI_API_KEY=xxx python scripts/tips_generator.py

# Ver categorías
python scripts/tips_generator.py --list-categories

# Estadísticas
python scripts/tips_generator.py --stats
```

## Estructura

```
scripts/
├── tips_generator.py              # script principal (Gemini + DB)
└── utils/
    └── tips_database.json         # 150 tips estáticos (fallback)
files/
├── noticias_historico.json        # noticias scraping (inspiración)
└── herramientas.json              # GitHub trending (inspiración)
tips_history.json                  # historial PERMANENTE (auto)
.github/workflows/
└── daily_tips.yml                 # workflow cada 6h
```

## Nunca se repiten

El sistema garantiza cero repeticiones:

1. **Historial permanente**: `tips_history.json` guarda el título de CADA tip enviado
2. **Gemini recibe el historial**: El prompt incluye los últimos 200 títulos enviados
3. **Noticias cambian**: Cada batch usa noticias diferentes del día
4. **Tools trending cambian**: Cada batch usa tools diferentes de GitHub
5. **DB se agota**: Cuando se usan los 150 tips, solo Gemini genera (con fuente infinita)

## Troubleshooting

| Problema | Solución |
|----------|----------|
| No llegan mensajes | Verifica secrets: TIPS_BOT_TOKEN y TIPS_CHAT_ID |
| Gemini no responde | Verifica GEMINI_API_KEY en GitHub secrets |
| Tips repetidos | Revisa tips_history.json, borra si es necesario |
| Error 403 Forbidden | Añade el bot como administrador del grupo |
| Error de Gemini | El script cae back a DB estática automáticamente |

## Añadir tips a la DB

Edita `scripts/utils/tips_database.json`:

```json
{
  "id": 151,
  "cat": "python",
  "title": "Tu tip nuevo",
  "body": "Explicación concisa del tip.",
  "difficulty": 1
}
```

Categorías: `linux`, `windows`, `ubuntu`, `macos`, `android`, `android_studio`, `ios`, `redes`, `seguridad`, `devops`, `git`, `docker`, `kubernetes`, `databases`, `ai`, `llms`, `ai_agents`, `prompt_engineering`, `machine_learning`, `programming`, `python`, `javascript`, `typescript`, `rust`, `go`, `java`, `kotlin`, `cpp`, `c`, `csharp`, `swift`, `php`, `ruby`, `sql`, `html_css`, `react`, `vue`, `angular`, `svelte`, `astro`, `nextjs`, `nuxt`, `nodejs`, `fastapi`, `django`, `flask`, `express`, `spring`, `dotnet`, `oop`, `design_patterns`, `rust_patterns`, `csharp_patterns`, `go_patterns`, `python_patterns`, `javascript_patterns`, `typescript_patterns`, `arch_hexagonal`, `arch_clean`, `arch_mvc`, `arch_cqrs`, `arch_event_sourcing`, `solid`, `func_prog`, `reactive_prog`, `concurrent_prog`, `async_prog`, `clean_code`, `testing`, `testing_python`, `testing_javascript`, `testing_rust`, `testing_go`, `testing_csharp`, `testing_java`, `api_design`, `microservices`, `graphql`, `bash`, `bash_scripting`, `python_auto`, `cloud`, `aws`, `azure`, `gcp`, `serverless`, `terraform`, `ansible`, `ci_cd`, `cybersecurity`, `devsecops`, `hardware`, `gadgets`, `virtualizacion`, `open_source`, `sdd`, `soft_skills`, `flutter`, `react_native`, `scraping`, `diseno_web`, `terminal`, `vim`, `vscode`, `admin_sistemas`, `linux_admin`, `nginx`, `observability`, `monitoring`, `iot`, `game_dev`, `unity`, `data_engineering`, `big_data`, `blockchain`, `documentation`, `api_docs`, `readme`, `swagger`, `technical_writing`, `deployment`, `docker_deploy`, `k8s_deploy`, `vercel`, `netlify`, `aws_deploy`, `nginx_deploy`, `ssl_tls`, `domain_dns`, `hosting`, `cdn`, `logging`, `backup`, `scaling`, `load_balancing`, `reverse_proxy`, `pm2`, `systemd`, `cron_jobs`, `env_config`, `monitoring_tools`, `prometheus`, `grafana`, `datadog`, `new_relic`, `sentry`, `uptime_kuma`, `log_analysis`, `alerts`, `apm`, `backend`, `frontend`, `api_rest`, `api_graphql`, `grpc`, `websockets`, `message_queue`, `rabbitmq`, `kafka`, `redis`, `memcached`, `cron_tasks`, `webhooks`, `oauth2`, `jwt`, `rate_limiting`, `concurrency`, `parallelism`, `goroutines`, `asyncio`, `threading`, `multiprocessing`, `locks`, `semaphores`, `channels`, `event_loop`, `project_management`, `trello`, `jira`, `notion`, `linear`, `asana`, `todoist`, `obsidian`, `n8n`, `n8n_workflows`, `make`, `zapier`, `power_automate`, `windows_server`, `active_directory`, `user_admin`, `rbac`, `group_policy`, `dns_server`, `dhcp`, `file_server`, `samba`, `ldap`, `sql_server`, `postgresql`, `mysql`, `mariadb`, `oracle_db`, `mongodb`, `couchdb`, `cassandra`, `elasticsearch`, `influxdb`, `timescaledb`, `cockroachdb`, `file_system`, `ext4`, `ntfs`, `btrfs`, `zfs`, `raid`, `lvm`, `nfs`, `smb_cifs`, `storage`, `backup_tools`, `proxmox`, `esxi`, `hyper_v`, `user_management`, `sudo_config`, `pam`, `ssh_keys`, `certificates_admin`, `folder_organization`, `project_structure`, `monorepo_setup`, `polyrepo`, `testing_unit`, `testing_integration`, `testing_e2e`, `testing_load`, `testing_security`, `testing_visual`, `testing_performance`, `mocking`, `test_containers`, `fallback_deploy`, `rollback`, `deploy_blue_green`, `deploy_canary`, `feature_flags`, `dark_launch`, `legend_friday`, `legend_99bugs`, `legend_it_works`, `legend_coment`, `legend_stackoverflow`, `legend_10x`, `legend_premature_opt`, `legend_no_docs`, `legend_resume_driven`, `conferences`, `podcasts_tech`, `roadmap_dev`, `salary_tech`, `interview_prep`, `cv_tech`, `freelance`, `remote_work`

Niveles: `1` = Básico, `2` = Intermedio, `3` = Avanzado
