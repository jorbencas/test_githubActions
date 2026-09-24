import asyncio
import re
import hashlib
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup


class TuWebDevScraper:
    """Scraper para obtener ideas de proyectos de tuweb.dev"""
    
    def __init__(self, base_url: str = "https://tuweb.dev/"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            follow_redirects=True
        )
    
    async def close(self):
        await self.client.aclose()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"[!] Error fetching {url}: {e}")
            return None
    
    def extract_project_ideas(self, html: str) -> List[Dict]:
        soup = BeautifulSoup(html, 'lxml')
        ideas = []
        
        # Buscar patrones comunes de ideas de proyectos
        # tuweb.dev puede tener diferentes estructuras, intentamos varias
        
        # 1. Artículos/posts con ideas
        for article in soup.find_all(['article', 'div', 'section'], class_=re.compile(r'(post|project|idea|card)', re.I)):
            text = article.get_text(strip=True)
            if self._looks_like_project_idea(text):
                ideas.append({
                    "titulo": self._extract_title(article) or "Proyecto sin título",
                    "descripcion": text[:500],
                    "url": self._extract_url(article),
                    "fuente": "tuweb.dev"
                })
        
        # 2. Listas de proyectos
        for li in soup.find_all('li'):
            text = li.get_text(strip=True)
            if self._looks_like_project_idea(text) and len(text) > 50:
                ideas.append({
                    "titulo": text[:100],
                    "descripcion": text[:500],
                    "url": self.base_url,
                    "fuente": "tuweb.dev"
                })
        
        # 3. Buscar en todo el texto patrones de ideas
        all_text = soup.get_text()
        project_patterns = [
            r'(?:proyecto|idea|app|aplicación|web|tool|herramienta)[\s:]+([^.]{50,300})',
            r'(?:build|crea|desarrolla|haz)[\s]+(?:un|una)[\s]+([^.]{50,300})',
            r'(?:project|idea|app|tool)[\s:]+([^.]{50,300})',
        ]
        
        for pattern in project_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                clean = match.strip()
                if self._looks_like_project_idea(clean):
                    ideas.append({
                        "titulo": clean[:100],
                        "descripcion": clean[:500],
                        "url": self.base_url,
                        "fuente": "tuweb.dev"
                    })
        
        # Deduplicar por hash de contenido
        seen = set()
        unique = []
        for idea in ideas:
            h = hashlib.md5(idea["descripcion"].encode()).hexdigest()[:12]
            if h not in seen:
                seen.add(h)
                unique.append(idea)
        
        return unique[:20]  # Máximo 20 ideas por scraping
    
    def _looks_like_project_idea(self, text: str) -> bool:
        keywords = [
            'proyecto', 'app', 'aplicación', 'web', 'tool', 'herramienta',
            'api', 'dashboard', 'bot', 'sistema', 'plataforma', 'servicio',
            'project', 'idea', 'build', 'create', 'develop', 'dashboard',
            'crud', 'management', 'tracker', 'generator', 'analyzer',
            'ecommerce', 'blog', 'cms', 'auth', 'chat', 'real-time'
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in keywords) and len(text) > 30
    
    def _extract_title(self, element) -> Optional[str]:
        for tag in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'strong', 'b']:
            found = element.find(tag)
            if found:
                return found.get_text(strip=True)
        return None
    
    def _extract_url(self, element) -> Optional[str]:
        link = element.find('a', href=True)
        if link:
            return urljoin(self.base_url, link['href'])
        return None
    
    async def scrape(self) -> List[Dict]:
        html = await self.fetch_page(self.base_url)
        if not html:
            return []
        return self.extract_project_ideas(html)


class TipsTelegramScraper:
    """Extrae ideas de la base de datos de tips del bot de Telegram"""
    
    def __init__(self, tips_db_path: str = "/home/jorge/dev/devjobs/downloader_telegram/data/tips_database.json"):
        self.tips_db_path = tips_db_path
    
    def extract_ideas(self) -> List[Dict]:
        import json
        try:
            with open(self.tips_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"[!] Error loading tips database: {e}")
            return []
        
        ideas = []
        tips = data.get("tips", [])
        
        for tip in tips:
            # Buscar tips que sugieran proyectos o herramientas
            content = tip.get("content", "") + " " + tip.get("title", "")
            if self._suggests_project(content):
                ideas.append({
                    "titulo": tip.get("title", "Tip de proyecto"),
                    "descripcion": content[:500],
                    "tags": tip.get("tags", []),
                    "fuente": "tips_telegram"
                })
        
        return ideas[:15]
    
    def _suggests_project(self, text: str) -> bool:
        project_keywords = [
            'proyecto', 'app', 'aplicación', 'web', 'tool', 'herramienta',
            'api', 'dashboard', 'bot', 'sistema', 'plataforma', 'crear',
            'build', 'develop', 'implement', 'project', 'idea', 'starter',
            'template', 'boilerplate', 'cli', 'library', 'framework'
        ]
        text_lower = text.lower()
        return any(kw in text_lower for kw in project_keywords)


async def scrape_all_sources(tuweb_url: str, tips_db_path: str) -> List[Dict]:
    all_ideas = []
    
    # Scraper tuweb.dev
    scraper = TuWebDevScraper(tuweb_url)
    try:
        tuweb_ideas = await scraper.scrape()
        all_ideas.extend(tuweb_ideas)
        print(f"[+] tuweb.dev: {len(tuweb_ideas)} ideas")
    finally:
        await scraper.close()
    
    # Scraper tips Telegram
    tips_scraper = TipsTelegramScraper(tips_db_path)
    tips_ideas = tips_scraper.extract_ideas()
    all_ideas.extend(tips_ideas)
    print(f"[+] tips_telegram: {len(tips_ideas)} ideas")
    
    return all_ideas