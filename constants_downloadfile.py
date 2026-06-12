import os
CONFIG = {
    "TELEGRAM_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TOKEN_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "DOWNLOADER_API_TOKEN": os.getenv("DOWNLOADER_API_TOKEN"),
    "FOLDER": "files",
    "IMAGES_FOLDER": "images",
    "IMAGES_PATH_PREFIX": "public/optimizado",
    "AI_MODELS": ["gemini-2.5-flash", "gemini-2.5-pro"],
    "IMAGE_MODELS": ["imagen-3.0-generate-002"] # Fallback para imagen
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
}

WEBS_RETOS = {
    "Retos de Programación": {"url": "https://retosdeprogramacion.com/ejercicios/", "selector": "a[href*='/retos/']"},
    "Codewars": {"url": "https://www.codewars.com/kata/latest", "selector": ".item-title a"},
    "RetosMoure": {"url": "https://retosdeprogramacion.com/semanales2024", "selector": "a[href*='/retos/']"}
}

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <title>Tech Dashboard</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <picture>
                <source srcset="optimizado/Image.avif" type="image/avif">
                <source srcset="optimizado/Image.webp" type="image/webp">
                <img src="optimizado/Image.png" alt="Logo" class="logo" width="120" height="40" style="aspect-ratio: 3/1; object-fit: contain;" loading="eager">
            </picture>
        </header>
        <div class="ia-box">
            <h2>🤖 Resumen</h2>
            <p>{resumen}</p>
        </div>

        <h2>📰 Noticias Históricas</h2>
        <ul class="news-list">{bloque_noticias}</ul>
        
        <div class="filter-section">
            <strong>📅 Por Tiempo:</strong>
            <div class="chip-container">{bloque_semanas}</div>
        </div>

        <div class="filter-section">
            <strong>👤 Por Canal:</strong>
            <div class="chip-container">{bloque_chips}</div>
        </div>

        <h2>📺 Multimedia (Vídeos y Shorts)</h2>
        <div class="video-grid">{bloque_videos}</div>
    </div>
