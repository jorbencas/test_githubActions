import os
import requests
import json
import re
import time
from playwright.sync_api import sync_playwright
from constants_downloadfile import CONFIG

# --- CONFIGURACIÓN ---
TELEGRAM_TOKEN = CONFIG.get('BOT_TOKEN')
TELEGRAM_CHAT_ID = CONFIG.get('CHAT_ID')
CACHE_FILE = "netflix_cache.json"

SERIES = {
    "La Dama del Armiño": "82152349",
    "Berlín": "81584733",
    "La casa de papel": "80192017"
}

def enviar_telegram(nombre, rating, desc, img_url):
    """Envía la notificación usando HTML para máxima compatibilidad."""
    if img_url and img_url.startswith('//'):
        img_url = f"https:{img_url}"
    
    msg = (f"<b>🔔 ¡CAMBIO DETECTADO!</b>\n\n"
           f"🎬 <b>Serie:</b> {nombre}\n"
           f"🔞 <b>Rating:</b> {rating}\n"
           f"📝 <b>Info:</b> {desc}\n"
           f"🔗 <a href='https://www.netflix.com/title'>Ver en Netflix</a>")

    base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
    
    try:
        # Intentar enviar FOTO
        if img_url:
            r = requests.post(f"{base_url}/sendPhoto", json={
                "chat_id": TELEGRAM_CHAT_ID, "photo": img_url, "caption": msg, "parse_mode": "HTML"
            })
            if r.status_code == 200: return
        
        # PLAN B: Enviar solo texto si la foto falla
        requests.post(f"{base_url}/sendMessage", json={
            "chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "HTML"
        })
    except Exception as e:
        print(f"❌ Error Telegram: {e}")

def get_data(page, name, n_id):
    url = f"https://www.netflix.com/es/title/{n_id}"
    print(f"🕵️  Analizando: {name}...")
    
    try:
        # Navegación con headers humanos
        page.goto(url, wait_until="domcontentloaded", timeout=60000)
        page.wait_for_timeout(3000) # Pausa anti-bot

        # --- EXTRACCIÓN PLAN A: Selectores Visuales ---
        rating = "Pendiente"
        desc = "Sin detalles"
        img_url = None

        if page.locator('.maturity-number').is_visible():
            rating = page.locator('.maturity-number').first.inner_text().strip()
            if page.locator('.maturity-description').is_visible():
                desc = page.locator('.maturity-description').first.inner_text().strip()
        
        # --- EXTRACCIÓN PLAN B: Búsqueda en el Código Fuente (Más robusto) ---
        if rating == "Pendiente":
            html_content = page.content()
            # Patrones comunes en el JSON de Netflix
            r_match = re.search(r'"maturityRating"\s*:\s*\{[^}]*"label"\s*:\s*"([^"]+)"', html_content)
            if r_match:
                rating = r_match.group(1)
            
            d_match = re.search(r'"maturityDescription"\s*:\s*"([^"]+)"', html_content)
            if d_match:
                desc = d_match.group(1)

        # Extraer imagen (Poster)
        img_el = page.locator('img.nm-collections-title-img, img.hero-artwork, img.title-logo-image').first
        if img_el.is_visible():
            img_url = img_el.get_attribute('src')
        else:
            # Fallback imagen por regex
            i_match = re.search(r'"og:image"\s*content="([^"]+)"', html_content if 'html_content' in locals() else page.content())
            if i_match: img_url = i_match.group(1)

        return rating, desc, img_url

    except Exception as e:
        print(f"⚠️ Error en {name}: {e}")
        return "Error", str(e), None

def main():
    # 1. Cargar Cache
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r', encoding='utf-8') as f:
            cache = json.load(f)
    else:
        cache = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            locale="es-ES"
        )
        page = context.new_page()

        cambios = False
        for nombre, n_id in SERIES.items():
            rating, desc, img_url = get_data(page, nombre, n_id)
            
            if rating == "Error": continue

            last_rating = cache.get(n_id, {}).get('rating', 'Pendiente')

            if rating != last_rating:
                print(f"📢 ¡CAMBIO! {nombre}: {last_rating} -> {rating}")
                enviar_telegram(nombre, rating, desc, img_url)
                cache[n_id] = {"rating": rating, "name": nombre}
                cambios = True
            else:
                print(f"✅ {nombre}: Sin cambios ({rating})")

        # 2. Guardar si hubo novedades
        if cambios:
            with open(CACHE_FILE, 'w', encoding='utf-8') as f:
                json.dump(cache, f, indent=4, ensure_ascii=False)

        browser.close()

if __name__ == "__main__":
    main()
