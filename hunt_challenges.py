import os, json, re, asyncio, requests
from bs4 import BeautifulSoup
from mtranslate import translate
from datetime import datetime
from google import genai
from constants_downloadfile import CONFIG, WEBS_RETOS, RETO_MD_TEMPLATE # Tu config original intacta

async def enviar_telegram(mensaje):
    """Envía notificación al Telegram del usuario."""
    token = CONFIG.get("BOT_TOKEN")
    chat_id = CONFIG.get("CHAT_ID")
    if token and chat_id:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": mensaje, "parse_mode": "Markdown"})

async def obtener_solucion_ia(titulo, nombre, client):
    prompt = f"Resuelve el reto técnico: {titulo} de {nombre}. Explica en español pero mantén términos técnicos en inglés (array, push, async, etc). JSON requerido: descripcion, paso1, paso2, paso3, codigo, lenguaje."
    response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
    return json.loads(re.sub(r'```json|```', '', response.text).strip())

async def hunt():
    client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
    folder = "./auto-challenges"
    os.makedirs(folder, exist_ok=True)
    
    retos_nuevos = []
    
    for nombre, config in WEBS_RETOS.items():
        try:
            r = requests.get(config["url"], timeout=15)
            soup = BeautifulSoup(r.text, 'html.parser')
            items = soup.select(config["selector"])[:5] 
            
            for i in items:
                titulo_es = translate(i.get_text(strip=True), 'es')
                slug = f"reto-{re.sub(r'[^a-z0-9]', '-', titulo_es.lower())[:40]}"
                path = f"{folder}/{slug}.md"
                
                if not os.path.exists(path):
                    sol = await obtener_solucion_ia(titulo_es, nombre, client)
                    if sol:
                        res = RETO_MD_TEMPLATE.replace("{titulo}", titulo_es)\
                            .replace("{resumen_corto}", sol.get('descripcion','')[:150]+"...")\
                            .replace("{fecha_pub}", datetime.now().strftime("%Y-%m-%d"))\
                            .replace("{slug_name}", slug)\
                            .replace("{tags_seo}", f"['{sol.get('lenguaje','ia').lower()}', 'retos']")\
                            .replace("{descripcion_ia}", sol.get('descripcion',''))\
                            .replace("{paso_1}", sol.get('paso1',''))\
                            .replace("{paso_2}", sol.get('paso2',''))\
                            .replace("{paso_3}", sol.get('paso3',''))\
                            .replace("{codigo_solucion}", sol.get('codigo',''))
                        
                        with open(path, "w", encoding="utf-8") as f: f.write(res)
                        retos_nuevos.append(titulo_es)
                        print(f"✅ Nuevo reto: {slug}")
                        await asyncio.sleep(3)
        except Exception as e: print(f"⚠️ Error en {nombre}: {e}")

    # Notificar si se cazaron nuevos retos
    if retos_nuevos:
        lista_retos = "\n".join([f"- {n}" for n in retos_nuevos])
        await enviar_telegram(f"🏹 *¡Cacería exitosa!* He encontrado {len(retos_nuevos)} nuevos retos:\n{lista_retos}")

if __name__ == "__main__":
    asyncio.run(hunt())