import os
CONFIG = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "TELEGRAM_CHAT_ID": os.getenv("TOKEN_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "DOWNLOADER_API_TOKEN": os.getenv("DOWNLOADER_API_TOKEN"),
    "FOLDER": "files",
    "IMAGES_FOLDER": "images",
    "IMAGES_PATH_PREFIX": "public/optimizado",
    "AI_MODELS": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "IMAGE_MODELS": ["imagen-3.0-generate-002"], # Fallback para imagen
    "NEWS_DIR": "auto-news"
}

# ── File paths (centralized) ──
NOTICIAS_FILENAME = "noticias_historico.json"
HERRAMIENTAS_FILENAME = "herramientas.json"
AI_TOOLS_CANDIDATES_FILENAME = "ai_tools_candidates.json"
CONCEPTS_FILENAME = "concepts_database.json"
CONCEPTS_PATH_DEFAULT = os.path.join(CONFIG["FOLDER"], CONCEPTS_FILENAME)
CONCEPTS_MAX = 200
CONCEPTS_PRUNE_BATCH = 20
CONCEPTS_MIN_INTERVIEW = 50
AVATARS_CACHE_FILENAME = "avatars_cache.json"
TELEGRAM_SENT_FILENAME = "telegram_sent.json"
TELEGRAM_VOICE_SENT_FILENAME = "telegram_voice_sent.json"
OPTIMIZED_CACHE_FILENAME = "optimized_cache.json"
LOGS_DIR = "logs"
LOG_FILES = {
    "news": "news.log",
    "tools": "tools.log",
    "concepts": "concepts.log",
    "weekly": "weekly.log",
    "telegram": "telegram.log",
    "email": "email.log",
}
DASHBOARD_DIR = "public"
DASHBOARD_HTML = "public/index.html"
AUTO_NEWS_DIR = "auto-news"
BLOG_AUTO_NEWS_REL = ("src", "content", "auto-news")
BLOG_PATH_DEFAULT = "blog"
HERRAMIENTAS_PATH_DEFAULT = os.path.join(CONFIG["FOLDER"], HERRAMIENTAS_FILENAME)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

URL_API_DESCARGA = "https://testactions1github-api-python.hf.space/download"
URL_API_SALUD = "https://testactions1github-api-python.hf.space/health"

TECH_KEYWORDS = [# Inteligencia Artificial
"IA", "AI", "LLM", "GPT-4", "GPT-4o", "Gemini", "Claude", "Llama 3", "DeepSeek",
"OpenAI", "Anthropic", "Mistral", "Stable Diffusion", "Midjourney", "Sora",
"RAG", "Fine-tuning", "Prompt", "Agente IA", "Copilot", "Neural", "Deep Learning",
"Python", "Rust", "TypeScript", "React", "Next.js", "Docker", "Kubernetes",
"API", "Backend", "Frontend", "Fullstack", "DevOps", "Serverless", "GitHub",
"Tailwind", "Node.js", "Go", "WebAssembly", "Ciberseguridad", "Zero Trust",
"NVIDIA", "H100", "Blackwell", "GPU", "NPU", "Apple Silicon", "M4", "Intel",
"AMD", "Snapdragon", "Quantum", "Chip", "Semicondutores",
"SaaS", "Startups", "Cloud", "Big Data", "Blockchain", "Web3", "Automatización",
"Fintech", "Cripto", "Metaverso", "IoT", "Open Source",
"reto progrmación", "challenge", "kata", "ctf", "vulnerabilidad", "hack", "desafío"
]

ALL_KEYWORDS = TECH_KEYWORDS

