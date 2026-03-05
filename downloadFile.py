import io
import locale
import os, json, re, requests, asyncio
from datetime import datetime, timedelta
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from collections import Counter
from mtranslate import translate
from google import genai
from gtts import gTTS  # Necesitas instalar: pip install gTTS


# --- 1. CONFIGURACIÓN ---
CONFIG = {
    "BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN"),
    "CHAT_ID": os.getenv("TOKEN_API_ID"),
    "GEMINI_KEY": os.getenv("GEMINI_API_KEY"),
    "MAIL_KEY": os.getenv("MAILGUN_API_KEY"),
    "MAIL_DOMAIN": os.getenv("MAILGUN_DOMAIN"),
    "EMAIL_TO": os.getenv("EMAIL_USER"),
    "FOLDER": "files"
}

TECH_KEYWORDS = ['ia', 'inteligencia artificial', 'empleo', 'software', 'programación', 'valencia', 'albaida', 'tecnología']
BECAS_KEYWORDS = ['beca', 'curso', 'ayuda', 'formación', 'subvención', 'taller']
ALL_KEYWORDS = TECH_KEYWORDS + BECAS_KEYWORDS

FUENTES = {
    "MoureDev": {"url": "https://mouredev.com/blog", "yt": "https://www.youtube.com/@mouredev/videos"},
    "Pelado Nerd": {"yt": "https://www.youtube.com/@PeladoNerd/videos"},
    "Midudev": {"yt": "https://www.youtube.com/@midudev/videos"},
    "Codigo facilito": {"yt": "https://www.youtube.com/@codigofacilito/videos"},
    "Carlos Azaustre": {"yt": "https://www.youtube.com/@CarlosAzaustre/videos"},
    "Clipset": {"yt": "https://www.youtube.com/@clipset/videos"},
    "CodelyTV": {"yt": "https://www.youtube.com/@CodelyTV/videos"},
    "EDteam": {"yt": "https://www.youtube.com/@EDteam/videos"},
    "Fazt": {"yt": "https://www.youtube.com/@FaztTech/videos"},
    "FreeCodeCamp": {"yt": "https://www.youtube.com/@freecodecamp/videos"},
    "HolaMundo": {"yt": "https://www.youtube.com/@holamundodev/videos"},
    "Victor Robles": {"yt": "https://www.youtube.com/@victorroblesweb/videos"},
    "Xataka": {"url": "https://www.xataka.com/", "yt":"https://www.youtube.com/@xatakatv/videos"},
    "Becas": {"url": "https://www.becas.com/noticias/"},
    "Genbeta": {"url":"https://www.genbeta.com/"},
    "HobbyConsolas": {"url": "https://www.hobbyconsolas.com/"},
    "El País Tecnología": {"url": "https://elpais.com/tecnologia/"},
    "Levante-EMV": {"url": "https://www.levante-emv.com/"},
    "Fundación Carolina": {"url": "https://www.fundacioncarolina.es/"},
}

# Auto-añadir secciones de Shorts
for nombre in list(FUENTES): # Usamos list() para poder modificar el dict mientras iteramos
    if "yt" in FUENTES[nombre]:
        url_s = FUENTES[nombre]["yt"].replace("/videos", "/shorts")
        FUENTES[f"{nombre} Shorts"] = {"yt": url_s}

os.makedirs(CONFIG["FOLDER"], exist_ok=True)
os.makedirs("./auto-news", exist_ok=True)

# --- 2. PLANTILLAS ---

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="styles.css">
    <title>Tech Dashboard</title>
</head>
<body>
    <div class="container">
        <header>
            <h1>Tech Pulse <small style="font-size: 0.4em; color: #666;">{fecha_hoy}</small></h1>
            <img src="optimizado/Image.png" alt="Logo" class="logo">
        </header>
        <div class="ia-box">
            <h2>🤖 Resumen</h2>
            <p>{resumen}</p>
        </div>

        <div class="filter-section">
            <strong>📅 Por Tiempo:</strong>
            <div class="chip-container">{bloque_semanas}</div>
        </div>

        <div class="filter-section">
            <strong>👤 Por Canal:</strong>
            <div class="chip-container">{bloque_chips}</div>
        </div>

        <h2>📺 Multimedia (Vídeos y Shorts)</h2>
        <div class="video-grid">{bloque_videos}</div>
        <h2>📰 Noticias Históricas</h2>
        <ul class="news-list">{bloque_noticias}</ul>
    </div>
