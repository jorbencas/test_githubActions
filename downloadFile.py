import os, json, re, requests, asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from mtranslate import translate
import google.generativeai as genai

# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TOKEN_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER")
}

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Xataka": {"url": "https://www.xataka.com/"},
    "Becas": {"url": "https://www.becas.com/noticias/"}
}

# --- 2. MOTOR DE SCRAPING SEGURO ---
class ScraperPro:
    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            r = requests.get(target, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if r.status_code != 200: return []
            
            if "yt" in info:
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\],"accessibility"', r.text)
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                for t, i in zip(titles[:3], ids[:3]):
                    # TRADUCCIÓN Y LIMPIEZA INMEDIATA
                    t_es = translate(t, 'es').replace('"', '') 
                    results.append({"titulo": t_es, "enlace": f"https://youtube.com/watch?v={i}", "fuente": nombre, "tipo": "video"})
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a')[:5]
                tipo = "beca" if "beca" in nombre.lower() else "noticia"
                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '') # Quitar comillas para evitar error YAML
                    t_es = translate(t_raw, 'es')
                    results.append({"titulo": t_es, "enlace": urljoin(target, i.get('href')), "fuente": nombre, "tipo": tipo})
        except: pass
        return results

# --- 3. LÓGICA DE IA ---
async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"]: return "Análisis no disponible."
    try:
        genai.configure(api_key=CONFIG["GEMINI_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        texto_noticias = ". ".join([n['titulo'] for n in noticias[:12]])
        prompt = f"Resume estas noticias en 3 párrafos profesionales en ESPAÑOL: {texto_noticias}"
        return model.generate_content(prompt).text
    except: return "Error en la IA."

# --- 4. ENVÍOS (CORREGIDO MAILGUN) ---
def distribuir_datos(nuevos, resumen, becas):
    # Telegram (Ahora forzado en Español y sin comillas rotas)
    if CONFIG["BOT_TOKEN"]:
        try:
            msg = f"🛰️ **REPORTE {datetime.now().strftime('%d/%m')}**\n\n"
            for n in nuevos[:8]:
                msg += f"• {n['titulo']}\n  🔗 [Enlace]({n['enlace']})\n\n"
            requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", 
                          json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"}, timeout=10)
        except: print("⚠️ Error Telegram")

    # Email (Mailgun) - Verificado
    if CONFIG["MAIL_KEY"] and CONFIG["MAIL_DOMAIN"]:
        try:
            html = f"<html><body><h2>🤖 Resumen IA</h2><p>{resumen}</p><h2>🎓 Becas</h2><ul>"
            for b in becas: html += f'<li><a href="{b["enlace"]}">{b["titulo"]}</a></li>'
            html += "</ul></body></html>"
            
            r = requests.post(f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages", 
                auth=("api", CONFIG["MAIL_KEY"]),
                data={"from": f"News Bot <postmaster@{CONFIG['MAIL_DOMAIN']}>", 
                      "to": [CONFIG["EMAIL_TO"]], 
                      "subject": f"🚀 Reporte Tech {datetime.now().strftime('%d/%m')}", 
                      "html": html}, timeout=15)
            print(f"Status Mailgun: {r.status_code}")
        except Exception as e: print(f"⚠️ Error Mailgun: {e}")

# --- 5. MAIN ---
async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = "all_news.json"
    h = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    vistos = {x['enlace'] for x in h}
    nuevos = [n for n in datos if n['enlace'] not in vistos]

    if nuevos:
        resumen = await obtener_resumen_ia(nuevos)
        becas = [n for n in nuevos if n['tipo'] == "beca"]
        
        distribuir_datos(nuevos, resumen, becas)
        
        # Generar index.html y Markdown (LIMPIANDO TÍTULOS PARA YAML)
        try:
            with open("index.html", "w", encoding="utf-8") as f:
                f.write(f"<html><body style='font-family:sans-serif;background:#121212;color:white;'>")
                f.write(f"<h1>Dashboard</h1><p>{resumen}</p>")
                for n in nuevos: f.write(f"<p><a href='{n['enlace']}' style='color:#00d4ff;'>{n['titulo']}</a></p>")
                f.write("</body></html>")
            
            os.makedirs("./auto-news", exist_ok=True)
            fecha = datetime.now().strftime("%Y-%m-%d")
            with open(f"./auto-news/reporte-{fecha}.md", "w", encoding="utf-8") as f:
                # Usamos comillas simples para el título de Astro para evitar conflictos con comillas dobles
                f.write(f"---\ntitle: '{nuevos[0]['titulo']}'\nlayout: '../../layouts/PostLayout.astro'\n---\n\n{resumen}")
        except: pass

        with open(archivo_h, 'w') as f: json.dump((nuevos + h)[:200], f, indent=4)
        print("✅ Proceso completado.")
    else: print("☕ Sin novedades.")

if __name__ == "__main__":
    asyncio.run(main())