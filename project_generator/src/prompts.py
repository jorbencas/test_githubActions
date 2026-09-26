import json
from typing import List, Dict, Optional
from pydantic import HttpUrl, TypeAdapter, ValidationError
from models import Nivel, Scope, TipoProyecto, Lenguaje, Herramienta, TechStack


_ADAPTER_URL = TypeAdapter(HttpUrl)

# Lo que los modelos devuelven cuando no saben una URL. Todo esto es una cadena
# no vacía, así que un `if not valor` no lo detecta y reventaba la validación.
_URLS_VACIAS = {
    "", "-", "--", "n/a", "na", "n/d", "none", "null", "nil", "no", "?",
    "no disponible", "sin url", "desconocido", "unknown", "no aplica",
}


def _url_es_valida(valor) -> bool:
    """True solo si la cadena es una URL que Pydantic puede parsear."""
    if not isinstance(valor, str) or valor.strip().lower() in _URLS_VACIAS:
        return False
    try:
        _ADAPTER_URL.validate_python(valor.strip())
        return True
    except ValidationError:
        return False


def limpiar_tech_stack(tech_stack) -> dict:
    """Normaliza los items de Herramienta para que no revienten al construir el modelo.

    El prompt pide `url_docs` como texto, así que el modelo responde cosas como
    "N/A" cuando no la conoce. Pydantic exige HttpUrl y un solo item malo
    tumbaba la ejecución entera, descartando los proyectos válidos del resto.
    """
    if not isinstance(tech_stack, dict):
        return tech_stack

    for lista in ("frameworks", "librerias", "bases_datos", "infraestructura",
                  "ia_ml", "testing", "otros"):
        items = tech_stack.get(lista)
        if not isinstance(items, list):
            tech_stack[lista] = []
            continue

        limpios = []
        for item in items:
            if not isinstance(item, dict):
                continue  # el modelo a veces devuelve strings sueltos
            if not item.get("nombre") or not item.get("categoria"):
                continue  # ambos son obligatorios en Herramienta
            if not _url_es_valida(item.get("url_docs")):
                item["url_docs"] = None
            limpios.append(item)
        tech_stack[lista] = limpios

    return tech_stack


SYSTEM_PROMPT = """Eres un arquitecto de software senior que genera ideas de proyectos técnicos reales, funcionales y útiles.

REGLAS ESTRICTAS (OBLIGATORIAS):
1. NUNCA repitas proyectos ya generados (usa hash_unicidad para verificar)
2. Proyectos DEBEN ser funcionales y útiles en el mundo real
3. Especifica NIVEL: junior / semisenior / senior
4. Especifica SCOPE: miniproyecto (1-2 sem) / proyecto (3-6 sem) / multiproyecto (6+ sem)
5. Especifica TIPO(S): web, api, cli, mobile, desktop, fullstack, microservicio, bot, ia_ml, datos, devops, testing, seguridad
6. Lenguajes: python, javascript, typescript, csharp, go, rust
7. Tech stack DETALLADO: frameworks, librerías, BD, infra, IA/ML, testing, otros
8. Para CADA herramienta: nombre, categoría, descripción, versión sugerida, URL docs, POR QUÉ se usa en ESTE proyecto
9. Si usa IA: ESPECIFICAR por qué y qué modelo/cliente (openai, anthropic, gemini, local, none)
10. NO proyectos solo iOS (Android OK, cross-platform OK)
11. Incluir: funcionalidades clave, casos de uso, reglas de negocio, complejidad, tiempo estimado, prerequisitos, riesgos, ideas de extensión
12. Fuente de inspiración: "tuweb.dev", "tips_telegram", "ia_generativa", "manual"
13. Si un campo no aplica, usa null. NUNCA pongas "N/A", "-", "none" ni texto vacío donde se espere una URL o un número: en `url_docs` o una URL válida (https://...) o null

FORMATO DE SALIDA (JSON estricto):
{
  "proyectos": [
    {
      "id": "uuid_corto",
      "titulo": "string",
      "descripcion_corta": "string (max 150 chars)",
      "descripcion_detallada": "string (500-2000 chars)",
      "nivel": "junior|semisenior|senior",
      "scope": "miniproyecto|proyecto|multiproyecto",
      "tipo": ["web", "api", ...],
      "tech_stack": {
        "lenguaje_principal": "python|javascript|typescript|csharp|go|rust",
        "frameworks": [{"nombre": "str", "categoria": "framework", "descripcion": "str", "version_sugerida": "str", "url_docs": "URL válida o null", "por_que": "str"}],
        "librerias": [...],
        "bases_datos": [...],
        "infraestructura": [...],
        "ia_ml": [...],
        "testing": [...],
        "otros": [...]
      },
      "funcionalidades_clave": ["str", ...],
      "casos_uso": ["str", ...],
      "reglas_negocio": ["str", ...],
      "por_que_ia": "str|null",
      "cliente_ia_sugerido": "openai|anthropic|gemini|local|none",
      "recursos_externos": ["str", ...],
      "complejidad_estimada": "baja|media|alta|muy_alta",
      "tiempo_estimado_semanas": int,
      "prerequisitos": ["str", ...],
      "riesgos": ["str", ...],
      "ideas_extension": ["str", ...],
      "fuente_inspiracion": "tuweb.dev|tips_telegram|ia_generativa|manual",
      "fecha_generacion": "ISO8601",
      "hash_unicidad": "md5_16chars"
    }
  ]
}"""