</body>
<script src="script.js"></script>
</html>
"""

EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Actualización Tecnológica</title>
</head>
<body style="margin: 0; padding: 0; background-color: #f4f7f9; font-family: Arial, sans-serif;">
    <div style="display: none; max-height: 0px; overflow: hidden;">
        Resumen de hoy: {total_noticias} novedades encontradas sobre {temas_clave}...
    </div>

    <table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" style="max-width: 600px; background-color: #ffffff; margin: 20px auto; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);">
        <tr>
            <td bgcolor="#1a73e8" style="padding: 40px 20px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: #ffffff; margin: 0; font-size: 26px; letter-spacing: 1px;">Tech Pulse News</h1>
                <p style="color: #c2e7ff; margin: 10px 0 0 0; font-size: 14px; font-weight: bold;">{fecha_hoy}</p>
            </td>
        </tr>
        
        <tr>
            <td style="padding: 20px 40px 0 40px;">
                <table width="100%" style="background: #f8f9fa; border-radius: 8px; padding: 15px; text-align: center;">
                    <tr>
                        <td width="33%"> <b style="font-size: 20px; color: #1a73e8;">{count_tech}</b><br><span style="font-size: 12px; color: #666;">Noticias Tech</span> </td>
                        <td width="33%" style="border-left: 1px solid #ddd; border-right: 1px solid #ddd;"> <b style="font-size: 20px; color: #2e7d32;">{count_becas}</b><br><span style="font-size: 12px; color: #666;">Becas/Ayudas</span> </td>
                        <td width="33%"> <b style="font-size: 20px; color: #d93025;">{count_vids}</b><br><span style="font-size: 12px; color: #666;">Multimedia</span> </td>
                    </tr>
                </table>
            </td>
        </tr>

        <tr>
            <td style="padding: 30px 40px;">
                <h2 style="color: #8e44ad; font-size: 18px; margin-bottom: 15px;">🤖 Resumen Inteligente</h2>
                <div style="line-height: 1.6; color: #3c4043; font-size: 15px; background: #fdf7ff; padding: 20px; border-radius: 8px; border-left: 4px solid #8e44ad;">
                    {contenido_html}
                </div>
            </td>
        </tr>

        <tr>
            <td style="padding: 0 40px 40px 40px;">
                <h2 style="color: #202124; font-size: 18px; margin-bottom: 20px; border-bottom: 1px solid #eee; padding-bottom: 10px;">📋 Selección para ti</h2>
                <table border="0" cellpadding="0" cellspacing="0" width="100%">
                    {lista_email}
                </table>
            </td>
        </tr>

        <tr>
            <td style="padding: 20px; text-align: center; background: #f1f3f4; border-radius: 0 0 10px 10px;">
                <p style="font-size: 12px; color: #70757a; margin: 0;">
                    Generado automáticamente para Jorge Beneyto.<br>
                    <a href="http://jorbencasdownloaderdocument.surge.sh" style="color: #1a73e8; text-decoration: none; font-weight: bold;">Acceder al Dashboard Histórico</a>
                </p>
            </td>
        </tr>
    </table>
</body>
</html>
"""

MD_TEMPLATE = """---
draft: false
title: "{titulo}"
description: "{resumen_corto}"
pubDate: "{fecha_pub}"
tags: ['web', 'tech', 'ia']
slug: "{slug_name}"
image: "/img/arquitectura_web.webp"
author: "Jorge Beneyto Castelló"
layout: "@layouts/PostLayout.astro"
---
{contenido}

### 🔗 Enlaces de interés
{lista_enlaces}
"""

# --- 3. FUNCIONES ---

