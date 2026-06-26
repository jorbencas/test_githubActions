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

BECAS_KEYWORDS = ['beca', 'curso', 'ayuda', 'formación', 'subvención', 'taller']
ALL_KEYWORDS = TECH_KEYWORDS + BECAS_KEYWORDS

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
    "Becas": {"url": "https://www.becas.com/noticias/"},
    "Genbeta": {"url": "https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
    "Applesfera": {"url": "https://www.applesfera.com/"},
    "Mixx.io": {"url": "https://mixx.io/"},
    "Wired": {"url": "https://www.wired.com/category/science/"},
    "The Verge": {"url": "https://www.theverge.com/tech"},
    "TechCrunch": {"url": "https://techcrunch.com/category/artificial-intelligence/"},
    "Hacker News": {"url": "https://news.ycombinator.com/"},
    "GitHub Blog": {"url": "https://github.blog/category/engineering/"},
    "OpenAI": {"url": "https://openai.com/news/"},
    "Google AI": {"url": "https://blog.google/technology/ai/"},
    "NVIDIA Blog": {"url": "https://blogs.nvidia.com/blog/category/deep-learning/"},
    "Dev.to": {"url": "https://dev.to/t/ai"},
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
    # ── Redes sociales (scraping sin API) ──
    "Midudev Twitter": {"url": "https://x.com/midudev", "selector": "article[data-testid='tweet'] div[lang]"},
    "Midudev Threads": {"url": "https://www.threads.net/@midudev", "selector": "article a[href*='/post/']"},
    "Bricemoure Twitter": {"url": "https://x.com/bricemoure", "selector": "article[data-testid='tweet'] div[lang]"},
    "Bricemoure Threads": {"url": "https://www.threads.net/@bricemoure", "selector": "article a[href*='/post/']"},
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
    <meta name="description" content="Tech Pulse Dashboard — Resumen inteligente de noticias tech, v\u00eddeos, becas y contenido curado por Jorge Beneyto Castell\u00f3. Actualizado diariamente con IA.">
    <meta property="og:title" content="Tech Pulse Dashboard — Jorge Beneyto Castell\u00f3">
    <meta property="og:description" content="Dashboard de tecnolog\u00eda con resumen IA, filtros por canal y fecha, v\u00eddeos y shorts de YouTube. Curado por Jorge Beneyto Castell\u00f3.">
    <meta property="og:type" content="website">
    <meta property="og:url" content="https://jorbencasdownloaderdocument.surge.sh">
    <meta property="og:site_name" content="Tech Pulse Dashboard">
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:site" content="@jorbencas">
    <meta name="twitter:creator" content="@jorbencas">
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
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <picture>
                <source srcset="optimizado/Image.avif" type="image/avif">
                <source srcset="optimizado/Image.webp" type="image/webp">
                <img src="optimizado/Image.png" alt="Tech Pulse Dashboard Logo" class="logo" width="120" height="40" style="aspect-ratio: 3/1; object-fit: contain;" loading="eager">
            </picture>
        </header>

        <div class="ia-box">
            <h2>\U0001f916 Resumen IA</h2>
            <p>{resumen}</p>
        </div>

        <div id="stats-bar" class="stats-bar"></div>

        <h2>\U0001f4f0 Noticias</h2>
        <div class="filter-section">
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
                <strong>\U0001f4c5 Tiempo:</strong>
                <div id="news-week-filters" class="chip-container" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;"></div>
            </div>
        </div>
        <div class="filter-section">
            <strong>\U0001f4f0 Filtro Canal:</strong>
            <div id="news-channel-filters" class="chip-container"></div>
        </div>
        <ul id="news-list" class="news-list"></ul>

        <h2>\U0001f4fa Multimedia (V\u00eddeos y Shorts)</h2>
        <div class="filter-section">
            <div style="display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
                <strong>\U0001f4c5 Tiempo:</strong>
                <div id="video-week-filters" class="chip-container" style="display:flex;flex-wrap:wrap;gap:8px;align-items:center;"></div>
            </div>
        </div>
        <div class="filter-section">
            <strong>\U0001f4fa Filtro Canal:</strong>
            <div id="video-channel-filters" class="chip-container"></div>
        </div>
        <div id="video-grid" class="video-grid"></div>
    </div>
</body>
<script>
  const API_BASE = "{api_url}";
  const TOKEN = "{api_token}";
  const DATA_URL = "data.json";
</script>
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
            a {{ color: #818cf8 !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    
    <div style="display: none; max-height: 0px; overflow: hidden;">
        {total_noticias} novedades tech · {count_tech} noticias · {count_becas} becas · resumen generado por IA · {temas_clave}
    </div>

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="container dark-card" style="max-width: 600px; background-color: #ffffff; margin: 30px auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05); overflow: hidden; border: 1px solid #e2e8f0;">
        
        <tr>
            <td class="header-cell" style="padding: 40px 40px 20px 40px; text-align: left; background-color: #ffffff; border-bottom: 2px solid #f1f5f9;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0">
                    <tr>
                        <td style="vertical-align: middle;">
                            <p style="margin: 0; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px;">EDICIÓN DIARIA</p>
                            <h1 style="color: #0f172a; margin: 4px 0 0 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1;">Tech Pulse</h1>
                            <div style="height: 4px; width: 40px; background-color: #6366f1; margin: 16px 0 0 0; border-radius: 2px;"></div>
                            <p style="color: #475569; margin: 12px 0 0 0; font-size: 14px; font-weight: 500;">{fecha_hoy}</p>
                        </td>
                        <td width="80" class="hide-mobile" style="vertical-align: middle; text-align: right;">
                            <span style="display: inline-block; background: #eef2ff; color: #4f46e5; font-size: 10px; font-weight: 700; padding: 4px 10px; border-radius: 20px; letter-spacing: 0.5px; text-transform: uppercase;">IA</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
        
        <tr>
            <td class="content" style="padding: 24px 40px 0 40px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" class="stat-table dark-stats" style="background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; padding: 16px; text-align: center;">
                    <tr>
                        <td width="33%" class="stat-cell" style="vertical-align: top;">
                            <b style="font-size: 22px; color: #4f46e5; font-weight: 800;">{count_tech}</b><br>
                            <span style="font-size: 12px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px;">Noticias Tech</span>
                        </td>
                        <td width="33%" class="stat-cell stat-border" style="vertical-align: top; border-left: 1px solid #e2e8f0; border-right: 1px solid #e2e8f0;">
                            <b style="font-size: 22px; color: #16a34a; font-weight: 800;">{count_becas}</b><br>
                            <span style="font-size: 12px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px;">Becas / Ayudas</span>
                        </td>
                        <td width="33%" class="stat-cell" style="vertical-align: top;">
                            <b style="font-size: 22px; color: #dc2626; font-weight: 800;">{count_vids}</b><br>
                            <span style="font-size: 12px; font-weight: 600; color: #64748b; display: inline-block; margin-top: 4px;">Multimedia</span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <td class="content" style="padding: 30px 40px 10px 40px;">
                <h2 style="color: #0f172a; font-size: 18px; font-weight: 700; margin: 0 0 14px 0; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">🤖</span> Resumen Inteligente del día
                    <span class="hide-mobile" style="margin-left: auto; font-size: 10px; font-weight: 600; color: #64748b; background: #f1f5f9; padding: 2px 8px; border-radius: 4px;">generado con Gemini</span>
                </h2>
                <div style="line-height: 1.6; color: #334155; font-size: 15px; background: #fafafa; padding: 24px; border-radius: 10px; border: 1px solid #e2e8f0; border-left: 4px solid #6366f1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.01);">
                    {contenido_html}
                </div>
            </td>
        </tr>

        <tr>
            <td class="content" style="padding: 20px 40px 40px 40px;">
                <h2 style="color: #0f172a; font-size: 18px; font-weight: 700; margin: 0 0 16px 0; padding-bottom: 8px; border-bottom: 2px solid #f1f5f9;">
                    <span style="margin-right: 8px;">📋</span> Lecturas y contenido seleccionado
                </h2>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    {lista_email}
                </table>
            </td>
        </tr>

        <tr>
            <td class="content" style="padding: 30px 40px; text-align: center; background: #f8fafc; border-top: 1px solid #e2e8f0;">
                <p style="font-size: 13px; color: #64748b; margin: 0; line-height: 1.5;">
                    Esta newsletter ha sido compilada de forma automatizada.<br>
                    Preparado en exclusiva para <strong>Jorge Beneyto Castelló</strong>.
                </p>
                <table border="0" cellpadding="0" cellspacing="0" align="center" style="margin-top: 20px;">
                    <tr>
                        <td align="center" bgcolor="#4f46e5" style="border-radius: 6px;">
                            <a href="http://jorbencasdownloaderdocument.surge.sh" target="_blank" style="font-size: 13px; font-weight: 600; color: #ffffff; text-decoration: none; display: inline-block; padding: 10px 18px;">
                                Abrir Dashboard Histórico →
                            </a>
                        </td>
                    </tr>
                </table>
                <p style="font-size: 11px; color: #94a3b8; margin: 24px 0 0 0;">
                    &copy; {year} Tech Pulse Briefing. Todos los derechos reservados.
                </p>
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

## 🚀 Lo más destacado de la semana

{introduccion}

{bloque_noticias}

---

## 📊 En cifras
- **{total_noticias}** noticias analizadas de **{total_fuentes}** fuentes distintas
- **Tiempo estimado de lectura:** {tiempo_lectura} min
- **Fuentes principales:** {fuentes_top}

---

## 📋 Listado completo de noticias

{lista_noticias}

---

### 🛠️ Herramienta o Repo de la Semana

:::tip
**[{repo_name}]({repo_url})** — {repo_desc}
:::

---

## 🏁 Conclusión rápida (TL;DR)
{conclusion_tldr}

---

## 🔮 Para la próxima semana

:::warning
{sneak_peek}
:::

---

> **Nota del autor:** {nota_personal}

📡 **[Ver dashboard completo con todos los vídeos y filtros](http://jorbencasdownloaderdocument.surge.sh)**
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
