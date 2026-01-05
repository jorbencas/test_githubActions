#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

# Lista de webs de tecnología en España
SOURCES = {
    "Xataka": "https://www.xataka.com/",
    "Genbeta": "https://www.genbeta.com/",
    "ComputerHoy": "https://computerhoy.com/",
    "El Español Tech": "https://www.elespanol.com/tecno/"
}

def scrape_news():
    news = []
    for source, url in SOURCES.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extraer artículos (ajustar selectores según la estructura del sitio)
            articles = soup.select('article, .post, .entry')[:5]  # Limitar a 5 por sitio
            
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

def main():
    # Crear directorio si no existe
    os.makedirs('./files', exist_ok=True)
    
    # Scraper noticias
    news = scrape_news()
    
    # Guardar en JSON
    date = datetime.now().strftime("%Y%m%d")
    json_file = f"./files/tech_news_{date}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    
    # Actualizar index.html
    html_content = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Noticias de Tecnología en España</title>
</head>
<body>
    <h1>Últimas Noticias de Tecnología</h1>
    <p>Actualizado: {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
    <ul>
"""
    for item in news:
        html_content += f'        <li><a href="{item["enlace"]}" target="_blank">{item["titulo"]}</a> - {item["fuente"]}</li>\n'
    
    html_content += """
    </ul>
</body>
</html>
"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Scraping completado. {len(news)} noticias guardadas.")

if __name__ == "__main__":
    main()