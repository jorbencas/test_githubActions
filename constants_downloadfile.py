import os
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TOKEN_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "FOLDER": "files"
}

TECH_KEYWORDS = ['ia', 'inteligencia artificial', 'empleo', 'software', 'programación', 'valencia', 'albaida', 'tecnología']
BECAS_KEYWORDS = ['beca', 'curso', 'ayuda', 'formación', 'subvención', 'taller']
ALL_KEYWORDS = TECH_KEYWORDS + BECAS_KEYWORDS

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Codigo facilito": {"yt": "https://www.youtube.com/@codigofacilito/videos"},
    "Carlos Azaustre": {"yt": "https://www.youtube.com/@CarlosAzaustre/videos"},
    "Clipset": {"yt": "https://www.youtube.com/@clipset/videos"},
    "CodelyTV": {"yt": "https://www.youtube.com/@CodelyTV/videos"},
    "EDteam": {"yt": "https://www.youtube.com/@EDteam/videos"},
    "Fazt": {"yt": "https://www.youtube.com/@FaztTech/videos"},
    "FreeCodeCamp": {"yt": "https://www.youtube.com/@freecodecamp/videos"},
    "HolaMundo": {"yt": "https://www.youtube.com/@holamundodev/videos"},
    "Victor Robles": {"yt": "https://www.youtube.com/@victorroblesweb/videos"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://www.youtube.com/@xatakatv/videos"},
    "Becas": {"url": "https://www.becas.com/noticias/"},
    "Genbeta": {"url":"https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
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
            <img src="optimizado/Image.png" alt="Logo" class="logo">
        </header>
        <div class="ia-box">
            <h2>🤖 Resumen</h2>
            <p>{resumen}</p>
        </div>

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
        <h2>📰 Noticias Históricas</h2>
        <ul class="news-list">{bloque_noticias}</ul>
    </div>
</body>
<script src="script.js"></script>
</html>
"""

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actualización Tecnológica</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7f9; font-family: Arial, sans-serif;">
    <div style="display: none; max-height: 0px; overflow: hidden;">
        Resumen de hoy: {total_noticias} novedades encontradas sobre {temas_clave}...
    </div>

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; margin: 20px auto; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <tr>
            <td bgcolor="#1a73e8" style="padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #ffffff; margin: 0; font-size: 26px; letter-spacing: 1px;">Tech Pulse News</h1>
                <p style="color: #c2e7ff; margin: 10px 0 0 0; font-size: 14px; font-weight: bold;">{fecha_hoy}</p>
            </td>
        </tr>
        
        <tr>
            <td style="padding: 20px 40px 0 40px;">
                <table width="100%" style="background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center;">
                    <tr>
                        <td width="33%"> <b style="font-size: 20px; color: #1a73e8;">{count_tech}</b><br><span style="font-size: 12px; color: #666;">Noticias Tech</span> </td>
                        <td width="33%" style="border-left: 1px solid #ddd; border-right: 1px solid #ddd;"> <b style="font-size: 20px; color: #2e7d32;">{count_becas}</b><br><span style="font-size: 12px; color: #666;">Becas/Ayudas</span> </td>
                        <td width="33%"> <b style="font-size: 20px; color: #d93025;">{count_vids}</b><br><span style="font-size: 12px; color: #666;">Multimedia</span> </td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <td style="padding: 30px 40px;">
                <h2 style="color: #8e44ad; font-size: 18px; margin-bottom: 15px;">🤖 Resumen Inteligente</h2>
                <div style="line-height: 1.6; color: #3c4043; font-size: 15px; background: #fdf7ff; padding: 20px; border-radius: 8px; border-left: 4px solid #8e44ad;">
                    {contenido_html}
                </div>
            </td>
        </tr>

        <tr>
            <td style="padding: 0 40px 40px 40px;">
                <h2 style="color: #202124; font-size: 18px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">📋 Selección para ti</h2>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    {lista_email}
                </table>
            </td>
        </tr>

        <tr>
            <td style="padding: 20px; text-align: center; background: #f1f3f4; border-radius: 0 0 10px 10px;">
                <p style="font-size: 12px; color: #70757a; margin: 0;">
                    Generado automáticamente para Jorge Beneyto.<br>
                    <a href="http://jorbencasdownloaderdocument.surge.sh" style="color: #1a73e8; text-decoration: none; font-weight: bold;">Acceder al Dashboard Histórico</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""

MD_TEMPLATE = """---
draft: false
title: "{titulo}"
description: "{resumen_corto}"
pubDate: "{fecha_pub}"
tags: ['web', 'tech', 'ia']
slug: "{slug_name}"
image: "/img/arquitectura_web.webp"
author: "Jorge Beneyto Castelló"
layout: "@layouts/PostLayout.astro"
---
{contenido}

### 🔗 Enlaces de interés
{lista_enlaces}
"""
