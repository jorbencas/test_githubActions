import os, json, re, requests, asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from mtranslate import translate
from google import genai 

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TELEGRAM_API_ID"),
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

# Auto-añadir secciones de Shorts
for nombre in list(FUENTES): # Usamos list() para poder modificar el dict mientras iteramos
    if "yt" in FUENTES[nombre]:
        url_s = FUENTES[nombre]["yt"].replace("/videos", "/shorts")
        FUENTES[f"{nombre} Shorts"] = {"yt": url_s}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)
os.makedirs("./auto-news", exist_ok=True)

# --- 2. PLANTILLAS ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{ font-family: 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #1c1e21; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }}
        .ia-box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #8e44ad; margin-bottom: 30px; }}
        
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; align-items: start; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        
        /* Estilo YouTube Normal */
        .card.tipo-video img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; background: #000; }}
        /* Estilo YouTube Shorts (Vertical) */
        .card.tipo-shorts {{ max-width: 200px; }}
        .card.tipo-shorts img {{ width: 100%; aspect-ratio: 9/16; object-fit: cover; background: #000; }}
        
        .card-content {{ padding: 12px; }}
        .meta {{ font-size: 0.75em; color: #65676b; font-weight: bold; text-transform: uppercase; margin-bottom: 5px; }}
        .news-list {{ list-style: none; padding: 0; display: grid; gap: 10px; }}
        .news-item {{ background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
        a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
        .logo {{ height: 50px; }}

        .chip {{ display: inline-flex; align-items: center; cursor: pointer; transition: all 0.3s ease; padding: 5px 15px 5px 5px; border-radius: 50px; background-color: #f1f1f1; border: 1px solid #ccc; font-family: Arial, sans-serif; font-size: 14px; color: #333; }}
        .chip-img {{ width: 32px; height: 32px; border-radius: 50%; margin-right: 10px; object-fit: cover; }}
        .chip:hover {{ background-color: #e0e0e0; border-color: #999; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .chip-text {{ font-weight: 500; }}
    </style>
    <title>Tech Dashboard</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <img src="./optimizado/Image.png" alt="Logo" class="logo">
        </header>
        <div class="ia-box">
            <h2>🤖 Resumen</h2>
            <p>{resumen}</p>
        </div>
        <h2>📺 Multimedia (Vídeos y Shorts)</h2>
        {bloque_chips}
        <div class="video-grid">{bloque_videos}</div>
        <h2>📰 Noticias Históricas</h2>
        <ul class="news-list">{bloque_noticias}</ul>
    </div>
</body>
<script>
    function filtrarCanal(canal) {
        const cards = document.querySelectorAll('.card');
        cards.forEach(card => {
            if (canal === 'all') {
                card.style.display = 'block';
            } else {
                // Comparamos el data-fuente de la card con el nombre del canal del chip
                if (card.getAttribute('data-fuente') === canal) {
                    card.style.display = 'block';
                } else {
                    card.style.display = 'none';
                }
            }
        });
    }
</script>
</html>
"""

EMAIL_TEMPLATE = """
<div style="font-family: Arial; max-width: 600px; margin: 0 auto; border: 1px solid #eee; padding: 20px;">
    <h2 style="color: #8e44ad;">🤖 Resumen IA</h2>
    <p>{contenido}</p>
    <hr>
    <h2 style="color: #007bff;">📋 Enlaces del día</h2>
    <ul>{lista_email}</ul>
</div>
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

# --- 3. FUNCIONES ---

class ScraperPro:
    def __init__(self):
        self.cache_file = os.path.join(CONFIG["FOLDER"], "avatars_cache.json")
        self.avatars = self.cargar_avatars()

    def cargar_avatars(self):
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f: return json.load(f)
        return {}

    def guardar_avatars(self):
        with open(self.cache_file, 'w') as f: json.dump(self.avatars, f)

    def obtener_avatar_canal(self, nombre, url_canal):
        # Si ya lo tenemos en caché, no entramos a YouTube
        if nombre in self.avatars: return self.avatars[nombre]
        
        try:
            print(f"🔍 Buscando avatar real para: {nombre}...")
            # Limpiamos la URL para ir al home del canal
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                url_avatar = meta_img['content']
                self.avatars[nombre] = url_avatar
                return url_avatar
        except: pass
        
        # Si falla, usamos avatar por defecto y no guardamos en caché para reintentar luego
        return f"https://ui-avatars.com/api/?name={nombre}&background=random"

    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            r = requests.get(target, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200: return []
            if "yt" in info:
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                clean_ids = list(dict.fromkeys(ids))
                for t, i in zip(titles[:5], clean_ids[:5]):
                    es_short = "shorts" in target or "Shorts" in nombre
                    results.append({
                        "titulo": translate(t.replace('"', ''), 'es'),
                        "enlace": f"https://youtube.com/shorts/{i}" if es_short else f"https://youtube.com/watch?v={i}",
                        "id_video": i, "fuente": nombre.replace(" Shorts", ""), 
                        "tipo": "shorts" if es_short else "video",
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a')[:5]
                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '')
                    results.append({
                        "titulo": translate(t_raw, 'es'),
                        "enlace": urljoin(target, i.get('href')),
                        "fuente": nombre, "tipo": "noticia",
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
        except: pass
        return results

async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"] or not noticias: return "Sin novedades para resumir hoy."
    try:
        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        texto = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Resume estas noticias tecnológicas en 3 párrafos en español: {texto}"
        )
        return response.text
    except Exception as e:
        print(f"⚠️ Error Gemini (Cuota agotada): {e}")
        return "Resumen no disponible por límite de cuota en la API de Gemini. Consulta los enlaces abajo."

def obtener_avatar_canal(self, url_canal):
    try:
        r = requests.get(url_canal, timeout=10)
        # Buscamos la meta etiqueta og:image que contiene el avatar del canal
        soup = BeautifulSoup(r.text, 'html.parser')
        meta_img = soup.find("meta", property="og:image")
        return meta_img['content'] if meta_img else None
    except:
        return None

def publicar_contenidos(historial, nuevos, resumen_ia, scr ):
    fecha_h = datetime.now().strftime("%d/%m/%Y")
    fecha_pub = datetime.now().strftime("%Y/%m/%d")
    fecha_iso = datetime.now().strftime("%Y-%m-%d")
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    
    v_html, n_html, email_list, md_links = "", "", "", ""
    resumen_final = resumen_ia if resumen_ia else "Actualización diaria de tecnología."

  # --- GENERAR CHIPS DE FILTRADO ---
    chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
    chips_html += '<div class="chip" onclick="filtrarCanal(\'all\')"><span class="chip-text">Todos</span></div>'
    
    canales_vistos = []
    for n, info in FUENTES.items():
        nombre_c = n.replace(" Shorts", "")
        if "yt" in info and nombre_c not in canales_vistos:
            img_url = scr.obtener_avatar_canal(nombre_c, info["yt"])
            chips_html += f"""
            <div class="chip" onclick="filtrarCanal('{nombre_c}')">
                <img src="{img_url}" alt="{nombre_c}" class="chip-img">
                <span class="chip-text">{nombre_c}</span>
            </div>"""
            canales_vistos.append(nombre_c)
    chips_html += "</div>"

    # Generar bloques para la WEB (Acumulativo 200)
    for n in historial[:200]:
        fecha_display = f" | {n['f']}" if n.get('f') else ""
        meta = f"{n['fuente']}{fecha_display}"
        
        if n.get('id_video'):
            clase = "tipo-shorts" if n.get('tipo') == "shorts" else "tipo-video"
            v_html += f"""
            <div class="card {clase}">
                <a href="{n['enlace']}" target="_blank">
                    <img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg">
                </a>
                <div class="card-content">
                    <div class="meta">{meta}</div>
                    <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
                </div>
            </div>"""
        else:
            n_html += f'<li class="news-item"><div class="meta">{meta}</div><a href="{n["enlace"]}">{n["titulo"]}</a></li>'

    # Guardar HTML
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_final, bloque_chips=chips_html, bloque_videos=v_html, bloque_noticias=n_html))

    # Guardar MD y Email (Solo si hay nuevos)
    if nuevos:
        for n in nuevos:
            md_links += f"- **{n['fuente']}**: [{n['titulo']}]({n['enlace']})\n"
            email_list += f"<li><b>{n['fuente']}</b>: <a href='{n['enlace']}'>{n['titulo']}</a></li>"
        
        # Guardar MD
        slug = f"reporte-{fecha_iso}"
        # Creamos la variable que faltaba y limpiamos comillas para evitar errores en Astro
        resumen_corto_limpio = resumen_final[:150].replace("\\n", " ").replace('"', '') + "..."
        
        with open(f"./auto-news/{slug}.md", "w", encoding="utf-8") as f:
            # Asegúrate de que los nombres coincidan con los de tu MD_TEMPLATE
            f.write(MD_TEMPLATE.format(
                titulo=f"Reporte Tech {fecha_h}",
                resumen_corto=resumen_corto_limpio,
                fecha_pub=fecha_pub,
                slug_name=f"{slug}.md",
                contenido=resumen_final,
                lista_enlaces=md_links
            ))
        print(F"HOLA HOLA HOLA {CONFIG['EMAIL_TO']}")
        # Enviar Email
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
            except Exception as e:
                print(f"⚠️ Error al enviar a email: {e}")
                pass

async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos if n['enlace'] not in vistos]
    total = nuevos + historial

    resumen = await obtener_resumen_ia(nuevos) if nuevos else "Todo al día por ahora."
    publicar_contenidos(total, nuevos, resumen, scr)

    # Guardar la caché de avatares para la próxima vez
    scr.guardar_avatars()
    
    if nuevos:
        # TELEGRAM
        if CONFIG["BOT_TOKEN"] and CONFIG["CHAT_ID"]:
            msg = f"🔔 *Novedades Tech {datetime.now().strftime('%d/%m')}*\n\n"
            for n in nuevos[:6]:
                msg += f"🔹 *{n['fuente']}*: {n['titulo']}\n🔗 [Link]({n['enlace']})\n\n"
            try:               
                requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"})
            except Exception as e:
                print(f"⚠️ Error al enviar a telegram: {e}")
                pass

        with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4)
        print(f"✅ {len(nuevos)} noticias nuevas procesadas.")
    else:
        print("☕ Sin cambios hoy.")

if __name__ == "__main__":
    asyncio.run(main())
