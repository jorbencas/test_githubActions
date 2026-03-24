import os
import requests
import json
from playwright.sync_api import sync_playwright

# Configuración
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CACHE_FILE = "netflix_cache.json"
SERIES = {
    "La Dama del Armiño": "82152349",
    "Berlín": "81584733",
    "La casa de papel": "80192017"
}

def enviar_telegram(nombre, rating, desc, img_url):
    """Envía la tarjeta a Telegram usando HTML y manejando errores de imagen"""
    # Limpieza de URL de imagen
    if img_url and img_url.startswith('//'):
        img_url = f"https:{img_url}"
    
    msg = (f"<b>🔔 ¡CAMBIO DETECTADO!</b>\n\n"
           f"🎬 <b>Serie:</b> {nombre}\n"
           f"🔞 <b>Rating:</b> {rating}\n"
           f"📝 <b>Info:</b> {desc}")

    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    
    try:
        if img_url:
            # Intentar enviar con foto
            r = requests.post(f"{base_url}/sendPhoto", json={
                "chat_id": TELEGRAM_CHAT_ID, "photo": img_url, "caption": msg, "parse_mode": "HTML"
            })
            if r.status_code == 200: return
        
        # Si no hay foto o falla el envío de foto, enviar solo texto
        requests.post(f"{base_url}/sendMessage", json={
            "chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"
        })
    except Exception as e:
        print(f"Error enviando Telegram: {e}")
        
def main():
    # 1. Cargar cache (el "if -f" de Python)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Importante: El user_agent evita que Netflix nos bloquee de entrada
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
        page = context.new_page()

        for nombre, n_id in SERIES.items():
            url = f"https://www.netflix.com/es/title/{n_id}"
            print(f"🕵️  Extrayendo datos de: {nombre}...")
            
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=60000)
                
                # --- EXTRACCIÓN REAL CON PLAYWRIGHT ---
                # Esperamos a que el elemento del rating sea visible
                page.wait_for_selector('.maturity-number', timeout=10000)
                
                rating_actual = page.locator('.maturity-number').first.inner_text().strip()
                desc_actual = page.locator('.maturity-description').first.inner_text().strip()
                
                # Buscamos la imagen del póster
                img_element = page.locator('img.nm-collections-title-img').first
                img_url = img_element.get_attribute('src') if img_element.is_visible() else None

                # --- LÓGICA DE COMPARACIÓN ---
                last_rating = cache.get(n_id, {}).get('rating')

                if rating_actual != last_rating:
                    print(f"📢 ¡Novedad en {nombre}! {last_rating} -> {rating_actual}")
                    enviar_telegram(nombre, rating_actual, desc_actual, img_url)
                    
                    # Actualizar cache
                    cache[n_id] = {"rating": rating_actual, "name": nombre}
                else:
                    print(f"✅ {nombre} sin cambios.")

            except Exception as e:
                print(f"❌ Error procesando {nombre}: {e}")

        # 2. Guardar Memoria actualizada
        with open(CACHE_FILE, 'w') as f:
            json.dump(cache, f, indent=4)
            
        browser.close()

if __name__ == "__main__":
    main()
