import os, json, re, requests, asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from mtranslate import translate
from google import genai 

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TELEGRAM_CHAT_ID"), # Asegúrate de usar CHAT_ID en tus secrets
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "FOLDER": "files" 
}

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Xataka": {"url": "https://www.xataka.com/"},
    "Becas": {"url": "https://www.becas.com/noticias/"}
}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)
os.makedirs("./auto-news", exist_ok=True)

# --- 2. PLANTILLAS (TEMPLATES) ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #1c1e21; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }}
        .ia-box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #8e44ad; margin-bottom: 30px; line-height: 1.6; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; height: 160px; object-fit: cover; }}
        .card-content {{ padding: 15px; }}
        .meta {{ font-size: 0.8em; color: #65676b; font-weight: bold; margin-bottom: 5px; }}
        .news-list {{ list-style: none; padding: 0; }}
        .news-item {{ background: white; margin-bottom: 10px; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
        a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
        .logo {{ height: 50px; }}
    </style>
    <title>Tech Pulse Dashboard</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <img src="./Image.png" alt="Logo" class="logo">
        </header>
        <div class="ia-box">
            <h2>🤖 Resumen Inteligente</h2>
            <p>{resumen}</p>
        </div>
        <h2>📺 Últimos Vídeos</h2>
        <div class="video-grid">{bloque_videos}</div>
        <h2>📰 Historial de Noticias</h2>
        <ul class="news-list">{bloque_noticias}</ul>
    </div>
</body>
</html>
"""

MD_TEMPLATE = """---
title: "{titulo}"
date: "{fecha_iso}"
layout: "@layouts/PostLayout.astro"
---

## 🤖 Resumen de la sesión
{contenido}

---
### 🔗 Enlaces detectados
{lista_enlaces}
"""

EMAIL_TEMPLATE = """
<div style="font-family: Arial; max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
    <h2 style="color: #8e44ad;">🤖 Resumen IA</h2>
    <p style="line-height: 1.6;">{contenido}</p>
    <hr>
    <h2 style="color: #007bff;">📋 Novedades</h2>
    <ul style="list-style: none; padding: 0;">
        {lista_email}
    </ul>
</div>
"""

# --- 3. CLASE SCRAPER ---

class ScraperPro:
    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            r = requests.get(target, timeout=15, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            if r.status_code != 200: return []
            
            if "yt" in info:
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                clean_ids = list(dict.fromkeys(ids))
                for t, i in zip(titles[:5], clean_ids[:5]):
                    results.append({
                        "titulo": translate(t.replace('"', ''), 'es'),
                        "enlace": f"https://youtube.com/watch?v={i}",
                        "id_video": i, "fuente": nombre, "tipo": "video",
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a, h2.title a')[:5]
                tipo = "beca" if "beca" in nombre.lower() else "noticia"
                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '')
                    if not t_raw: continue
                    results.append({
                        "titulo": translate(t_raw, 'es'),
                        "enlace": urljoin(target, i.get('href')),
                        "fuente": nombre, "tipo": tipo,
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
        except: pass
        return results

# --- 4. FUNCIONES DE PROCESAMIENTO ---

async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"] or not noticias: return "Hoy no hay nuevas noticias para resumir."
    try:
        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        texto = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Actúa como analista tech. Resume estas noticias en 3 párrafos en español: {texto}"
        )
        return response.text
    except Exception as e:
        print(f"Error IA: {e}")
        return "Resumen temporalmente no disponible."

def publicar_contenidos(historial_completo, nuevos, resumen_ia):
    fecha_h = datetime.now().strftime("%d/%m/%Y")
    fecha_iso = datetime.now().strftime("%Y-%m-%d")
    
    # Ordenar historial (Más reciente arriba)
    historial_completo.sort(key=lambda x: x.get('ts', ''), reverse=True)

    v_html, n_html, md_list, email_list = "", "", "", ""
    resumen_final = resumen_ia if resumen_ia else "Listado de actualizaciones del día."

    # Bloques para la Web (Acumulativo - Top 100)
    for n in historial_completo[:100]:
        meta = f"{n['fuente']} | {n.get('f', '--/--')}"
        if n['tipo'] == "video":
            v_html += f"""
            <div class="card">
                <img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg">
                <div class="card-content">
                    <div class="meta">{meta}</div>
                    <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
                </div>
            </div>"""
        else:
            n_html += f"""
            <li class="news-item">
                <div class="meta">{meta}</div>
                <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
            </li>"""

    # Bloques para MD y Email (Solo los NUEVOS)
    for n in nuevos:
        md_list += f"- **{n['fuente']}**: [{n['titulo']}]({n['enlace']}) ({n.get('f')})\n"
        email_list += f"<li style='margin-bottom:10px;'><b>{n['fuente']}</b> ({n.get('f')}): <br><a href='{n['enlace']}'>{n['titulo']}</a></li>"

    # 1. Guardar Web
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_final, bloque_videos=v_html, bloque_noticias=n_html))

    # 2. Guardar Markdown (Solo si hay nuevos)
    if nuevos:
        titulo_md = nuevos[0]['titulo'].replace("'", "")
        with open(f"./auto-news/reporte-{fecha_iso}.md", "w", encoding="utf-8") as f:
            f.write(MD_TEMPLATE.format(titulo=titulo_md, fecha_iso=fecha_iso, contenido=resumen_final, lista_enlaces=md_list))

        # 3. Enviar Email
        if CONFIG["MAIL_KEY"]:
            try:
                requests.post(f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages",
                    auth=("api", CONFIG["MAIL_KEY"]),
                    data={
                        "from": f"Tech Pulse <postmaster@{CONFIG['MAIL_DOMAIN']}>",
                        "to": [CONFIG["EMAIL_TO"]],
                        "subject": f"🚀 Reporte Tech {fecha_h}",
                        "html": EMAIL_TEMPLATE.format(contenido=resumen_final, lista_email=email_list)
                    })
            except: pass

# --- 5. MAIN ---

async def main():
    scr = ScraperPro()
    datos_web = []
    for nombre, info in FUENTES.items():
        datos_web += scr.extraer(nombre, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos_web if n['enlace'] not in vistos]

    # Unión de datos
    total_acumulado = nuevos + historial
    
    # Obtener resumen IA (Solo si hay nuevos para ahorrar cuota)
    resumen = await obtener_resumen_ia(nuevos) if nuevos else None

    # Generar salidas
    publicar_contenidos(total_acumulado, nuevos, resumen)

    if nuevos:
        # Telegram
        if CONFIG["BOT_TOKEN"] and CONFIG["CHAT_ID"]:
            msg = f"🔔 *Novedades Tech {datetime.now().strftime('%d/%m')}*\n\n"
            for n in nuevos[:6]:
                msg += f"🔹 *{n['fuente']}*: {n['titulo']}\n🔗 [Ver]({n['enlace']})\n\n"
            requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", 
                          json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"})

        # Guardar historial actualizado
        with open(archivo_h, 'w') as f:
            json.dump(total_acumulado[:500], f, indent=4)
        print(f"✅ {len(nuevos)} novedades procesadas.")
    else:
        print("☕ Sin noticias nuevas. Web actualizada con historial.")

if __name__ == "__main__":
    asyncio.run(main())