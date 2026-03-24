import os
import requests
import json
from playwright.sync_api import sync_playwright

# Configuración
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CACHE_FILE = "netflix_cache.json"

def enviar_a_telegram(nombre, rating, descripcion, url_imagen):
    """Envía una foto con un pie de página formateado"""
    url_api = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    
    mensaje = (
        f"🔔 *¡CAMBIO DETECTADO!*\n\n"
        f"🎬 *Serie:* {nombre}\n"
        f"🔞 *Nuevo Rating:* {rating}\n"
        f"📝 *Info:* {descripcion}"
    )
    
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "photo": url_imagen if url_imagen else "https://via.placeholder.com/400x600?text=Netflix",
        "caption": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url_api, json=payload)
        response.raise_for_status()
        print(f"🚀 Notificación enviada para {nombre}")
    except Exception as e:
        print(f"❌ Error al enviar a Telegram: {e}")

def main():
    # 1. Cargar cache (el "if -f" de Python)
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            cache = json.load(f)
    else:
        cache = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # ... (aquí iría tu bucle de SERIES y la extracción de datos) ...
        # Supongamos que extraemos estos datos de "Berlín":
        nombre_extraido = "Berlín"
        id_serie = "81584733"
        rating_actual = "16+" 
        desc_actual = "Violencia, lenguaje descortés"
        img_extraida = "https://example.com/poster_berlin.jpg"

        # 2. COMPARACIÓN CRÍTICA
        last_rating = cache.get(id_serie, {}).get('rating')

        if rating_actual != last_rating:
            # ¡SOLO ENVIAMOS SI ES DIFERENTE!
            enviar_a_telegram(nombre_extraido, rating_actual, desc_actual, img_extraida)
            
            # 3. Actualizar la memoria
            cache[id_serie] = {"rating": rating_actual}
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f)
        else:
            print(f"Sigue igual ({rating_actual}), no molesto por Telegram.")

        browser.close()

if __name__ == "__main__":
    main()
