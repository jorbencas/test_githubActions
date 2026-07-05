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
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"url":"https://midu.dev/", "yt": "https://www.youtube.com/@midudev/videos"},
    "Codigo facilito": {"yt": "https://www.youtube.com/@codigofacilito/videos"},
    "Carlos Azaustre": {"url":"https://carlosazaustre.es/blog", "yt": "https://www.youtube.com/@CarlosAzaustre/videos"},
    "Clipset": {"yt": "https://www.youtube.com/@clipset/videos"},
    "CodelyTV": {"yt": "https://www.youtube.com/@CodelyTV/videos"},
    "EDteam": {"yt": "https://www.youtube.com/@EDteam/videos"},
    "Fazt": {"yt": "https://www.youtube.com/@FaztTech/videos"},
    "FreeCodeCamp": {"yt": "https://www.youtube.com/@freecodecamp/videos"},
    "HolaMundo": {"yt": "https://www.youtube.com/@holamundodev/videos"},
    "Victor Robles": {"yt": "https://www.youtube.com/@victorroblesweb/videos"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://www.youtube.com/@xatakatv/videos"},
    "Genbeta": {"url": "https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/tags/temas/tecnologia.html"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/tags/tecnologia/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
    "Applesfera": {"url": "https://www.applesfera.com/"},
    "Mixx.io": {"url": "https://mixx.io/"},
    "Wired": {"url": "https://www.wired.com/category/science/"},
    "The Verge": {"url": "https://www.theverge.com/tech"},
    "TechCrunch": {"url": "https://techcrunch.com/category/artificial-intelligence/"},
    "GitHub Blog": {"url": "https://github.blog/category/engineering/"},
    "OpenAI": {"url": "https://openai.com/news/"},
    "Google AI": {"url": "https://blog.google/technology/ai/"},
    "NVIDIA Blog": {"url": "https://blogs.nvidia.com/blog/category/deep-learning/"},
    "Ars Technica": {"url": "https://arstechnica.com/gadgets/"},
    "Slashdot": {"url": "https://slashdot.org/", "selector": "h2.story-title a"},
    "HackTheBox": {"url": "https://www.hackthebox.com/blog/", "selector": ".blog-post-card h3"},
    # ── Nuevas fuentes ──
    "ADSL Zone": {"url": "https://www.adslzone.net/", "selector": "article h2 a"},
    "MuyComputer": {"url": "https://www.muycomputer.com/", "selector": "a[rel=\"bookmark\"]"},
    "ComputerHoy": {"url": "https://www.computerhoy.com/", "selector": ".c-article__title a"},
    "Hipertextual": {"url": "https://hipertextual.com/"},
    "Hugging Face Blog": {"url": "https://huggingface.co/blog", "selector": "article.overview-card-wrapper a[role=\"link\"]"},
    "Anthropic": {"url": "https://www.anthropic.com/blog", "selector": "a[class*=\"FeaturedGrid\"], a[class*=\"PublicationList\"]"},
    "Meta AI": {"url": "https://engineering.fb.com/category/artificial-intelligence/", "selector": "h3 a"},
    "DeepMind": {"url": "https://deepmind.google/discover/blog/", "selector": "h3.card__title"},
    "MIT Technology Review": {"url": "https://www.technologyreview.com/topic/artificial-intelligence/"},  # JS-rendered; RSS feed available at /topic/artificial-intelligence/feed/
    "VentureBeat AI": {"url": "https://venturebeat.com/category/ai/", "selector": "header.text-editorial-headline-030 h2 a"},
    # ── Fuentes IA especializadas ──
    "AssemblyAI": {"url": "https://www.assemblyai.com/blog/", "selector": "article h2 a"},
    "Cohere": {"url": "https://cohere.com/blog", "selector": "a[href*='/blog/'] h3"},
    "Scale AI": {"url": "https://scale.com/blog", "selector": "a[class*='blog-card']"},
    "LangChain": {"url": "https://blog.langchain.dev/", "selector": "article h2 a"},
    "Pinecone": {"url": "https://www.pinecone.io/blog/", "selector": "a[class*='post-title']"},
    "Weights & Biases": {"url": "https://wandb.ai/fully-connected", "selector": "article h2 a"},
    "Hugging Face": {"url": "https://huggingface.co/blog", "selector": "article.overview-card-wrapper a[role='link']"},
    "LlamaIndex": {"url": "https://www.llamaindex.ai/blog", "selector": "a[class*='blog-post']"},
    "Anthropic Research": {"url": "https://www.anthropic.com/research", "selector": "a[class*='card']"},
    "Claude Blog": {"url": "https://docs.anthropic.com/en/release-notes", "selector": "article h2 a"},
    "OpenCode": {"url": "https://opencode.ai"},
    "Google Research": {"url": "https://research.google/blog/", "selector": "article h2 a"},
    "Google Cloud AI": {"url": "https://cloud.google.com/blog/products/ai-machine-learning", "selector": "article h3 a"},
    "Google AI Dev": {"url": "https://ai.google.dev/"},
    "Microsoft AI": {"url": "https://blogs.microsoft.com/ai/", "selector": "article h2 a"},
    "Microsoft Research AI": {"url": "https://www.microsoft.com/en-us/research/topic/artificial-intelligence/", "selector": "article h2 a"},
    "Azure AI": {"url": "https://azure.microsoft.com/en-us/blog/product/azure-ai/", "selector": "article h2 a"},
    "AWS ML": {"url": "https://aws.amazon.com/blogs/machine-learning/", "selector": "article h2 a"},
    "Apple ML Research": {"url": "https://machinelearning.apple.com/", "selector": "article h2 a"},
    "xAI": {"url": "https://x.ai/blog", "selector": "article h2 a"},
    "Perplexity AI": {"url": "https://blog.perplexity.ai/", "selector": "article h2 a"},
    "Meta AI Research": {"url": "https://ai.meta.com/blog/", "selector": "article h3 a"},
    "Stability AI": {"url": "https://stability.ai/news", "selector": "article h2 a"},
    "Replicate": {"url": "https://replicate.com/blog", "selector": "article h2 a"},
    "Modal": {"url": "https://modal.com/blog", "selector": "article h2 a"},
    "Together AI": {"url": "https://www.together.ai/blog", "selector": "article h2 a"},
    "Fireworks AI": {"url": "https://fireworks.ai/blog", "selector": "article h2 a"},
    "Cursor": {"url": "https://www.cursor.com/blog", "selector": "article h2 a"},
    "Codeium": {"url": "https://codeium.com/blog", "selector": "article h2 a"},
    "TabbyML": {"url": "https://tabby.tabbyml.com/blog", "selector": "article h2 a"},
    "Continue.dev": {"url": "https://docs.continue.dev/changelog", "selector": "article h2 a"},
    "Aider": {"url": "https://aider.chat/docs/faq.html"},
    # ── GitHub Topics (AI tools, LLMs, agents) ──
    "GitHub Topic AI": {"url": "https://github.com/topics/artificial-intelligence?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic"},
    "GitHub Topic LLM": {"url": "https://github.com/topics/llm?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic"},
    "GitHub Topic AI Agents": {"url": "https://github.com/topics/ai-agents?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic"},
    "GitHub Topic ML": {"url": "https://github.com/topics/machine-learning?o=desc&s=stars", "tipo": "herramienta", "subtipo": "github-topic"},
    "GitHub Collections AI": {"url": "https://github.com/collections/ai-tools", "tipo": "herramienta", "subtipo": "github-collection"},
    # ── Trending GitHub diario ──
    "GitHub Trending Daily": {"url": "https://github.com/trending?since=daily", "tipo": "herramienta", "subtipo": "github"},
    "GitHub Trending Weekly": {"url": "https://github.com/trending?since=weekly", "tipo": "herramienta", "subtipo": "github"},
    # ── Noticias generales IA ──
    "BBC AI": {"url": "https://www.bbc.com/news/topics/c302m85qtk1t", "selector": "a[data-testid='internal-link']"},
    "El Mundo Tecnología": {"url": "https://www.elmundo.es/tecnologia.html", "selector": "article h2 a"},
    # ── Más creadores de contenido (YouTube + redes) ──
    "LinkTV": {"yt": "https://www.youtube.com/@LinkTVA/videos"},
    "Ringa Tech": {"yt": "https://www.youtube.com/@RingaTech/videos"},
    "Nethermind": {"yt": "https://www.youtube.com/@NethermindDev/videos"},
    "Develoteca": {"yt": "https://www.youtube.com/@Develoteca/videos"},
    "Linkfydev": {"yt": "https://www.youtube.com/@Linkfydev/videos"},
    "Esa Operativa": {"yt": "https://www.youtube.com/@EsaOperativa/videos"},
    "Programador X": {"yt": "https://www.youtube.com/@ProgramadorX/videos"},
    # ── Tech news ──
    "ZDNet": {"url": "https://www.zdnet.com/topic/artificial-intelligence/", "selector": "article h3 a"},
    "CNET": {"url": "https://www.cnet.com/tech/", "selector": "a[class*='title']"},
    "Android Authority": {"url": "https://www.androidauthority.com/", "selector": "h3 a"},
    "The Next Web": {"url": "https://thenextweb.com/topic/artificial-intelligence", "selector": "article h2 a"},
    "InfoWorld": {"url": "https://www.infoworld.com/category/artificial-intelligence/", "selector": "h3 a"},
    # ── Blogs de desarrollo ──
    "LogRocket": {"url": "https://blog.logrocket.com/", "selector": "article h2 a"},
    "Smashing Magazine": {"url": "https://www.smashingmagazine.com/articles/", "selector": "article h2 a"},
    "CSS-Tricks": {"url": "https://css-tricks.com/", "selector": "article h2 a"},
    "freeCodeCamp": {"url": "https://www.freecodecamp.org/news/", "selector": "article h2 a"},
    "DigitalOcean": {"url": "https://www.digitalocean.com/blog", "selector": "a[class*='blog-card'] h3"},
    # ── Fuentes de modelos de IA ──
    "MiniMax": {"url": "https://minimax.io/blog", "selector": "article h2 a"},
    "DeepSeek": {"url": "https://deepseek.com/blog", "selector": "article h2 a"},
    "Qwen": {"url": "https://qwen.readthedocs.io/en/latest/", "selector": "article h2 a"},
    "AI21 Labs": {"url": "https://www.ai21.com/blog", "selector": "article h2 a"},
    # ── Más fuentes IA y tecnología ──
    "The Decoder": {"url": "https://the-decoder.com/"},
    "MarkTechPost": {"url": "https://www.marktechpost.com/"},
    "LinkedIn Engineering": {"url": "https://engineering.linkedin.com/blog", "selector": "article h3 a"},
    "Facebook Engineering": {"url": "https://engineering.fb.com/", "selector": "article h3 a"},

    # ── Fuentes RSS (lectores XML) [quick: True → tier light] ──
    "OpenAI Blog": {"rss": "https://openai.com/news/feed.xml", "quick": True},
    "Anthropic Blog": {"rss": "https://www.anthropic.com/feed.xml", "quick": True},
    "Google DeepMind": {"rss": "https://deepmind.google/blog/rss/", "quick": True},
    "Meta AI Blog": {"rss": "https://ai.meta.com/blog/rss/", "quick": True},
    "Mistral AI News": {"rss": "https://mistral.ai/feed.xml", "quick": True},
    "GitHub Engineering": {"rss": "https://github.blog/engineering/feed/", "quick": True},
    "Stack Overflow Blog": {"rss": "https://stackoverflow.blog/feed/", "quick": True},
    "Hacker News": {"rss": "https://hnrss.org/frontpage", "quick": True},
    "LangChain Blog": {"rss": "https://blog.langchain.dev/feed/", "quick": True},
    "Google AI Blog": {"rss": "https://blog.google/technology/ai/rss/", "quick": True},
    "MIT Tech Review AI": {"rss": "https://www.technologyreview.com/topic/artificial-intelligence/feed/", "quick": True},
    "Google Search Central": {"rss": "https://developers.google.com/search/blog/feed.xml", "quick": True},
    "Google Developers": {"rss": "https://developers.googleblog.com/feed.xml", "quick": True},
    "Moz Blog SEO": {"rss": "https://moz.com/blog/feed.xml", "quick": True},
    "Search Engine Journal": {"rss": "https://www.searchenginejournal.com/feed/", "quick": True},
    "Wired AI": {"rss": "https://www.wired.com/feed/rss", "quick": True},
    "The Verge AI": {"rss": "https://www.theverge.com/ai-artificial-intelligence/rss.xml", "quick": True},
    "TechCrunch AI": {"rss": "https://techcrunch.com/category/artificial-intelligence/feed/", "quick": True},
    "Ars Technica AI": {"rss": "https://feeds.arstechnica.com/arstechnica/index", "quick": True},
    "Dev.to": {"rss": "https://dev.to/feed", "quick": True},
    "Cohere RSS": {"rss": "https://cohere.com/blog/rss.xml", "quick": True},
    "Hugging Face Daily Papers": {"rss": "https://huggingface.co/papers/feed", "quick": True},
    # ── Fuentes de herramientas ──
    "GitHub Trending": {"url": "https://github.com/trending", "tipo": "herramienta", "subtipo": "github"},
    "Product Hunt": {"url": "https://www.producthunt.com/", "tipo": "herramienta", "subtipo": "producthunt"},
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
            .social-cell {{ display: block !important; width: 100% !important; text-align: center !important; padding-top: 8px !important; }}
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

                <!-- Social links -->
                <table width="100%" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="padding: 0 40px 20px 40px; text-align: center;">
                            <p style="margin: 0 0 12px 0; font-size: 11px; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px;">Sígueme</p>
                            <table border="0" cellpadding="0" cellspacing="0" align="center">
                                <tr>
                                    <td style="padding: 0 6px;">
                                        <a href="https://github.com/jorbencas" target="_blank" style="display: inline-block; width: 36px; height: 36px; background: #0f172a; border-radius: 8px; text-align: center; line-height: 36px; text-decoration: none; font-size: 16px; color: #f8fafc; transition: all 0.2s;">GH</a>
                                    </td>
                                    <td style="padding: 0 6px;">
                                        <a href="https://twitter.com/jorgevenkas" target="_blank" style="display: inline-block; width: 36px; height: 36px; background: #1d9bf0; border-radius: 8px; text-align: center; line-height: 36px; text-decoration: none; font-size: 14px; font-weight: 700; color: #ffffff;">X</a>
                                    </td>
                                    <td style="padding: 0 6px;">
                                        <a href="https://gitlab.com/jorbencas" target="_blank" style="display: inline-block; width: 36px; height: 36px; background: #e24329; border-radius: 8px; text-align: center; line-height: 36px; text-decoration: none; font-size: 14px; font-weight: 700; color: #ffffff;">GL</a>
                                    </td>
                                    <td style="padding: 0 6px;">
                                        <a href="mailto:jorgebeneytocastello@gmail.com" target="_blank" style="display: inline-block; width: 36px; height: 36px; background: #ea4335; border-radius: 8px; text-align: center; line-height: 36px; text-decoration: none; font-size: 16px; color: #ffffff;">@</a>
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
draft: false
readingTime: {tiempo_lectura}
categories: ["tech", "weekly-recap"]
---

## 🚀 Radiografía de la semana

{introduccion}

{bloque_noticias}

---

## 📊 El panel en datos

| Métrica | Valor |
|---------|-------|
| Noticias analizadas | **{total_noticias}** |
| Fuentes distintas | **{total_fuentes}** |
| Fuentes RSS | **{total_rss}** |
| Tiempo estimado de lectura | {tiempo_lectura} min |
| Categoría principal | {top_categorias} |

### Distribución por categoría

{stats_categorias}

### Top fuentes

{fuentes_top}

---

## 📋 Listado completo de noticias

{lista_noticias}

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

MISSION: Analiza las noticias de la semana y genera un RECAP SEMANAL que un programador quiera leer.

═══ NORMAS DE ESTILO (OBLIGATORIO) ═══
- Voz directa: nada de "En el cambiante mundo digital..." o "La era de la IA transforma..."
- Asume que el lector ya sabe qué es OpenAI, Docker o Kubernetes
- Si una noticia es solo marketing, dilo ("mucho ruido, pocas nueces")
- Sé específico: nombres, versiones, cifras concretas
- Conecta temas: si OpenAI y Google sacan algo similar, agrúpalos
- La introducción debe enganchar en la primera frase

═══ NOTICIAS DE LA SEMANA (AGRUPADAS POR CATEGORÍA) ═══

{resumen_cats}

Total noticias RSS: {total_rss}

{texto_noticias}

═══ INSTRUCCIONES DE SALIDA ═══

Genera un JSON con esta estructura EXACTA:

{{
  "introduccion": "Párrafo de 4-6 líneas. Primera frase: tema principal de la semana. Luego conecta 2-3 tendencias clave con sus categorías. Tono analítico, no sensacionalista. (max 700 chars)",
  "noticias_destacadas": [
    {{
      "titulo": "Título descriptivo + categoría entre paréntesis (ej: 'GPT-5: OpenAI supera expectativas (🤖 IA)')",
      "suceso": "Qué ocurrió con datos concretos: nombres, versiones, cifras. 2-3 líneas. (max 300 chars)",
      "impacto": "Por qué importa AHORA. Conecta con tendencias del sector. 2-3 líneas. (max 300 chars)"
    }}
  ],
  "repo": {{
    "nombre": "Nombre del repo/herramienta más interesante de la semana",
    "url": "URL del repo (de preferencia uno de las noticias o de GitHub Trending)",
    "desc": "Qué problema resuelve y por qué debería probarlo. 1-2 frases."
  }},
  "tldr": [
    "Punto 1: tema principal + contexto (max 160 chars)",
    "Punto 2: segunda tendencia + dato concreto (max 160 chars)",
    "Punto 3: herramienta/repo destacado (max 160 chars)",
    "Punto 4: preview de lo que viene (max 160 chars)"
  ],
  "tags": ["tech", "tag_tema_principal", "tag_tema2", "tag_tema3"],
  "sneak_peek": "Predicción concreta basada en lo visto esta semana. Sin promesas vacías. (max 350 chars)",
  "nota_personal": "Reflexión genuina como si se lo dijeras a un colega. Menciona algo que te sorprendió o un aprendizaje. (max 320 chars)"
}}

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
EMAIL_ROW_TEMPLATE = """<tr>
    <td style="padding: 14px 0; border-bottom: 1px solid #f1f5f9;">
        <table width="100%" border="0" cellpadding="0" cellspacing="0">
            <tr>
                <td width="28" style="vertical-align: top; padding-top: 2px;">
                    <span style="font-size: 16px;">{icon}</span>
                </td>
                <td style="vertical-align: top; padding-left: 10px;">
                    <span style="color: #94a3b8; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;">{fuente}</span>
                    <div style="margin-top: 3px;">
                        <a href="{enlace}" target="_blank" style="color: #1e293b; text-decoration: none; font-weight: 600; font-size: 14px; line-height: 1.4;">{titulo}</a>
                    </div>
                    {resumen_html}
                </td>
            </tr>
        </table>
    </td>
</tr>"""

# ── JS config (inyectado en HTML pre-renderizado) ──
JS_CONFIG = {
    "ALL_YT_CHANNELS": [
        "MoureDev", "Midudev", "Pelado Nerd", "HolaMundo", "FreeCodeCamp",
        "Fazt", "Clipset", "CodelyTV", "EDteam", "Programa Con Arnau",
        "El Pingüino de Mario", "Carlos Azaustre", "Codigo facilito", "Victor Robles",
        "LinkTV", "Ringa Tech", "Nethermind", "Develoteca", "Programador X",
        "Linkfydev", "Esa Operativa", "Xataka",
    ],
    "TABS_MULTIMEDIA": [
        {"id": "youtube", "label": "🎬 YouTube"},
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
]