def build_user_prompt(
    count: int,
    existing_hashes: List[str],
    inspiration_sources: List[Dict],
    preferred_levels: Optional[List[Nivel]] = None,
    preferred_scopes: Optional[List[Scope]] = None,
    preferred_languages: Optional[List[Lenguaje]] = None,
    preferred_types: Optional[List[TipoProyecto]] = None
) -> str:
    prompt = f"""Genera EXACTAMENTE {count} proyectos NUEVOS y DIFERENTES.

PROYECTOS YA GENERADOS (NO REPETIR - hashes): {len(existing_hashes)} proyectos previos
Hashes recientes: {existing_hashes[-20:] if existing_hashes else 'ninguno'}

FUENTES DE INSPIRACIÓN DISPONIBLES ({len(inspiration_sources)} items):
"""
    
    for i, src in enumerate(inspiration_sources[:10], 1):
        prompt += f"\n{i}. [{src.get('fuente', 'desconocida')}] {src.get('titulo', 'Sin título')}: {src.get('descripcion', '')[:200]}"
    
    if len(inspiration_sources) > 10:
        prompt += f"\n... y {len(inspiration_sources) - 10} fuentes más"
    
    prompt += "\n\nPREFERENCIAS (opcional, pero intenta variar):"
    
    if preferred_levels:
        prompt += f"\n- Niveles preferidos: {[l.value for l in preferred_levels]}"
    if preferred_scopes:
        prompt += f"\n- Scopes preferidos: {[s.value for s in preferred_scopes]}"
    if preferred_languages:
        prompt += f"\n- Lenguajes preferidos: {[l.value for l in preferred_languages]}"
    if preferred_types:
        prompt += f"\n- Tipos preferidos: {[t.value for t in preferred_types]}"
    
    prompt += """

REQUISITOS CRÍTICOS:
- Cada proyecto debe tener un hash_unicidad único (MD5 de titulo+lenguaje+descripcion_corta, primeros 16 chars)
- NO uses hashes que ya existan en la lista
- Variedad real: mezcla niveles, scopes, lenguajes, tipos
- Proyectos MOBILE permitidos (Flutter, React Native, MAUI) - NO solo iOS nativo
- Si usas IA en el proyecto, JUSTIFÍCALO en por_que_ia (ej: "Clasificación de tickets con embeddings", "Generación de reportes con LLM", "Detección de anomalías en logs")
- Tech stack debe ser COHERENTE con el nivel y scope
- Junior: 1-2 frameworks, BD simple, testing básico
- Senior: Arquitectura limpia, patrones avanzados, observabilidad, CI/CD, multi-servicio
- Incluye SIEMPRE: por_que para cada herramienta del tech stack

EJEMPLOS DE BUENA JUSTIFICACIÓN HERRAMIENTA:
- "FastAPI: tipado automático, validación Pydantic, OpenAPI nativo, rendimiento async"
- "PostgreSQL: JSONB para metadata flexible, constraints, transacciones ACID, extensiones"
- "Redis: cache distribuido, pub/sub para WebSockets, rate limiting, session store"
- "Pytest: fixtures parametrizadas, plugins rico, coverage, paralelo nativo"
- "Docker: reproducibilidad, aislamiento, multi-stage builds, compose para dev"

Genera SOLO el JSON válido. Sin markdown, sin explicaciones extra."""
    
    return prompt


def validate_project_json(data: dict) -> List[dict]:
    """Valida y limpia la respuesta JSON de la IA"""
    if not isinstance(data, dict):
        raise ValueError("Response is not a dict")
    
    proyectos = data.get("proyectos", [])
    if not isinstance(proyectos, list):
        raise ValueError("'proyectos' must be a list")
    
    validated = []
    for p in proyectos:
        if not isinstance(p, dict):
            continue
        
        # Validar campos requeridos
        required = ["titulo", "descripcion_corta", "descripcion_detallada", "nivel", "scope", "tipo", "tech_stack", "funcionalidades_clave"]
        if not all(k in p for k in required):
            continue
        
        # Validar enums
        if p["nivel"] not in [e.value for e in Nivel]:
            p["nivel"] = "semisenior"
        if p["scope"] not in [e.value for e in Scope]:
            p["scope"] = "proyecto"
        
        # Validar tipos
        valid_tipos = [e.value for e in TipoProyecto]
        p["tipo"] = [t for t in p["tipo"] if t in valid_tipos]
        if not p["tipo"]:
            p["tipo"] = ["web"]
        
        # Validar lenguaje
        if "tech_stack" in p and "lenguaje_principal" in p["tech_stack"]:
            lang = p["tech_stack"]["lenguaje_principal"]
            if lang not in [e.value for e in Lenguaje]:
                p["tech_stack"]["lenguaje_principal"] = "python"

        # Normalizar herramientas: sin esto un url_docs inválido tumba el run
        if isinstance(p.get("tech_stack"), dict):
            limpiar_tech_stack(p["tech_stack"])
        
        # Asegurar arrays
        for field in ["funcionalidades_clave", "casos_uso", "reglas_negocio", "recursos_externos", "prerequisitos", "riesgos", "ideas_extension"]:
            if field not in p or not isinstance(p[field], list):
                p[field] = []
        
        # Generar hash si no existe
        if "hash_unicidad" not in p:
            import hashlib
            content = f"{p['titulo']}{p['tech_stack'].get('lenguaje_principal', '')}{p['descripcion_corta']}"
            p["hash_unicidad"] = hashlib.md5(content.encode()).hexdigest()[:16]
        
        # Fecha
        if "fecha_generacion" not in p:
            from datetime import datetime
            p["fecha_generacion"] = datetime.now().isoformat()
        
        # Fuente
        if "fuente_inspiracion" not in p:
            p["fuente_inspiracion"] = "ia_generativa"
        
        validated.append(p)
    
    return validated