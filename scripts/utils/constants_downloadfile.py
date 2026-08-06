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
AVATARS_CACHE_FILENAME = "avatars_cache.json"
TELEGRAM_SENT_FILENAME = "telegram_sent.json"
TELEGRAM_VOICE_SENT_FILENAME = "telegram_voice_sent.json"
OPTIMIZED_CACHE_FILENAME = "optimized_cache.json"
LOGS_DIR = "logs"
LOG_FILES = {
    "news": "news.log",
    "tools": "tools.log",
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

FUENTES = {
    "Programa Con Arnau": {"yt":"https://youtube.com/@progconarnau?si=AFBTWjGeo-UpuJdE"},
    "El Pingüino de Mario": {"yt":"https://www.youtube.com/@elpinguinodemario?si=DvMsCTK74FQfFzwH"},
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos", "selector": "a[href*='/blog/']"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"url":"https://midu.dev/", "yt": "https://www.youtube.com/@midudev/videos", "selector": "article a[href]"},
    "Codigo facilito": {"yt": "https://www.youtube.com/@codigofacilito/videos"},
    "Carlos Azaustre": {"url":"https://carlosazaustre.es/blog", "yt": "https://www.youtube.com/@CarlosAzaustre/videos", "selector": "a[href*='/blog/']"},
    "Clipset": {"yt": "https://www.youtube.com/@clipset/videos"},
    "CodelyTV": {"yt": "https://www.youtube.com/@CodelyTV/videos"},
    "EDteam": {"yt": "https://www.youtube.com/@EDteam/videos"},
    "Fazt": {"yt": "https://www.youtube.com/@FaztTech/videos"},
    "FreeCodeCamp": {"yt": "https://www.youtube.com/@freecodecamp/videos"},
    "HolaMundo": {"yt": "https://www.youtube.com/@holamundodev/videos"},
    "Victor Robles": {"yt": "https://www.youtube.com/@victorroblesweb/videos"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://www.youtube.com/@xatakatv/videos", "quick": True, "selector": "article a[href]"},
    "Genbeta": {"url": "https://www.genbeta.com/", "selector": "article a[href]"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/tags/temas/tecnologia.html", "selector": "article a[href]"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/", "selector": "article a[href]"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/tags/tecnologia/", "selector": "article a[href]"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/", "selector": "h3 a[href]"},
    "Applesfera": {"url": "https://www.applesfera.com/", "selector": "article a[href]"},
    "Wired": {"url": "https://www.wired.com/category/science/"},
    "The Verge": {"url": "https://www.theverge.com/tech"},
    "TechCrunch": {"url": "https://techcrunch.com/category/artificial-intelligence/"},
    "GitHub Blog": {"url": "https://github.blog/category/engineering/", "selector": "article a[href]"},
    "Google AI": {"url": "https://blog.google/technology/ai/", "selector": "article a[href]"},
    "NVIDIA Blog": {"url": "https://blogs.nvidia.com/blog/category/deep-learning/", "selector": "article a[href]"},
    "Ars Technica": {"url": "https://arstechnica.com/gadgets/"},
    "Slashdot": {"url": "https://slashdot.org/", "selector": "article a[href]"},
    "HackTheBox": {"url": "https://www.hackthebox.com/blog/", "selector": "a[href*='/blog/']"},
    # ── Nuevas fuentes ──
    "ADSL Zone": {"url": "https://www.adslzone.net/", "selector": "article h2 a"},
    "MuyComputer": {"url": "https://www.muycomputer.com/", "selector": "a[rel=\"bookmark\"]"},
    "ComputerHoy": {"url": "https://www.computerhoy.com/", "selector": ".c-article__title a"},
    "Hipertextual": {"url": "https://hipertextual.com/"},
    "Hugging Face Blog": {"url": "https://huggingface.co/blog", "selector": "article.overview-card-wrapper a[role=\"link\"]"},
    "Anthropic": {"url": "https://www.anthropic.com/blog", "selector": "a[class*=\"FeaturedGrid\"], a[class*=\"PublicationList\"]"},
    "Meta AI": {"url": "https://engineering.fb.com/category/artificial-intelligence/", "selector": "article a[href]"},
    "DeepMind": {"url": "https://deepmind.google/discover/blog/", "selector": "h3.card__title"},
    "VentureBeat AI": {"url": "https://venturebeat.com/category/ai/", "selector": "header.text-editorial-headline-030 h2 a"},
    # ── Fuentes IA especializadas ──
    "AssemblyAI": {"url": "https://www.assemblyai.com/blog/", "selector": "article h2 a"},
    "Cohere": {"url": "https://cohere.com/blog", "selector": "a[href*='/blog/'] h3"},
    "Scale AI": {"url": "https://scale.com/blog", "selector": "a[href*='/blog/']"},
    "LangChain": {"url": "https://blog.langchain.dev/", "selector": "article h2 a"},
    "Pinecone": {"url": "https://www.pinecone.io/blog/", "selector": "a[href*='/blog/']"},
    "Weights & Biases": {"url": "https://wandb.ai/fully-connected", "selector": "article h2 a"},
    "Hugging Face": {"url": "https://huggingface.co/blog", "selector": "article.overview-card-wrapper a[role='link']"},
    "LlamaIndex": {"url": "https://www.llamaindex.ai/blog", "selector": "a[href*='/blog/']"},
    "Anthropic Research": {"url": "https://www.anthropic.com/research", "selector": "a[class*='card']"},
    "Claude Blog": {"url": "https://docs.anthropic.com/en/release-notes", "selector": "article a[href]"},
    "OpenCode": {"url": "https://opencode.ai/changelog", "selector": "article a[href]"},
    "Google Research": {"url": "https://research.google/blog/", "selector": "a[href*='/blog/']"},
    "Google Cloud AI": {"url": "https://cloud.google.com/blog/products/ai-machine-learning", "selector": "a[href*='/blog/']"},
    "Google AI Dev": {"url": "https://ai.google.dev/", "selector": "article a[href]"},
    "Microsoft AI": {"url": "https://blogs.microsoft.com/ai/", "selector": "article h2 a"},
    "Microsoft Research AI": {"url": "https://www.microsoft.com/en-us/research/topic/artificial-intelligence/", "selector": "article h2 a"},
    "Azure AI": {"url": "https://azure.microsoft.com/en-us/blog/product/azure-ai/", "selector": "article a[href]"},
    "AWS ML": {"url": "https://aws.amazon.com/blogs/machine-learning/", "selector": "article h2 a"},
    "Apple ML Research": {"url": "https://machinelearning.apple.com/", "selector": ".card a[href]"},
    "xAI": {"url": "https://x.ai/blog", "selector": "article h2 a"},
    "Perplexity AI": {"url": "https://blog.perplexity.ai/", "selector": "article h2 a"},
    "Meta AI Research": {"url": "https://ai.meta.com/blog/", "selector": "a[href*='/blog/']"},
    "Stability AI": {"url": "https://stability.ai/news", "selector": "article a[href]"},
    "Replicate": {"url": "https://replicate.com/blog", "selector": "a[href*='/blog/']"},
    "Modal": {"url": "https://modal.com/blog", "selector": "article h2 a"},
    "Together AI": {"url": "https://www.together.ai/blog", "selector": "a[href*='/blog/']"},
    "Fireworks AI": {"url": "https://fireworks.ai/blog", "selector": "a[href*='/blog/']"},
    "Cursor": {"url": "https://www.cursor.com/blog", "selector": "article a[href]"},
    "Codeium": {"url": "https://codeium.com/blog", "selector": "a[href*='/blog/']"},
    "TabbyML": {"url": "https://tabby.tabbyml.com/blog", "selector": "a[href*='/blog/']"},
    "Continue.dev": {"url": "https://docs.continue.dev/changelog", "selector": "article h2 a"},
    "Aider": {"rss": "https://aider.chat/feed.xml", "quick": True},
    # ── GitHub Topics (AI tools, LLMs, agents) ──
    "GitHub Topic AI": {"url": "https://github.com/topics/artificial-intelligence?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic LLM": {"url": "https://github.com/topics/llm?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic AI Agents": {"url": "https://github.com/topics/ai-agents?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic ML": {"url": "https://github.com/topics/machine-learning?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    # ── GitHub Topics (Video, Content, Git, Docker, Algorithms, OpenSource) ──
    "GitHub Topic Video Editing": {"url": "https://github.com/topics/video-editing?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Screen Recording": {"url": "https://github.com/topics/screen-recording?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Content Creation": {"url": "https://github.com/topics/content-creation?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Markdown": {"url": "https://github.com/topics/markdown?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Git": {"url": "https://github.com/topics/git?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Version Control": {"url": "https://github.com/topics/version-control?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Docker": {"url": "https://github.com/topics/docker?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Container": {"url": "https://github.com/topics/container?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Kubernetes": {"url": "https://github.com/topics/kubernetes?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Algorithms": {"url": "https://github.com/topics/algorithms?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Data Structures": {"url": "https://github.com/topics/data-structures?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Competitive Programming": {"url": "https://github.com/topics/competitive-programming?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Generative AI": {"url": "https://github.com/topics/generative-ai?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic AI Coding": {"url": "https://github.com/topics/ai-coding?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Open Source": {"url": "https://github.com/topics/open-source?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Awesome Lists": {"url": "https://github.com/topics/awesome-lists?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    # ── GitHub Topics (Image, Office, Presentations, Data Workflow) ──
    "GitHub Topic Image Processing": {"url": "https://github.com/topics/image-processing?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Image Editing": {"url": "https://github.com/topics/image-editing?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Computer Vision": {"url": "https://github.com/topics/computer-vision?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Document Processing": {"url": "https://github.com/topics/document-processing?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic PDF": {"url": "https://github.com/topics/pdf?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Office": {"url": "https://github.com/topics/office?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Presentation": {"url": "https://github.com/topics/presentation?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Slide Deck": {"url": "https://github.com/topics/slide-deck?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Data Pipeline": {"url": "https://github.com/topics/data-pipeline?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic ETL": {"url": "https://github.com/topics/etl?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Workflow Automation": {"url": "https://github.com/topics/workflow-automation?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Documentation Generator": {"url": "https://github.com/topics/documentation-generator?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic AI Code Review": {"url": "https://github.com/topics/ai-code-review?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    # ── GitHub Topics (Meetings, Documentation, AI Agents) ──
    "GitHub Topic Meeting Assistant": {"url": "https://github.com/topics/meeting-assistant?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Transcription": {"url": "https://github.com/topics/transcription?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Speech to Text": {"url": "https://github.com/topics/speech-to-text?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Wiki": {"url": "https://github.com/topics/wiki?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Knowledge Base": {"url": "https://github.com/topics/knowledge-base?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic AI Agent": {"url": "https://github.com/topics/ai-agent?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic LLM": {"url": "https://github.com/topics/llm?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic RAG": {"url": "https://github.com/topics/rag?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    # ── Repos específicos innovadores ──
    "OpenWiki": {"url": "https://github.com/langchain-ai/openwiki", "tipo": "herramienta", "subtipo": "github-repo", "selector": "article a[href]"},
    "Meetily": {"url": "https://github.com/Zackriya-Solutions/meetily", "tipo": "herramienta", "subtipo": "github-repo", "selector": "article a[href]"},
    "Code-to-Docs": {"url": "https://github.com/redhat-community-ai-tools/code-to-docs", "tipo": "herramienta", "subtipo": "github-repo", "selector": "article a[href]"},
    "AutoPR": {"url": "https://github.com/irgolic/autopr", "tipo": "herramienta", "subtipo": "github-repo", "selector": "article a[href]"},
    "PR-Agent": {"url": "https://github.com/qodo-ai/pr-agent", "tipo": "herramienta", "subtipo": "github-repo", "selector": "article a[href]"},
    # ── GitHub Topics (Web Standards, Linux Config, Best Practices) ──
    "GitHub Topic CSS": {"url": "https://github.com/topics/css?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic HTML": {"url": "https://github.com/topics/html?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Web Standards": {"url": "https://github.com/topics/web-standards?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Frontend": {"url": "https://github.com/topics/frontend?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Linux Config": {"url": "https://github.com/topics/linux-config?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Dotfiles": {"url": "https://github.com/topics/dotfiles?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Linux Admin": {"url": "https://github.com/topics/linux-admin?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Best Practices": {"url": "https://github.com/topics/best-practices?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Coding Guidelines": {"url": "https://github.com/topics/coding-guidelines?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic Style Guide": {"url": "https://github.com/topics/style-guide?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic XML": {"url": "https://github.com/topics/xml?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    "GitHub Topic YAML": {"url": "https://github.com/topics/yaml?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic", "selector": "article a[href]"},
    # ── RSS/Web: Web Standards (CSS, HTML, XML, YAML, web dev) ──
    "web.dev": {"rss": "https://web.dev/feed.xml", "quick": True},
    "MDN Blog": {"rss": "https://developer.mozilla.org/en-US/blog/rss.xml", "quick": True},
    "CSS-Tricks": {"rss": "https://css-tricks.com/feed/", "quick": True},
    "Smashing Magazine": {"rss": "https://www.smashingmagazine.com/feed/", "quick": True},
    "Can I Use": {"rss": "https://caniuse.com/feed", "quick": True},
    "Chrome Developers": {"rss": "https://developer.chrome.com/blog/feed.xml", "quick": True},
    "W3C Blog": {"rss": "https://www.w3.org/blog/feed/", "quick": True},
    # ── RSS/Web: Linux, DevOps, Infraestructura ──
    "Linux.com": {"rss": "https://www.linux.com/feed/", "quick": True},
    "Hacker News": {"rss": "https://hnrss.org/frontpage", "quick": True},
    "Lobsters": {"rss": "https://lobste.rs/rss", "quick": True},
    "InfoQ": {"rss": "https://www.infoq.com/feed/", "quick": True},
    # ── RSS/Web: General Tech, AI, Science ──
    "Ars Technica": {"rss": "https://feeds.arstechnica.com/arstechnica/index", "quick": True},
    "OpenAI Blog": {"rss": "https://openai.com/news/rss.xml", "quick": True},
    "Google AI Blog": {"rss": "https://blog.google/technology/ai/rss/", "quick": True},
    # ── Trending GitHub diario ──
    "GitHub Trending Daily": {"url": "https://github.com/trending?since=daily", "tipo": "herramienta", "subtipo": "github", "selector": "article a[href]"},
    "GitHub Trending Weekly": {"url": "https://github.com/trending?since=weekly", "tipo": "herramienta", "subtipo": "github", "selector": "article a[href]"},
    # ── Noticias generales IA ──
    "BBC AI": {"url": "https://www.bbc.com/news/topics/c302m85qtk1t", "selector": "a[data-testid='internal-link']"},
    "El Mundo Tecnología": {"url": "https://www.elmundo.es/tecnologia.html", "selector": "article a[href]"},
    # ── Más creadores de contenido (YouTube + redes) ──
    "LinkTV": {"yt": "https://www.youtube.com/@LinkTVA/videos"},
    "Ringa Tech": {"yt": "https://www.youtube.com/@RingaTech/videos"},
    "Nethermind": {"yt": "https://www.youtube.com/@NethermindDev/videos"},
    "Develoteca": {"yt": "https://www.youtube.com/@Develoteca/videos"},
    "Linkfydev": {"yt": "https://www.youtube.com/@Linkfydev/videos"},
    "Esa Operativa": {"yt": "https://www.youtube.com/@EsaOperativa/videos"},
    "Programador X": {"yt": "https://www.youtube.com/@ProgramadorX/videos"},
    # ── Subscripciones de @jorbencas ──
    "3DHumbe": {"yt": "https://www.youtube.com/@3DHumbe/videos"},
    "4tomik": {"yt": "https://www.youtube.com/@4tomik434/videos"},
    "AfroCode": {"yt": "https://www.youtube.com/@Afro-code/videos"},
    "Agustín Medina | AI Agency Academy": {"yt": "https://www.youtube.com/@agustinmedinaIA/videos"},
    "Aivars Meijers": {"yt": "https://www.youtube.com/@AivarsMeijers/videos"},
    "ALDI SCRAP PCB": {"yt": "https://www.youtube.com/@aldiscrap/videos"},
    "aleccisWithX": {"yt": "https://www.youtube.com/@alecciswithx9137/videos"},
    "Alejandro Pérez": {"yt": "https://www.youtube.com/@alejandroperez/videos"},
    "AlexCG Design": {"yt": "https://www.youtube.com/@AlexCGDesign/videos"},
    "Antonio Sarosi": {"yt": "https://www.youtube.com/@AntonioSarosi/videos"},
    "AprenDevOps": {"yt": "https://www.youtube.com/@AprenDevOps/videos"},
    "Aprendiendo Frontend": {"yt": "https://www.youtube.com/@AprendiendoFrontendChannel/videos"},
    "Atípico Mental": {"yt": "https://www.youtube.com/@atipicomental/videos"},
    "BettaTech": {"yt": "https://www.youtube.com/@BettaTech/videos"},
    "Bita Byte Ibiza": {"yt": "https://www.youtube.com/@bitabyteibiza1177/videos"},
    "Bro Code": {"yt": "https://www.youtube.com/@BroCodez/videos"},
    "campusMVP.es": {"yt": "https://www.youtube.com/@campusmvp/videos"},
    "Carlos Alfaro": {"yt": "https://www.youtube.com/@CarlosAlfaroSV/videos"},
    "Carlos Azaustre Two": {"yt": "https://www.youtube.com/@CarlosAzaustreTV/videos"},
    "Chilango Radio": {"yt": "https://www.youtube.com/@chilangoradiomx/videos"},
    "Clever Programmer": {"yt": "https://www.youtube.com/@CleverProgrammer/videos"},
    "clipset shorts": {"yt": "https://www.youtube.com/@clipsetshorts/videos"},
    "ClipsetTEST": {"yt": "https://www.youtube.com/@testunit/videos"},
    "Code Monkey": {"yt": "https://www.youtube.com/@CodeMonkeyUnity/videos"},
    "CodeBorn Dev": {"yt": "https://www.youtube.com/@codeborn-dev/videos"},
    "Codificandolo": {"yt": "https://www.youtube.com/@codificandolo/videos"},
    "Codigo Estudiante": {"yt": "https://www.youtube.com/@codigoestudiante/videos"},
    "Consejos C#": {"yt": "https://www.youtube.com/@ConsejosCSharp/videos"},
    "Contando Bits": {"yt": "https://www.youtube.com/@ContandoBits/videos"},
    "Control 3D": {"yt": "https://www.youtube.com/@Control3D/videos"},
    "Cristian Torres": {"yt": "https://www.youtube.com/@krizalfaro/videos"},
    "d3vcloud": {"yt": "https://www.youtube.com/@d3vcloud/videos"},
    "Daniel Diaz": {"yt": "https://www.youtube.com/@DanielDiazGranizo/videos"},
    "DanieloTech": {"yt": "https://www.youtube.com/@danielotech/videos"},
    "DesarrolloWeb.com": {"yt": "https://www.youtube.com/@deswebcom/videos"},
    "DesignCourse": {"yt": "https://www.youtube.com/@DesignCourse/videos"},
    "Devon Crawford": {"yt": "https://www.youtube.com/@DevonCrawford/videos"},
    "diegoveloper": {"yt": "https://www.youtube.com/@diegoveloper/videos"},
    "DistroTube": {"yt": "https://www.youtube.com/@DistroTube/videos"},
    "Domingo Gomes": {"yt": "https://www.youtube.com/@new3sc/videos"},
    "dotnet": {"yt": "https://www.youtube.com/@dotnet/videos"},
    "Enrique Dans": {"yt": "https://www.youtube.com/@edans/videos"},
    "FalconMasters": {"yt": "https://www.youtube.com/@FalconMasters/videos"},
    "Fazt Code": {"yt": "https://www.youtube.com/@FaztCode/videos"},
    "Fernando Herrera": {"yt": "https://www.youtube.com/@fernando_her85/videos"},
    "freeCodeCamp Español": {"yt": "https://www.youtube.com/@freecodecampes/videos"},
    "GitHub": {"yt": "https://www.youtube.com/@GitHub/videos"},
    "Google": {"yt": "https://www.youtube.com/@Google/videos"},
    "GoogleDoodles": {"yt": "https://www.youtube.com/@googledoodles/videos"},
    "grenasfrijolito": {"yt": "https://www.youtube.com/@grenasfrijolito/videos"},
    "Guillermo Garcia": {"yt": "https://www.youtube.com/@GuillermoGarcia46840/videos"},
    "Hallden": {"yt": "https://www.youtube.com/@Hallden_/videos"},
    "Hdeleon Clips": {"yt": "https://www.youtube.com/@hdeleonClips/videos"},
    "hdeleon.net": {"yt": "https://www.youtube.com/@hdeleonnet/videos"},
    "IA con Daniel": {"yt": "https://www.youtube.com/@IAconDaniel/videos"},
    "IAmTimCorey": {"yt": "https://www.youtube.com/@IAmTimCorey/videos"},
    "Ildefonso Segura Tutoriales": {"yt": "https://www.youtube.com/@ildefonsosegura/videos"},
    "IndevError": {"yt": "https://www.youtube.com/@IndevError/videos"},
    "Informatic.com": {"yt": "https://www.youtube.com/@ProgramaInformatic/videos"},
    "Informática DP": {"yt": "https://www.youtube.com/@informaticadp/videos"},
    "Internet no pesa nada": {"yt": "https://www.youtube.com/@internetnopesanada/videos"},
    "JD Productions HD": {"yt": "https://www.youtube.com/@MrJDTutoriales/videos"},
    "Jerry Sawhney": {"yt": "https://www.youtube.com/@Innovativecoder/videos"},
    "Jesse Dietrichson": {"yt": "https://www.youtube.com/@JesseDietrichson/videos"},
    "Jesus Luque Medina": {"yt": "https://www.youtube.com/@JesusLuqueMedina/videos"},
    "Jorebza": {"yt": "https://www.youtube.com/@Jorebza/videos"},
    "Jose Maria Alonso": {"yt": "https://www.youtube.com/@MalignoAlonso/videos"},
    "jotajotavm": {"yt": "https://www.youtube.com/@jotajotavm/videos"},
    "JustDjango": {"yt": "https://www.youtube.com/@justdjango/videos"},
    "Kala360Gamer": {"yt": "https://www.youtube.com/@Kala360Gamer/videos"},
    "Karan Kumar": {"yt": "https://www.youtube.com/@krn-751/videos"},
    "Kiko Palomares": {"yt": "https://www.youtube.com/@kikopalomares/videos"},
    "Leigh en Español": {"yt": "https://www.youtube.com/@LeighenEspañol/videos"},
    "Leonidas Esteban": {"yt": "https://www.youtube.com/@LeonidasEsteban/videos"},
    "LinuxScoop": {"yt": "https://www.youtube.com/@linuxscoop/videos"},
    "linuxware": {"yt": "https://www.youtube.com/@iqpi18/videos"},
    "Luis Cambra": {"yt": "https://www.youtube.com/@LuisCambraps/videos"},
    "Make it Real": {"yt": "https://www.youtube.com/@MakeitrealCamp1/videos"},
    "makigas": {"yt": "https://www.youtube.com/@makigas/videos"},
    "ManzDev": {"yt": "https://www.youtube.com/@ManzDev/videos"},
    "Martín Gesualdo": {"yt": "https://www.youtube.com/@migesualdo/videos"},
    "Microsoft Developer": {"yt": "https://www.youtube.com/@MicrosoftDeveloper/videos"},
    "Microsoft IoT Developers": {"yt": "https://www.youtube.com/@MicrosoftIoTDevelopers/videos"},
    "midulive": {"yt": "https://www.youtube.com/@midulive/videos"},
    "Migma": {"yt": "https://www.youtube.com/@xMigma/videos"},
    "Moldeo Interactive": {"yt": "https://www.youtube.com/@moldeointeractive/videos"},
    "MoureDev TV": {"yt": "https://www.youtube.com/@mouredevtv/videos"},
    "Mr. Resumen": {"yt": "https://www.youtube.com/@MrResumen/videos"},
    "Mundos Apple Pro": {"yt": "https://www.youtube.com/@MundosApplePro/videos"},
    "Món de llengua - Dr. Zalbidea": {"yt": "https://www.youtube.com/@Móndellengua-Dr.Zalbidea/videos"},
    "NASeros": {"yt": "https://www.youtube.com/@naseros/videos"},
    "Nekszer": {"yt": "https://www.youtube.com/@NEKSZER/videos"},
    "nicobytes": {"yt": "https://www.youtube.com/@nicobytes/videos"},
    "No es Brujería, es Tecnología": {"yt": "https://www.youtube.com/@brujeriatech/videos"},
    "Noticias Tech y ya!": {"yt": "https://www.youtube.com/@NoticiasTechyya/videos"},
    "Octarine Code": {"yt": "https://www.youtube.com/@OctarineCode/videos"},
    "Online Tutorials": {"yt": "https://www.youtube.com/@OnlineTutorialsYT/videos"},
    "PhoneGapSpain": {"yt": "https://www.youtube.com/@PhoneGapSpain/videos"},
    "Pildoras de programación": {"yt": "https://www.youtube.com/@pildorasdeprogramacion/videos"},
    "pildorasinformaticas": {"yt": "https://www.youtube.com/@pildorasinformaticas/videos"},
    "Pirple": {"yt": "https://www.youtube.com/@Pirple/videos"},
    "Platzi": {"yt": "https://www.youtube.com/@Platzi/videos"},
    "Programación en español": {"yt": "https://www.youtube.com/@programacion-es/videos"},
    "Programming w/ Professor Sluiter": {"yt": "https://www.youtube.com/@shadsluiter/videos"},
    "Programming with Mosh": {"yt": "https://www.youtube.com/@programmingwithmosh/videos"},
    "React-Native by Wilhelm": {"yt": "https://www.youtube.com/@reactuikit/videos"},
    "Ready Set Click": {"yt": "https://www.youtube.com/@readysetclick9870/videos"},
    "render2web": {"yt": "https://www.youtube.com/@render2web/videos"},
    "RobotSolar": {"yt": "https://www.youtube.com/@robotsolar7783/videos"},
    "Sergio Alejandro Campos - EXCELeINFO": {"yt": "https://www.youtube.com/@SergioAlejandroCampos/videos"},
    "Simon Grimm": {"yt": "https://www.youtube.com/@galaxies_dev/videos"},
    "Sin Rueda Tecnológica": {"yt": "https://www.youtube.com/@sinruedatecnologica/videos"},
    "Software Lion": {"yt": "https://www.youtube.com/@softwarelion-oficial/videos"},
    "Sonfil": {"yt": "https://www.youtube.com/@Sonfil/videos"},
    "Sonny Sangha": {"yt": "https://www.youtube.com/@SonnySangha/videos"},
    "Sosteniblevida": {"yt": "https://www.youtube.com/@Sosteniblevida/videos"},
    "Soy Dalto": {"yt": "https://www.youtube.com/@soydalto/videos"},
    "subelealruido": {"yt": "https://www.youtube.com/@subelealruido/videos"},
    "Super Excel": {"yt": "https://www.youtube.com/@super-excel/videos"},
    "Tech Point Fundamentals": {"yt": "https://www.youtube.com/@TechPointFundamentals/videos"},
    "TechHut": {"yt": "https://www.youtube.com/@TechHut/videos"},
    "TecnoBinaria": {"yt": "https://www.youtube.com/@Tecnobinaria/videos"},
    "TecnoXplora": {"yt": "https://www.youtube.com/@TecnoXplora/videos"},
    "TEDx Talks": {"yt": "https://www.youtube.com/@TEDx/videos"},
    "The Coder Cave | Programación y Tecnología": {"yt": "https://www.youtube.com/@TheCoderCave/videos"},
    "TIFF Trailers": {"yt": "https://www.youtube.com/@TIFFTrailers/videos"},
    "Toni Dev": {"yt": "https://www.youtube.com/@tonidev_/videos"},
    "Topes de Gama": {"yt": "https://www.youtube.com/@TopesdeGama/videos"},
    "Tu Area De Informatica": {"yt": "https://www.youtube.com/@TuAreaDeInformatica/videos"},
    "tutorialesJJ": {"yt": "https://www.youtube.com/@tutorialesJJ/videos"},
    "tutorialsEU": {"yt": "https://www.youtube.com/@tutorialsEU/videos"},
    "Unity": {"yt": "https://www.youtube.com/@unity/videos"},
    "Victor Abarca": {"yt": "https://www.youtube.com/@VictorAbarca/videos"},
    "Vida MRR - Programacion web": {"yt": "https://www.youtube.com/@vidamrr/videos"},
    "Video Tutoriales Android": {"yt": "https://www.youtube.com/@VideoTutorialesAndroidMovil/videos"},
    "Web Dev Simplified": {"yt": "https://www.youtube.com/@WebDevSimplified/videos"},
    # ── Tech news ──
    "ZDNet": {"url": "https://www.zdnet.com/topic/artificial-intelligence/", "selector": "article h3 a"},
    "CNET": {"url": "https://www.cnet.com/tech/", "selector": "a[class*='title']"},
    "Android Authority": {"url": "https://www.androidauthority.com/", "selector": "h3 a"},
    "The Next Web": {"url": "https://thenextweb.com/topic/artificial-intelligence", "selector": "article h2 a"},
    "InfoWorld": {"url": "https://www.infoworld.com/category/artificial-intelligence/", "selector": "article a[href]"},
    # ── Blogs de desarrollo ──
    "LogRocket": {"url": "https://blog.logrocket.com/", "selector": "a[class*='card']"},
    "Smashing Magazine": {"url": "https://www.smashingmagazine.com/articles/", "selector": "article h2 a"},
    "CSS-Tricks": {"url": "https://css-tricks.com/", "selector": "article h2 a"},
    "freeCodeCamp": {"url": "https://www.freecodecamp.org/news/", "selector": "article h2 a"},
    "DigitalOcean": {"url": "https://www.digitalocean.com/blog", "selector": "a[class*='blog-card'] h3"},
    # ── Fuentes de modelos de IA ──
    "MiniMax": {"url": "https://minimax.io/blog", "selector": "a[href*='/blog/']"},
    "DeepSeek": {"url": "https://deepseek.com/blog", "selector": "article h2 a"},
    "Qwen": {"url": "https://qwen.readthedocs.io/en/latest/", "selector": "article h2 a"},
    "AI21 Labs": {"url": "https://www.ai21.com/blog", "selector": "article h2 a"},
    # ── Más fuentes IA y tecnología ──
    "The Decoder": {"url": "https://the-decoder.com/", "selector": "article a[href]"},
    "MarkTechPost": {"url": "https://www.marktechpost.com/", "selector": "h3 a[href]"},
    "LinkedIn Engineering": {"url": "https://engineering.linkedin.com/blog", "selector": ".post-title a"},
    "Facebook Engineering": {"url": "https://engineering.fb.com/", "selector": "article a[href]"},
    # ── Noticias IA: herramientas, modelos, comparativas ──
    "AI Bytes": {"url": "https://aibytes.blog/", "selector": "article a[href]", "quick": True, "tipo": "noticia"},
    "ToolChase": {"url": "https://toolchase.com/blog/", "selector": "a[href*='/blog/']", "quick": True, "tipo": "noticia"},
    "ThePlanetTools": {"url": "https://theplanettools.ai/", "selector": "a[class*='card']", "quick": True, "tipo": "noticia"},
    "CompareThe.ai": {"url": "https://www.comparethe.ai/blog", "selector": "a[href*='/blog/']", "quick": True, "tipo": "noticia"},
    "YourAIChoice": {"url": "https://youraichoice.com/", "selector": "article h2 a, h3 a", "quick": True, "tipo": "noticia"},
    "DeeperInsights": {"url": "https://deeperinsights.com/ai-review/", "selector": "a[class*='card']", "quick": True, "tipo": "noticia"},
    "AI Weekly": {"url": "https://aiweekly.co/", "selector": "h2 a", "quick": True, "tipo": "noticia"},
    "NeelsWorld": {"url": "https://neelsworld.in/", "selector": "article h2 a, h3 a", "quick": True, "tipo": "noticia"},
    "CleverAI": {"url": "https://cleverai.app/es/blog", "selector": "article a[href]", "quick": True, "tipo": "noticia"},
    "IA News": {"url": "https://ia-news.es/", "selector": ".card a[href]", "quick": True, "tipo": "noticia"},
    "DonWeb IA": {"url": "https://blog.donweb.com/ia-todos-lados-2026/", "selector": "article a[href]", "quick": True, "tipo": "noticia"},

    # ── Fuentes RSS (lectores XML) [quick: True → tier light] ──
    "GitHub Engineering": {"rss": "https://github.blog/engineering/feed/", "quick": True},
    "Stack Overflow Blog": {"rss": "https://stackoverflow.blog/feed/", "quick": True},
    "Hacker News": {"rss": "https://hnrss.org/frontpage", "quick": True},
    "Google AI Blog": {"rss": "https://blog.google/technology/ai/rss/", "quick": True},
    "MIT Tech Review AI": {"rss": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "quick": True},
    "Google Search Central": {"rss": "https://developers.google.com/search/blog/feed.xml", "quick": True},
    "Moz Blog SEO": {"rss": "https://moz.com/blog/feed.xml", "quick": True},
    "Search Engine Journal": {"rss": "https://www.searchenginejournal.com/feed/", "quick": True},
    "Wired AI": {"rss": "https://www.wired.com/feed/rss", "quick": True},
    "TechCrunch AI": {"rss": "https://techcrunch.com/category/artificial-intelligence/feed/", "quick": True},
    "Ars Technica AI": {"rss": "https://feeds.arstechnica.com/arstechnica/index", "quick": True},
    "Dev.to": {"rss": "https://dev.to/feed", "quick": True},
    # ── IA empresas: web scraping (sin RSS) ──
    "Anthropic Research": {"url": "https://www.anthropic.com/research", "selector": "a[href*='/research/']", "tipo": "noticia", "quick": True},
    "Ollama Blog": {"url": "https://ollama.com/blog", "selector": "a[href^='/blog/'] h2", "tipo": "noticia", "quick": True},
    "Mistral News": {"url": "https://mistral.ai/news", "selector": "a[href^='/news/']", "tipo": "noticia", "quick": True},
    "Cohere Blog": {"url": "https://cohere.com/blog", "selector": "a[href*='/blog/']", "tipo": "noticia", "quick": True},
    "LangChain Blog": {"url": "https://blog.langchain.dev", "selector": "a[href*='/p/'] h2, a[href*='/p/'] h3", "tipo": "noticia", "quick": True},
    "Google Developers Blog": {"url": "https://developers.googleblog.com/en/", "selector": ".post-item__link, a.glue-carousel__item", "tipo": "noticia", "quick": True},
    "HuggingFace Papers": {"url": "https://huggingface.co/papers", "selector": "article a", "tipo": "noticia", "quick": True},
    "Mozilla Hacks": {"url": "https://hacks.mozilla.org", "selector": "h3.post__title a", "tipo": "noticia", "quick": True},
    # ── IA China: RSS + web scraping ──
    "量子位 (QbitAI)": {"rss": "https://www.qbitai.com/feed", "quick": True},
    "36氪 AI": {"rss": "https://36kr.com/feed", "quick": True},
    "Qwen Blog": {"url": "https://qwen.ai/blog", "selector": "article h2, .post h2", "tipo": "noticia", "quick": True},
    "DeepSeek Blog": {"url": "https://api-docs.deepseek.com/", "selector": "article a[href]", "tipo": "noticia", "quick": True},
    "01.AI News": {"url": "https://01.ai/", "selector": ".news-item a, a[href*='news']", "tipo": "noticia", "quick": True},
    "THUDM ChatGLM": {"rss": "https://github.com/zai-org/ChatGLM3/releases.atom", "quick": True},
    # ── Noticias tech y general ──
    "Business Insider Big Tech": {"rss": "https://www.businessinsider.es/rss/big-tech/", "url": "https://www.businessinsider.es/big-tech/", "selector": "article h2 a", "quick": True, "tipo": "noticia"},
    "Business Insider Tecnología": {"rss": "https://www.businessinsider.es/rss/tecnologia/", "url": "https://www.businessinsider.es/tecnologia/", "selector": "article h2 a", "quick": True, "tipo": "noticia"},
    "Hipertextual": {"rss": "https://hipertextual.com/feed/", "quick": True},
    "ADSL Zone": {"rss": "https://www.adslzone.net/feed", "quick": True},
    "MuyComputer": {"rss": "https://www.muycomputer.com/feed/", "quick": True},
    "The Verge": {"rss": "https://www.theverge.com/rss/index.xml", "quick": True},
    "TechCrunch": {"rss": "https://techcrunch.com/feed/", "quick": True},
    "Wired": {"rss": "https://www.wired.com/feed/rss", "quick": True},
    "Ars Technica": {"rss": "https://feeds.arstechnica.com/arstechnica/index", "quick": True},
    "Engadget": {"rss": "https://www.engadget.com/rss.xml", "quick": True},
    "ZDNet": {"rss": "https://www.zdnet.com/news/rss.xml", "quick": True},
    "CNET": {"rss": "https://www.cnet.com/rss/news/", "quick": True},
    "Tom's Hardware": {"rss": "https://www.tomshardware.com/feeds/all", "quick": True},
    # ── Google, Apple, Microsoft ──
    "Google Blog": {"rss": "https://blog.google/rss/", "quick": True},
    "Apple Newsroom": {"rss": "https://www.apple.com/newsroom/rss-feed.rss", "quick": True},
    "Microsoft Dev Blog": {"rss": "https://devblogs.microsoft.com/feed/", "quick": True},
    # ── Astro framework ──
    "Astro Blog": {"url": "https://astro.build/blog/", "selector": "a[href^='/blog/']", "tipo": "noticia", "quick": True},
    "Astro GitHub Releases": {"rss": "https://github.com/withastro/astro/releases.atom", "quick": True},
    # ── Software libre y Open Source ──
    "Phoronix": {"rss": "https://www.phoronix.com/rss.php", "quick": True},
    "OMG Ubuntu": {"rss": "https://www.omgubuntu.co.uk/feed", "quick": True},
    "It's FOSS": {"rss": "https://itsfoss.com/feed/", "quick": True},
    "Docker Blog": {"rss": "https://www.docker.com/blog/feed/", "quick": True},
    "Kubernetes Blog": {"rss": "https://kubernetes.io/feed.xml", "quick": True},
    # ── Sandbox, herramientas IA, infraestructura ──
    "Vercel Blog": {"rss": "https://vercel.com/atom", "quick": True},
    "Cloudflare Blog": {"rss": "https://blog.cloudflare.com/rss/", "quick": True},
    "Railway Blog": {"rss": "https://blog.railway.app/rss.xml", "quick": True},
    # ── AI Research / Papers ──
    "AI Alignment Forum": {"rss": "https://www.alignmentforum.org/feed.xml", "quick": True},
    "LessWrong AI": {"rss": "https://www.lesswrong.com/feed.xml", "quick": True},
    "Machine Learning Mastery": {"rss": "https://machinelearningmastery.com/feed/", "quick": True},
    "NVIDIA Developer Blog": {"rss": "https://developer.nvidia.com/blog/feed/", "quick": True},
    # ── Seguridad y DevOps ──
    "Krebs on Security": {"rss": "https://krebsonsecurity.com/feed/", "quick": True},
    "The Hacker News": {"rss": "https://feeds.feedburner.com/TheHackersNews", "quick": True},
    "SANS ISC": {"rss": "https://isc.sans.edu/rssfeed.xml", "quick": True},
    "HashiCorp Blog": {"rss": "https://www.hashicorp.com/blog/feed.xml", "quick": True},
    # ── Fuentes de herramientas ──
    "GitHub Trending": {"url": "https://github.com/trending", "tipo": "herramienta", "subtipo": "github", "selector": "article a[href]"},
    # ── Noticias IA: RSS feeds ──
    "The Decoder RSS": {"rss": "https://the-decoder.com/feed/", "quick": True},
    "MarkTechPost RSS": {"rss": "https://www.marktechpost.com/feed/", "quick": True},
    "VentureBeat AI RSS": {"rss": "https://venturebeat.com/category/ai/feed/", "quick": True},
    "AI News": {"rss": "https://www.artificialintelligence-news.com/feed/", "quick": True},
    "Towards AI": {"rss": "https://pub.towardsai.net/feed", "quick": True},
    "Analytics India Magazine": {"rss": "https://analyticsindiamag.com/feed/", "quick": True},
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="author" content="Jorge Beneyto Castelló">
    <meta name="description" content="Tech Pulse Dashboard — Resumen inteligente de noticias tech, v\u00eddeos y contenido curado por Jorge Beneyto Castell\u00f3. Actualizado diariamente con IA.">
    <meta property="og:title" content="Tech Pulse Dashboard — Jorge Beneyto Castell\u00f3">
    <meta property="og:description" content="Dashboard de tecnolog\u00eda con resumen IA, filtros por canal y fecha, v\u00eddeos y shorts de YouTube. Curado por Jorge Beneyto Castell\u00f3.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://jorbencasdownloaderdocument.surge.sh">
    <meta property="og:site_name" content="Tech Pulse Dashboard">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@jorbencas">
    <meta name="twitter:creator" content="@jorbencas">
    <meta id="api-base-token" content="{downloader_api_token}">
    <link rel="canonical" href="https://jorbencasdownloaderdocument.surge.sh">
    <link rel="stylesheet" href="styles.css">
    <title>Tech Pulse Dashboard — Jorge Beneyto Castell\u00f3</title>
    <script type="application/ld+json">
    {{
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "Tech Pulse Dashboard",
        "url": "https://jorbencasdownloaderdocument.surge.sh",
        "author": {{
            "@type": "Person",
            "name": "Jorge Beneyto Castell\u00f3",
            "url": "https://github.com/jorbencas"
        }},
        "description": "Dashboard de tecnolog\u00eda con resumen IA, filtros por canal y fecha, v\u00eddeos y shorts de YouTube."
    }}
    </script>
</head>
<body>
    <div class="container">
        <header>
            <h1 class="header-gradient">Tech Pulse</h1>
            <div style="display:flex;align-items:center;gap:12px;">
                <button id="theme-toggle" class="theme-toggle" aria-label="Cambiar tema">🌙</button>
                <picture>
                    <source srcset="optimizado/Image.avif" type="image/avif">
                    <source srcset="optimizado/Image.webp" type="image/webp">
                    <img src="optimizado/Image.png" alt="Tech Pulse Dashboard Logo" class="logo" width="120" height="40" style="aspect-ratio: 3/1; object-fit: contain;" loading="eager">
                </picture>
            </div>
        </header>

        <div id="stats-bar" class="stats-bar">{stats_html}</div>

        <h2>\U0001f4f0 Noticias</h2>
        <div class="filter-section">
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
                <strong>\U0001f50d Buscar:</strong>
                {news_search_html}
            </div>
        </div>
        <details class="filter-collapse" open>
            <summary>\U0001f310 Webs</summary>
            <div id="news-channel-filters" class="chip-container">{news_channel_filters_html}</div>
        </details>
        <ul id="news-list" class="news-list">{news_list_html}</ul>

        <h2>\U0001f3ac Multimedia</h2>
        <div class="filter-section" id="multimedia-filter-section">
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
                <strong>\U0001f50d Buscar:</strong>
                {video_search_html}
            </div>
        </div>
        <details class="filter-collapse" open>
            <summary>\U0001f4fa Filtro Canal</summary>
            <div id="video-channel-filters" class="chip-container">{video_channel_filters_html}</div>
        </details>
        <div class="chip-container" id="multimedia-tabs">{multimedia_tabs_html}</div>
        <div id="multimedia-content" class="video-grid">{multimedia_content_html}</div>

        <h2>\u2b50 Ranking GitHub Stars</h2>
        <div class="filter-section">
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
                <strong>\U0001f524 Buscar:</strong>
                <input type="text" id="github-filter" class="search-input" placeholder="Buscar por nombre o lenguaje...">
            </div>
        </div>
        <div id="github-ranking">{github_ranking_html}</div>


        <footer class="site-footer">
            <p>Creado con <span class="footer-heart">❤️</span> y sin ánimo de lucro por <a href="https://github.com/jorbencas" target="_blank" rel="noopener">@jorbencas</a></p>
            <p class="footer-disclaimer">Este sitio no almacena, aloja ni se atribuye la propiedad de ningún contenido externo. Simplemente enlaza y muestra fragmentos de fuentes públicas con fines informativos y educativos. Cada pieza de contenido pertenece a su legítimo autor o medio original.</p>
        </footer>
    </div>
</body>
<script src="script.js"></script>
</html>
"""

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="color-scheme" content="light dark">
    <meta name="supported-color-schemes" content="light dark">
    <title>Tech Pulse Newsletter</title>
    <style>
        :root {{
            color-scheme: light dark;
            supported-color-schemes: light dark;
        }}
        @media only screen and (max-width: 620px) {{
            .container {{ width: 100% !important; margin: 0 !important; border-radius: 0 !important; }}
            .content {{ padding: 20px !important; }}
            .stat-cell {{ display: block !important; width: 100% !important; border: none !important; padding: 10px 0 !important; }}
            .stat-border {{ border: none !important; border-top: 1px solid #e2e8f0 !important; border-bottom: 1px solid #e2e8f0 !important; }}
            .stat-table {{ padding: 12px !important; }}
            .header-cell {{ padding: 28px 24px 16px 24px !important; }}
            .hide-mobile {{ display: none !important; }}
        }}
        @media (prefers-color-scheme: dark) {{
            .dark-bg {{ background-color: #1e293b !important; }}
            .dark-card {{ background-color: #0f172a !important; border-color: #334155 !important; }}
            .dark-text {{ color: #f1f5f9 !important; }}
            .dark-text-secondary {{ color: #94a3b8 !important; }}
            .dark-border {{ border-color: #334155 !important; }}
            .dark-stats {{ background-color: #0f172a !important; border-color: #334155 !important; }}
            .dark-ia-box {{ background-color: #1e293b !important; border-color: #334155 !important; }}
            .dark-footer {{ background-color: #0f172a !important; border-color: #334155 !important; }}
            a {{ color: #818cf8 !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background: linear-gradient(180deg, #f0f4f8 0%, #e8edf3 100%); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    
    <div style="display: none; max-height: 0px; overflow: hidden;">
        {total_noticias} noticias tech · {count_tech} tech · resumen generado por IA · {temas_clave}
    </div>

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="container dark-card" style="max-width: 600px; background-color: #ffffff; margin: 30px auto; border-radius: 12px; box-shadow: 0 4px 24px rgba(15, 23, 42, 0.08); overflow: hidden; border: 1px solid #e2e8f0;">
        
        <!-- Header -->
        <tr>
            <td class="header-cell" style="padding: 0; text-align: left;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 36px 40px 28px 40px;">
                    <tr>
                        <td style="vertical-align: middle; padding: 36px 40px 28px 40px;">
                            <p style="margin: 0; font-size: 11px; font-weight: 700; color: #94a3b8; text-transform: uppercase; letter-spacing: 2px;">EDICIÓN DIARIA</p>
                            <h1 style="color: #f8fafc; margin: 6px 0 0 0; font-size: 34px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1;">Tech Pulse</h1>
                            <div style="height: 3px; width: 48px; background: linear-gradient(90deg, #3b82f6, #8b5cf6); margin: 16px 0 0 0; border-radius: 2px;"></div>
                            <p style="color: #94a3b8; margin: 14px 0 0 0; font-size: 14px; font-weight: 500;">{fecha_hoy}</p>
                        </td>
                        <td width="80" class="hide-mobile" style="vertical-align: middle; text-align: right; padding: 36px 40px 28px 0;">
                            <span style="display: inline-block; background: rgba(59,130,246,0.15); color: #60a5fa; font-size: 10px; font-weight: 700; padding: 5px 12px; border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase; border: 1px solid rgba(59,130,246,0.2);">IA</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <!-- Stats -->
        <tr>
            <td class="content" style="padding: 24px 40px 0 40px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" class="stat-table dark-stats" style="background: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0; padding: 16px; text-align: center;">
                    <tr>
                        <td width="33%" class="stat-cell" style="vertical-align: top; padding: 14px 8px;">
                            <b style="font-size: 24px; color: #3b82f6; font-weight: 800;">{count_tech}</b><br>
                            <span style="font-size: 11px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.3px;">Tech</span>
                        </td>
                        <td width="33%" class="stat-cell" style="vertical-align: top; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0; padding: 14px 8px;">
                            <b style="font-size: 24px; color: #ef4444; font-weight: 800;">{total_noticias}</b><br>
                            <span style="font-size: 11px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.3px;">Total</span>
                        </td>
                        <td width="33%" class="stat-cell" style="vertical-align: top; padding: 14px 8px;">
                            <b style="font-size: 24px; color: #8b5cf6; font-weight: 800;">IA</b><br>
                            <span style="font-size: 11px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.3px;">Gemini</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- AI Summary -->
        <tr>
            <td class="content" style="padding: 28px 40px 10px 40px;">
                <h2 style="color: #0f172a; font-size: 16px; font-weight: 700; margin: 0 0 14px 0;">
                    <span style="margin-right: 6px;">🤖</span> Resumen del día
                    <span class="hide-mobile" style="margin-left: auto; font-size: 9px; font-weight: 600; color: #94a3b8; background: #f1f5f9; padding: 3px 8px; border-radius: 4px; vertical-align: middle;">Gemini</span>
                </h2>
                <div style="line-height: 1.7; color: #334155; font-size: 14px; background: #fafbfc; padding: 20px 24px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 4px solid #3b82f6;">
                    {contenido_html}
                </div>
            </td>
        </tr>

        <!-- News list -->
        <tr>
            <td class="content" style="padding: 20px 40px 32px 40px;">
                <h2 style="color: #0f172a; font-size: 16px; font-weight: 700; margin: 0 0 14px 0; padding-bottom: 10px; border-bottom: 2px solid #f1f5f9;">
                    <span style="margin-right: 6px;">📋</span> Lecturas seleccionadas
                </h2>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    {lista_email}
                </table>
            </td>
        </tr>

        <!-- Videos section -->
        <tr>
            <td class="content" style="padding: 0 40px 32px 40px;">
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    {videos_html}
                </table>
            </td>
        </tr>

        <!-- Footer -->
        <tr>
            <td class="content dark-footer" style="padding: 0; background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%); border-top: 1px solid #e2e8f0;">
                
                <!-- CTA Button -->
                <table width="100%" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding: 28px 40px 20px 40px; text-align: center;">
                            <table border="0" cellpadding="0" cellspacing="0" align="center">
                                <tr>
                                    <td align="center" bgcolor="#3b82f6" style="border-radius: 8px; background: linear-gradient(135deg, #3b82f6, #2563eb);">
                                        <a href="http://jorbencasdownloaderdocument.surge.sh" target="_blank" style="font-size: 13px; font-weight: 700; color: #ffffff; text-decoration: none; display: inline-block; padding: 12px 24px; letter-spacing: 0.3px;">
                                            Abrir Dashboard →
                                        </a>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>

                <!-- Credits -->
                <table width="100%" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding: 16px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="font-size: 12px; color: #94a3b8; margin: 0; line-height: 1.5;">
                                Compilada automáticamente con <strong style="color: #64748b;">Gemini IA</strong> · Preparada para <strong style="color: #64748b;">Jorge Beneyto Castelló</strong>
                            </p>
                            <p style="font-size: 11px; color: #cbd5e1; margin: 10px 0 0 0;">
                                &copy; {year} Tech Pulse Briefing · 
                                <a href="https://blog-jorbencas.vercel.app/" target="_blank" style="color: #94a3b8; text-decoration: none;">Blog</a> · 
                                <a href="https://github.com/jorbencas/test_githubActions" target="_blank" style="color: #94a3b8; text-decoration: none;">Código</a>
                            </p>
                        </td>
                    </tr>
                </table>

            </td>
        </tr>
    </table>
</body>
</html>
"""



MD_TEMPLATE = """---
title: "{titulo}"
description: "{description}"
pubDate: "{fecha_iso}"
author: "{author}"
image: "{ruta_imagen}"
tags: {tags}
slug: "{slug_name}"
draft: true
readingTime: {tiempo_lectura}
categories: ["tech", "weekly-recap"]
---

## 🚀 Radiografía de la semana

{introduccion}

---

## 📊 La semana en números

{stats_categorias}

---

## 🔥 Lo más destacado

{bloque_noticias}

---

## 🗂️ Por categorías

{categorias_seccion}

---

## 📋 Noticias por fuente

{noticias_por_fuente}

---

## 🎬 Videos destacados

{videos_seccion}

---

### 🛠️ Herramienta o Repo de la Semana

:::tip
**[{repo_name}]({repo_url})** — {repo_desc}
:::

---

## 🏁 En 30 segundos (TL;DR)

{conclusion_tldr}

---

## 🔮 Qué esperar la próxima semana

:::warning
{sneak_peek}
:::

---

> **Nota del autor:** {nota_personal}

📡 **[Ver dashboard completo con todos los filtros](http://jorbencasdownloaderdocument.surge.sh)**
"""

# --- En constants_downloadfile.py ---
PROMPT_IMAGEN_TEMPLATE = """
Create a high-quality, professional wide-angle image (16:9 aspect ratio, 1200x630 recommended) 
representing the following concept: "{titulo_post}".
The visual style should be cinematic and futuristic, featuring a blend of clean technological elements, 
soft ambient lighting, and a depth of field that keeps the subject in focus. 
Color palette: deep digital blues, crisp white highlights, and subtle neon green accents. 
Ensure the composition is balanced and suitable for a tech article header. 
Highly detailed, photorealistic, 8k resolution, modern aesthetic, professional photography style.
IMPORTANT: Do NOT include any text, letters, numbers, labels, or watermarks in the image.
"""

# ── AI Prompts ──
PROMPT_RESUMIR_LOTE = """Eres el editor de "Tech Pulse", una newsletter tech diaria para profesionales del sector.
Escribe un párrafo de 2-3 líneas en español que introduzca los titulares de hoy.

REGLAS:
- Sé directo, sin florituras ni frases vacías
- Menciona 2-3 temas concretos (IA, programación, hardware, seguridad...)
- Si hay un tema dominante, ponlo en primera línea
- Tono: cercano pero profesional, como un colega que te cuenta lo importante

TITULARES:
{texto}

RESPONDE SOLO EL PÁRRAFO, sin intro ni etiquetas. Máx 300 caracteres."""

PROMPT_RESUMIR_NOTICIA = """Eres el editor de "Tech Pulse". Resume esta noticia en 3-4 líneas en español.

REGLAS:
1. Primera línea: qué ha ocurrido exactamente (hecho concreto, no genérico)
2. Segunda línea: por qué es relevante para un programador o profesional tech
3. Tercera línea: un dato concreto si aparece (versión, cifra, fecha)
4. Evita frases tipo "en un mundo cada vez más digital" o "la revolución de la IA"

TÍTULO: {titulo}
FUENTE: {fuente}
TEXTO:
{texto}

Responde SOLO con el resumen, sin introducciones ni etiquetas. (máx 500 caracteres)"""

PROMPT_RECAP_SEMANAL = """Eres el editor senior de "Tech Pulse", una newsletter semanal de tecnología.
Tu estilo: directo, analítico, sin hype vacío. Como Xataka mezclado con The Verge en español.
Ecribes como si le hablaras a un colega programador en una cafetería. Natural, sin preamblos.

MISSION: Analiza las noticias de la semana y genera un RECAP SEMANAL que un programador quiera leer.

═══ CONTEXTO ═══
Fecha actual: {fecha_actual}
Semana: {semana_info}

═══ NORMAS DE ESTILO (OBLIGATORIO) ═══
- Lenguaje HUMANO: como si se lo contaras a un amigo. Nada de frases de comunicado de prensa
- NUNCA uses: "En el cambiante mundo digital", "La era de la IA transforma", "En un paso revolucionario"
- Usa: "esto es lo que ha pasado", "lo que viene es interesante porque...", "aquí va lo gordo"
- Asume que el lector ya sabe qué es OpenAI, Docker o Kubernetes
- Si una noticia es solo marketing, dilo ("mucho ruido, pocas nueces")
- Sé específico: nombres, versiones, cifras concretas
- Conecta temas: si OpenAI y Google sacan algo similar, agrúpalos
- La introducción debe ser ÚNICA cada semana. NO repitas estructura de semanas anteriores
- Si hay una efeméride, festividad o evento especial esta semana, menciónalo de forma natural en la introducción (ej: "Entre Navidades y el CES...", "Para cerrar el año...", "Semana de descanso pero la IA no para...")
- La primera frase debe enganchar: puede ser una pregunta, un dato impactante, o una observación directa
- Varía el tono: una semana puede ser más serio, otra más casual. NO seas monótono

═══ NOTICIAS DE LA SEMANA (AGRUPADAS POR CATEGORÍA) ═══

{resumen_cats}

Total noticias RSS: {total_rss}

{texto_noticias}

═══ INSTRUCCIONES DE SALIDA ═══

Genera un JSON con esta estructura EXACTA:

{{
  "introduccion": "Párrafo de 4-6 líneas. Tono HUMANO y natural. Primera frase: gancho único (pregunta, dato impactante, o referencia al momento del año si aplica). Luego conecta 2-3 tendencias clave. Si hay efeméride/festividad esta semana, inclúyela de forma orgánica. NUNCA empieces con 'Esta semana en tecnología...' (max 700 chars)",
  "noticias_destacadas": [
    {{
      "titulo": "Título descriptivo + categoría entre paréntesis (ej: 'GPT-5: OpenAI supera expectativas (🤖 IA)')",
      "suceso": "Qué ocurrió con datos concretos: nombres, versiones, cifras. 2-3 líneas. Tono conversacional. (max 300 chars)",
      "impacto": "Por qué importa AHORA. Conecta con tendencias del sector. Como si se lo explicaras a un colega. (max 300 chars)",
      "categoria": "🤖 IA" o "💻 Programación" o "🔒 Seguridad" o "📊 Negocios" o "🎓 General" o "💡 Otro"
    }}
  ],
  "repo": {{
    "nombre": "Nombre del repo/herramienta más interesante de la semana",
    "url": "URL del repo (de preferencia uno de las noticias o de GitHub Trending)",
    "desc": "Qué problema resuelve y por qué debería probarlo. 1-2 frases, tono recomendación de colega."
  }},
  "tldr": [
    "Punto 1: tema principal + contexto (max 160 chars)",
    "Punto 2: segunda tendencia + dato concreto (max 160 chars)",
    "Punto 3: herramienta/repo destacado (max 160 chars)",
    "Punto 4: seguridad/privacidad + qué hacer (max 160 chars)",
    "Punto 5: negocio/inversión + cifra (max 160 chars)",
    "Punto 6: preview de lo que viene (max 160 chars)"
  ],
  "tags": ["tech", "weekly-recap", "tag_tema_principal", "tag_tema2", "tag_tema3", "tag_tema4", "tag_fuente_top1", "tag_fuente_top2"],
  "categorias_resumen": {{
    "🤖 IA": "Resumen de 1-2 líneas de lo más relevante en IA esta semana",
    "💻 Programación": "Resumen de 1-2 líneas de lo más relevante en programación",
    "🔒 Seguridad": "Resumen de 1-2 líneas de lo más relevante en seguridad",
    "📊 Negocios": "Resumen de 1-2 líneas de lo más relevante en negocios tech",
    "🎓 General": "Resumen de 1-2 líneas de lo más relevante en general"
  }},
  "sneak_peek": "Predicción concreta basada en lo visto esta semana. Tono: como le dijeras a un colega lo que viene. (max 350 chars)",
  "nota_personal": "Reflexión genuina como si se lo dijeras a un colega tomando un café. Menciona algo que te sorprendió o un aprendizaje real. (max 320 chars)"
}}

REGLAS PARA tags:
- Siempre incluir "tech" y "weekly-recap"
- Añadir 4-6 tags descriptivos de los temas principales (ej: "openai", "docker", "rust", "ciberseguridad", "llm", "devops")
- Añadir 1-2 tags de las fuentes más activas (ej: "xataka", "genbeta")
- Total: 8-10 tags

REGLAS PARA categorias_resumen:
- Incluir SOLO las categorías que tengan noticias reales esta semana
- Cada resumen: 1-2 líneas con los 2-3 temas más importantes de esa categoría
- Si una categoría no tiene noticias, no incluirla

RESPONDE SOLO EL JSON, sin markdown, sin comentarios, sin explicaciones."""

PROMPT_TRADUCIR_TITULOS = """Traduce estos titulares de tecnología al español de forma profesional y natural.
Mantén nombres propios, marcas y acrónimos (OpenAI, NVIDIA, iPhone, etc.) sin traducir.
Conserva el formato "id|título" en la respuesta.
Devuelve SOLO JSON, sin markdown ni explicaciones.

TEXTO:
{texto_a_traducir}

FORMATO:
{{"traducciones": [{{"id": 0, "tr": "Título traducido 0"}}, {{"id": 1, "tr": "Título traducido 1"}}]}}"""

# ── Fallback values ──
FALLBACK_IMAGE_URL = "public/img/arquitectura_web.webp"
FALLBACK_GITHUB_IMAGE = "https://github.com/jorbencas/test_githubActions/blob/master/public/optimizado/Image.png?raw=true"
FALLBACK_SNEAK_PEEK = "Seguiremos de cerca la evolución del sector. ¡No te lo pierdas!"
FALLBACK_NOTA_PERSONAL = "Keep coding!"
FALLBACK_RECAP_INTRO = "Esta semana hemos seguido de cerca las principales tendencias en tecnología y desarrollo."

# ── Telegram ──
TELEGRAM_TTS_VOZ = "es-ES-AlvaroNeural"
TELEGRAM_DASHBOARD_URL = "http://jorbencasdownloaderdocument.surge.sh"
TELEGRAM_MENSAJE_TEMPLATE = "{icono} *{titulo}*\n📰 `{fuente}` | `{fecha}`\n\n{cuerpo}\n🔗 [Abrir noticia]({enlace})\n🌐 [Ver más en el Dashboard]({dashboard_url})"

# ── Email ──
EMAIL_SOURCE_HEADER = """<tr>
    <td style="padding: 20px 0 8px 0;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding: 0; border-bottom: 2px solid {source_color};">
                    <span style="font-size: 12px; font-weight: 700; color: {source_color}; text-transform: uppercase; letter-spacing: 0.5px; padding-bottom: 6px; display: inline-block;">{source_icon} {source_name}</span>
                    <span style="font-size: 10px; color: #94a3b8; margin-left: 8px;">{source_count} noticias</span>
                </td>
            </tr>
        </table>
    </td>
</tr>"""

EMAIL_ROW_TEMPLATE = """<tr>
    <td style="padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="28" style="vertical-align: top; padding-top: 2px;">
                    <span style="font-size: 16px;">{icon}</span>
                </td>
                <td style="vertical-align: top; padding-left: 10px;">
                    <a href="{enlace}" target="_blank" style="color: #0f172a; text-decoration: none; font-weight: 700; font-size: 15px; line-height: 1.4;">{titulo}</a>
                    {resumen_html}
                    <div style="margin-top: 8px;">
                        <a href="{enlace}" target="_blank" style="display: inline-block; font-size: 11px; font-weight: 600; color: #3b82f6; text-decoration: none; background: #eff6ff; padding: 5px 12px; border-radius: 6px; border: 1px solid #dbeafe;">Leer noticia →</a>
                    </div>
                </td>
            </tr>
        </table>
    </td>
</tr>"""

EMAIL_VIDEO_HEADER = """<tr>
    <td style="padding: 24px 0 8px 0;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td style="padding: 0; border-bottom: 2px solid #ef4444;">
                    <span style="font-size: 12px; font-weight: 700; color: #ef4444; text-transform: uppercase; letter-spacing: 0.5px; padding-bottom: 6px; display: inline-block;">🎬 VIDEOS</span>
                    <span style="font-size: 10px; color: #94a3b8; margin-left: 8px;">{video_count} nuevos</span>
                </td>
            </tr>
        </table>
    </td>
</tr>"""

EMAIL_VIDEO_ROW = """<tr>
    <td style="padding: 10px 0; border-bottom: 1px solid #f1f5f9;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="120" style="vertical-align: top;">
                    <a href="{enlace}" target="_blank" style="text-decoration: none; display: block;">
                        <img src="{thumbnail}" width="110" height="62" style="border-radius: 6px; display: block; object-fit: cover; background: #1e293b;" alt="{titulo}">
                    </a>
                </td>
                <td style="vertical-align: top; padding-left: 12px;">
                    <span style="color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{canal}</span>
                    <div style="margin-top: 3px;">
                        <a href="{enlace}" target="_blank" style="color: #1e293b; text-decoration: none; font-weight: 600; font-size: 13px; line-height: 1.4;">{titulo}</a>
                    </div>
                    <span style="color: #94a3b8; font-size: 11px;">{duracion}</span>
                </td>
            </tr>
        </table>
    </td>
</tr>"""

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
    "DASHBOARD_URL": "http://jorbencasdownloaderdocument.surge.sh",
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