</body>
<script>
  const API_BASE = "{api_url}";
  const TOKEN = "{api_token}";
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
    <title>Tech Pulse Newsletter</title>
    <style>
        @media only screen and (max-width: 620px) {{
            .container {{ width: 100% !important; margin: 0 !important; border-radius: 0 !important; }}
            .content {{ padding: 20px !important; }}
            .stat-cell {{ display: block !important; width: 100% !important; border: none !important; padding: 10px 0 !important; }}
            .stat-border {{ border: none !important; border-top: 1px solid #e2e8f0 !important; border-bottom: 1px solid #e2e8f0 !important; }}
        }}
    </style>
</head>
<body style="margin: 0; padding: 0; background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; -webkit-font-smoothing: antialiased;">
    
    <!-- Preheader invisible para lectores de correo -->
    <div style="display: none; max-height: 0px; overflow: hidden;">
        Resumen de hoy: {total_noticias} novedades encontradas sobre {temas_clave}...
    </div>

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" class="container" style="max-width: 600px; background-color: #ffffff; margin: 30px auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(15, 23, 42, 0.05); overflow: hidden; border: 1px solid #e2e8f0;">
        
        <!-- ENCABEZADO ESTILO NEWSLETTER -->
        <tr>
            <td style="padding: 40px 40px 20px 40px; text-align: left; background-color: #ffffff; border-bottom: 2px solid #f1f5f9;">
                <p style="margin: 0; font-size: 11px; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 1.5px;">EDICIÓN DIARIA</p>
                <h1 style="color: #0f172a; margin: 4px 0 0 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px; line-height: 1.1;">Tech Pulse</h1>
                <div style="height: 4px; width: 40px; background-color: #6366f1; margin: 16px 0 0 0; border-radius: 2px;"></div>
                <p style="color: #475569; margin: 12px 0 0 0; font-size: 14px; font-weight: 500;">{fecha_hoy}</p>
            </td>
        </tr>
        
        <!-- DASHBOARD DE METRICAS RAPIDAS -->
        <tr>
            <td class="content" style="padding: 24px 40px 0 40px;">
                <table width="100%" border="0" cellpadding="0" cellspacing="0" style="background: #f8fafc; border-radius: 8px; border: 1px solid #e2e8f0; padding: 16px; text-align: center;">
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

        <!-- CONTENIDO PRINCIPAL: RESUMEN IA -->
        <tr>
            <td class="content" style="padding: 30px 40px 10px 40px;">
                <h2 style="color: #0f172a; font-size: 18px; font-weight: 700; margin: 0 0 14px 0; display: flex; align-items: center;">
                    <span style="margin-right: 8px;">🤖</span> Resumen Inteligente del día
                </h2>
                <div style="line-height: 1.6; color: #334155; font-size: 15px; background: #fafafa; padding: 24px; border-radius: 10px; border-left: 4px solid #6366f1; border: 1px solid #e2e8f0; border-left: 4px solid #6366f1; box-shadow: inset 0 1px 2px rgba(0,0,0,0.01);">
                    {contenido_html}
                </div>
            </td>
        </tr>

        <!-- LISTA CURADA DE ENLACES -->
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

        <!-- PIE DE PAGINA -->
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
---

## 🚀 Lo más destacado de la semana

{introduccion}

{bloque_noticias}

---

### 🛠️ Herramienta o Repo de la Semana
He encontrado este recurso que te puede ahorrar horas de trabajo:
- **Link:** [{repo_name}]({repo_url})
- **Utilidad:** {repo_desc}

---

## 🏁 Conclusión rápida (TL;DR)
{conclusion_tldr}

---
> **Nota del autor:** {nota_personal}
"""

# --- En constants_downloadfile.py ---
PROMPT_IMAGEN_TEMPLATE = """
Create a high-quality, professional wide-angle image representing the following concept: "{titulo_post}".
The visual style should be cinematic and futuristic, featuring a blend of clean technological elements, 
soft ambient lighting, and a depth of field that keeps the subject in focus. 
Color palette: deep digital blues, crisp white highlights, and subtle neon green accents. 
Ensure the composition is balanced and suitable for a tech article header. 
Highly detailed, photorealistic, 8k resolution, modern aesthetic, professional photography style.
"""


PROMPT_IMAGEN_TEMPLATE_RETO = """
Minimalist tech illustration of {titulo_post}. 
Style: Flat vector art, isometric perspective, cyberpunk aesthetics. 
Palette: Deep slate background, neon cyan and electric blue highlights. 
Clean lines, high contrast, professional digital art, centered composition. 
No text, no faces, simple geometric shapes.
"""

# Template para retos generados dinámicamente por IA (hunt_challenges.py)
RETO_MD_TEMPLATE = """---
draft: false
title: "🏆 RETO: {titulo}"
description: "{resumen_corto}"
pubDate: "{fecha_pub}"
tags: {tags_seo}
slug: "{slug_name}"
image: "{ruta_imagen}"
author: "Jorge Beneyto Castelló"
difficulty: "{dificultad}"
---

import Challenge from '@components/Challenge.astro';

# 🎯 Desafío: {titulo}

### 📝 Descripción del Reto
{descripcion_ia}

<Challenge 
  nivel="{dificultad}" 
  mision="{resumen_corto}" 
/>

---

## 💡 Guía de Solución Paso a Paso

<details>
<summary><b>Ver explicación y código 🛠️ (¡No hagas spoiler!)</b></summary>
<div class="details-content">

### 🏗️ Paso 1: Análisis de la lógica
{paso_1}

### ⚙️ Paso 2: Implementación en {lenguaje_display}
{paso_2}

### 🚀 Paso 3: Complejidad y Optimización
{paso_3}

### 💻 Código de la Solución ({lenguaje_display})

```{lenguaje_lower}
{codigo_solucion}
```

</div>
</details>
"""