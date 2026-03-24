import os
import requests
import json
from playwright.sync_api import sync_playwright

# Configuración
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CACHE_FILE = "netflix_cache.json"

def enviar_telegram(nombre, rating, desc, img_url):
    """
    Envía una notificación a Telegram. 
    Usa HTML para evitar errores de parseo y valida la URL de la imagen.
    """
    # 1. Limpieza de la URL de la imagen (Netflix usa a veces // o /)
    if img_url:
        if img_url.startswith('//'):
            img_url = f"https:{img_url}"
        elif img_url.startswith('/'):
            img_url = f"https://www.netflix.com{img_url}"
    
    # 2. Configuración de URLs de la API
    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    url_foto = f"https://api.telegram.org/bot{token}/sendPhoto"
    url_texto = f"https://api.telegram.org/bot{token}/sendMessage"

    # 3. Formateo del mensaje en HTML (Más robusto que Markdown)
    mensaje = (
        f"<b>🔔 ¡ACTUALIZACIÓN DETECTADA!</b>\n\n"
        f"🎬 <b>Serie:</b> {nombre}\n"
        f"🔞 <b>Clasificación:</b> {rating}\n"
        f"📝 <b>Detalles:</b> {desc}"
    )

    try:
        # Intentamos enviar FOTO si hay una URL válida
        if img_url and img_url.startswith('http'):
            payload = {
                "chat_id": chat_id,
                "photo": img_url,
                "caption": mensaje,
                "parse_mode": "HTML"
            }
            response = requests.post(url_foto, json=payload)
        else:
            # Si no hay imagen, enviamos solo texto para evitar el Error 400
            raise ValueError("Imagen no válida, usando modo texto.")

        # Si el envío de la foto falla (ej. Telegram no puede descargarla), pasamos a texto
        if response.status_code != 200:
            print(f"⚠️ Falló envío de foto ({response.status_code}), reintentando solo texto...")
            raise ConnectionError("Reintento en modo texto")

    except Exception:
        # PLAN B: Enviar solo el texto
        payload = {
            "chat_id": chat_id,
            "text": mensaje,
            "parse_mode": "HTML"
        }
        response = requests.post(url_texto, json=payload)

    # Verificación final
    if response.status_code == 200:
        print(f"✅ Notificación enviada para {nombre}")
    else:
        print(f"❌ Error crítico en Telegram: {response.status_code} - {response.text}")
        
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
