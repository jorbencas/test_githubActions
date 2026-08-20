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
HISTORY_MAX = 60

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


def _pick_frase(saludo, history_keys):
    """Elige una frase inspiradora nueva (sin repetir) según el momento del día."""
    franja = "dias" if "Buenos días" in saludo else "noches"
    lista = CONFIG["frases"].get(franja, [])
    disponibles = [f for f in lista if f"frase:{f}" not in history_keys]
    if not disponibles:
        disponibles = list(lista)
    return random.choice(disponibles)


FONT_CANDIDATOS = ("DejaVuSans-Bold.ttf", "Arial.ttf", "FreeSans.ttf")


def _cargar_fuente(tam):
    from PIL import ImageFont
    for f in FONT_CANDIDATOS:
        try:
            return ImageFont.truetype(f, tam)
        except Exception:
            continue
    return ImageFont.load_default()


def _color_texto(img):
    """Color del texto en función del tono medio de la imagen.

    Calcula la luminosidad media y devuelve un color de alto contraste que
    armoniza con la imagen (texto claro sobre fondos oscuros y viceversa).
    """
    try:
        from PIL import ImageStat
        stat = ImageStat.Stat(img.convert("RGB"))
        r, g, b = stat.mean
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum > 150:
            return (30, 40, 60)      # texto oscuro sobre imagen clara
        return (255, 255, 255)       # texto claro sobre imagen oscura
    except Exception:
        return (255, 255, 255)


def _enrollar_lineas(draw, texto, font, max_w):
    """Divide el texto en líneas que no superen max_w (por palabras)."""
    lineas = []
    actual = ""
    for palabra in texto.split():
        prueba = (actual + " " + palabra).strip()
        bbox = draw.textbbox((0, 0), prueba, font=font)
        if bbox[2] - bbox[0] <= max_w or not actual:
            actual = prueba
        else:
            lineas.append(actual)
            actual = palabra
    if actual:
        lineas.append(actual)
    return lineas


def _alto_bloque(draw, lineas_con_fuente, gap):
    return sum(
        draw.textbbox((0, 0), txt, font=f)[3] - draw.textbbox((0, 0), txt, font=f)[1]
        for txt, f in lineas_con_fuente
    ) + gap * (len(lineas_con_fuente) - 1)


