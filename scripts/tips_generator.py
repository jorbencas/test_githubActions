"""
Tip Diario de IT — Envía 10 tips cada 6 horas por Telegram.
Gemini genera tips dinámicos usando noticias y tools como fuente.
DB estática como fallback. Nunca repite tips.

Uso:
    python scripts/tips_generator.py                    # envía 10 tips
    python scripts/tips_generator.py --dry-run          # solo muestra, no envía
    python scripts/tips_generator.py --list-categories  # lista categorías
    python scripts/tips_generator.py --stats            # estadísticas
"""

import json
import os
import random
import sys
from datetime import datetime
from pathlib import Path

import requests

# ── Paths ──
SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "utils" / "tips_database.json"
HISTORY_PATH = SCRIPT_DIR.parent / "tips_history.json"
NEWS_PATH = SCRIPT_DIR.parent / "files" / "noticias_historico.json"
TOOLS_PATH = SCRIPT_DIR.parent / "files" / "herramientas.json"

# ── Telegram config ──
BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TIPS_CHAT_ID", "")
API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ── Gemini config ──
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

# ── Todas las categorías (130+) ──
CAT_EMOJI = {
    "linux": "🐧",
    "windows": "🪟",
    "ubuntu": "🟠",
    "macos": "🍎",
    "android": "📱",
    "android_studio": "🤖",
    "ios": "🍎",
    "redes": "🌐",
    "seguridad": "🔒",
    "devops": "⚙️",
    "git": "🔀",
    "docker": "🐳",
    "kubernetes": "☸️",
    "databases": "🗄️",
    "ai": "🤖",
    "llms": "🧠",
    "ai_agents": "🦾",
    "prompt_engineering": "💬",
    "machine_learning": "📊",
    "programming": "💻",
    "python": "🐍",
    "javascript": "📜",
    "typescript": "🟦",
    "rust": "🦀",
    "go": "🐹",
    "java": "☕",
    "kotlin": "🟣",
    "cpp": "⚡",
    "c": "🔧",
    "csharp": "🎮",
    "swift": "🦅",
    "php": "🐘",
    "ruby": "💎",
    "sql": "🔍",
    "html_css": "🎨",
    "react": "⚛️",
    "vue": "💚",
    "angular": "🔴",
    "svelte": "🟠",
    "astro": "🚀",
    "nextjs": "▲",
    "nuxt": "💚",
    "nodejs": "🟢",
    "fastapi": "⚡",
    "django": "🎸",
    "flask": "🧪",
    "express": "🚂",
    "spring": "🌱",
    "dotnet": "🟣",
    "oop": "🏗️",
    "design_patterns": "🧩",
    "rust_patterns": "🦀",
    "csharp_patterns": "🎮",
    "go_patterns": "🐹",
    "python_patterns": "🐍",
    "javascript_patterns": "📜",
    "typescript_patterns": "🟦",
    "arch_hexagonal": "⬡",
    "arch_clean": "✨",
    "arch_mvc": "📐",
    "arch_cqrs": "📋",
    "arch_event_sourcing": "📡",
    "solid": "💪",
    "func_prog": "λ",
    "reactive_prog": "🔄",
    "concurrent_prog": "⚡",
    "async_prog": "⏳",
    "clean_code": "✨",
    "testing": "🧪",
    "testing_python": "🐍",
    "testing_javascript": "📜",
    "testing_rust": "🦀",
    "testing_go": "🐹",
    "testing_csharp": "🎮",
    "testing_java": "☕",
    "api_design": "🔌",
    "microservices": "🔗",
    "graphql": "📡",
    "bash": "⌨️",
    "bash_scripting": "📜",
    "python_auto": "🐍",
    "cloud": "☁️",
    "aws": "☁️",
    "azure": "☁️",
    "gcp": "☁️",
    "serverless": "⚡",
    "terraform": "🏗️",
    "ansible": "🔧",
    "ci_cd": "🔄",
    "cybersecurity": "🛡️",
    "devsecops": "🔒",
    "hardware": "🔧",
    "gadgets": "📲",
    "virtualizacion": "📦",
    "open_source": "💖",
    "sdd": "📦",
    "soft_skills": "🗣️",
    "flutter": "🐦",
    "react_native": "📱",
    "scraping": "🕷️",
    "diseno_web": "🎨",
    "terminal": "💻",
    "vim": "📝",
    "vscode": "💙",
    "admin_sistemas": "🖥️",
    "linux_admin": "🐧",
    "nginx": "🌐",
    "observability": "👁️",
    "monitoring": "📊",
    "iot": "📡",
    "game_dev": "🎮",
    "unity": "🎯",
    "data_engineering": "📈",
    "big_data": "🗃️",
    "blockchain": "⛓️",
    "documentation": "📖",
    "api_docs": "📘",
    "readme": "📄",
    "swagger": "📋",
    "technical_writing": "✍️",
    "deployment": "🚀",
    "docker_deploy": "🐳",
    "k8s_deploy": "☸️",
    "vercel": "▲",
    "netlify": "🟢",
    "aws_deploy": "☁️",
    "nginx_deploy": "🌐",
    "ssl_tls": "🔒",
    "domain_dns": "🌍",
    "hosting": "🏠",
    "cdn": "🌐",
    "logging": "📝",
    "backup": "💾",
    "scaling": "📈",
    "load_balancing": "⚖️",
    "reverse_proxy": "🔄",
    "pm2": "🟢",
    "systemd": "⚙️",
    "cron_jobs": "⏰",
    "env_config": "🔐",
    "monitoring_tools": "📊",
    "prometheus": "🔥",
    "grafana": "📊",
    "datadog": "🐕",
    "new_relic": "🟢",
    "sentry": "🔴",
    "uptime_kuma": "📡",
    "log_analysis": "📝",
    "alerts": "🔔",
    "apm": "📈",
    "backend": "⚙️",
    "frontend": "🎨",
    "api_rest": "🔌",
    "api_graphql": "📡",
    "grpc": "⚡",
    "websockets": "🔗",
    "message_queue": "📮",
    "rabbitmq": "🐰",
    "kafka": "📨",
    "redis": "🔴",
    "memcached": "⚡",
    "cron_tasks": "⏰",
    "webhooks": "🪝",
    "oauth2": "🔐",
    "jwt": "🎫",
    "rate_limiting": "🚦",
    "concurrency": "⚡",
    "parallelism": "🔀",
    "goroutines": "🐹",
    "asyncio": "⏳",
    "threading": "🧵",
    "multiprocessing": "💻",
    "locks": "🔒",
    "semaphores": "🚦",
    "channels": "📡",
    "event_loop": "🔄",
    "project_management": "📋",
    "trello": "📋",
    "jira": "📋",
    "notion": "📝",
    "linear": "📐",
    "asana": "✅",
    "todoist": "☑️",
    "obsidian": "💎",
    "n8n": "⚡",
    "n8n_workflows": "🔄",
    "make": "🔧",
    "zapier": "⚡",
    "power_automate": "⚙️",
    "windows_server": "🪟",
    "active_directory": "🏢",
    "user_admin": "👤",
    "rbac": "🔐",
    "group_policy": "📜",
    "dns_server": "🌐",
    "dhcp": "📡",
    "file_server": "📁",
    "samba": "🐾",
    "ldap": "🏢",
    "sql_server": "🗄️",
    "postgresql": "🐘",
    "mysql": "🐬",
    "mariadb": "🐬",
    "oracle_db": "🔴",
    "mongodb": "🍃",
    "couchdb": "🛋️",
    "cassandra": "👁️",
    "elasticsearch": "🔍",
    "influxdb": "📈",
    "timescaledb": "⏰",
    "cockroachdb": "🪳",
    "file_system": "📁",
    "ext4": "🐧",
    "ntfs": "🪟",
    "btrfs": "🌳",
    "zfs": "🐟",
    "raid": "💾",
    "lvm": "📦",
    "nfs": "🌐",
    "smb_cifs": "🔗",
    "storage": "💾",
    "backup_tools": "💾",
    "proxmox": "📦",
    "esxi": "☁️",
    "hyper_v": "🪟",
    "user_management": "👥",
    "sudo_config": "🔑",
    "pam": "🔐",
    "ssh_keys": "🔑",
    "certificates_admin": "📜",
    "folder_organization": "📁",
    "project_structure": "🏗️",
    "monorepo_setup": "📦",
    "polyrepo": "📦",
    "testing_unit": "🧪",
    "testing_integration": "🔗",
    "testing_e2e": "🌐",
    "testing_load": "📊",
    "testing_security": "🔒",
    "testing_visual": "👁️",
    "testing_performance": "⚡",
    "mocking": "🎭",
    "test_containers": "🐳",
    "fallback_deploy": "🔄",
    "rollback": "⏪",
    "deploy_blue_green": "🔵🟢",
    "deploy_canary": "🐦",
    "feature_flags": "🚩",
    "dark_launch": "🌑",
    "legend_friday": "😱",
    "legend_99bugs": "🐛",
    "legend_it_works": "🤷",
    "legend_coment": "💬",
    "legend_stackoverflow": "📋",
    "legend_10x": "⚡",
    "legend_premature_opt": "🐌",
    "legend_no_docs": "📝",
    "legend_resume_driven": "📄",
    "conferences": "🎤",
    "podcasts_tech": "🎧",
    "roadmap_dev": "🗺️",
    "salary_tech": "💰",
    "interview_prep": "🎯",
    "cv_tech": "📄",
    "freelance": "💼",
    "remote_work": "🏠",
}

