#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time

# Configuración
BASE_URL = "https://jorbencas.github.io/"  # Cambiado al portfolio
MAX_DEPTH = 2  # Profundidad de crawling
TIMEOUT = 10

def get_all_links(url, visited, depth=0):
    if depth > MAX_DEPTH or url in visited:
        return set()
    visited.add(url)
    links = set()
    try:
        response = requests.get(url, timeout=TIMEOUT)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            full_url = urljoin(url, href)
            if urlparse(full_url).netloc == urlparse(BASE_URL).netloc:  # Solo enlaces internos
                links.add(full_url)
    except Exception as e:
        print(f"Error crawling {url}: {e}")
    return links

def check_links():
    visited = set()
    to_check = set([BASE_URL])
    broken_links = []
    working_links = []

    while to_check:
        current_url = to_check.pop()
        if current_url in visited:
            continue
        visited.add(current_url)
        
        try:
            response = requests.head(current_url, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code >= 400:
                broken_links.append({"url": current_url, "status": response.status_code})
            else:
                working_links.append({"url": current_url, "status": response.status_code})
        except Exception as e:
            broken_links.append({"url": current_url, "error": str(e)})
        
        # Obtener más enlaces internos
        new_links = get_all_links(current_url, visited, depth=len(visited))
        to_check.update(new_links)
        time.sleep(0.5)  # Delay para no sobrecargar

    return working_links, broken_links

def scrape_news():
    # Mantener scraping de noticias como opción
    SOURCES = {
        "Xataka": "https://www.xataka.com/",
        "Genbeta": "https://www.genbeta.com/",
        "ComputerHoy": "https://computerhoy.com/",
        "HobbyConsolas": "https://www.hobbyconsolas.com/",
        "El País Tecnología": "https://elpais.com/tecnologia/",
        "ABC Tecnología": "https://www.abc.es/tecnologia/",
        "Vida Extra": "https://www.vidaextra.com/"
    }
    news = []
    for source, url in SOURCES.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('article, .post, .entry')[:5]
            for article in articles:
                title_tag = article.select_one('h1, h2, h3, .title')
                link_tag = article.select_one('a')
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = url.rstrip('/') + '/' + link.lstrip('/')
                    news.append({
                        "titulo": title,
                        "enlace": link,
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                        "fuente": source
                    })
        except Exception as e:
            print(f"Error scraping {source}: {e}")
    return news

def generate_sitemap():
    # Generador simple de sitemap
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    # Aquí agregar URLs del sitio, por simplicidad, usar enlaces encontrados
    working, _ = check_links()
    for link in working[:50]:  # Limitar
        sitemap += f'  <url><loc>{link["url"]}</loc><lastmod>{datetime.now().strftime("%Y-%m-%d")}</lastmod></url>\n'
    sitemap += '</urlset>'
    return sitemap

def main():
    os.makedirs('./files', exist_ok=True)
    date = datetime.now().strftime("%Y%m%d")
    
    # 1. Checker de enlaces rotos
    print("Checking links...")
    working, broken = check_links()
    link_report = {"working": working, "broken": broken}
    with open(f"./files/link_check_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(link_report, f, ensure_ascii=False, indent=4)
    
    # 2. Scraping de noticias
    print("Scraping news...")
    news = scrape_news()
    with open(f"./files/tech_news_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    
    # 3. Generar sitemap
    print("Generating sitemap...")
    sitemap = generate_sitemap()
    with open('sitemap.xml', 'w', encoding='utf-8') as f:
        f.write(sitemap)
    
    # Actualizar index.html con reporte
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Reporte Diario</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f4f4f4; }}
        h1 {{ color: #333; }}
        h2 {{ color: #555; border-bottom: 2px solid #ddd; padding-bottom: 5px; }}
        ul {{ list-style-type: none; padding: 0; }}
        li {{ background: #fff; margin: 5px 0; padding: 10px; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }}
        a {{ color: #007bff; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .broken {{ background: #ffe6e6; }}
        .working {{ background: #e6ffe6; }}
        .section {{ margin-bottom: 30px; }}
    </style>
</head>
<body>
    <h1>Reporte Diario - {datetime.now().strftime("%Y-%m-%d %H:%M")}</h1>
    
    <div class="section">
        <h2>Enlaces Rotos</h2>
        <ul>
"""
    for broken_link in broken[:10]:  # Mostrar primeros 10
        status = broken_link.get("status", "Error")
        html_content += f'            <li class="broken">{broken_link["url"]} - Status: {status}</li>\n'
    html_content += """
        </ul>
    </div>
    
    <div class="section">
        <h2>Últimas Noticias de Tecnología</h2>
        <ul>
"""
    for item in news[:10]:
        html_content += f'            <li><a href="{item["enlace"]}" target="_blank">{item["titulo"]}</a> - {item["fuente"]}</li>\n'
    html_content += """
        </ul>
    </div>
    
    <div class="section">
        <p><a href="sitemap.xml">Ver Sitemap</a></p>
    </div>
</body>
</html>
"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Todo completado.")

if __name__ == "__main__":
    main()