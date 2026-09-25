import json
import hashlib
import os
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path

from config import settings
from models import Proyecto, ProyectoGenerado, HistorialProyectos, Nivel, Scope, TipoProyecto, Lenguaje
from ai_providers import get_provider, AIProvider, DeterministicProvider
from prompts import SYSTEM_PROMPT, build_user_prompt, validate_project_json
from scrapers import scrape_all_sources


class ProjectGenerator:
    def __init__(self):
        self.data_dir = Path(settings.data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.data_dir / settings.history_file
        self.history = self._load_history()
        self.provider: Optional[AIProvider] = None
    
    def _load_history(self) -> HistorialProyectos:
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return HistorialProyectos(**data)
            except Exception as e:
                print(f"[!] Error loading history: {e}")
        return HistorialProyectos()
    
    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history.model_dump(mode='json'), f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[!] Error saving history: {e}")
    
    def _init_provider(self):
        if self.provider is None:
            self.provider = get_provider("gemini", settings.gemini_api_key, settings.ai_model)
    
    def _get_inspiration_sources(self) -> List[Dict]:
        sources = []
        
        # Tips de Telegram
        tips_path = "/home/jorge/dev/devjobs/downloader_telegram/data/tips_database.json"
        if os.path.exists(tips_path):
            try:
                with open(tips_path, 'r', encoding='utf-8') as f:
                    tips_data = json.load(f)
                for tip in tips_data.get("tips", [])[:30]:
                    sources.append({
                        "fuente": "tips_telegram",
                        "titulo": tip.get("title", ""),
                        "descripcion": tip.get("content", ""),
                        "tags": tip.get("tags", [])
                    })
            except Exception:
                pass
        
        return sources
    
    async def _get_external_inspiration(self) -> List[Dict]:
        if not settings.scrape_tuweb_dev:
            return []
        
        try:
            tips_path = "/home/jorge/dev/devjobs/downloader_telegram/data/tips_database.json"
            ideas = await scrape_all_sources(settings.tuweb_dev_url, tips_path)
            return ideas
        except Exception as e:
            print(f"[!] Error scraping external sources: {e}")
            return []
    
    async def generate_projects(
        self,
        count: Optional[int] = None,
        preferred_levels: Optional[List[Nivel]] = None,
        preferred_scopes: Optional[List[Scope]] = None,
        preferred_languages: Optional[List[Lenguaje]] = None,
        preferred_types: Optional[List[TipoProyecto]] = None
    ) -> List[ProyectoGenerado]:
        
        count = count or settings.projects_per_run
        self._init_provider()
        
        # Obtener fuentes de inspiración
        inspiration = self._get_inspiration_sources()
        external = await self._get_external_inspiration()
        inspiration.extend(external)
        
        # Hashes existentes para evitar duplicados
        existing_hashes = [p.proyecto.hash_unicidad for p in self.history.proyectos]
        
        # Construir prompt
        user_prompt = build_user_prompt(
            count=count,
            existing_hashes=existing_hashes,
            inspiration_sources=inspiration,
            preferred_levels=preferred_levels,
            preferred_scopes=preferred_scopes,
            preferred_languages=preferred_languages,
            preferred_types=preferred_types
        )
        
        print(f"[*] Generating {count} projects using {self.provider.get_model_name()}...")
        print(f"[*] Inspiration sources: {len(inspiration)}")
        print(f"[*] Existing projects: {len(existing_hashes)}")
        
        # Generar
        try:
            response = await self.provider.generate(
                prompt=user_prompt,
                system_prompt=SYSTEM_PROMPT,
                temperature=0.8,
                max_tokens=8000
            )
        except Exception as e:
            print(f"[!] AI generation failed: {e}")
            # Fallback a determinístico
            if not isinstance(self.provider, DeterministicProvider):
                print("[*] Falling back to deterministic provider...")
                self.provider = DeterministicProvider()
                response = await self.provider.generate(
                    prompt=user_prompt,
                    system_prompt=SYSTEM_PROMPT
                )
            else:
                raise
        
        # Parsear y validar
        try:
            data = json.loads(response)
            validated = validate_project_json(data)
        except json.JSONDecodeError as e:
            print(f"[!] Invalid JSON from AI: {e}")
            print(f"Response preview: {response[:500]}")
            return []
        except ValueError as e:
            print(f"[!] Validation error: {e}")
            return []
        
        # Filtrar duplicados por hash
        new_projects = []
        for p_data in validated:
            proj_hash = p_data["hash_unicidad"]
            if proj_hash in existing_hashes:
                print(f"[~] Skipping duplicate: {p_data['titulo']} (hash: {proj_hash})")
                continue
            
            existing_hashes.append(proj_hash)
            
            # Crear objeto Proyecto
            proyecto = Proyecto(**p_data)
            generado = ProyectoGenerado(proyecto=proyecto, metadata={
                "provider": self.provider.get_model_name(),
                "prompt_hash": hashlib.md5(user_prompt.encode()).hexdigest()[:16]
            })
            new_projects.append(generado)
        
        # Guardar en historial
        for gp in new_projects:
            self.history.proyectos.append(gp)
            self.history.ultimos_hashes.append(gp.proyecto.hash_unicidad)
        
        # Mantener solo últimos 100 hashes
        self.history.ultimos_hashes = self.history.ultimos_hashes[-100:]
        self.history.total_generados += len(new_projects)
        self.history.fecha_ultima_generacion = datetime.now()
        
        self._save_history()
        
        print(f"[✓] Generated {len(new_projects)} new projects")
        return new_projects


async def main():
    """Entry point para ejecución directa"""
    generator = ProjectGenerator()
    projects = await generator.generate_projects()
    
    for gp in projects:
        p = gp.proyecto
        print(f"\n{'='*60}")
        print(f"📋 {p.titulo} ({p.nivel.value} | {p.scope.value})")
        print(f"{'='*60}")
        print(f"📝 {p.descripcion_corta}")
        print(f"🔧 Lenguaje: {p.tech_stack.lenguaje_principal.value}")
        print(f"📦 Frameworks: {[f['nombre'] for f in p.tech_stack.frameworks]}")
        print(f"⚡ Funcionalidades: {', '.join(p.funcionalidades_clave[:5])}")
        if p.por_que_ia:
            print(f"🤖 IA: {p.por_que_ia} (cliente: {p.cliente_ia_sugerido})")
        print(f"⏱️  ~{p.tiempo_estimado_semanas} semanas | Complejidad: {p.complejidad_estimada}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())