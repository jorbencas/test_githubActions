from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import json
from tenacity import retry, stop_after_attempt, wait_exponential


class AIProvider(ABC):
    @abstractmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass


class GeminiProvider(AIProvider):
    """Proveedor Gemini sobre el SDK `google-genai` (mismo que el resto del repo)."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
        except ImportError:
            raise RuntimeError("google-genai package not installed. Run: pip install google-genai")
        self.client = genai.Client(api_key=self.api_key)

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        if not self.client:
            self._init_client()

        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
        }
        # `system_instruction` solo existe en los modelos 2.x (en 1.x iba dentro del prompt)
        if self.model.startswith("gemini-2"):
            config["system_instruction"] = system_prompt
            contents = prompt
        else:
            contents = f"{system_prompt}\n\n{prompt}"

        response = await asyncio.to_thread(
            self.client.models.generate_content,
            model=self.model,
            contents=contents,
            config=config,
        )
        if not response or not response.text:
            raise RuntimeError(f"Gemini devolvió respuesta vacía (modelo={self.model})")
        return response.text

    def get_model_name(self) -> str:
        return f"gemini:{self.model}"


class DeterministicProvider(AIProvider):
    """Proveedor determinístico basado en plantillas - sin IA externa"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, Any]:
        return {
            "python": [
                {
                    "titulo": "CLI de gestión de tareas con persistencia local",
                    "descripcion_corta": "Gestor de tareas en terminal con SQLite y rich",
                    "nivel": "junior",
                    "scope": "miniproyecto",
                    "tipo": ["cli"],
                    "lenguaje": "python",
                    "frameworks": [{"nombre": "typer", "categoria": "framework"}, {"nombre": "rich", "categoria": "ui"}],
                    "librerias": [{"nombre": "sqlite3", "categoria": "db"}, {"nombre": "pydantic", "categoria": "validacion"}],
                    "funcionalidades": ["CRUD tareas", "Filtrado por etiquetas", "Exportar JSON/CSV", "Recordatorios"],
                    "complejidad": "baja",
                    "tiempo_semanas": 1
                },
                {
                    "titulo": "API REST para gestión de inventario multi-almacén",
                    "descripcion_corta": "FastAPI + PostgreSQL + Redis cache",
                    "nivel": "semisenior",
                    "scope": "proyecto",
                    "tipo": ["api"],
                    "lenguaje": "python",
                    "frameworks": [{"nombre": "fastapi", "categoria": "framework"}, {"nombre": "sqlalchemy", "categoria": "orm"}],
                    "librerias": [{"nombre": "redis", "categoria": "cache"}, {"nombre": "alembic", "categoria": "migraciones"}],
                    "funcionalidades": ["Multi-tenant", "Stock tiempo real", "Alertas bajo stock", "Audit log"],
                    "complejidad": "media",
                    "tiempo_semanas": 3
                }
            ],
            "javascript": [
                {
                    "titulo": "Dashboard de métricas en tiempo real con WebSockets",
                    "descripcion_corta": "React + Socket.io + Chart.js para monitoring",
                    "nivel": "semisenior",
                    "scope": "proyecto",
                    "tipo": ["web", "fullstack"],
                    "lenguaje": "typescript",
                    "frameworks": [{"nombre": "react", "categoria": "framework"}, {"nombre": "socket.io", "categoria": "realtime"}],
                    "librerias": [{"nombre": "chart.js", "categoria": "visualizacion"}, {"nombre": "zustand", "categoria": "state"}],
                    "funcionalidades": ["Métricas live", "Alertas visuales", "Historial", "Multi-usuario"],
                    "complejidad": "media",
                    "tiempo_semanas": 3
                }
            ],
            "csharp": [
                {
                    "titulo": "Microservicio de procesamiento de pedidos con gRPC",
                    "descripcion_corta": "ASP.NET Core + gRPC + Entity Framework",
                    "nivel": "senior",
                    "scope": "multiproyecto",
                    "tipo": ["microservicio", "api"],
                    "lenguaje": "csharp",
                    "frameworks": [{"nombre": "asp.net core", "categoria": "framework"}, {"nombre": "grpc", "categoria": "comunicacion"}],
                    "librerias": [{"nombre": "entity framework core", "categoria": "orm"}, {"nombre": "mediatr", "categoria": "patrones"}],
                    "funcionalidades": ["CQRS", "Event sourcing", "Health checks", "Distributed tracing"],
                    "complejidad": "alta",
                    "tiempo_semanas": 6
                }
            ]
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        import random
        import hashlib
        
        # Usar hash del prompt para selección determinística pero variada
        seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        random.seed(seed)
        
        all_templates = []
        for lang_templates in self.templates.values():
            all_templates.extend(lang_templates)
        
        selected = random.sample(all_templates, min(3, len(all_templates)))
        
        result = {
            "proyectos": [
                {
                    "id": f"det_{random.randint(1000,9999)}",
                    "titulo": t["titulo"],
                    "descripcion_corta": t["descripcion_corta"],
                    "descripcion_detallada": f"{t['descripcion_corta']}. Nivel: {t['nivel']}. Scope: {t['scope']}. Incluye: {', '.join(t['funcionalidades'])}",
                    "nivel": t["nivel"],
                    "scope": t["scope"],
                    "tipo": t["tipo"],
                    "tech_stack": {
                        "lenguaje_principal": t["lenguaje"],
                        "frameworks": t.get("frameworks", []),
                        "librerias": t.get("librerias", []),
                        "bases_datos": [],
                        "infraestructura": [],
                        "ia_ml": [],
                        "testing": [],
                        "otros": []
                    },
                    "funcionalidades_clave": t["funcionalidades"],
                    "casos_uso": [f"Usuario {f.lower()}" for f in t["funcionalidades"]],
                    "reglas_negocio": [],
                    "por_que_ia": None,
                    "cliente_ia_sugerido": "none",
                    "recursos_externos": [],
                    "complejidad_estimada": t["complejidad"],
                    "tiempo_estimado_semanas": t["tiempo_semanas"],
                    "prerequisitos": [f"Conocimientos de {t['lenguaje']}", "Git básico"],
                    "riesgos": ["Scope creep", "Tiempo limitado"],
                    "ideas_extensión": ["Añadir tests", "CI/CD", "Documentación"],
                    "fuente_inspiracion": "template_deterministico",
                    "fecha_generacion": "2024-01-01T00:00:00",
                    "hash_unicidad": hashlib.md5(f"{t['titulo']}{t['lenguaje']}".encode()).hexdigest()[:16]
                }
                for t in selected
            ]
        }
        
        return json.dumps(result, ensure_ascii=False)
    
    def get_model_name(self) -> str:
        return "deterministic:templates"


def get_provider(provider_name: str, api_key: Optional[str], model: str) -> AIProvider:
    provider_name = (provider_name or "gemini").lower()

    if provider_name == "gemini":
        if not api_key:
            raise ValueError("GEMINI_API_KEY required for Gemini provider")
        return GeminiProvider(api_key, model)
    elif provider_name == "deterministic":
        return DeterministicProvider()
    else:
        raise ValueError(f"Unknown provider: {provider_name} (solo 'gemini' o 'deterministic')")