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

# Lista de webs de tecnología en España
SOURCES = {
    "Xataka": "https://www.xataka.com/",
    "Genbeta": "https://www.genbeta.com/",
    "ComputerHoy": "https://computerhoy.com/",
    "HobbyConsolas": "https://www.hobbyconsolas.com/",
    "El País Tecnología": "https://elpais.com/tecnologia/",
    "ABC Tecnología": "https://www.abc.es/tecnologia/",
    "Vida Extra": "https://www.vidaextra.com/"
}

# Fuentes de becas y cursos en Vall d'Albaida y alrededores (Comunidad Valenciana)
BECAS_SOURCES = {
    "Levante-EMV": "https://www.levante-emv.com/",
    "Valencia Plaza": "https://valenciaplaza.com/",
    "Fundación Carolina": "https://www.fundacioncarolina.es/"
}

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

def scrape_becas():
    becas = []
    for source, url in BECAS_SOURCES.items():
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select('article, .post, .entry, .news, .noticia, .beca')[:5]  # Más selectores
            
            for article in articles:
                title_tag = article.select_one('h1, h2, h3, .title, a')
                link_tag = article.select_one('a')
                
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = url.rstrip('/') + '/' + link.lstrip('/')
                    
                    # Filtrar por becas y cursos en informática, IA, tecnología, etc.
                    tech_keywords = ['informática', 'ia', 'inteligencia artificial', 'programación', 'desarrollo', 'tecnología', 'software', 'hardware', 'ciberseguridad', 'machine learning', 'deep learning', 'data science', 'big data', 'blockchain', 'criptomonedas', 'iot', 'internet de las cosas', 'cloud', 'nube', 'devops', 'agile', 'scrum']
                    scholarship_keywords = ['beca', 'curso', 'ayuda', 'subvención', 'formación', 'certificación', 'diploma', 'master', 'doctorado', 'fp', 'vocacional', 'valencia', 'vall', 'albaida']
                    all_keywords = tech_keywords + scholarship_keywords
                    
                    if any(keyword in title.lower() for keyword in all_keywords):
                        # Evitar duplicados
                        if not any(b['titulo'] == title for b in becas):
                            becas.append({
                                "titulo": title,
                                "enlace": link,
                                "fecha": datetime.now().strftime("%Y-%m-%d"),
                                "fuente": source
                            })
        except Exception as e:
            print(f"Error scraping becas {source}: {e}")
    
    return becas

def generate_md_posts(news):
    os.makedirs('./auto-news', exist_ok=True)
    slugs = []
    for item in news:
        # Crear slug simple
        base_slug = item["titulo"].lower().replace(" ", "_").replace("/", "_").replace(":", "").replace("?", "")[:50]
        slug = base_slug + ".md"
        counter = 1
        while os.path.exists(f'./auto-news/{slug}'):
            slug = f"{base_slug}_{counter}.md"
            counter += 1
        pub_date = item["fecha"]
        md_content = f"""---
draft: false
title: "{item["titulo"]}"
description: "Noticia automática de {item["fuente"]}"
pubDate: "{pub_date.replace("-", "/")}"
tags: ['tecnologia', 'auto']
slug: "{slug}"
image: "/img/tech_news.webp"
author: "Bot Scraper"
layout: "../../layouts/PostLayout.astro"
---

# {item["titulo"]}

Fuente: {item["fuente"]}

[Leer la noticia completa]({item["enlace"]})

*Esta es una noticia automática scrapeada. Para más detalles, visita el enlace original.*
"""
        with open(f'./auto-news/{slug}', 'w', encoding='utf-8') as f:
            f.write(md_content)
        slugs.append(slug)
    return slugs

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
    # Filtrar enlaces sospechosos
    news = [item for item in news if 'ads' not in item['enlace'].lower() and 'track' not in item['enlace'].lower()]
    with open(f"./files/tech_news_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(news, f, ensure_ascii=False, indent=4)
    
    # 3. Scraping de becas
    print("Scraping becas...")
    becas = scrape_becas()
    with open(f"./files/becas_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(becas, f, ensure_ascii=False, indent=4)
    
    # 4. Generar posts MD
    print("Generating MD posts...")
    slugs = generate_md_posts(news)
    
    # 5. Scraping de becas
    print("Scraping becas...")
    becas = scrape_becas()
    with open(f"./files/becas_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(becas, f, ensure_ascii=False, indent=4)
    
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
        .date {{ font-size: 0.9em; color: #666; }}
        .logo {{ width: 50px; height: 50px; float: right; }}
    </style>
</head>
<body>
    <img src="https://img.icons8.com/color/96/000000/technology-items.png" alt="Logo Tecnología" class="logo">
    <h1>Reporte Diario - {datetime.now().strftime("%Y-%m-%d %H:%M")}</h1>
    <p class="date">Generado el {datetime.now().strftime("%d de %B de %Y")}</p>
    
    <div class="section">
        <h2>Enlaces Rotos Verificados</h2>
        <p>Esta sección muestra enlaces rotos encontrados en el sitio web durante la verificación automática de enlaces internos.</p>
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
        <h2>Nuevos Posts Automáticos en el Blog</h2>
        <ul>
"""
    for slug in slugs[:10]:
        post_url = f"https://jorbencas.github.io/blog/posts/auto-news/{slug.replace('.md', '')}"
        html_content += f'            <li><a href="{post_url}" target="_blank">{slug.replace(".md", "").replace("_", " ")}</a></li>\n'
    html_content += """
        </ul>
    </div>
    
    <div class="section">
        <h2>Becas y Cursos en España (Vall de Albaida)</h2>
        <ul>
"""
    for beca in becas[:10]:
        html_content += f'            <li><a href="{beca["enlace"]}" target="_blank">{beca["titulo"]}</a> - {beca["fuente"]}</li>\n'
    html_content += """
        </ul>
    </div>
    
    <div class="section">
        <p><a href="sitemap.xml">Ver Sitemap</a></p>
"""
    
    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print("Todo completado.")

if __name__ == "__main__":
    main()