def _encajar_texto(img, frase, saludo, max_fraccion=0.95):
    """Busca un tamaño de fuente y un ajuste en líneas tal que todo el bloque
    (frase + saludo) quepa dentro de la imagen sin desbordar el ancho ni el alto.

    Devuelve (lineas_con_fuente, gap, tam). Se reduce el tamaño o se trocea
    en más líneas hasta hallar un encaje cómodo y legible."""
    from PIL import ImageDraw, ImageFont

    w, h = img.size
    margen = max(int(w * 0.06), 30)
    max_w = w - margen * 2
    max_h = h - margen * 2

    draw = ImageDraw.Draw(img)

    tam = max(24, int(min(w, h) * 0.06))
    min_tam = 26
    gap = max(6, int(tam * 0.28))

    for tam in range(tam, min_tam - 1, -2):
        f_frase = _cargar_fuente(tam)
        f_saludo = _cargar_fuente(int(tam * 0.66)) if hasattr(f_frase, "font_variant") else _cargar_fuente(tam)
        lineas_frase = _enrollar_lineas(draw, frase, f_frase, max_w)
        lineas_saludo = _enrollar_lineas(draw, saludo, f_saludo, max_w)
        bloque = [(t, f_frase) for t in lineas_frase] + [(t, f_saludo) for t in lineas_saludo]
        alto = _alto_bloque(draw, bloque, gap)
        ancho_max = max(draw.textbbox((0, 0), t, font=f)[2] - draw.textbbox((0, 0), t, font=f)[0]
                        for t, f in bloque)
        if alto <= max_h * max_fraccion and ancho_max <= max_w:
            return bloque, gap, tam

    f_frase = _cargar_fuente(min_tam)
    f_saludo = _cargar_fuente(max(min_tam // 2, 18))
    lineas_frase = _enrollar_lineas(draw, frase, f_frase, max_w)
    lineas_saludo = _enrollar_lineas(draw, saludo, f_saludo, max_w)
    return ([(t, f_frase) for t in lineas_frase]
            + [(t, f_saludo) for t in lineas_saludo]), gap, min_tam


def _panel_de_contraste(draw, x, y, w, h, radio, alpha=170):
    """Panel semitransparente redondeado que da legibilidad al texto sobre la
    imagen, con un toque elegante (esquinas suaves)."""
    draw.rounded_rectangle(
        [x, y, x + w, y + h],
        radius=radio,
        fill=(15, 18, 28, alpha),
        outline=(255, 255, 255, 26),
        width=2,
    )


def _nitidez(img, objetivo=1024):
    """Garantiza imagen nítida y clara para su publicación.

    - Si viene pequeña, la amplía (Lanczos) a 1024px en su lado mayor.
    - Aplica un enfoque suave (UnsharpMask) para recuperar detalle y contraste,
      sin halos ni artefactos. Devuelve la imagen en modo RGB."""
    from PIL import Image, ImageFilter

    img = img.convert("RGB")
    w, h = img.size
    lado = max(w, h)
    if lado < objetivo:
        escala = objetivo / lado
        img = img.resize((max(1, int(w * escala)), max(1, int(h * escala))), Image.LANCZOS)
    img = img.filter(ImageFilter.UnsharpMask(radius=2, percent=115, threshold=3))
    return img


def _superponer_texto(img_bytes, frase, saludo):
    """Dibuja el texto de la frase DENTRO de la imagen, con color de alto
    contraste, texto ajustado al ancho (multi-línea) y sobre un panel
    semitransparente redondeado que garantiza la legibilidad.

    Respeta las proporciones originales (no la distorsiona) y devuelve los
    bytes de la imagen con el texto sobrepuesto."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        return img_bytes
    try:
        import io
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        # Nítida y clara: amplía si viene pequeña y enfoca sin artefactos
        img = _nitidez(img)

        color = (255, 255, 255)   # siempre claro: el panel oscuro da el contraste
        sombra = (0, 0, 0, 220)

        w, h = img.size
        bloque, gap, tam = _encajar_texto(img, frase, saludo)

        margen = max(int(w * 0.06), 30)
        # Colocación inteligente: arriba o en el centro vertical, según nieve la
        # composición no lo sabemos; usamos un tercio desde abajo para dejar que
        # la ilustración respire arriba, o centrado si el bloque es muy alto.
        alto_bloque = _alto_bloque(ImageDraw.Draw(img), bloque, gap)
        area_arriba = margen
        area_abajo = h - margen - alto_bloque
        y = margen
        if alto_bloque <= int(h * 0.30):
            # espacio para texto arriba
            pass
        elif area_abajo >= margen:
            y = area_abajo   # mejor abajo, dejando la ilustración arriba
        else:
            y = int(h / 2) - alto_bloque // 2

        draw = ImageDraw.Draw(img, "RGBA")

        # Panel semitransparente redondeado detrás del texto
        ancho_panel = max(draw.textbbox((0, 0), t, font=f)[2] - draw.textbbox((0, 0), t, font=f)[0]
                          for t, f in bloque)
        pad_x = int(margen * 0.5)
        pad_y = int(gap * 0.8)
        px = (w - ancho_panel) // 2 - pad_x
        py = y - pad_y
        pw = ancho_panel + pad_x * 2
        ph = alto_bloque + pad_y * 2
        _panel_de_contraste(draw, px, py, pw, ph, radio=min(28, int(tam * 0.5)))

        yc = y
        for texto, f in bloque:
            bbox = draw.textbbox((0, 0), texto, font=f)
            tw = bbox[2] - bbox[0]
            tx = (w - tw) // 2
            draw.text((tx + 2, yc + 2), texto, font=f, fill=sombra)
            draw.text((tx, yc), texto, font=f, fill=color)
            yc += (bbox[3] - bbox[1]) + gap

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()
    except Exception as e:
        print(f"⚠️  Error superponiendo texto: {e}")
        return img_bytes


def _fecha_legible(now):
    """Fecha en español cuidada: 'jueves, 20 de agosto'."""
    dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
    meses = ["enero", "febrero", "marzo", "abril", "mayo", "junio",
             "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
    return f"{dias[now.weekday()]} {now.day} de {meses[now.month - 1]}".capitalize()


def _build_prompt(saludo, frase, now, festivo_nombre, festivo_temas, estilo, publico, emocion, materia, temporada):
    fecha_legible = _fecha_legible(now)
    contexto = f"Celebramos {festivo_nombre}, ambiente de {festivo_temas}." if festivo_nombre else f"Es temporada de {temporada}."
    return (
        f"Crea una ilustración digital de altísima calidad y acabado profesional de {saludo.lower()} "
        f"para compartir en redes, EN ESPAÑOL, {emocion}. Tema central: {materia}, con {publico}. "
        f"Estilo artístico: {estilo}. "
        f"Aplica este estilo de forma decidida y evidente, con acabado profesional y pulido "
        f"(como ilustración editorial, portada de manga, fotograma de película o pictograma de marca premium). "
        f"Atmósfera: {contexto} "
        f"Día representado: {fecha_legible}. "
        f"Composición cuidada: iluminación cálida y suave, paleta de color armoniosa, "
        f"detalles delicados y atractivos, profundidad de campo sutil, encuadre equilibrado. "
        f"BUEN CONTRASTE cinematográfico entre luces y sombras: zonas iluminadas cálidas y "
        f"brillantes que resaltan, sombras suaves y profundas que dan volumen, claroscuro "
        f"armonioso que hace destacar los personajes y la escena sin perder ternura. "
        f"NÍTIDA y CLARA: imagen enfocada, alta resolución (1024px), detalles definidos, "
        f"sin borrosidad, sin artifacts. "
        f"Estilo adorable, entrañable y entrañablemente bonito: personajes de rasgos suaves, "
        f"proporciones redondeadas y armoniosas, miradas cálidas, gestos cariñosos que despiertan "
        f"ternura y cariño al verlas. "
        f"NO dibujes animales, gatos, mascotas ni criaturas deformes. "
        f"Evita figuras distorsionadas, cuerpos abultados, extremidades anómalas, rostros raros "
        f"o cualquier elemento que resulte feo o grotesco. TODO debe verse bonito, dulce y proporcionado. "
        f"NO incluyas NINGÚN texto, letras, palabras ni tipografía en la imagen. "
        f"Deja una zona despejada y limpia (cielo, pared suave, fondo desenfocado) en la parte "
        f"inferior o central para poder añadir el texto después. "
        f"Que sea cálida, positiva, elegante y acogedora. "
        f"NO terror, NO horror, NO sangre, NO nada inquietante. La imagen debe ser CUADRADA (1:1)."
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


def fallback_pollinations(saludo, publico, materia, estilo="cartoon", emocion="positivo", temporada=""):
    """Genera la imagen con Pollinations.ai (flux). SIN registro ni API key.

    Usa un prompt enriquecido con estilo y emoción, similar al de Gemini pero
    sin pedir texto incrustado (el texto se superpone después por PIL).
    Es una simple petición GET con el prompt en la URL. El límite anónimo
    (1 petición/15s) sobra para un envío cada 3 horas.
    Devuelve bytes JPEG o None si hay error."""
    try:
        base = f"{saludo}, {materia}, con {publico}, estilo {estilo}, {emocion}, ilustración cálida y acogedora, en español, alta calidad"
        if temporada:
            base += f", atmósfera de {temporada}"
        base += ", adorables y entrañables, personajes de rasgos suaves y proporciones redondeadas y armoniosas"
        base += ", sin animales, sin gatos, sin mascotas, sin criaturas deformes, sin figuras distorsionadas, todo bonito y proporcionado"
        base += ", sin texto, sin tipografía, composición equilibrada, iluminación suave"
        base += ", buen contraste cinematografico de luces y sombras, claroscuro armonioso, zonas iluminadas cálidas y sombras profundas suaves"
        base += ", nitida y clara, enfocada, alta resolucion, detalles definidos"
        url = (
            "https://image.pollinations.ai/prompt/"
            + requests.utils.quote(base)
            + "?width=1024&height=1024&model=flux&nologo=true&seed=42"
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
        w, h = 1024, 1024
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
    frase = _pick_frase(saludo, history_keys)

    print(f"📅 Fecha local: {now.isoformat()} (offset {TZ_OFFSET}h)")
    print(f"👋 Saludo: {saludo}")
    print(f"💬 Frase: {frase}")
    if festivo_nombre:
        print(f"🎉 Festivo detectado: {festivo_nombre}")
    print(f"🎨 {estilo} + {publico} + {emocion} + {materia}")

    if festivo_nombre and festivo_temas:
        materia = festivo_temas

    prompt = _build_prompt(
        saludo, frase, now, festivo_nombre, festivo_temas, estilo, publico, emocion, materia, temporada
    )

    image_bytes = generate_image(prompt)
    fuente = "gemini"
    if not image_bytes:
        print("⚠️  Gemini falló; probando fallback Pollinations (sin registro)...")
        image_bytes = fallback_pollinations(saludo, publico, materia, estilo, emocion, temporada)
        fuente = "pollinations"
    if not image_bytes:
        print("⚠️  Pollinations falló; probando fallback PIL local...")
        image_bytes = fallback_pil(saludo, publico)
        fuente = "pil"
    if not image_bytes:
        print("❌ No se pudo generar la imagen con ninguna fuente.")
        sys.exit(1)

    # Garantiza que el texto (frase + saludo) quede DENTRO de la imagen,
    # en el color de la misma y sin distorsionar sus proporciones.
    image_bytes = _superponer_texto(image_bytes, frase, saludo)

    if dry_run:
        print("\n--- VISTA PREVIA (dry-run) ---")
        print(f"Prompt: {prompt}")
        print(f"Imagen generada: {len(image_bytes)} bytes (fuente: {fuente})")
        print("--- FIN VISTA PREVIA ---")
        return

    caption = f"✨ {frase} ✨\n{saludo}! 💛 Te mando un abrazo con cariño."
    print(f"🎨 Fuente de imagen: {fuente}")
    if send_photo(image_bytes, caption):
        for k in (f"estilo:{estilo}", f"publico:{publico}",
                  f"emocion:{emocion}", f"materia:{materia}", f"frase:{frase}"):
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