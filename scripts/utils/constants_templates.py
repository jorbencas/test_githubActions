"""Templates HTML, email, markdown y prompts de IA."""

# ── HTML Dashboard ──
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

# ── Email Newsletter ──
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
            .header-cell {{ padding: 28px 24px 16px 24px !important; }}
            .hide-mobile {{ display: none !important; }}
        }}
        @media (prefers-color-scheme: dark) {{
            .dark-bg {{ background-color: #1e293b !important; }}
            .dark-card {{ background-color: #0f172a !important; border-color: #334155 !important; }}
            .dark-text {{ color: #f1f5f9 !important; }}
            .dark-text-secondary {{ color: #94a3b8 !important; }}
            .dark-border {{ border-color: #334155 !important; }}
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

# ── Markdown Blog Post ──
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

# ── Prompt para imagen IA ──
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

# ── Prompt resumir noticias (lote) ──
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

# ── Prompt resumir noticia individual ──
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

# ── Prompt recap semanal ──
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

# ── Prompt traducir titulares ──
PROMPT_TRADUCIR_TITULOS = """Traduce estos titulares de tecnología al español de forma profesional y natural.
Manten nombres propios, marcas y acrónimos (OpenAI, NVIDIA, iPhone, etc.) sin traducir.
Conserva el formato "id|título" en la respuesta.
Devuelve SOLO JSON, sin markdown ni explicaciones.

TEXTO:
{texto_a_traducir}

FORMATO:
{{"traducciones": [{{"id": 0, "tr": "Título traducido 0"}}, {{"id": 1, "tr": "Título traducido 1"}}]}}"""

# ── Email source header ──
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

# ── Email row ──
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

# ── Email video header ──
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

# ── Email video row ──
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
