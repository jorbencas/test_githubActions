import os
import re
from playwright.sync_api import sync_playwright

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

SERIES = {
    "La Dama del Armiño": "82152349",
    "Berlín": "81584733",
    "La casa de papel": "80192017"
}
"https://www.netflix.com/title/82152349"


def get_data(page, name, n_id):
    url = f"https://www.netflix.com/es/title/{n_id}"
    page.goto(url, wait_until="networkidle")
    
    html = page.content()
    
    # Extraer Rating
    rating = "Pendiente"
    r_match = re.search(r'"maturityRating":\s*"([^"]+)"', html)
    if r_match:
        rating = r_match.group(1)

    # Extraer Descriptores
    desc = "Sin detalles"
    d_match = re.search(r'"maturityDescription":\s*"([^"]+)"', html)
    if d_match:
        desc = d_match.group(1)
    
    print(f"Analizando {name}: Rating={rating}, Desc={desc}")
    return rating, desc

def main():
    with sync_playwright() as p:
        # Lanzamos un navegador real
        browser = p.chromium.launch(headless=True)
        # Usamos un perfil de usuario normal para no parecer un bot
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        
        results = []
        for name, n_id in SERIES.items():
            rating, desc = get_data(page, name, n_id)
            # Solo si encontramos algo real, preparamos el mensaje
            if rating != "Pendiente":
                results.append(f"🎬 *{name}*\n🔞 Edad: {rating}\n⚠️ Detalles: {desc}")

        if results:
            msg = "🚀 *Novedades Netflix:*\n\n" + "\n\n".join(results)
            import requests
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

        browser.close()

if __name__ == "__main__":
    main()