CATEGORIAS = {
    "⚡ Hardware": ["NVIDIA", "H100", "Blackwell", "GPU", "NPU", "Apple Silicon", "M4",
                    "Intel", "AMD", "Snapdragon", "Chip", "Semicondutores", "procesador",
                    "Qualcomm", "ARM", "RTX"],
    "🤖 IA": ["IA", "AI", "LLM", "GPT", "Gemini", "Claude", "Llama 3", "DeepSeek",
               "OpenAI", "Anthropic", "Mistral", "Stable Diffusion", "Midjourney", "Sora",
               "RAG", "Fine-tuning", "Prompt", "neural", "Deep Learning",
               "Hugging Face", "Transformer", "difusión", "modelo",
               "inteligencia artificial", "aprendizaje automático"],
    "💻 Programación": ["Python", "Rust", "TypeScript", "React", "Next.js", "Node.js", "Go",
                        "WebAssembly", "JavaScript", "Java", "C#", "PHP", "Ruby", "Dart",
                        "Swift", "Kotlin", "Tailwind", "API", "Backend", "Frontend",
                        "Fullstack", "reto programación", "challenge", "kata", "framework",
                        "librería", "compilador"],
    "🐳 DevOps": ["Docker", "Kubernetes", "DevOps", "Serverless", "CI/CD", "Terraform",
                  "GitHub Actions", "GitLab", "Jenkins", "infra", "despliegue", "contenedor",
                  "orquestación"],
    "🔒 Ciberseguridad": ["Ciberseguridad", "Zero Trust", "hack", "vulnerabilidad", "ctf",
                          "malware", "ransomware", "phishing", "firewall", "ciberataque"],
    "📊 Negocios": ["SaaS", "Startups", "Cloud", "Big Data", "Blockchain", "Web3",
                    "Fintech", "Cripto", "Metaverso", "IoT", "Automatización", "Open Source",
                    "inversión", "millon"],
}


