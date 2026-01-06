#!/usr/bin/env python3
# Script para scraping de noticias tecnológicas y becas, actualizado con permisos corregidos
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime
from urllib.parse import urljoin, urlparse
import time
import re


# Configuración
BASE_URL = "https://blog-jorbencas.vercel.app/"  # Cambiado al blog
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
                date_tag = article.select_one('time, .date, .published, [datetime]')
                img_tag = article.select_one('img')
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = url.rstrip('/') + '/' + link.lstrip('/')
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    if date_tag:
                        if date_tag.get('datetime'):
                            fecha = date_tag['datetime'][:10]  # YYYY-MM-DD
                        else:
                            fecha_text = date_tag.get_text(strip=True)
                            # Intentar parsear fecha, pero por simplicidad, usar actual si falla
                    imagen = ""
                    if img_tag and img_tag.get('src'):
                        imagen = urljoin(url, img_tag['src'])
                    # Evitar duplicados
                    if not any(n['titulo'] == title for n in news):
                        news.append({
                            "titulo": title,
                            "enlace": link,
                            "fecha": fecha,
                            "imagen": imagen,
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
                date_tag = article.select_one('time, .date, .published, [datetime]')
                img_tag = article.select_one('img')
                
                if title_tag and link_tag:
                    title = title_tag.get_text(strip=True)
                    link = link_tag['href']
                    if not link.startswith('http'):
                        link = url.rstrip('/') + '/' + link.lstrip('/')
                    
                    fecha = datetime.now().strftime("%Y-%m-%d")
                    if date_tag:
                        if date_tag.get('datetime'):
                            fecha = date_tag['datetime'][:10]
                    imagen = ""
                    if img_tag and img_tag.get('src'):
                        imagen = urljoin(url, img_tag['src'])
                    
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
                                "fecha": fecha,
                                "imagen": imagen,
                                "fuente": source
                            })
        except Exception as e:
            print(f"Error scraping becas {source}: {e}")
    
    return becas

def clean_slug(text):
    # Convertir a minúsculas, reemplazar espacios por _, quitar caracteres no alfanuméricos excepto _ y -
    text = text.lower().replace(' ', '_')
    text = re.sub(r'[^a-z0-9_-]', '', text)
    return text[:50]

def generate_md_posts(news):
    os.makedirs('./auto-news', exist_ok=True)
    # No limpiar archivos antiguos para hacer acumulativas
    slugs = []
    for item in news:
        # Crear slug simple
        base_slug = clean_slug(item["titulo"])
        slug = base_slug + ".md"
        counter = 1
        while os.path.exists(f'./auto-news/{slug}'):
            slug = f"{base_slug}_{counter}.md"
            counter += 1
        pub_date = item["fecha"]
        image_url = item.get("imagen", "/img/tech_news.webp")
        md_content = f"""---
draft: false
title: "{item["titulo"]}"
description: "Noticia automática de {item["fuente"]}"
pubDate: "{pub_date.replace("-", "/")}"
tags: ['tecnologia', 'auto']
slug: "{slug}"
image: "{image_url}"
author: "Bot Scraper"
layout: "../../layouts/PostLayout.astro"
---

# {item["titulo"]}

Fuente: {item["fuente"]}

[Leer la noticia completa]({item["enlace"]})

*Esta es una noticia automática scrapeada. Para más detalles, visita el enlace original.*
"""
        if not os.path.exists(f'./auto-news/{slug}'):
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
    
    # Acumular todas las noticias
    all_news_file = "./files/all_news.json"
    if os.path.exists(all_news_file):
        with open(all_news_file, 'r', encoding='utf-8') as f:
            all_news = json.load(f)
    else:
        all_news = []
    # Agregar nuevas sin duplicados (por título)
    existing_titles = {n['titulo'] for n in all_news}
    for item in news:
        if item['titulo'] not in existing_titles:
            all_news.append(item)
            existing_titles.add(item['titulo'])
    # Ordenar por fecha descendente
    all_news.sort(key=lambda x: x['fecha'], reverse=True)
    with open(all_news_file, 'w', encoding='utf-8') as f:
        json.dump(all_news, f, ensure_ascii=False, indent=4)
    
    # 3. Scraping de becas
    print("Scraping becas...")
    becas = scrape_becas()
    with open(f"./files/becas_{date}.json", 'w', encoding='utf-8') as f:
        json.dump(becas, f, ensure_ascii=False, indent=4)
    
    # Acumular todas las becas
    all_becas_file = "./files/all_becas.json"
    if os.path.exists(all_becas_file):
        with open(all_becas_file, 'r', encoding='utf-8') as f:
            all_becas = json.load(f)
    else:
        all_becas = []
    # Agregar nuevas sin duplicados (por título)
    existing_titles_b = {b['titulo'] for b in all_becas}
    for item in becas:
        if item['titulo'] not in existing_titles_b:
            all_becas.append(item)
            existing_titles_b.add(item['titulo'])
    # Ordenar por fecha descendente
    all_becas.sort(key=lambda x: x['fecha'], reverse=True)
    with open(all_becas_file, 'w', encoding='utf-8') as f:
        json.dump(all_becas, f, ensure_ascii=False, indent=4)
    
    # 4. Generar posts MD
    print("Generating MD posts...")
    slugs = generate_md_posts(news)
    
    # Actualizar index.html con reporte
    # Ya no se regenera el HTML, ahora es estático con JS
    print("Index.html is now static with JS loading data.")
    
    print("Todo completado.")

if __name__ == "__main__":
    main()