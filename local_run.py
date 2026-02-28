import os
import http.server
import socketserver
import webbrowser
import threading
import time
from dotenv import load_dotenv

def run_scraper():
    # Cargamos las variables del .env
    load_dotenv()
    
    # Para evitar que toque 'auto-news', le decimos al script 
    # que no envíe correos ni genere posts (simulando que no hay 'nuevos')
    # O simplemente ejecutamos el script principal. 
    print("🚀 Ejecutando scraper...")
    import downloadFile 
    # Al importar y ejecutar main(), se generará el index.html
    import asyncio
    asyncio.run(downloadFile.main())

def serve_local():
    PORT = 8000
    Handler = http.server.SimpleHTTPRequestHandler
    
    # Permitir reutilizar el puerto si cerramos y abrimos rápido
    socketserver.TCPServer.allow_reuse_address = True
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🌍 Servidor local activo en: http://localhost:{PORT}")
        print("💡 Presiona CTRL+C para detener el servidor.")
        
        # Abrir el navegador tras un segundo para dar tiempo al server
        threading.Timer(1.5, lambda: webbrowser.open(f"http://localhost:{PORT}")).start()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Servidor detenido.")
            httpd.server_close()

if __name__ == "__main__":
    # 1. Ejecutar el proceso de descarga/generación de index.html
    run_scraper()
    
    # 2. Servir el resultado
    serve_local()














import os, json, re, requests, asyncio
from datetime import datetime, timedelta
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

# Palabras clave para el filtro de Becas/IA/Tech
TECH_KEYWORDS = ['beca', 'curso', 'ayuda', 'formación', 'ia', 'inteligencia artificial', 'tecnología', 'programación', 'empleo', 'valencia', 'albaida']

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://www.youtube.com/@xatakatv/videos"},
    "Genbeta": {"url":"https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
}

