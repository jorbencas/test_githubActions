import os
import requests
import re

# Configuración desde Secrets de GitHub
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Diccionario de series: { "Nombre": "ID_Netflix" }
SERIES_A_MONITORIZAR = {
    "Berlin y La Dama del Armiño": "82152349",
    "Berlin": "81586657",
    "Entre tierras": "81700632",
    "La casa de papel":"80192098",
}

STATUS_FILE = "last_ratings.txt"

def get_netflix_info(name, n_id):
    url = f"https://www.netflix.com/es/title/{n_id}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "es-ES,es;q=0.9"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        html = response.text

        # 1. Buscamos el Rating (ej: 16+, 18+)
        rating_match = re.search(r'"maturityRating":\s*"([^"]+)"', html)
        rating = rating_match.group(1) if rating_match else "Pendiente"

        # 2. Buscamos los Descriptores (violencia, sexo, sustancias...)
        # Buscamos en el bloque JSON 'maturityDescription'
        desc_match = re.search(r'"maturityDescription":\s*"([^"]+)"', html)
        descriptors = desc_match.group(1) if desc_match else None

        return rating, descriptors
    except Exception as e:
        print(f"Error con {name}: {e}")
        return None, None

def load_previous_status():
    if os.path.exists(STATUS_FILE):
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_status(content):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(content)

def send_telegram(msg):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    requests.post(url, json={"chat_id": TELEGRAM_CHAT_ID, "text": msg, "parse_mode": "Markdown"})

def main():
    previous_full_status = load_previous_status()
    current_status_list = []
    changes_detected = False
    final_message = "🚀 *Novedades en Clasificaciones Netflix:*\n\n"

    for name, n_id in SERIES_A_MONITORIZAR.items():
        rating, desc = get_netflix_info(name, n_id)
        
        # Formateamos el estado de esta serie
        status_line = f"{name}: {rating} ({desc if desc else 'Sin detalles'})"
        current_status_list.append(status_line)

        # Si este estado no estaba en el archivo anterior Y tiene descriptores reales
        if status_line not in previous_full_status and desc:
            changes_detected = True
            final_message += f"🎬 *{name}*\n🔞 Edad: {rating}\n⚠️ Detalles: {desc}\n\n"

    if changes_detected:
        send_telegram(final_message)
        # Guardamos el nuevo estado global
        save_status("\n".join(current_status_list))
    else:
        print("No hay cambios relevantes o faltan descriptores.")

if __name__ == "__main__":
    main()