SKILLS = {
    "💻 Programación": ["Python", "JavaScript", "TypeScript", "Rust", "Go", "Java", "C#", "PHP", "Ruby", "Swift", "Kotlin", "Dart", "C", "C++", "Zig"],
    "🤖 IA/ML": ["Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Reinforcement Learning", "MLOps", "Fine-tuning", "RAG", "Agentes IA", "Prompt Engineering"],
    "☁️ Cloud/DevOps": ["Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "Serverless", "GitHub Actions"],
    "🔒 Seguridad": ["Pentesting", "CTF", "Bug Bounty", "Ciberseguridad", "Zero Trust", "OSINT", "Hacking"],
    "📊 Datos": ["SQL", "NoSQL", "Big Data", "Data Analysis", "BI", "ETL", "Data Engineering"],
}

LLMS = {
    "Propietarios": ["GPT-4", "GPT-4o", "GPT-4o-mini", "Claude 3.5 Sonnet", "Claude 3 Opus", "Gemini 1.5 Pro", "Gemini 2.5 Pro", "Gemini 2.5 Flash", "Grok", "Copilot"],
    "Open Source": ["Llama 3.1", "Llama 3", "Mistral Large", "Mixtral", "DeepSeek V2", "DeepSeek Coder", "Qwen 2.5", "Phi-3", "Gemma 2", "Falcon 2", "Command R+"],
    "Especializados": ["CodeLlama", "StarCoder", "SQLCoder", "BioMistral", "Meditron", "FinGPT"],
}

LENGUAJES = {
    "Web": ["JavaScript", "TypeScript", "HTML", "CSS"],
    "Sistema": ["Rust", "Go", "C", "C++", "Zig"],
    "Datos/IA": ["Python", "R", "Julia", "SQL"],
    "Mobile": ["Swift", "Kotlin", "Dart"],
    "Empresarial": ["Java", "C#", "PHP", "Ruby"],
}

FRAMEWORKS = {
    "Frontend": ["React", "Next.js", "Vue", "Nuxt", "Svelte", "Solid", "Astro", "Remix", "Angular", "Qwik"],
    "Backend": ["Django", "FastAPI", "Flask", "Express", "NestJS", "Spring Boot", "Laravel", "ASP.NET", "Actix"],
    "Mobile/Desktop": ["React Native", "Flutter", "SwiftUI", "Jetpack Compose", "Tauri", ".NET MAUI"],
    "CSS/UI": ["Tailwind", "Bootstrap", "Material UI", "Shadcn/ui", "Chakra UI", "Radix UI"],
}

LIBRERIAS = {
    "IA/ML": ["TensorFlow", "PyTorch", "LangChain", "LlamaIndex", "Hugging Face Transformers", "Scikit-learn", "XGBoost", "JAX"],
    "Testing": ["Jest", "Playwright", "Vitest", "Cypress", "Pytest", "Selenium", "Testing Library"],
    "DevOps": ["Ansible", "Prometheus", "Grafana", "Helm", "Vault", "Packer"],
    "Utilidades": ["Lodash", "Day.js", "Zod", "React Query", "Prisma", "Drizzle ORM", "RxJS", "tRPC"],
}


def clasificar_noticia(titulo: str) -> str:
    t_padded = " " + titulo.lower() + " "
    for cat, keywords in CATEGORIAS.items():
        for k in keywords:
            if " " + k.lower() + " " in t_padded:
                return cat
    return "💡 General"

# ── JS config (inyectado en HTML pre-renderizado) ──
JS_CONFIG = {
    "ALL_YT_CHANNELS": [
        "3DHumbe", "4tomik", "AfroCode",
        "Agustín Medina | AI Agency Academy", "Aivars Meijers",
        "ALDI SCRAP PCB", "aleccisWithX", "Alejandro Pérez",
        "AlexCG Design", "Antonio Sarosi", "AprenDevOps",
        "Aprendiendo Frontend", "Atípico Mental", "BettaTech",
        "Bita Byte Ibiza", "Bro Code", "campusMVP.es",
        "Carlos Alfaro", "Carlos Azaustre", "Carlos Azaustre Two",
        "Chilango Radio", "Clever Programmer", "clipset shorts", "Clipset",
        "ClipsetTEST", "Code Monkey", "CodeBorn Dev", "CodelyTV",
        "Codificandolo", "Codigo Estudiante", "Codigo facilito",
        "Consejos C#", "Contando Bits", "Control 3D", "Cristian Torres",
        "d3vcloud", "Daniel Diaz", "DanieloTech",
        "DesarrolloWeb.com", "DesignCourse", "Develoteca",
        "Devon Crawford", "diegoveloper", "DistroTube", "Domingo Gomes",
        "dotnet", "EDteam", "El Pingüino de Mario", "Enrique Dans",
        "Esa Operativa", "FalconMasters", "Fazt", "Fazt Code",
        "Fernando Herrera", "freeCodeCamp Español", "FreeCodeCamp",
        "GitHub", "Google", "GoogleDoodles", "grenasfrijolito",
        "Guillermo Garcia", "Hallden", "Hdeleon Clips", "hdeleon.net",
        "HolaMundo", "IA con Daniel", "IAmTimCorey",
        "Ildefonso Segura Tutoriales", "IndevError", "Informatic.com",
        "Informática DP", "Internet no pesa nada", "JD Productions HD",
        "Jerry Sawhney", "Jesse Dietrichson", "Jesus Luque Medina",
        "Jorebza", "Jose Maria Alonso", "jotajotavm", "JustDjango",
        "Kala360Gamer", "Karan Kumar", "Kiko Palomares",
        "Leigh en Español", "Leonidas Esteban", "Linkfydev", "LinkTV",
        "LinuxScoop", "linuxware", "Luis Cambra", "Make it Real",
        "makigas", "ManzDev", "Martín Gesualdo",
        "Microsoft Developer", "Microsoft IoT Developers", "Midudev",
        "midulive", "Migma", "Moldeo Interactive",
        "Món de llengua - Dr. Zalbidea", "MoureDev", "MoureDev TV",
        "Mr. Resumen", "Mundos Apple Pro", "NASeros", "Nekszer",
        "Nethermind", "nicobytes", "No es Brujería, es Tecnología",
        "Noticias Tech y ya!", "Octarine Code", "Online Tutorials",
        "Pelado Nerd", "PhoneGapSpain", "Pildoras de programación",
        "pildorasinformaticas", "Pirple", "Platzi",
        "Programa Con Arnau", "Programación en español", "Programador X",
        "Programming w/ Professor Sluiter", "Programming with Mosh",
        "React-Native by Wilhelm", "Ready Set Click", "render2web",
        "Ringa Tech", "RobotSolar",
        "Sergio Alejandro Campos - EXCELeINFO", "Simon Grimm",
        "Sin Rueda Tecnológica", "Software Lion", "Sonfil",
        "Sonny Sangha", "Sosteniblevida", "Soy Dalto", "subelealruido",
        "Super Excel", "Tech Point Fundamentals", "TechHut",
        "TecnoBinaria", "TecnoXplora", "TEDx Talks",
        "The Coder Cave | Programación y Tecnología", "TIFF Trailers",
        "Toni Dev", "Topes de Gama", "Tu Area De Informatica",
        "tutorialesJJ", "tutorialsEU", "Unity", "Victor Abarca",
        "Victor Robles", "Vida MRR - Programacion web",
        "Video Tutoriales Android", "Web Dev Simplified", "Xataka",
    ],
    "TABS_MULTIMEDIA": [
        {"id": "youtube", "label": "🎬 YouTube"},
        {"id": "shorts", "label": "🩳 Shorts"},
        {"id": "live", "label": "🔴 En directo"},
    ],
    "EMOJIS_CATEGORIA": "⚡🤖💻🐳🔒📊🎓💡",
    "DASHBOARD_URL": "https://jorbencasdownloaderdocument.surge.sh",
}

# ── Dict key constants ──
YT_KEY = "yt"
RSS_KEY = "rss"
URL_KEY = "url"
TIPO_KEY = "tipo"
SUBTIPO_KEY = "subtipo"
QUICK_KEY = "quick"
SELECTOR_KEY = "selector"
ORIGEN_KEY = "origen"
BADGE_KEY = "badge"
SUB_VAL_GITHUB = "github"
SUB_VAL_GITHUB_TOPIC = "github-topic"
SUB_VAL_GITHUB_COLLECTION = "github-collection"
SUB_VAL_PRODUCTHUNT = "producthunt"
TIPO_VAL_HERRAMIENTA = "herramienta"
TIPO_VAL_NOTICIA = "noticia"
TIPO_VAL_VIDEO = "video"
TIPO_VAL_SHORTS = "shorts"
TIPO_VAL_LIVE = "live"

VAL_RSS = "rss"
VAL_TECH = "Tech"
PLAYWRIGHT_KEY = "pw"


# ── Item schema key constants ──
ENLACE_KEY = "enlace"
FUENTE_KEY = "fuente"
TITULO_KEY = "titulo"
CATEGORIA_KEY = "categoria"
ESTRELLAS_KEY = "estrellas"
DESCRIPCION_KEY = "descripcion"
LENGUAJE_KEY = "lenguaje"
REPO_KEY = "repo"
TS_KEY = "ts"
F_KEY = "f"
FECHA_REAL_KEY = "fecha_real"
FECHA_PUB_KEY = "fecha_publicacion"
ID_VIDEO_KEY = "id_video"
IMAGEN_URL_KEY = "imagen_url_original"
ULTIMA_VERIF_KEY = "ultima_verificacion"

# ── Fuentes inglesas para traducción automática ──
FUENTES_INGLES = [
    "wired", "verge", "techcrunch", "github", "openai", "hacker news",
    "ars", "nvidia", "anthropic", "venturebeat", "mit", "hugging face",
    "google ai", "deepmind", "dev.to",
    "freecodecamp", "nethermind",
]

# ── Fallback values ──
FALLBACK_IMAGE_URL = "public/img/arquitectura_web.webp"
FALLBACK_GITHUB_IMAGE = "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true"
FALLBACK_SNEAK_PEEK = "Seguiremos de cerca la evolución del sector. ¡No te lo pierdas!"
FALLBACK_NOTA_PERSONAL = "Keep coding!"
FALLBACK_RECAP_INTRO = "Esta semana hemos seguido de cerca las principales tendencias en tecnología y desarrollo."

# ── Telegram ──
TELEGRAM_TTS_VOZ = "es-ES-AlvaroNeural"
TELEGRAM_TTS_VOZ_EN = "en-US-GuyNeural"
TELEGRAM_DASHBOARD_URL = "https://jorbencasdownloaderdocument.surge.sh"
TELEGRAM_MENSAJE_TEMPLATE = "{icono} *{titulo}*\n📰 `{fuente}` | `{fecha}`\n\n{cuerpo}\n🔗 [Abrir noticia]({enlace})\n🌐 [Ver más en el Dashboard]({dashboard_url})"

# ── Re-exports para compatibilidad (imports existentes siguen funcionando) ──
from scripts.utils.constants_sources import FUENTES  # noqa: E402, F401
from scripts.utils.constants_templates import (  # noqa: E402, F401
    HTML_TEMPLATE, EMAIL_TEMPLATE, MD_TEMPLATE,
    PROMPT_IMAGEN_TEMPLATE, PROMPT_RESUMIR_LOTE, PROMPT_RESUMIR_NOTICIA,
    PROMPT_RECAP_SEMANAL, PROMPT_TRADUCIR_TITULOS,
    EMAIL_SOURCE_HEADER, EMAIL_ROW_TEMPLATE,
    EMAIL_VIDEO_HEADER, EMAIL_VIDEO_ROW,
)
