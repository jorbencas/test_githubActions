#!/usr/bin/env python3
"""
Migra recursos del blog a herramientas.json para el bot de Telegram.
"""
import json
from datetime import datetime
from pathlib import Path

BLOG_RESOURCES = Path("/home/jorge/dev/blog/src/data/resources.json")
OUTPUT_FILE = Path("/home/jorge/dev/test_githubActions/files/recursos_blog.json")

# Mapeo de categorías del blog a categorías del bot
CATEGORY_MAP = {
    "administración de sistemas": "🖥️ Sistemas",
    "algoritmos y práctica": "🧮 Algoritmos",
    "apis": "🔌 APIs",
    "aprendizaje": "📚 Aprendizaje",
    "backend as a service": "⚡ BaaS",
    "blogs": "📝 Blogs",
    "canales de youtube": "📺 YouTube",
    "certificaciones informáticas": "🎓 Certificaciones",
    "cms": "📰 CMS",
    "componentes ui": "🎨 UI",
    "comunidad": "👥 Comunidad",
    "conversión de archivos": "🔄 Archivos",
    "diseño gráfico / figma": "✏️ Diseño",
    "documentación": "📖 Docs",
    "dominios": "🌐 Dominios",
    "editores con ia / editores multimedia": "🎬 Editores",
    "extensiones": "🧩 Extensiones",
    "extracción de información de imágenes/vídeos": "🖼️ Extracción",
    "frameworks": "🏗️ Frameworks",
    "gaming / vr / ar": "🎮 Gaming",
    "git / control de versiones": "🔀 Git",
    "hacking / ciberseguridad": "🛡️ Seguridad",
    "herramientas dev": "🛠️ Dev Tools",
    "hosting / nube": "☁️ Hosting",
    "iconos": "🔷 Iconos",
    "inteligencia artificial": "🤖 IA",
    "multimedia": "🎵 Multimedia",
    "noticias de tecnología": "📰 Noticias",
    "nuevas herramientas descubiertas": "🆕 Nuevas",
    "nuevas-herramientas": "🆕 Nuevas",
    "productividad": "⚡ Productividad",
    "redes / wifi / ethernet": "📶 Redes",
    "rendimiento": "🚀 Rendimiento",
    "recursos": "📦 Recursos",
    "seguridad": "🔒 Seguridad",
    "servidores": "🖥️ Servidores",
    "software de escritorio": "💻 Desktop",
    "streaming": "📡 Streaming",
    "template / boilerplate": "📋 Templates",
    "testing": "🧪 Testing",
    "traducción": "🌐 Traducción",
    "api": "🔌 APIs",
    "herramientas": "🛠️ Dev Tools",
}

def migrate():
    # Leer recursos del blog
    with open(BLOG_RESOURCES, "r", encoding="utf-8") as f:
        resources = json.load(f)
    
    print(f"📚 Recursos encontrados en el blog: {len(resources)}")
    
    # Convertir al formato del bot
    tools = []
    now = datetime.now().isoformat()
    date_str = datetime.now().strftime("%d/%m")
    
    for r in resources:
        category = r.get("category", "").lower()
        bot_category = CATEGORY_MAP.get(category, "💡 General")
        
        tool = {
            "titulo": r.get("title", ""),
            "enlace": r.get("href", ""),
            "fuente": "Blog Recursos",
            "tipo": "herramienta",
            "f": date_str,
            "fecha_publicacion": "",
            "subtipo": "recurso_blog",
            "descripcion": r.get("description", ""),
            "repo": "",
            "fecha_real": date_str,
            "ts": now,
            "categoria": bot_category,
            "pricing": r.get("pricing", ""),
            "blog_category": r.get("category", ""),
        }
        tools.append(tool)
    
    # Guardar
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(tools, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Migration complete: {len(tools)} recursos guardados en {OUTPUT_FILE}")
    
    # Resumen por categoría
    cat_counts = {}
    for t in tools:
        cat = t["categoria"]
        cat_counts[cat] = cat_counts.get(cat, 0) + 1
    
    print("\n📊 Distribución por categoría:")
    for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
        print(f"   {cat}: {count}")

if __name__ == "__main__":
    migrate()