CAT_NAMES = {
    "linux": "Linux",
    "windows": "Windows",
    "ubuntu": "Ubuntu",
    "macos": "macOS",
    "android": "Android",
    "android_studio": "Android Studio",
    "ios": "iOS/Swift",
    "redes": "Redes",
    "seguridad": "Seguridad",
    "devops": "DevOps",
    "git": "Git",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "databases": "Bases de datos",
    "ai": "Inteligencia Artificial",
    "llms": "LLMs/Modelos",
    "ai_agents": "AI Agents/Skills",
    "prompt_engineering": "Prompt Engineering",
    "machine_learning": "Machine Learning",
    "programming": "Programación",
    "python": "Python",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "rust": "Rust",
    "go": "Go",
    "java": "Java",
    "kotlin": "Kotlin",
    "cpp": "C/C++",
    "c": "C",
    "csharp": "C#",
    "swift": "Swift",
    "php": "PHP",
    "ruby": "Ruby",
    "sql": "SQL",
    "html_css": "HTML/CSS",
    "react": "React",
    "vue": "Vue.js",
    "angular": "Angular",
    "svelte": "Svelte",
    "astro": "Astro",
    "nextjs": "Next.js",
    "nuxt": "Nuxt.js",
    "nodejs": "Node.js",
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "express": "Express.js",
    "spring": "Spring Boot",
    "dotnet": ".NET/C#",
    "oop": "OOP/POO",
    "design_patterns": "Patrones de diseño",
    "rust_patterns": "Patrones en Rust",
    "csharp_patterns": "Patrones en C#",
    "go_patterns": "Patrones en Go",
    "python_patterns": "Patrones en Python",
    "javascript_patterns": "Patrones en JavaScript",
    "typescript_patterns": "Patrones en TypeScript",
    "arch_hexagonal": "Arquitectura Hexagonal",
    "arch_clean": "Clean Architecture",
    "arch_mvc": "MVC/MVVM",
    "arch_cqrs": "CQRS/Event Sourcing",
    "arch_event_sourcing": "Event Sourcing",
    "solid": "Principios SOLID",
    "func_prog": "Programación Funcional",
    "reactive_prog": "Programación Reactiva",
    "concurrent_prog": "Programación Concurrency",
    "async_prog": "Programación Asíncrona",
    "clean_code": "Clean Code",
    "testing": "Testing/TDD",
    "testing_python": "Testing en Python",
    "testing_javascript": "Testing en JavaScript",
    "testing_rust": "Testing en Rust",
    "testing_go": "Testing en Go",
    "testing_csharp": "Testing en C#",
    "testing_java": "Testing en Java",
    "api_design": "Diseño de APIs",
    "microservices": "Microservicios",
    "graphql": "GraphQL",
    "bash": "Bash/Shell",
    "bash_scripting": "Bash Scripting",
    "python_auto": "Python Automation",
    "cloud": "Cloud",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "Google Cloud",
    "serverless": "Serverless",
    "terraform": "Terraform",
    "ansible": "Ansible",
    "ci_cd": "CI/CD",
    "cybersecurity": "Ciberseguridad",
    "devsecops": "DevSecOps",
    "hardware": "Hardware",
    "gadgets": "Gadgets/Tech",
    "virtualizacion": "Virtualización",
    "open_source": "Open Source",
    "sdd": "Desarrollo/CI/CD",
    "soft_skills": "Soft Skills",
    "flutter": "Flutter/Dart",
    "react_native": "React Native",
    "scraping": "Scraping/Web Scraping",
    "diseno_web": "Diseño Web",
    "terminal": "Terminal/CLI",
    "vim": "Vim/Neovim",
    "vscode": "VS Code",
    "admin_sistemas": "Administración de Sistemas",
    "linux_admin": "Linux Admin",
    "nginx": "Nginx",
    "observability": "Observabilidad",
    "monitoring": "Monitoreo",
    "iot": "IoT/Internet of Things",
    "game_dev": "Game Development",
    "unity": "Unity",
    "data_engineering": "Data Engineering",
    "big_data": "Big Data",
    "blockchain": "Blockchain",
    "documentation": "Documentación",
    "api_docs": "Documentación de APIs",
    "readme": "README/Guias",
    "swagger": "Swagger/OpenAPI",
    "technical_writing": "Escritura Técnica",
    "deployment": "Despliegue/Deploy",
    "docker_deploy": "Deploy con Docker",
    "k8s_deploy": "Deploy con Kubernetes",
    "vercel": "Vercel",
    "netlify": "Netlify",
    "aws_deploy": "Deploy en AWS",
    "nginx_deploy": "Deploy con Nginx",
    "ssl_tls": "SSL/TLS/Certificados",
    "domain_dns": "Dominios/DNS",
    "hosting": "Hosting",
    "cdn": "CDN",
    "logging": "Logging",
    "backup": "Backup/Respaldos",
    "scaling": "Escalabilidad",
    "load_balancing": "Load Balancing",
    "reverse_proxy": "Reverse Proxy",
    "pm2": "PM2/Node Process Manager",
    "systemd": "Systemd",
    "cron_jobs": "Cron Jobs/Tasks",
    "env_config": "Variables de Entorno",
    "monitoring_tools": "Herramientas Monitoreo",
    "prometheus": "Prometheus",
    "grafana": "Grafana",
    "datadog": "Datadog",
    "new_relic": "New Relic",
    "sentry": "Sentry",
    "uptime_kuma": "Uptime Kuma",
    "log_analysis": "Análisis de Logs",
    "alerts": "Alertas",
    "apm": "APM",
    "backend": "Backend",
    "frontend": "Frontend",
    "api_rest": "API REST",
    "api_graphql": "API GraphQL",
    "grpc": "gRPC",
    "websockets": "WebSockets",
    "message_queue": "Colas de Mensajes",
    "rabbitmq": "RabbitMQ",
    "kafka": "Kafka",
    "redis": "Redis",
    "memcached": "Memcached",
    "cron_tasks": "Tareas Programadas",
    "webhooks": "Webhooks",
    "oauth2": "OAuth2",
    "jwt": "JWT",
    "rate_limiting": "Rate Limiting",
    "concurrency": "Concurrencia",
    "parallelism": "Paralelismo",
    "goroutines": "Goroutines",
    "asyncio": "Asyncio",
    "threading": "Threading",
    "multiprocessing": "Multiprocessing",
    "locks": "Locks/Mutex",
    "semaphores": "Semáforos",
    "channels": "Channels",
    "event_loop": "Event Loop",
    "project_management": "Gestión de Proyectos",
    "trello": "Trello",
    "jira": "Jira",
    "notion": "Notion",
    "linear": "Linear",
    "asana": "Asana",
    "todoist": "Todoist",
    "obsidian": "Obsidian",
    "n8n": "n8n",
    "n8n_workflows": "Workflows n8n",
    "make": "Make/Integromat",
    "zapier": "Zapier",
    "power_automate": "Power Automate",
    "windows_server": "Windows Server",
    "active_directory": "Active Directory",
    "user_admin": "Administración Usuarios",
    "rbac": "RBAC/Permisos",
    "group_policy": "Group Policy",
    "dns_server": "DNS Server",
    "dhcp": "DHCP",
    "file_server": "Servidor de Archivos",
    "samba": "Samba",
    "ldap": "LDAP",
    "sql_server": "SQL Server",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mariadb": "MariaDB",
    "oracle_db": "Oracle DB",
    "mongodb": "MongoDB",
    "couchdb": "CouchDB",
    "cassandra": "Cassandra",
    "elasticsearch": "Elasticsearch",
    "influxdb": "InfluxDB",
    "timescaledb": "TimescaleDB",
    "cockroachdb": "CockroachDB",
    "file_system": "Sistemas de Archivos",
    "ext4": "EXT4",
    "ntfs": "NTFS",
    "btrfs": "BTRFS",
    "zfs": "ZFS",
    "raid": "RAID",
    "lvm": "LVM",
    "nfs": "NFS",
    "smb_cifs": "SMB/CIFS",
    "storage": "Almacenamiento",
    "backup_tools": "Herramientas Backup",
    "proxmox": "Proxmox",
    "esxi": "ESXi",
    "hyper_v": "Hyper-V",
    "user_management": "Gestión de Usuarios",
    "sudo_config": "Configuración Sudo",
    "pam": "PAM/Auth",
    "ssh_keys": "SSH Keys",
    "certificates_admin": "Certificados",
    "folder_organization": "Organización Carpetas",
    "project_structure": "Estructura de Proyectos",
    "monorepo_setup": "Monorepo",
    "polyrepo": "Polyrepo",
    "testing_unit": "Testing Unitario",
    "testing_integration": "Testing Integración",
    "testing_e2e": "Testing E2E",
    "testing_load": "Testing Carga",
    "testing_security": "Testing Seguridad",
    "testing_visual": "Testing Visual",
    "testing_performance": "Testing Rendimiento",
    "mocking": "Mocking/Stubbing",
    "test_containers": "TestContainers",
    "fallback_deploy": "Fallback Deploy",
    "rollback": "Rollback",
    "deploy_blue_green": "Deploy Blue-Green",
    "deploy_canary": "Deploy Canary",
    "feature_flags": "Feature Flags",
    "dark_launch": "Dark Launch",
    "legend_friday": "Leyenda: Viernes no Deploy",
    "legend_99bugs": "Leyenda: 99 bugs",
    "legend_it_works": "Leyenda: Funciona no toques",
    "legend_coment": "Leyenda: El comentario",
    "legend_stackoverflow": "Leyenda: Copiar de StackOverflow",
    "legend_10x": "Leyenda: Programador 10x",
    "legend_premature_opt": "Leyenda: Optimización prematura",
    "legend_no_docs": "Leyenda: No documentar",
    "legend_resume_driven": "Leyenda: Resume-driven dev",
    "conferences": "Conferencias Tech",
    "podcasts_tech": "Podcasts Tech",
    "roadmap_dev": "Roadmaps de Dev",
    "salary_tech": "Salarios Tech",
    "interview_prep": "Preparación Entrevistas",
    "cv_tech": "CV/Currículum Tech",
    "freelance": "Freelance",
    "remote_work": "Trabajo Remoto",
}

