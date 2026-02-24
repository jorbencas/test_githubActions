import os, json, re, requests, asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from mtranslate import translate
from google import genai # <-- Cambio de importación
# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TELEGRAM_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "FOLDER": "files" # Carpeta para el JSON
}

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Xataka": {"url": "https://www.xataka.com/"},
    "Becas": {"url": "https://www.becas.com/noticias/"}
}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)

class ScraperPro:
    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            r = requests.get(target, timeout=15, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            if r.status_code != 200: return []
            
            if "yt" in info:
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\],"accessibility"', r.text)
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                for t, i in zip(titles[:3], ids[:3]):
                    t_clean = t.replace('"', '').replace("'", "")
                    t_es = translate(t_clean, 'es')
                    results.append({
                        "titulo": t_es, 
                        "enlace": f"https://youtube.com/watch?v={i}", 
                        "id_video": i, # Guardamos el ID para la miniatura
                        "fuente": nombre, 
                        "tipo": "video"
                    })
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a')[:5]
                tipo = "beca" if "beca" in nombre.lower() else "noticia"
                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '').replace("'", "")
                    t_es = translate(t_raw, 'es')
                    results.append({
                        "titulo": t_es, 
                        "enlace": urljoin(target, i.get('href')), 
                        "fuente": nombre, 
                        "tipo": tipo
                    })
        except: pass
        return results

async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"]: return None
    try:
        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        texto_noticias = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
        prompt = f"Actúa como analista tech. Resume estas noticias en 3 párrafos profesionales en español: {texto_noticias}"        

        # Nueva forma de generar contenido
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        return response.text
    except Exception as e:
        print(f"Error IA: {e}")
        return "Error generando resumen."

# --- GENERACIÓN DE WEB (CON VÍDEOS) ---
def generar_index(nuevos, resumen):
    try:
        videos = [n for n in nuevos if n['tipo'] == "video"]
        otros = [n for n in nuevos if n['tipo'] != "video"]
        
        html = f"""
        <!DOCTYPE html>
        <html lang="es">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; color: #333; }}
                h1 {{ color: #222; }}
                h2 {{ color: #444; border-bottom: 2px solid #ccc; padding-bottom: 10px; margin-top: 40px; }}
                .section {{ margin-bottom: 30px; }}
                
                /* Grid para vídeos */
                .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 20px; }}
                .video-card {{ background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
                .video-card img {{ width: 100%; display: block; }}
                .video-card-content {{ padding: 10px; }}
                .video-card b {{ color: #d32f2f; font-size: 0.8em; text-transform: uppercase; }}
                
                /* Lista para noticias */
                ul {{ list-style: none; padding: 0; }}
                li {{ background: #fff; margin: 10px 0; padding: 15px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); border-left: 5px solid #007bff; }}
                
                a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
                a:hover {{ text-decoration: underline; }}
                .logo {{ width: 60px; float: right; }}
                .ia-box {{ background: #eef2f7; padding: 20px; border-radius: 10px; border: 1px solid #d1d9e6; line-height: 1.6; }}
            </style>
        </head>
        <body>
            <img src="./Image.png" alt="Logo" class="logo">
            <h1>Reporte Tecnológico <span style="font-size:0.5em; color:#666;">{datetime.now().strftime('%d/%m/%Y')}</span></h1>
            
            <div class="section">
                <h2>🤖 Resumen de Inteligencia Artificial</h2>
                <div class="ia-box">{resumen if resumen else 'No se pudo generar el resumen hoy.'}</div>
            </div>

            <div class="section">
                <h2>📺 Últimos Vídeos</h2>
                <div class="video-grid">
        """
        for v in videos:
            thumb = f"https://img.youtube.com/vi/{v['id_video']}/mqdefault.jpg"
            html += f"""
                <div class="video-card">
                    <a href="{v['enlace']}" target="_blank">
                        <img src="{thumb}" alt="Thumbnail">
                    </a>
                    <div class="video-card-content">
                        <b>{v['fuente']}</b><br>
                        <a href="{v['enlace']}">{v['titulo']}</a>
                    </div>
                </div>
            """
        
        html += """
                </div>
            </div>

            <div class="section">
                <h2>📰 Noticias y Becas</h2>
                <ul>
        """
        for o in otros:
            html += f"<li><b>{o['fuente']}</b>: <a href='{o['enlace']}'>{o['titulo']}</a></li>"
        
        html += """
                </ul>
            </div>
        </body>
        </html>
        """
        with open("index.html", "w", encoding="utf-8") as f: f.write(html)
    except Exception as e: print(f"Error web: {e}")

# --- MAIN REESTRUCTURADO ---
async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    h = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    vistos = {x['enlace'] for x in h}
    nuevos = [n for n in datos if n['enlace'] not in vistos]

    if nuevos:
        resumen = await obtener_resumen_ia(nuevos)
        
        # 1. Enviar Telegram (Diseño limpio)
        if CONFIG["BOT_TOKEN"] and CONFIG["CHAT_ID"]:
            msg = f"🔔 *Reporte Tech {datetime.now().strftime('%d/%m')}*\n\n"
            for n in nuevos[:6]:
                msg += f"🔹 *{n['fuente']}*: {n['titulo']}\n🔗 [Link]({n['enlace']})\n\n"
            requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", 
                          json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"})

        # 2. Generar Web Multimedia
        generar_index(nuevos, resumen)
        
        # 3. Guardar histórico y Astro
        os.makedirs("./auto-news", exist_ok=True)
        with open(f"./auto-news/reporte-{datetime.now().strftime('%Y-%m-%d')}.md", "w", encoding="utf-8") as f:
            t = nuevos[0]['titulo'].replace("'", "")
            f.write(f"---\ntitle: '{t}'\nlayout: '../../layouts/PostLayout.astro'\n---\n\n{resumen}")
 
        with open(archivo_h, 'w') as f: json.dump((nuevos + h)[:200], f, indent=4)
        print("✅ Éxito.")
    else: print("☕ Sin cambios.")

if __name__ == "__main__":
    asyncio.run(main())