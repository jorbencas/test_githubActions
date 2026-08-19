"""
Saludo con Imagen IA — Genera y envía por Telegram una imagen de Buenos días /
Buenas tardes / Buenas noches según la hora local. La imagen se adapta a la
fecha: festivos, temporadas y temas variados (dibujo, acuarela, cartoon...),
con públicos y emociones distintas. Nada de terror.

Uso:
    python scripts/saludo_imagen.py                    # genera y envía
    python scripts/saludo_imagen.py --dry-run          # solo genera, no envía
    python scripts/saludo_imagen.py --list-config      # muestra config disponible

Variables de entorno:
    TIPS_BOT_TOKEN / TIPS_CHAT_ID  -> Telegram (igual que tips)
    GEMINI_API_KEY                 -> Google GenAI
    SALUDOS_TZ_OFFSET              -> desfase horario en horas (ej. "2" para CEST)
"""

import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
CONFIG_PATH = SCRIPT_DIR / "utils" / "saludos_config.json"
HISTORY_PATH = SCRIPT_DIR.parent / "saludos_history.json"
IMAGES_DIR = SCRIPT_DIR.parent / "files" / "saludos"
HISTORY_MAX = 30

BOT_TOKEN = os.environ.get("TIPS_BOT_TOKEN", "")
CHAT_ID = os.environ.get("SALUDO_CHAT_ID", os.environ.get("TIPS_CHAT_ID", "-1004296712840"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
TZ_OFFSET = float((os.environ.get("SALUDOS_TZ_OFFSET") or "").strip() or "0")

MODELO_IMAGEN = "gemini-3.1-flash-image"   # Nano Banana 2

CONFIG = {}


def load_config():
    global CONFIG
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        CONFIG = json.load(f)


def load_history():
    if HISTORY_PATH.exists():
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"keys": [], "last_run": None, "total_runs": 0}


def save_history(history):
    HISTORY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_PATH, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def now_local():
    return datetime.now(timezone.utc) + timedelta(hours=TZ_OFFSET)


def _greeting_for_hour(hour):
    if 5 <= hour < 12:
        return "Buenos días"
    return "Buenas noches"


def _festivo(now):
    key = now.strftime("%m-%d")
    for fest, (nombre, temas) in CONFIG["festivos"].items():
        if key == fest:
            return nombre, temas
    return None, None


def _temporada(now):
    return CONFIG["temporadas"].get(now.strftime("%m"), "una estación del año")


def _pick(key_list, history_keys, config_key):
    available = [k for k in CONFIG[key_list] if f"{config_key}:{k}" not in history_keys]
    if not available:
        available = list(CONFIG[key_list])
    return random.choice(available)


def _build_prompt(saludo, now, festivo_nombre, festivo_temas, estilo, publico, emocion, materia, temporada):
    fecha_legible = now.strftime("%A %d de %B").capitalize()
    contexto = f"Celebramos {festivo_nombre} ({festivo_temas})." if festivo_nombre else f"Es temporada de {temporada}."
    return (
        f"Crea una ilustración en {saludo.lower()} para compartir, EN ESPAÑOL, "
        f"{emocion}. Tema: {materia}, con {publico}. "
        f"Estilo: {estilo}. "
        f"Atmósfera: {contexto} "
        f"Día: {fecha_legible}. "
        f"Incluye en la imagen el texto claro y legible: '{saludo}'. "
        f"Que sea cálida, positiva y acogedora. NO terror, NO horror, NO sangre, NO nada inquietante."
    )


def generate_image(prompt):
    if not GEMINI_API_KEY:
        print("⚠️  GEMINI_API_KEY no configurada.")
        return None
    try:
        import base64

        from google import genai

        client = genai.Client(api_key=GEMINI_API_KEY)

        # Gemini 3 image models (Nano Banana 2) usan la Interactions API.
        if MODELO_IMAGEN.startswith("gemini-3"):
            interaction = client.interactions.create(
                model=MODELO_IMAGEN,
                input=prompt,
                response_modalities=["image"],
            )
            out = interaction.output_image
            if out is None:
                print("⚠️  Gemini no devolvió imagen (output_image vacío)")
                print(f"   Estado interaction: {getattr(interaction, 'status', '?')}")
                return None
            raw = out.data
            if isinstance(raw, str):
                if "base64," in raw:
                    raw = raw.split("base64,", 1)[1]
                return base64.b64decode(raw)
            if isinstance(raw, bytes):
                return raw
            print(f"⚠️  Formato de salida inesperado: {type(raw)}")
            return None

        # Modelos legacy (gemini-2.5-flash-image) usan generate_images.
        from google.genai import types

        response = client.models.generate_images(
            model=MODELO_IMAGEN,
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=1,
                aspect_ratio="1:1",
                language="es",
            ),
        )
        for img in response.generated_images:
            if img.image.image_bytes:
                return img.image.image_bytes
        print("⚠️  Gemini no devolvió bytes de imagen")
        return None
    except Exception as e:
        print(f"⚠️  Error generando imagen: {e}")
        return None