ALL_CATEGORIES = list(CAT_EMOJI.keys())

DIFF_NAMES = {1: "Básico", 2: "Intermedio", 3: "Avanzado"}


def load_database():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"sent_titles": [], "last_run": None, "total_runs": 0, "db_exhausted": False}


def save_history(history):
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def load_recent_news(count=15):
    if not NEWS_PATH.exists():
        return []
    try:
        with open(NEWS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        recent = sorted(data, key=lambda x: x.get("ts", ""), reverse=True)[:count]
        result = []
        for item in recent:
            titulo = item.get("titulo", "")
            cat = item.get("categoria", "")
            fuente = item.get("fuente", "")
            if titulo:
                result.append(f"- {titulo} [{cat}] ({fuente})")
        return result
    except Exception:
        return []


def load_recent_tools(count=10):
    if not TOOLS_PATH.exists():
        return []
    try:
        with open(TOOLS_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            return []
        recent = sorted(data, key=lambda x: x.get("ts", ""), reverse=True)[:count]
        result = []
        for item in recent:
            titulo = item.get("titulo", "")
            desc = item.get("descripcion", "")
            lang = item.get("lenguaje", "")
            stars = item.get("estrellas", "")
            if titulo:
                result.append(f"- {titulo} ({lang}, ⭐{stars}): {desc}")
        return result
    except Exception:
        return []


def select_random_categories(count=6):
    return random.sample(ALL_CATEGORIES, min(count, len(ALL_CATEGORIES)))


def select_tips_from_db(database, history, count=5):
    all_tips = database["tips"]
    sent_titles = set(history.get("sent_titles", []))
    available = [t for t in all_tips if t["title"] not in sent_titles]
    if len(available) < count:
        available = all_tips
    random.shuffle(available)
    selected = []
    used_cats = set()
    for tip in available:
        if len(selected) >= count:
            break
        if tip["cat"] not in used_cats:
            selected.append(tip)
            used_cats.add(tip["cat"])
    if len(selected) < count:
        for tip in available:
            if len(selected) >= count:
                break
            if tip not in selected:
                selected.append(tip)
    return selected[:count]


def build_gemini_prompt(categories, sent_titles, news, tools):
    cats_str = ", ".join(categories)
    titles_str = "\n".join(sent_titles[:200]) if sent_titles else "(nunca se han enviado tips antes)"
    news_str = "\n".join(news[:15]) if news else "(no hay noticias recientes disponibles)"
    tools_str = "\n".join(tools[:10]) if tools else "(no hay herramientas trending disponibles)"

    return f"""Eres un profesor experto en tecnologías de la información. Generas tips técnicos EN ESPAÑOL para profesionales de IT.

=== CATEGORÍAS DE ESTE BATCH ===
{cats_str}

=== CONCEPTOS/TIPS YA ENVIADOS (NUNCA REPETIR) ===
{titles_str}

=== NOTICIAS TECH DE HOY (usar como inspiración, basa tips en ellas siempre que sea posible) ===
{news_str}

=== HERRAMIENTAS/REPOS TRENDING DE HOY (inspiración secundaria) ===
{tools_str}

=== REGLAS ESTRICTAS ===
1. Genera EXACTAMENTE 5 tips
2. Cada tip = UNA categoría DIFERENTE del batch
3. NUNCA repitas título, concepto ni idea de la lista de enviados
4. Cada tip debe tener UNA SOLA idea clara y concreta
5. Si el tip es sobre un comando, SQL, bash, scripting, código, framework o herramienta técnica: DEBE incluir un ejemplo de código o comando real
6. Si el tip es sobre un concepto, principio, patrón o idea general: NO pongas código, solo explicación clara
7. Todo en ESPAÑOL correcto, sin anglicismos innecesarios
8. NUNCA uses emojis en el body ni en el título
9. Usa términos técnicos en INGLÉS cuando sea estándar (cold start, hot function, load balancer, etc.)
10. Varía dificultad: 1=básico, 2=intermedio, 3=avanzado
11. Cuando el tip mencione una SIGLA o acrónimo (por ejemplo: VPN, SSL, LLM, SVN, WISPr, DNS, HTTP, API, SQL, SSH, TLS, SMTP, RAID, VM, CI, CD, IaC, RBAC, ETL, MQTT, NAT, WAN, LAN...), SIEMPRE expande la sigla entre paréntesis la primera vez que aparezca y añade UNA frase breve que la explique en contexto. Ejemplo: "VPN (Virtual Private Network, red privada virtual) cifra tu conexión..."
12. Cuando el tip describa una práctica, comando o configuración técnicos, SIEMPRE rellena los campos "mala" (cómo NO se debe hacer) y "buena" (cómo se debe hacer correctamente), redactados como frases breves. Si el tip es un concepto teórico puro, deja "mala" y "buena" vacíos ("").
13. El campo "body" describe el tema de forma neutra; los campos "mala" y "buena" muestran el contraste de práctica. Cada tip DEBE tener los campos "id"/"title","cat","body","difficulty" y opcionalmente "mala"/"buena". Siempre con mala/buena rellenados en tips prácticos.

=== CUÁNDO INCLUIR CÓDIGO ===
- Comandos de terminal (linux, docker, git, etc.)
- SQL queries
- Scripts bash
- Código de programación (python, javascript, rust, etc.)
- Configuraciones (nginx, docker-compose, etc.)
- APIs y endpoints

=== CUÁNDO NO INCLUIR CÓDIGO ===
- Conceptos abstractos (polimorfismo, herencia, etc.)
- Principios y buenas prácticas
- Consejos de carrera
- Leyendas de programación
- Organización y arquitectura

=== EJEMPLO CON CÓDIGO ===
{{
  "cat": "postgresql",
  "title": "Explicar un query SQL lento",
  "body": "En PostgreSQL: EXPLAIN ANALYZE seguido de tu query te muestra el plan de ejecución real y cuánto tarda cada paso. Esencial para optimizar.",
  "mala": "SELECT * FROM usuarios WHERE email = 'test@mail.com'; sin saber por qué va lento.",
  "buena": "EXPLAIN ANALYZE SELECT * FROM usuarios WHERE email = 'test@mail.com'; para ver el plan real y los tiempos de cada paso.",
  "difficulty": 2
}}

=== EJEMPLO SIN CÓDIGO (concepto teórico: mala/buena vacías) ===
{{
  "cat": "programming",
  "title": "¿Qué es polimorfismo?",
  "body": "Objetos de diferentes clases respondiendo al mismo método. Un gato.hablar() dice 'miau', un perro.hablar() dice 'guau'. El código que usa hablar() no necesita saber qué animal es.",
  "mala": "",
  "buena": "",
  "difficulty": 2
}}

=== EJEMPLO CON SIGLA EXPLICADA ===
{{
  "cat": "redes",
  "title": "Para qué sirve una VPN",
  "body": "Una VPN (Virtual Private Network, red privada virtual) crea un túnel cifrado entre tu equipo y un servidor remoto. Sirve para ocultar tu IP, protegerte en redes Wi-Fi públicas y acceder a recursos internos de una empresa como si estuvieras en la oficina.",
  "mala": "",
  "buena": "",
  "difficulty": 1
}}

=== RESPUESTA ===
SOLO el JSON array, sin markdown, sin texto adicional:
[{{"cat": "...", "title": "...", "body": "...", "mala": "...", "buena": "...", "difficulty": 1}}, ...]"""


def generate_tips_gemini(count, categories, sent_titles):
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY no configurada. Solo se usarán tips de la DB.")
        return None

    try:
        from google import genai
        client = genai.Client(api_key=GEMINI_API_KEY)
    except ImportError:
        print("⚠️  google-genai no instalado. Solo se usarán tips de la DB.")
        return None
    except Exception as e:
        print(f"⚠️  Error al inicializar Gemini: {e}")
        return None

    news = load_recent_news(15)
    tools = load_recent_tools(10)
    prompt = build_gemini_prompt(categories, sent_titles, news, tools)

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
        )
        text = response.text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        tips = json.loads(text)
        if isinstance(tips, list) and len(tips) > 0:
            valid = []
            for t in tips:
                if all(k in t for k in ("cat", "title", "body", "difficulty")):
                    if t["cat"] in CAT_EMOJI:
                        valid.append(t)
            if valid:
                print(f"✅ Gemini generó {len(valid)} tips nuevos")
                return valid[:count]
        print("⚠️  Respuesta de Gemini no tiene formato válido")
        return None
    except json.JSONDecodeError:
        print("⚠️  Gemini respondió con JSON inválido")
        return None
    except Exception as e:
        print(f"⚠️  Error al llamar a Gemini: {e}")
        return None


def mix_tips(gemini_tips, db_tips, total=10):
    mixed = []
    g = gemini_tips or []
    d = db_tips or []
    random.shuffle(g)
    random.shuffle(d)
    i_g, i_d = 0, 0
    while len(mixed) < total:
        added = False
        if i_g < len(g) and len(mixed) < total:
            mixed.append(g[i_g])
            i_g += 1
            added = True
        if i_d < len(d) and len(mixed) < total:
            mixed.append(d[i_d])
            i_d += 1
            added = True
        if not added:
            break
    return mixed[:total]


def format_tip_message(tip, index):
    cat = tip.get("cat", "")
    emoji = CAT_EMOJI.get(cat, "?")
    nombre = CAT_NAMES.get(cat, cat)
    header = f"{index}. {emoji} {nombre}{': ' + tip['title'] if tip.get('title') else ''} — {tip.get('body', '')}"
    if tip.get("mala") and tip.get("buena"):
        return f"{header}\n❌ Mala práctica: {tip['mala']}\n✅ Buena práctica: {tip['buena']}"
    return f"{index}. {emoji} {nombre} — {tip.get('body', '')}"


def build_daily_message(tips):
    greeting = _get_time_greeting(datetime.now())
    header = f"{greeting}\n"

    body_parts = []
    for i, tip in enumerate(tips, 1):
        body_parts.append(format_tip_message(tip, i))

    body = "\n\n".join(body_parts)

    footer = ""

    return header + "\n\n" + body + footer


def _get_time_greeting(now):
    hour = now.hour
    if 5 <= hour < 12:
        return "*Buenos días*"
    elif 12 <= hour < 19:
        return "*Buenas tardes*"
    else:
        return "*Buenas noches*"


def send_telegram(text):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  TIPS_BOT_TOKEN o TIPS_CHAT_ID no configurados.")
        print("   Configura las variables de entorno o usa --dry-run.")
        return False

    payload = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }

    try:
        resp = requests.post(API_URL, json=payload, timeout=30)
        if resp.status_code == 200:
            print("✅ Mensaje enviado a Telegram.")
            return True
        else:
            print(f"❌ Error Telegram ({resp.status_code}): {resp.text}")
            return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def main():
    dry_run = "--dry-run" in sys.argv
    list_cats = "--list-categories" in sys.argv
    show_stats = "--stats" in sys.argv

    if list_cats:
        print("📂 Categorías disponibles:")
        for cat in sorted(ALL_CATEGORIES):
            emoji = CAT_EMOJI.get(cat, "?")
            name = CAT_NAMES.get(cat, cat)
            print(f"   {emoji} {cat}: {name}")
        print(f"\n   Total: {len(ALL_CATEGORIES)} categorías")
        return

    if not DB_PATH.exists():
        print(f"❌ No se encontró la base de datos: {DB_PATH}")
        sys.exit(1)

    database = load_database()
    history = load_history()
    sent_titles = history.get("sent_titles", [])

    if show_stats:
        print(f"📊 Estadísticas del sistema de tips:")
        print(f"   Tips en DB: {len(database['tips'])}")
        print(f"   Tips enviados (total): {len(sent_titles)}")
        print(f"   DB agotada: {'Sí' if history.get('db_exhausted') else 'No'}")
        print(f"   Última ejecución: {history.get('last_run', 'Nunca')}")
        print(f"   Total ejecuciones: {history.get('total_runs', 0)}")
        print(f"   Categorías disponibles: {len(ALL_CATEGORIES)}")
        news = load_recent_news(1)
        tools = load_recent_tools(1)
        print(f"   Noticias en DB: {len(news)} recientes cargadas")
        print(f"   Tools en DB: {len(tools)} recientes cargadas")
        return

    categories = select_random_categories(6)
    print(f"📂 Categorías de este batch: {', '.join(categories)}")

    db_exhausted = history.get("db_exhausted", False)

    if db_exhausted:
        print("🔄 DB agotada. Generando 10 tips con Gemini...")
        gemini_tips = generate_tips_gemini(10, categories, sent_titles)
        if gemini_tips:
            for t in gemini_tips:
                t["source"] = "gemini"
            tips = gemini_tips
        else:
            print("⚠️  Gemini no disponible. Reintentando con DB (puede repetir)...")
            db_tips = select_tips_from_db(database, history, 10)
            tips = db_tips
    else:
        print("🔄 Generando tips (Gemini + DB)...")
        gemini_tips = generate_tips_gemini(5, categories, sent_titles)
        if gemini_tips:
            for t in gemini_tips:
                t["source"] = "gemini"
        db_tips = select_tips_from_db(database, history, 5)
        tips = mix_tips(gemini_tips, db_tips, total=10)

    message = build_daily_message(tips)

    print(f"\n📋 Tips seleccionados ({len(tips)}):")
    for i, tip in enumerate(tips, 1):
        emoji = CAT_EMOJI.get(tip["cat"], "?")
        src = tip.get("source", "db")
        print(f"   {i}. {emoji} [{tip['cat']}] {tip['title']} ({src})")

    if dry_run:
        print("\n--- VISTA PREVIA (dry-run) ---\n")
        print(message)
        print("\n--- FIN VISTA PREVIA ---")
        return

    if send_telegram(message):
        for tip in tips:
            title = tip.get("title", "")
            if title and title not in sent_titles:
                history["sent_titles"].append(title)
        history["last_run"] = datetime.now().isoformat()
        history["total_runs"] = history.get("total_runs", 0) + 1
        if not db_exhausted and len(database["tips"]) > 0:
            db_sent = sum(1 for t in tips if t.get("source") != "gemini")
            if db_sent > 0:
                remaining = len([t for t in database["tips"]
                                 if t["title"] not in set(history["sent_titles"])])
                if remaining == 0:
                    history["db_exhausted"] = True
                    print("🔄 DB estática agotada. A partir de ahora solo Gemini.")
        save_history(history)
        print(f"📊 Total tips enviados: {len(history['sent_titles'])}")


if __name__ == "__main__":
    main()