for nombre in list(FUENTES):
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
        
        .filter-section {{ background: white; padding: 15px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        .chip-container {{ display: flex; flex-wrap: wrap; gap: 8px; margin-top: 10px; }}
        
        .chip {{ display: inline-flex; align-items: center; cursor: pointer; transition: all 0.2s; padding: 6px 12px; border-radius: 50px; background: #f1f1f1; border: 1px solid #ccc; font-size: 13px; }}
        .chip-img {{ width: 24px; height: 24px; border-radius: 50%; margin-right: 8px; object-fit: cover; }}
        .chip.active {{ background: #007bff !important; color: white !important; border-color: #0056b3; }}

        .video-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; }}
        .card {{ background: white; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }}
        .card img {{ width: 100%; aspect-ratio: 16/9; object-fit: cover; }}
        .card.tipo-shorts {{ max-width: 200px; }}
        .card.tipo-shorts img {{ aspect-ratio: 9/16; }}
        
        .card-content {{ padding: 12px; }}
        .meta {{ font-size: 0.75em; color: #65676b; font-weight: bold; text-transform: uppercase; }}
        .news-list {{ list-style: none; padding: 0; display: grid; gap: 10px; }}
        .news-item {{ background: white; padding: 15px; border-radius: 8px; border-left: 5px solid #007bff; }}
        a {{ color: #007bff; text-decoration: none; font-weight: bold; }}
    </style>
    <title>Tech Dashboard</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <img src="./optimizado/Image.png" alt="Logo" style="height:50px;">
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

        <h2>📺 Multimedia</h2>
        <div class="video-grid">{bloque_videos}</div>
        
        <h2>📰 Noticias</h2>
        <ul class="news-list">{bloque_noticias}</ul>
    </div>

    <script>
        let selSemana = {{ ini: 'all', fin: 'all' }};
        let selCanal = 'all';

        function filtrarSemana(el) {{
            const chips = el.parentElement.querySelectorAll('.chip');
            chips.forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            selSemana.ini = el.getAttribute('data-inicio');
            selSemana.fin = el.getAttribute('data-fin');
            aplicarFiltros();
        }}

        function filtrarCanal(canal, el) {{
            const chips = el.parentElement.querySelectorAll('.chip');
            chips.forEach(c => c.classList.remove('active'));
            el.classList.add('active');
            selCanal = canal;
            aplicarFiltros();
        }}

        function aplicarFiltros() {{
            document.querySelectorAll('.card, .news-item').forEach(item => {{
                const itemTS = new Date(item.getAttribute('data-ts'));
                const itemFuente = item.getAttribute('data-fuente');

                const okSemana = (selSemana.ini === 'all') || 
                                 (itemTS >= new Date(selSemana.ini) && itemTS <= new Date(selSemana.fin));
                const okCanal = (selCanal === 'all') || (itemFuente === selCanal);

                item.style.display = (okSemana && okCanal) ? 'block' : 'none';
            }});
        }}

        window.onload = () => {{
            const activeWeek = document.querySelector('.chip[data-inicio]:not([data-inicio="all"]).active');
            if(activeWeek) filtrarSemana(activeWeek);
        }};
    </script>
</body>
</html>
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
        if nombre in self.avatars: return self.avatars[nombre]
        try:
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                self.avatars[nombre] = meta_img['content']
                return meta_img['content']
        except: pass
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
                items = soup.select('article, .post, .entry, h2, h3')[:10]
                for i in items:
                    link = i.find('a', href=True)
                    if not link: continue
                    t_raw = link.get_text(strip=True).replace('"', '')
                    
                    # FILTRO DE PALABRAS CLAVE (Becas, IA, etc)
                    if any(k in t_raw.lower() for k in TECH_KEYWORDS):
                        results.append({
                            "titulo": translate(t_raw, 'es'),
                            "enlace": urljoin(target, link['href']),
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
            contents=f"Resume estas noticias en 3 párrafos cortos: {texto}"
        )
        return response.text
    except: return "Resumen no disponible."

def publicar_contenidos(historial, nuevos, resumen_ia, scr):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    
    # --- GENERAR CHIPS DE SEMANAS ---
    bloque_semanas = ""
    for i in range(4):
        inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
        inicio = inicio.replace(hour=0, minute=0, second=0)
        fin = inicio + timedelta(days=6, hours=23, minutes=59)
        clase_activa = "active" if i == 0 else ""
        txt = f"Semana {inicio.strftime('%d/%m')} - {fin.strftime('%d/%m')}"
        bloque_semanas += f'<div class="chip {clase_activa}" data-inicio="{inicio.isoformat()}" data-fin="{fin.isoformat()}" onclick="filtrarSemana(this)">{txt}</div>'
    bloque_semanas += '<div class="chip" data-inicio="all" onclick="filtrarSemana(this)">Historial Completo</div>'

    # --- GENERAR CHIPS DE CANALES ---
    bloque_chips = '<div class="chip active" data-filtro="all" onclick="filtrarCanal(\'all\', this)">Todos</div>'
    canales_vistos = []
    for n, info in FUENTES.items():
        nombre_c = n.replace(" Shorts", "")
        if nombre_c not in canales_vistos:
            img_url = scr.obtener_avatar_canal(nombre_c, info.get("yt") or info.get("url"))
            bloque_chips += f'<div class="chip" data-filtro="{nombre_c}" onclick="filtrarCanal(\'{nombre_c}\', this)"><img src="{img_url}" class="chip-img">{nombre_c}</div>'
            canales_vistos.append(nombre_c)

    v_html, n_html, email_list = "", "", ""
    for n in historial[:300]:
        fuente_id = n['fuente'].replace(" Shorts", "")
        ts = n.get('ts', ahora.isoformat())
        meta = f"{n['fuente']} | {n['f']}"
        
        if n.get('id_video'):
            clase = "tipo-shorts" if n.get('tipo') == "shorts" else "tipo-video"
            v_html += f"""
            <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_id}">
                <a href="{n['enlace']}" target="_blank"><img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg"></a>
                <div class="card-content">
                    <div class="meta">{meta}</div>
                    <a href="{n['enlace']}">{n['titulo']}</a>
                </div>
            </div>"""
        else:
            n_html += f'<li class="news-item" data-ts="{ts}" data-fuente="{fuente_id}"><div class="meta">{meta}</div><a href="{n["enlace"]}">{n["titulo"]}</a></li>'
            # EMAIL: Solo noticias de texto (NO YouTube)
            if nuevos and n in nuevos:
                email_list += f"<li><b>{n['fuente']}</b>: <a href='{n['enlace']}'>{n['titulo']}</a></li>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_ia, bloque_semanas=bloque_semanas, bloque_chips=bloque_chips, bloque_videos=v_html, bloque_noticias=n_html))

    if nuevos and CONFIG["MAIL_KEY"]:
        try:
            requests.post(f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages",
                auth=("api", CONFIG["MAIL_KEY"]),
                data={{"from": f"Tech Pulse <postmaster@{CONFIG['MAIL_DOMAIN']}>", "to": [CONFIG["EMAIL_TO"]], 
                        "subject": f"🚀 Reporte Tech {fecha_h}", "html": f"<ul>{email_list}</ul>"}})
        except: pass

async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos if n['enlace'] not in vistos]
    total = nuevos + historial

    resumen = await obtener_resumen_ia(nuevos)
    publicar_contenidos(total, nuevos, resumen, scr)
    scr.guardar_avatars()

    if nuevos:
        with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4)

if __name__ == "__main__":
    asyncio.run(main())