def fallback_pollinations(saludo, publico, materia):
    """Genera la imagen con Pollinations.ai (flux). SIN registro ni API key.

    Es una simple petición GET con el prompt en la URL. El límite anónimo
    (1 petición/15s) sobra para un envío cada 3 horas.
    Devuelve bytes JPEG o None si hay error."""
    try:
        prompt = f"{saludo}, {materia}, ilustración cálida y acogedora, en español, estilo cartoon"
        url = (
            "https://image.pollinations.ai/prompt/"
            + requests.utils.quote(prompt)
            + "?width=1024&height=576&model=flux&nologo=true&seed=42"
        )
        resp = requests.get(url, timeout=90)
        if resp.status_code != 200:
            print(f"❌ Pollinations ({resp.status_code}): {resp.text[:120]}")
            return None
        if not resp.content or resp.content[:2] != b"\xff\xd8":
            print("⚠️  Pollinations no devolvió una imagen JPEG válida.")
            return None
        print(f"✅ Imagen generada con Pollinations.ai ({len(resp.content)} bytes)")
        return resp.content
    except Exception as e:
        print(f"⚠️  Error con Pollinations: {e}")
        return None


def fallback_pil(saludo, publico):
    """Genera una imagen simple con PIL: texto del saludo sobre degradado.
    Infalible: no depende de APIs externas ni cuotas."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("⚠️  Pillow no instalado; sin fallback local.")
        return None
    try:
        w, h = 1280, 720
        img = Image.new("RGB", (w, h), "#1e3a8a")
        draw = ImageDraw.Draw(img)
        for i in range(h):
            r = int(30 + (20 + 60 * i / h))
            g = int(58 + (20 + 40 * i / h))
            b = int(138 + (80 + 30 * i / h))
            draw.line([(0, i), (w, i)], fill=(min(r, 255), min(g, 255), min(b, 255)))
        font = None
        for f in ("DejaVuSans-Bold.ttf", "Arial.ttf", "FreeSans.ttf"):
            try:
                font = ImageFont.truetype(f, 72)
                break
            except Exception:
                continue
        if font is None:
            font = ImageFont.load_default()
        text = f"{saludo}!\nCon cariño para ti {publico}."
        lines = text.splitlines()
        line_h = 100
        total = line_h * len(lines)
        y = (h - total) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            tw = bbox[2] - bbox[0]
            draw.text(((w - tw) // 2, y), line, fill="white", font=font)
            y += line_h
        import io
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        print(f"✅ Imagen local generada con PIL ({len(buf.getvalue())} bytes)")
        return buf.getvalue()
    except Exception as e:
        print(f"⚠️  Error generando imagen local: {e}")
        return None


def send_photo(image_bytes, caption):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️  TIPS_BOT_TOKEN o TIPS_CHAT_ID no configurados.")
        return False
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        files = {"photo": ("saludo.png", image_bytes, "image/png")}
        payload = {"chat_id": CHAT_ID, "caption": caption}
        resp = requests.post(url, data=payload, files=files, timeout=90)
        if resp.status_code == 200:
            print("✅ Imagen enviada a Telegram.")
            return True
        print(f"❌ Error Telegram ({resp.status_code}): {resp.text}")
        return False
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False


def list_config():
    print("🎨 Estilos:")
    for k, v in CONFIG["estilos"].items():
        print(f"   • {k}: {v}")
    print("👥 Públicos:")
    for k, v in CONFIG["publicos"].items():
        print(f"   • {k}: {v}")
    print("😊 Emociones:")
    for k, v in CONFIG["emociones"].items():
        print(f"   • {k}: {v}")
    print("🖼️ Materias:")
    for k, v in CONFIG["materias"].items():
        print(f"   • {k}: {v}")
    print("📅 Festivos:")
    for k, (nombre, _) in CONFIG["festivos"].items():
        print(f"   • {k}: {nombre}")
    print("🗓️ Temporadas:")
    for k, v in CONFIG["temporadas"].items():
        print(f"   • Mes {k}: {v}")


def main():
    load_config()
    dry_run = "--dry-run" in sys.argv
    list_cfg = "--list-config" in sys.argv

    if list_cfg:
        list_config()
        return

    history = load_history()
    now = now_local()
    saludo = _greeting_for_hour(now.hour)

    festivo_nombre, festivo_temas = _festivo(now)
    temporada = _temporada(now)

    history_keys = history.get("keys", [])

    estilo = _pick("estilos", history_keys, "estilo")
    publico = _pick("publicos", history_keys, "publico")
    emocion = _pick("emociones", history_keys, "emocion")
    materia = _pick("materias", history_keys, "materia")

    print(f"📅 Fecha local: {now.isoformat()} (offset {TZ_OFFSET}h)")
    print(f"👋 Saludo: {saludo}")
    if festivo_nombre:
        print(f"🎉 Festivo detectado: {festivo_nombre}")
    print(f"🎨 {estilo} + {publico} + {emocion} + {materia}")

    if festivo_nombre and festivo_temas:
        materia = festivo_temas

    prompt = _build_prompt(
        saludo, now, festivo_nombre, festivo_temas, estilo, publico, emocion, materia, temporada
    )

    image_bytes = generate_image(prompt)
    fuente = "gemini"
    if not image_bytes:
        print("⚠️  Gemini falló; probando fallback Pollinations (sin registro)...")
        image_bytes = fallback_pollinations(saludo, publico, materia)
        fuente = "pollinations"
    if not image_bytes:
        print("⚠️  Pollinations falló; probando fallback PIL local...")
        image_bytes = fallback_pil(saludo, publico)
        fuente = "pil"
    if not image_bytes:
        print("❌ No se pudo generar la imagen con ninguna fuente.")
        sys.exit(1)

    if dry_run:
        print("\n--- VISTA PREVIA (dry-run) ---")
        print(f"Prompt: {prompt}")
        print(f"Imagen generada: {len(image_bytes)} bytes (fuente: {fuente})")
        print("--- FIN VISTA PREVIA ---")
        return

    caption = f"{saludo}! ☀️🌙\nCon cariño para ti {publico}."
    print(f"🎨 Fuente de imagen: {fuente}")
    if send_photo(image_bytes, caption):
        for k in (f"estilo:{estilo}", f"publico:{publico}",
                  f"emocion:{emocion}", f"materia:{materia}"):
            history.setdefault("keys", []).append(k)
        history["keys"] = history["keys"][-HISTORY_MAX:]
        history["last_run"] = now.isoformat()
        history["total_runs"] = history.get("total_runs", 0) + 1
        save_history(history)
        print(f"📊 Total saludos enviados: {history['total_runs']}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()