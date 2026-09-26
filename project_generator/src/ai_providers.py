from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
import asyncio
import json
import re
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception


class AIProviderError(RuntimeError):
    """Fallo genérico de un proveedor de IA."""


class QuotaExhaustedError(AIProviderError):
    """La cuota diaria del free tier de Gemini está agotada.

    Reintentar es inútil: el límite es por día, proyecto y modelo, no por
    minuto, así que solo se recupera al día siguiente.
    """


_RETRY_DELAY_RE = re.compile(r"retry in ([\d.]+)\s*s", re.IGNORECASE)


def _es_error_429(exc: Exception) -> bool:
    """True si la excepción es un 429 RESOURCE_EXHAUSTED del SDK de Gemini."""
    try:
        from google.genai import errors as genai_errors
    except ImportError:
        return False
    return isinstance(exc, genai_errors.ClientError) and getattr(exc, "code", None) == 429


def _es_tope_diario(exc: Exception) -> bool:
    """True si el 429 agota la cuota diaria, no solo el ritmo por minuto."""
    texto = str(exc).lower()
    return "perday" in texto or "free_tier" in texto or "requestsperday" in texto


def _es_error_404(exc: Exception) -> bool:
    """True si el modelo no existe o no está habilitado (404 NOT_FOUND)."""
    try:
        from google.genai import errors as genai_errors
    except ImportError:
        return False
    if not isinstance(exc, genai_errors.ClientError) or getattr(exc, "code", None) != 404:
        return False
    texto = str(exc).lower()
    return "not_found" in texto or "not found" in texto or "404" in texto


def _espera_sugerida_por_la_api(exc: Exception) -> Optional[float]:
    """Segundos que indica la propia API en el RetryInfo del error 429."""
    match = _RETRY_DELAY_RE.search(str(exc))
    if not match:
        return None
    return min(float(match.group(1)), 120.0)


def _debe_reintentar(exc: Exception) -> bool:
    """Los 429 los gestiona `_llamar_con_reintentos`; tenacity solo el resto.

    Sin esto los reintentos se multiplican (3 del bucle x 3 de tenacity = 9
    llamadas) y un límite de ritmo se convierte en una tanda de peticiones
    inútiles. Los AIProviderError tampoco se reintentan: un 404 o una respuesta
    vacía no son transitorios, y reintentarlos solo los envuelve en RetryError,
    que esconde la causa real.
    """
    if isinstance(exc, AIProviderError):
        return False
    return not _es_error_429(exc)


class AIProvider(ABC):
    @abstractmethod
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass


class ModelNotAvailableError(AIProviderError):
    """El modelo no existe o no está disponible para esta API key (404)."""


class GeminiProvider(AIProvider):
    """Proveedor Gemini sobre el SDK `google-genai` (mismo que el resto del repo).

    `model` admite una lista separada por comas y se prueba en orden. Se pasa al
    siguiente cuando el anterior no está disponible (404) o se ha quedado sin
    cuota (429). Como el cupo del free tier es por modelo, esta lista también
    sirve de reserva: no es solo un mecanismo de errores.
    """

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.models = [m.strip() for m in str(model).split(",") if m.strip()] or ["gemini-2.5-flash"]
        self.model = self.models[0]
        self.client = None
        self._init_client()

    def _init_client(self):
        try:
            from google import genai
        except ImportError:
            raise RuntimeError("google-genai package not installed. Run: pip install google-genai")
        self.client = genai.Client(api_key=self.api_key)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception(_debe_reintentar),
    )
    async def generate(self, prompt: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 4000) -> str:
        if not self.client:
            self._init_client()

        config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "response_mime_type": "application/json",
        }
        return await self._probar_modelos(prompt, system_prompt, config)

    def _preparar_contenidos(self, model: str, prompt: str, system_prompt: str, config: Dict[str, Any]):
        """`system_instruction` solo existe en los modelos 2.x (en 1.x iba en el prompt)."""
        config = dict(config)
        if model.startswith("gemini-2"):
            config["system_instruction"] = system_prompt
            return prompt, config
        return f"{system_prompt}\n\n{prompt}", config

    async def _probar_modelos(self, prompt: str, system_prompt: str, config: Dict[str, Any]) -> str:
        """Recorre la lista de modelos saltando los que no sirven."""
        for posicion, model in enumerate(self.models):
            contents, config_modelo = self._preparar_contenidos(model, prompt, system_prompt, config)
            try:
                return await self._llamar_con_reintentos(model, contents, config_modelo)
            except (ModelNotAvailableError, QuotaExhaustedError) as e:
                if posicion == len(self.models) - 1:
                    raise
                siguiente = self.models[posicion + 1]
                motivo = "sin cuota" if isinstance(e, QuotaExhaustedError) else "no disponible"
                print(f"[!] {model} {motivo}; pruebo {siguiente}.")
        raise AIProviderError(f"ningún modelo de {self.models} respondió")

    async def _llamar_con_reintentos(self, model: str, contents: str, config: Dict[str, Any]) -> str:
        """Llama a un modelo separando el 429 transitorio del tope diario de cuota.

        El SDK reintenta por su cuenta los 429, pero con esperas fijas de
        segundos: si la API pide 41s no llega a reintentar a tiempo y el error
        sale como RetryError, que oculta que el problema es la cuota. Aquí se
        respeta el RetryInfo del servidor y, si el límite es diario, se
        aborta sin reintentar.
        """
        for intento in range(3):
            try:
                response = await asyncio.to_thread(
                    self.client.models.generate_content,
                    model=model,
                    contents=contents,
                    config=config,
                )
            except Exception as e:
                if _es_error_404(e):
                    raise ModelNotAvailableError(f"{model} no está disponible para esta API key") from e
                if not _es_error_429(e):
                    raise
                if _es_tope_diario(e):
                    raise QuotaExhaustedError(
                        f"Cuota diaria de {model} agotada (free tier: 20 peticiones/día "
                        "por proyecto y modelo). Es una cuota compartida: la consumen también "
                        "los workflows de scraping, así que puede agotarse aunque este "
                        "workflow no haya enviado ni una petición."
                    ) from e
                espera = _espera_sugerida_por_la_api(e)
                if espera is None or intento == 2:
                    raise
                print(f"[!] {model} limitado por cuota (429), reintento {intento + 1}/3 en {espera:.0f}s")
                await asyncio.sleep(espera)
                continue

            if not response or not response.text:
                raise AIProviderError(f"Gemini devolvió respuesta vacía (modelo={model})")

            return response.text

        raise AIProviderError(f"Gemini no devolvió contenido (modelo={self.model})")

    def get_model_name(self) -> str:
        if len(self.models) == 1:
            return f"gemini:{self.model}"
        return f"gemini:{' > '.join(self.models)}"


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