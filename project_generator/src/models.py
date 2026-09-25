from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum
import uuid


class Nivel(str, Enum):
    JUNIOR = "junior"
    SEMISENIOR = "semisenior"
    SENIOR = "senior"


class Scope(str, Enum):
    MINIPROYECTO = "miniproyecto"
    PROYECTO = "proyecto"
    MULTIPROYECTO = "multiproyecto"


class Lenguaje(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    CSHARP = "csharp"
    GO = "go"
    RUST = "rust"


class TipoProyecto(str, Enum):
    WEB = "web"
    API = "api"
    CLI = "cli"
    MOBILE = "mobile"
    DESKTOP = "desktop"
    FULLSTACK = "fullstack"
    MICROSERVICIO = "microservicio"
    BOT = "bot"
    IA_ML = "ia_ml"
    DATOS = "datos"
    DEVOPS = "devops"
    TESTING = "testing"
    SEGURIDAD = "seguridad"


class Herramienta(BaseModel):
    nombre: str
    categoria: str  # framework, lib, db, cloud, ia, testing, etc.
    descripcion: Optional[str] = None
    version_sugerida: Optional[str] = None
    url_docs: Optional[HttpUrl] = None
    por_que: Optional[str] = None  # por qué se sugiere para este proyecto


class TechStack(BaseModel):
    lenguaje_principal: Lenguaje
    frameworks: List[Herramienta] = []
    librerias: List[Herramienta] = []
    bases_datos: List[Herramienta] = []
    infraestructura: List[Herramienta] = []
    ia_ml: List[Herramienta] = []
    testing: List[Herramienta] = []
    otros: List[Herramienta] = []


class Proyecto(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    titulo: str
    descripcion_corta: str
    descripcion_detallada: str
    nivel: Nivel
    scope: Scope
    tipo: List[TipoProyecto]
    tech_stack: TechStack
    funcionalidades_clave: List[str]
    casos_uso: List[str]
    reglas_negocio: List[str] = []
    por_que_ia: Optional[str] = None  # si usa IA, por qué y qué modelo
    cliente_ia_sugerido: Optional[str] = None  # openai, anthropic, gemini, local, none
    recursos_externos: List[str] = []  # APIs, datasets, servicios
    complejidad_estimada: Literal["baja", "media", "alta", "muy_alta"]
    tiempo_estimado_semanas: int
    prerequisitos: List[str] = []
    riesgos: List[str] = []
    ideas_extensión: List[str] = []
    fuente_inspiracion: Optional[str] = None  # "tuweb.dev", "tips_telegram", "ia_generativa", "manual"
    fecha_generacion: datetime = Field(default_factory=datetime.now)
    hash_unicidad: str  # para evitar duplicados


class ProyectoGenerado(BaseModel):
    proyecto: Proyecto
    metadata: dict = {}


class HistorialProyectos(BaseModel):
    proyectos: List[ProyectoGenerado] = []
    ultimos_hashes: List[str] = []  # últimos 100 hashes para anti-duplicados
    total_generados: int = 0
    fecha_ultima_generacion: Optional[datetime] = None