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
    "Codigo facilito": {"yt": "https://youtube.com/@codigofacilito?si=vEBAZLbRsySBwr-w"},
    "Carlos Azaustre": {"yt": "https://www.youtube.com/@CarlosAzaustre/videos"},
    "Clipset": {"yt": "https://www.youtube.com/@clipset/videos"},
    "Codely": {"yt": "https://www.youtube.com/@CodelyTV/videos"},
    "EDteam": {"yt": "https://www.youtube.com/@EDteam/videos"},
    "Fazt": {"yt": "https://www.youtube.com/@FaztTech/videos"},
    "FreeCodeCamp": {"yt": "https://www.youtube.com/@freecodecamp/videos"},
    "HolaMundo": {"yt": "https://youtube.com/@holamundodev?si=96mb2LLLAE8HlYQN"},
    "Kiko palomares": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Victor Robles": {"yt": "https://youtube.com/@victorroblesweb?si=Lbdm1hvF0rd8ovgi"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://youtube.com/@xatakatv?si=LVD_3XvpoVPdAZNT"},
    "Becas": {"url": "https://www.becas.com/noticias/"},
    "Genbeta": {"url":"https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
}

# Añadir versiones de SHORTS para los canales principales
canales_con_shorts = ["MoureDev", "Midudev", "Carlos Azaustre", "Fazt", "EDteam"]
for canal in canales_con_shorts:
    url_base = FUENTES[canal]["yt"].replace("/videos", "/shorts")
    FUENTES[f"{canal} Shorts"] = {"yt": url_base}
    
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
        body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: #f0f2f5; color: #1c1e21; }}
        .container {{ max-width: 1000px; margin: 0 auto; }}
        header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #007bff; padding-bottom: 10px; margin-bottom: 30px; }}
        .ia-box {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); border-left: 6px solid #8e44ad; margin-bottom: 30px; line-height: 1.6; }}
        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; height: 160px; object-fit: cover; background: #ddd; }}
        .card-content {{ padding: 15px; }}
        .meta {{ font-size: 0.8em; color: #65676b; font-weight: bold; margin-bottom: 5px; }}
        .news-list {{ list-style: none; padding: 0; }}
        .news-item {{ background: white; margin-bottom: 10px; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; box-shadow: 0 1px 2px rgba(0,0,0,0.1); }}
        a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
        .logo {{ height: 50px; }}
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
        <h2>📺 Últimos Vídeos y Shorts</h2>
        <div class="video-grid">{bloque_videos}</div>
        <h2>📰 Noticias</h2>
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
{contenido}

### 🔗 Enlaces
{lista_enlaces}
"""

# --- 3. FUNCIONES ---

class ScraperPro:
    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            r = requests.get(target, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200: return []
            if "yt" in info:
                # Detectar IDs de video y shorts
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                clean_ids = list(dict.fromkeys(ids))
                for t, i in zip(titles[:5], clean_ids[:5]):
                    # Si la URL original tenía "shorts", el enlace debe ser de shorts
                    tipo_link = "shorts" if "shorts" in target else "watch?v="
                    results.append({
                        "titulo": translate(t.replace('"', ''), 'es'),
                        "enlace": f"https://youtube.com/{tipo_link}{i}" if "shorts" in tipo_link else f"https://youtube.com/watch?v={i}",
                        "id_video": i, "fuente": nombre, "tipo": "video",
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
    if not CONFIG["GEMINI_KEY"] or not noticias: return "No hay noticias nuevas para resumir."
    try:
        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        texto = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=f"Resume estas noticias en 3 párrafos en español: {texto}"
        )
        return response.text
    except Exception as e:
        print(f"Aviso IA (Probable cuota agotada): {e}")
        return "Resumen no disponible por límite de cuota de IA. Consulta los enlaces abajo."

def publicar_contenidos(historial, nuevos, resumen_ia):
    fecha_h = datetime.now().strftime("%d/%m/%Y")
    fecha_iso = datetime.now().strftime("%Y-%m-%d")
    
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    v_html, n_html, md_list = "", "", ""
    resumen_final = resumen_ia if resumen_ia else "Actualización de noticias."

    for n in historial[:100]:
        meta = f"{n['fuente']} | {n.get('f', '--/--')}"
        if n.get('tipo') == "video" and n.get('id_video'): # Validación extra para evitar KeyError
            v_html += f"""
            <div class="card">
                <img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg">
                <div class="card-content">
                    <div class="meta">{meta}</div>
                    <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
                </div>
            </div>"""
        else:
            n_html += f'<li class="news-item"><div class="meta">{meta}</div><a href="{n["enlace"]}">{n["titulo"]}</a></li>'

    # Guardar Web
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_final, bloque_videos=v_html, bloque_noticias=n_html))

    # Guardar MD si hay nuevos
    if nuevos:
        for n in nuevos: md_list += f"- **{n['fuente']}**: [{n['titulo']}]({n['enlace']})\n"
        titulo_md = nuevos[0]['titulo'].replace("'", "")
        with open(f"./auto-news/reporte-{fecha_iso}.md", "w", encoding="utf-8") as f:
            f.write(MD_TEMPLATE.format(titulo=titulo_md, fecha_iso=fecha_iso, contenido=resumen_final, lista_enlaces=md_list))

# --- 4. MAIN ---
async def main():
    scr = ScraperPro()
    datos_actuales = []
    for nombre, info in FUENTES.items(): datos_actuales += scr.extraer(nombre, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos_actuales if n['enlace'] not in vistos]
    total_acumulado = nuevos + historial

    resumen = await obtener_resumen_ia(nuevos) if nuevos else "Sin novedades hoy."
    
    # Esta función ahora es segura contra KeyErrors y fallos de IA
    publicar_contenidos(total_acumulado, nuevos, resumen)

    if nuevos:
        if CONFIG["BOT_TOKEN"] and CONFIG["CHAT_ID"]:
            msg = f"🔔 *Novedades Tech*\n\n" + "\n".join([f"• {n['fuente']}: {n['titulo']}" for n in nuevos[:5]])
            requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", 
                          json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"})

        with open(archivo_h, 'w') as f: json.dump(total_acumulado[:500], f, indent=4)
        print(f"✅ Procesado con {len(nuevos)} noticias nuevas.")
    else:
        print("☕ Todo al día.")

if __name__ == "__main__":
    asyncio.run(main())
