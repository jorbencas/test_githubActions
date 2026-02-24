import os, sys, json, subprocess, platform, re, requests, asyncio
from datetime import datetime
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from mtranslate import translate
import google.generativeai as genai

# --- 2. CONFIGURACIÓN ---
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

# --- 3. SCRAPER CON TRY-EXCEPT ---
class ScraperPro:
    def safe_request(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, timeout=15, headers=headers)
            r.raise_for_status()
            return r.text
        except Exception as e:
            print(f"❌ Error de conexión en {url}: {e}")
            return None

    def extraer(self, nombre, info):
        results = []
        html = self.safe_request(info.get("yt") or info.get("url"))
        if not html: return []

        try:
            if "yt" in info:
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\],"accessibility"', html)
                ids = re.findall(r'"videoId":"(.*?)"', html)
                for t, i in zip(titles[:3], ids[:3]):
                    results.append({"titulo": t, "enlace": f"https://youtube.com/watch?v={i}", "fuente": nombre, "tipo": "video"})
            else:
                soup = BeautifulSoup(html, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a')[:5]
                tipo = "beca" if "beca" in nombre.lower() else "noticia"
                for i in items:
                    results.append({"titulo": i.get_text(strip=True), "enlace": urljoin(info["url"], i.get('href')), "fuente": nombre, "tipo": tipo})
        except Exception as e:
            print(f"⚠️ Error procesando contenido de {nombre}: {e}")
        return results

# --- 4. COMUNICACIÓN BLINDADA ---
async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"]: return "Análisis no disponible."
    try:
        genai.configure(api_key=CONFIG["GEMINI_KEY"])
        model = genai.GenerativeModel('gemini-pro')
        
        # AQUÍ USAMOS TRANSLATE:
        # Traducimos la lista de títulos al español para que la IA entienda todo perfectamente
        texto_para_ia = ""
        for n in noticias[:12]:
            titulo_es = translate(n['titulo'], 'es') # Traduce cada título a español
            texto_para_ia += f"- {titulo_es}. "

        prompt = f"Actúa como analista tech. Resume estas noticias en 3 párrafos profesionales: {texto_para_ia}"
        response = model.generate_content(prompt)
        return response.text
    except:
        return "Error procesando el resumen con IA."

def enviar_telegram(noticias):
    try:
        if not CONFIG["BOT_TOKEN"]: return
        msg = "🛰️ **NOVEDADES**\n\n" + "\n".join([f"• {n['titulo']} [Link]({n['enlace']})" for n in noticias[:8]])
        requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendMessage", json={"chat_id": CONFIG["CHAT_ID"], "text": msg, "parse_mode": "Markdown"}, timeout=10)
    except: print("⚠️ Falló envío a Telegram.")

def enviar_email(resumen, becas):
    try:
        if not CONFIG["MAIL_KEY"]: return
        html = f"<h2>🤖 Resumen IA</h2><p>{resumen}</p><h2>🎓 Becas</h2><ul>"
        for b in becas: html += f'<li><a href="{b["enlace"]}">{b["titulo"]}</a></li>'
        requests.post(f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages", auth=("api", CONFIG["MAIL_KEY"]),
            data={"from": "Bot <postmaster@" + CONFIG['MAIL_DOMAIN'] + ">", "to": [CONFIG["EMAIL_TO"]], "subject": "🚀 Reporte Tech", "html": html + "</ul>"}, timeout=15)
    except Exception as e: print(f"⚠️ Error Mailgun: {e}")

# --- 5. GENERACIÓN DE ARCHIVOS ---
def salvar_datos(nuevos, resumen):
    try:
        # index.html (Surge)
        with open("index.html", "w", encoding="utf-8") as f:
            f.write(f"<html><body><h1>Dashboard</h1><p>{resumen}</p>")
            for n in nuevos: f.write(f"<p>{n['fuente']}: <a href='{n['enlace']}'>{n['titulo']}</a></p>")
            f.write("</body></html>")
        
        # Astro .md
        os.makedirs("./auto-news", exist_ok=True)
        with open(f"./auto-news/reporte-{datetime.now().strftime('%Y-%m-%d')}.md", "w", encoding="utf-8") as f:
            f.write(f"---\ntitle: 'Reporte'\nlayout: '../../layouts/PostLayout.astro'\n---\n\n{resumen}")
    except Exception as e: print(f"⚠️ Error guardando archivos: {e}")

# --- 6. MAIN ---
async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = "all_news.json"
    try:
        h = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    except: h = []

    vistos = {x['enlace'] for x in h}
    nuevos = [n for n in datos if n['enlace'] not in vistos]

    if nuevos:
        resumen = await obtener_resumen_ia(nuevos)
        becas = [n for n in nuevos if n['tipo'] == "beca"]
        
        enviar_telegram(nuevos)
        enviar_email(resumen, becas)
        salvar_datos(nuevos, resumen)
        
        try:
            with open(archivo_h, 'w') as f: json.dump((nuevos + h)[:200], f, indent=4)
        except: pass
        print("✅ Fin.")
    else: print("☕ Sin cambios.")

if __name__ == "__main__":
    asyncio.run(main())