class ScraperPro:
    def __init__(self):
        self.cache_file = os.path.join(CONFIG["FOLDER"], "avatars_cache.json")
        self.avatars = self.cargar_avatars()
        self.cambios_en_cache = False

    def cargar_avatars(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f: return json.load(f)
            except: return {}
        return {}

    def guardar_avatars(self):
        if self.cambios_en_cache:
            with open(self.cache_file, 'w') as f: 
                json.dump(self.avatars, f, indent=4)
            print("💾 Caché de avatares actualizada.")

    def obtener_avatar_canal(self, nombre, url_canal):
        # Si ya lo tenemos en caché, no entramos a YouTube
        if nombre in self.avatars: return self.avatars[nombre]
        
        try:
            print(f"🔍 Buscando avatar real para: {nombre}...")
            # Limpiamos la URL para ir al home del canal
            target = url_canal.replace("/videos", "").replace("/shorts", "")
            r = requests.get(target, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
            soup = BeautifulSoup(r.text, 'html.parser')
            meta_img = soup.find("meta", property="og:image")
            if meta_img:
                url_avatar = meta_img['content']
                self.avatars[nombre] = url_avatar
                self.cambios_en_cache = True 
                return url_avatar
        except: pass
        
        # Si falla, usamos avatar por defecto y no guardamos en caché para reintentar luego
        return f"https://ui-avatars.com/api/?name={nombre}&background=random"

    def extraer(self, nombre, info):
        results = []
        target = info.get("yt") or info.get("url")
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept-Language': 'es-ES,es;q=0.9'
            }
            r = requests.get(target, timeout=15, headers=headers)
            if r.status_code != 200: return []
            if "yt" in info:
                ids = re.findall(r'"videoId":"(.*?)"', r.text)
                titles = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                clean_ids = list(dict.fromkeys(ids))
                # 2. Extraer Títulos (Diferentes patrones según si es /videos o /shorts)
                # Patrón para videos normales
                titles_video = re.findall(r'"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                # Patrón específico para Shorts (overlayMetadata)
                titles_shorts = re.findall(r'"overlayMetadata":\{"title":\{"runs":\[\{"text":"(.*?)"\}\]', r.text)
                
                # Combinamos o elegimos según el tipo
                titles = titles_shorts if "shorts" in target.lower() else titles_video
                
                # Si fallan ambos, intentamos un patrón genérico de accesibilidad
                if not titles:
                    titles = re.findall(r'title="([^"]*)"[^>]*aria-describedby', r.text)

                for t, i in zip(titles[:5], clean_ids[:5]):
                    es_short = "shorts" in target or "Shorts" in nombre
                    t_clean = t.encode().decode('unicode-escape').replace('"', '')
                    results.append({
                        "titulo": translate(t_clean, 'es'),
                        "enlace": f"https://youtube.com/shorts/{i}" if es_short else f"https://youtube.com/watch?v={i}",
                        "id_video": i, "fuente": nombre.replace(" Shorts", ""), 
                        "tipo": "shorts" if es_short else "video",
                        "ultima_verificacion": datetime.now().isoformat(),
                        "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                    })
            else:
                soup = BeautifulSoup(r.text, 'html.parser')
                items = soup.select('article h2 a, .post-title a, h3 a, .title a')[:5]
                
                for i in items:
                    t_raw = i.get_text(strip=True).replace('"', '')
                    t_low = t_raw.lower()
                        
                    # Comprobamos si coincide con alguna de nuestras keywords totales
                    if any(key in t_low for key in ALL_KEYWORDS):
                        # Clasificamos: Si tiene algo de becas, es "Beca", si no "Tech"
                        categoria = "Beca" if any(k in t_low for k in BECAS_KEYWORDS) else "Tech"

                        results.append({
                            "titulo": translate(t_raw, 'es'),
                            "enlace": urljoin(target, i.get('href')),
                            "fuente": nombre, "tipo": "noticia",
                            "ultima_verificacion": datetime.now().isoformat(),
                            "badge": categoria, # Nueva propiedad
                            "ts": datetime.now().isoformat(), "f": datetime.now().strftime("%d/%m")
                        })
        except: pass
        return results

async def obtener_resumen_ia(noticias):
    if not CONFIG["GEMINI_KEY"] or not noticias: return "Sin novedades para resumir hoy."
    try:
        client = genai.Client(api_key=CONFIG["GEMINI_KEY"])
        texto = ". ".join([f"{n['fuente']}: {n['titulo']}" for n in noticias[:12]])
        prompt = (
            "Actúa como un editor de noticias tecnológicas. "
            "Resume los siguientes titulares en 3 párrafos claros y concisos en español. "
            f"Aquí tienes las noticias:\n{texto}"
        )

        # 4. Llamada al modelo 'flash-lite' (El mejor para el Tier Gratuito)
        response = client.models.generate_content(
            model="gemini-2.5-flash-lite",
            contents=prompt
        )
        raw_text = response.text if response.text else "Resumen no disponible."
        # --- FORMATEO PARA WEB ---
        # Convertimos Markdown de la IA (**texto**) a HTML (<b>texto</b>)
        html_text = raw_text.replace("**", "<b>").replace("**", "</b>")
        # Convertimos saltos de línea dobles en párrafos HTML
        parrafos = html_text.split("\n\n")
        resumen_formateado = "".join([f"<p style='margin-bottom:15px; line-height:1.6;'>{p}</p>" for p in parrafos if p.strip()])
        return resumen_formateado
    except Exception as e:
        # Imprime el error real en tu terminal para saber qué pasa exactamente
        print(f"❌ Error en obtener_resumen_ia: {e}")
        
        # Mensajes amigables según el tipo de error
        if "429" in str(e):
            return "Límite de cuota alcanzado. Inténtalo en unos minutos."
        return "Resumen no disponible en este momento. Revisa los enlaces directos."

def publicar_contenidos(historial, nuevos, resumen_ia, scr ):
    ahora = datetime.now()
    fecha_h = ahora.strftime("%d/%m/%Y")
    fecha_pub = ahora.strftime("%Y/%m/%d")
    fecha_iso = ahora.strftime("%Y-%m-%d")
    historial.sort(key=lambda x: x.get('ts', ''), reverse=True)
    
    # --- GENERAR CHIPS DE SEMANAS ---
    conteo_meses = Counter()
    for n in historial:
        try:
            # Extraemos el mes y año de la fecha de la noticia (ts)
            dt_n = datetime.fromisoformat(n.get('ts'))
            mes_key = dt_n.strftime('%B %Y').capitalize()
            conteo_meses[mes_key] += 1
        except: continue

    # --- 2. GENERAR NAVEGACIÓN POR SEMANAS ---
    try: locale.setlocale(locale.LC_TIME, "es_ES.UTF-8") 
    except: pass

    # Chip rápido (Últimas 2 semanas)
    bloque_semanas = '<div class="chip active" data-inicio="all_recent" onclick="filtrarSemana(this)">🔄 Últimas 2 Semanas</div>'
    
    selector_html = '<select id="selectorSemanas" onchange="filtrarDesdeSelector(this)" style="padding: 10px 15px; border-radius: 20px; border: 2px solid #007bff; background: white; color: #007bff; font-weight: bold; cursor: pointer; outline: none; margin-left: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">'
    selector_html += '<option value="all">📅 Archivo Histórico...</option>'

    mes_actual = ""
    # Recorremos las últimas 26 semanas
    for i in range(26):
        inicio = ahora - timedelta(days=ahora.weekday() + (7*i))
        inicio = inicio.replace(hour=0, minute=0, second=0, microsecond=0)
        fin = inicio + timedelta(days=6, hours=23, minutes=59, seconds=59)
        
        nombre_mes = inicio.strftime('%B %Y').capitalize()
        
        # Si cambia el mes, cerramos el grupo anterior y abrimos el nuevo con el CONTADOR
        if nombre_mes != mes_actual:
            if mes_actual != "": selector_html += '</optgroup>'
            total_mes = conteo_meses.get(nombre_mes, 0)
            selector_html += f'<optgroup label="── {nombre_mes} ({total_mes} ítems) ──">'
            mes_actual = nombre_mes
        
        txt_semana = f"Semana {inicio.strftime('%d/%m/%y')}"
        val_ini = inicio.isoformat()
        val_fin = fin.isoformat()
        
        selector_html += f'<option value="{val_ini}|{val_fin}">{txt_semana}</option>'
    
    selector_html += '</optgroup></select>'
    
    # Bloque final para el template
    bloque_semanas_completo = f'<div class="filter-group" style="display:flex; align-items:center; flex-wrap:wrap; gap:10px;">{bloque_semanas} {selector_html}</div>'

    v_html, n_html, email_list, md_links = "", "", "", ""
    resumen_final = resumen_ia if resumen_ia else "Actualización diaria de tecnología."

    # --- GENERAR CHIPS DE FILTRADO ---
    chips_html = '<div class="filter-container" style="margin-bottom: 20px; display: flex; flex-wrap: wrap; gap: 10px;">'
    chips_html += '<div class="chip active" data-filtro="\'all\'" onclick="filtrarCanal(\'all\', this)"><span class="chip-text">Todos</span></div>'

    canales_vistos = []
    for n, info in FUENTES.items():
        nombre_c = n.replace(" Shorts", "")
        if "yt" in info and nombre_c not in canales_vistos:
            img_url = scr.obtener_avatar_canal(nombre_c, info["yt"])
            chips_html += f"""
            <div class="chip" data-filtro="{nombre_c}" onclick="filtrarCanal('{nombre_c}', this)">
                <img src="{img_url}" alt="{nombre_c}" class="chip-img">
                <span class="chip-text">{nombre_c}</span>
            </div>"""
            canales_vistos.append(nombre_c)
    chips_html += "</div>"

    # Generar bloques para la WEB (Acumulativo 200)
    for n in historial[:200]:
        fecha_display = f" | {n['f']}" if n.get('f') else ""
        meta = f"{n['fuente']}{fecha_display}"
        fuente_limpia = n['fuente'].replace(" Shorts", "")
        ts = n.get('ts', ahora.isoformat())

        if n.get('id_video'):
            clase = "tipo-shorts" if n.get('tipo') == "shorts" else "tipo-video"

            v_html += f"""
            <div class="card {clase}" data-ts="{ts}" data-fuente="{fuente_limpia}">
                <a href="{n['enlace']}" target="_blank">
                    <img src="https://img.youtube.com/vi/{n['id_video']}/mqdefault.jpg">
                </a>
                <div class="card-content">
                    <div class="meta">{meta}</div>
                    <a href="{n['enlace']}" target="_blank">{n['titulo']}</a>
                </div>
            </div>"""
        else:
            # Determinar qué badge poner
            badge_type = n.get('badge', 'Tech')
            badge_class = "badge-beca" if badge_type == "Beca/Ayuda" else "badge-tech"
            if "youtube.com" not in n['enlace'] and "youtu.be" not in n['enlace']:
                n_html += f'''
                <li class="news-item" data-ts="{ts}" data-fuente="{fuente_limpia}">
                    <div class="meta">{meta}</div> 
                    <span class="badge {badge_class}">{badge_type}</span> 
                    <a href="{n["enlace"]}">{n["titulo"]}</a>
                </li>'''

    # Guardar HTML
    with open("public/index.html", "w", encoding="utf-8") as f:
        f.write(HTML_TEMPLATE.format(fecha_hoy=fecha_h, resumen=resumen_final, bloque_semanas=bloque_semanas_completo, bloque_chips=chips_html, bloque_videos=v_html, bloque_noticias=n_html))

    # Guardar MD y Email (Solo si hay nuevos)
    if nuevos:
        nuevos = filtrar_solo_noticias(nuevos)
        if len(nuevos) == 0:
            return
        for n in nuevos:
            md_links += f"- **{n['fuente']}**: [{n['titulo']}]({n['enlace']})\n"
            email_list += f"<li><b>{n['fuente']}</b>: <a href='{n['enlace']}'>{n['titulo']}</a></li>"
        
        # Guardar MD
        slug = f"reporte-{fecha_iso}"
        # Creamos la variable que faltaba y limpiamos comillas para evitar errores en Astro
        resumen_corto_limpio = resumen_final[:150].replace("\\n", " ").replace('"', '') + "..."
        
        with open(f"./auto-news/{slug}.md", "w", encoding="utf-8") as f:
            # Asegúrate de que los nombres coincidan con los de tu MD_TEMPLATE
            f.write(MD_TEMPLATE.format(
                titulo=f"Reporte Tech {fecha_h}",
                resumen_corto=resumen_corto_limpio,
                fecha_pub=fecha_pub,
                slug_name=f"{slug}.md",
                contenido=resumen_final,
                lista_enlaces=md_links
            ))

def filtrar_solo_noticias(nuevos):
    """Retorna solo items que NO sean vídeos ni shorts."""
    return [n for n in nuevos if n.get('tipo') == 'noticia']

def enviar_email_reporte(resumen_html, noticias_texto):
    """Genera y envía el reporte por email con diseño anti-spam y estadísticas."""
    if not CONFIG["MAIL_KEY"] or not noticias_texto:
        return
    nuevos = filtrar_solo_noticias(noticias_texto)
    if len(nuevos) == 0:
        return
    # 1. Cálculos para el "Minigráfico" de actividad
    c_tech = len([x for x in nuevos if x.get('badge') == 'Tech'])
    c_becas = len([x for x in nuevos if x.get('badge') == 'Beca'])
    c_vids = len([x for x in nuevos if x.get('id_video')])
    
    # 2. Construir la lista de noticias en formato tabla HTML
    filas_noticias = ""
    for n in nuevos[:15]:  # Limitamos a 15 para no saturar el correo
        icon = "📺" if n.get('id_video') else ("🎓" if n.get('badge') == "Beca" else "💻")
        
        filas_noticias += f"""
        <tr>
            <td style="padding: 12px 0; border-bottom: 1px solid #edf2f7;">
                <span style="font-size: 18px; margin-right: 8px;">{icon}</span>
                <span style="color: #718096; font-size: 11px; font-weight: bold; text-transform: uppercase; letter-spacing: 0.5px;">{n['fuente']}</span><br>
                <a href="{n['enlace']}" target="_blank" style="color: #1a73e8; text-decoration: none; font-weight: 600; font-size: 15px; line-height: 1.4;">{n['titulo']}</a>
            </td>
        </tr>
        """

    # 3. Asunto Dinámico Anti-Spam (basado en la noticia principal)
    # Evitamos asuntos repetitivos como "Reporte diario" que van directo a SPAM
    top_titular = nuevos[0]['titulo']
    asunto = f"🔥 {top_titular[:55]}... y {len(nuevos)-1} más"
    
    # Temas clave para el preheader invisible
    temas_clave = ", ".join(list(set([n['fuente'] for n in nuevos[:3]])))

    # 4. Componer el HTML final
    html_final = EMAIL_TEMPLATE.format(
        fecha_hoy=datetime.now().strftime("%d de %B, %Y"),
        contenido_html=resumen_html,
        lista_email=filas_noticias,
        count_tech=c_tech,
        count_becas=c_becas,
        count_vids=c_vids,
        total_noticias=len(nuevos),
        temas_clave=temas_clave
    )

    # 5. Envío mediante Mailgun API
    try:
        r = requests.post(
            f"https://api.mailgun.net/v3/{CONFIG['MAIL_DOMAIN']}/messages",
            auth=("api", CONFIG["MAIL_KEY"]),
            data={
                "from": f"Tech Pulse Newsletter <newsletter@{CONFIG['MAIL_DOMAIN']}>",
                "to": [CONFIG["EMAIL_TO"]],
                "subject": asunto,
                "html": html_final
            }
        )
        if r.status_code == 200:
            print(f"📧 Email enviado con éxito: {asunto}")
    except Exception as e:
        print(f"⚠️ Fallo en el envío de email: {e}")

def enviar_telegram_con_audio(resumen, noticias_texto):
    if not CONFIG["BOT_TOKEN"] or not CONFIG["CHAT_ID"]: return
    nuevos = filtrar_solo_noticias(noticias_texto)
    # 1. Limpiar el resumen HTML para que sea compatible con Markdown de Telegram
    # Quitamos los tags de párrafo y los convertimos en saltos de línea
    resumen_md = resumen.replace("<p style='margin-bottom:15px; line-height:1.6;'>", "").replace("</p>", "\n\n")
    # Convertimos negritas HTML <b> a Markdown *
    resumen_md = resumen_md.replace("<b>", "*").replace("</b>", "*")
    fecha_str = datetime.now().strftime('%d/%m')
    caption = f"🤖 *RESUMEN IA - {fecha_str}*\n"
    
    # Añadimos el resumen (limitamos a 600 caracteres para dejar espacio a los links)
    resumen_recortado = (resumen_md[:600] + '...') if len(resumen_md) > 600 else resumen_md
    caption += f"{resumen_recortado.strip()}\n\n"
    caption += f"📋 *TOP ENLACES:*\n"

    # 3. Añadir enlaces controlando el espacio restante
    # Dejamos un margen de seguridad (100 caracteres para el botón y despedida)
    LIMITE_TELEGRAM = 1024
    MARGEN_SEGURIDAD = 100

    if len(nuevos) == 0:
        return
    for n in nuevos[:10]: # Intentamos meter hasta 10
        if n.get('id_video'): icono = "📺"
        elif n.get('badge') == "Beca": icono = "🎓"
        else: icono = "💻"
        
        nuevo_item = f"{icono} [{n['fuente']}]({n['enlace']}) "
        
        # Si añadir este link supera el límite, paramos
        if len(caption) + len(nuevo_item) > (LIMITE_TELEGRAM - MARGEN_SEGURIDAD):
            caption += "\n\n⚠️ _Hay más enlaces en el Dashboard..._"
            break
        else:
            caption += nuevo_item

    url_dashboard = "http://jorbencasdownloaderdocument.surge.sh"     
    reply_markup = {
        "inline_keyboard": [[
            {"text": "🌐 Ver Dashboard Completo", "url": url_dashboard}
        ]]
    }

    # 5. Generar y enviar el AUDIO (TTS)
    try:
        # Usamos el texto limpio de Markdown para que la voz no lea los asteriscos
        texto_para_voz = resumen_md.replace("*", "")
        tts = gTTS(text=texto_para_voz, lang='es')
        audio_buffer = io.BytesIO()
        loop = asyncio.get_event_loop()
        loop.run_in_executor(None, tts.write_to_fp, audio_buffer)
        audio_buffer.seek(0) # Resetear puntero al inicio
        
        # Enviamos el audio con el caption y el botón
        files = {'voice': ('resumen.mp3', audio_buffer, 'audio/mpeg')}
        payload={
            "chat_id": CONFIG["CHAT_ID"], 
            "caption": caption, 
            "parse_mode": "Markdown",
            "reply_markup": json.dumps(reply_markup)
        }
        test = {
            "data":payload, 
            "files":files
        }

        print(f"chat id: {test}")
        r = requests.post(f"https://api.telegram.org/bot{CONFIG['BOT_TOKEN']}/sendVoice", test)
        if r.status_code == 200:
            print(f"🤖 Mensaje telegram enviado con éxito")
    except Exception as e:
        print(f"⚠️ Error TTS/Telegram: {e}")

# --- FUNCIONALIDAD LINK CHECKER ---
async def main():
    scr = ScraperPro()
    datos = []
    for n, info in FUENTES.items(): datos += scr.extraer(n, info)

    archivo_h = os.path.join(CONFIG["FOLDER"], "all_news.json")
    historial = json.load(open(archivo_h)) if os.path.exists(archivo_h) else []
    
    vistos = {x['enlace'] for x in historial}
    nuevos = [n for n in datos if n['enlace'] not in vistos]
    total = nuevos + historial

    resumen = await obtener_resumen_ia(nuevos) if nuevos else "Todo al día por ahora."
    publicar_contenidos(total, nuevos, resumen, scr)

    # Guardar la caché de avatares para la próxima vez
    #scr.guardar_avatars()
    
    #  if nuevos:
        # Enviar Email
        # enviar_email_reporte(resumen, nuevos)
        # TELEGRAM
    enviar_telegram_con_audio(resumen, historial)
        # with open(archivo_h, 'w') as f: json.dump(total[:600], f, indent=4)
    print(f"✅ {len(nuevos)} noticias nuevas procesadas.")
    # else:
    #   print("☕ Sin cambios hoy.")

if __name__ == "__main__":
    asyncio.run(main())
