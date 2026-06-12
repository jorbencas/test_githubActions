import os, json
from string import Template

POSTS_DIR = "/home/jorge/dev/blog/src/content/posts"

TEMPLATE = Template("""---
draft: false
title: "$title"
description: "$description"
pubDate: "2026-06-11"
tags: $tags
image: "/img/default.jpg"
author: "Jorge Beneyto Castelló"
---

# $title

$intro

## 🛠️ Requisitos e Instalación

$installation

## 🚀 Hola Mundo y Sintaxis Básica

```$lang_code
$hello_world
```

$basic_syntax

## 🏗️ Frameworks Populares

### $framework_name

**Instalación:**
```bash
$framework_install
```

**Estructura Principal:**
$framework_structure

## 📝 Ejercicios Prácticos

1. **$ex1_title**: $ex1_desc
2. **$ex2_title**: $ex2_desc
3. **$ex3_title**: $ex3_desc

## 📚 Recursos y Documentación

- [Documentación Oficial]($doc_url)
- [Repositorio en GitHub]($github_url)
- [Recurso Adicional]($extra_url)
""")

GUIDES = {
    "python": {
        "title": "Guía de Python: De 0 a 100",
        "description": "Domina Python desde los conceptos básicos hasta frameworks como FastAPI.",
        "tags": ["python", "guia", "backend"],
        "intro": "Python es un lenguaje versátil, fácil de leer y potente, ideal para ciencia de datos y web.",
        "installation": "1. Descarga desde python.org.\n2. Instala usando el instalador oficial.\n3. Verifica con `python --version`.",
        "lang_code": "python",
        "hello_world": 'print("Hola Mundo")',
        "basic_syntax": "Usa indentación para bloques. Tipado dinámico pero fuerte.",
        "framework_name": "FastAPI",
        "framework_install": "pip install fastapi uvicorn",
        "framework_structure": "Usa decoradores para rutas. Soporta tipado de Python para validación automática.",
        "ex1_title": "Calculadora", "ex1_desc": "Crea una función que sume dos números.",
        "ex2_title": "Web API", "ex2_desc": "Un endpoint simple con FastAPI que retorne un JSON.",
        "ex3_title": "Scraper", "ex3_desc": "Usa requests para obtener el HTML de una web.",
        "doc_url": "https://docs.python.org/3/",
        "github_url": "https://github.com/python/cpython",
        "extra_url": "https://realpython.com/"
    },
    "javascript": {
        "title": "Guía de JavaScript: De 0 a 100",
        "description": "El lenguaje de la web. Aprende JS moderno y frameworks potentes.",
        "tags": ["javascript", "guia", "frontend"],
        "intro": "JavaScript es el lenguaje esencial para la interactividad en la web y mucho más con Node.js.",
        "installation": "1. Instalar Node.js desde nodejs.org.\n2. Incluir etiquetas <script> en HTML o ejecutar archivos .js con `node`.",
        "lang_code": "javascript",
        "hello_world": 'console.log("Hola Mundo");',
        "basic_syntax": "Sintaxis basada en C. Usa `let` y `const` para variables.",
        "framework_name": "React",
        "framework_install": "npx create-react-app my-app",
        "framework_structure": "Arquitectura basada en componentes funcionales y Hooks.",
        "ex1_title": "Contador", "ex1_desc": "Haz un script que cuente hasta 100 en consola.",
        "ex2_title": "DOM", "ex2_desc": "Cambia el color de un botón al hacer click.",
        "ex3_title": "Fetch API", "ex3_desc": "Obtén datos de una API pública y muéstralos.",
        "doc_url": "https://developer.mozilla.org/es/docs/Web/JavaScript",
        "github_url": "https://github.com/v8/v8",
        "extra_url": "https://javascript.info/"
    },
    "typescript": {
        "title": "Guía de TypeScript: De 0 a 100",
        "description": "JavaScript con superpoderes de tipado estático. Escalabilidad total.",
        "tags": ["typescript", "guia", "frontend"],
        "intro": "TypeScript añade tipado estático a JavaScript, permitiendo detectar errores antes de ejecutar el código.",
        "installation": "1. Instalar Node.js.\n2. Ejecutar `npm install -g typescript`.\n3. Compilar con `tsc`.",
        "lang_code": "typescript",
        "hello_world": 'let msg: string = "Hola Mundo"; console.log(msg);',
        "basic_syntax": "Define tipos con interfaces y tipos. Soporta clases modernas.",
        "framework_name": "NestJS",
        "framework_install": "npm i -g @nestjs/cli && nest new project-name",
        "framework_structure": "Arquitectura modular inspirada en Angular (Módulos, Controladores, Servicios).",
        "ex1_title": "Interface", "ex1_desc": "Crea una interfaz de Usuario y una función que la use.",
        "ex2_title": "Generic", "ex2_desc": "Implementa una función genérica de identidad.",
        "ex3_title": "Decorator", "ex3_desc": "Usa un decorador simple para loguear llamadas a clases.",
        "doc_url": "https://www.typescriptlang.org/docs/",
        "github_url": "https://github.com/microsoft/TypeScript",
        "extra_url": "https://www.typescriptlang.org/play"
    },
    "go": {
        "title": "Guía de Go (Golang): De 0 a 100",
        "description": "Simplicidad y concurrencia. El lenguaje de Google para sistemas escalables.",
        "tags": ["go", "guia", "backend"],
        "intro": "Go es un lenguaje compilado enfocado en la simplicidad, la eficiencia y el manejo de concurrencia mediante goroutines.",
        "installation": "1. Descarga desde go.dev.\n2. Configura el GOPATH.\n3. Verifica con `go version`.",
        "lang_code": "go",
        "hello_world": 'package main\nimport "fmt"\n\nfunc main() {\n    fmt.Println("Hola Mundo")\n}',
        "basic_syntax": "Sin clases, usa structs e interfaces. Manejo de paquetes explícito.",
        "framework_name": "Gin Gonic",
        "framework_install": "go get -u github.com/gin-gonic/gin",
        "framework_structure": "Enfoque en middleware y rutas ultra-rápidas mediante un árbol de búsqueda.",
        "ex1_title": "Goroutines", "ex1_desc": "Ejecuta un bucle en paralelo usando la palabra clave `go`.",
        "ex2_title": "JSON API", "ex2_desc": "Crea un servidor HTTP que responda un JSON usando Gin.",
        "ex3_title": "Channels", "ex3_desc": "Comunica dos goroutines usando un canal.",
        "doc_url": "https://go.dev/doc/",
        "github_url": "https://github.com/golang/go",
        "extra_url": "https://gobyexample.com/"
    },
    "rust": {
        "title": "Guía de Rust: De 0 a 100",
        "description": "Seguridad de memoria sin recolector de basura. El futuro del sistema.",
        "tags": ["rust", "guia", "sistemas"],
        "intro": "Rust garantiza seguridad de memoria mediante su sistema de propiedad (ownership) y préstamo (borrowing).",
        "installation": "1. Usar rustup: `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`.",
        "lang_code": "rust",
        "hello_world": 'fn main() {\n    println!("Hola Mundo");\n}',
        "basic_syntax": "Fuertemente tipado. Usa `match` para control de flujo exhaustivo.",
        "framework_name": "Actix-Web",
        "framework_install": "cargo add actix-web",
        "framework_structure": "Basado en actores y procesamiento asíncrono eficiente.",
        "ex1_title": "Ownership", "ex1_desc": "Experimenta moviendo una variable de un scope a otro.",
        "ex2_title": "Error Handling", "ex2_desc": "Usa Result e Option para manejar un caso de error.",
        "ex3_title": "Calculadora CLI", "ex3_desc": "Lee de la entrada estándar y realiza operaciones básicas.",
        "doc_url": "https://doc.rust-lang.org/book/",
        "github_url": "https://github.com/rust-lang/rust",
        "extra_url": "https://play.rust-lang.org/"
    },
    "java": {
        "title": "Guía de Java: De 0 a 100",
        "description": "Escribe una vez, ejecuta en cualquier lugar (JVM). Estabilidad empresarial.",
        "tags": ["java", "guia", "enterprise"],
        "intro": "Java es un lenguaje orientado a objetos, robusto y con un ecosistema gigante.",
        "installation": "1. Instalar JDK (OpenJDK recomendado).\n2. Configurar JAVA_HOME.\n3. Probar con `java -version`.",
        "lang_code": "java",
        "hello_world": 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hola Mundo");\n    }\n}',
        "basic_syntax": "Todo ocurre dentro de clases. Tipado estático y verboso.",
        "framework_name": "Spring Boot",
        "framework_install": "Generar vía start.spring.io",
        "framework_structure": "Inyección de dependencias y configuración automática mediante anotaciones.",
        "ex1_title": "POO", "ex1_desc": "Crea una clase Animal y una subclase Perro.",
        "ex2_title": "Streams API", "ex2_desc": "Filtra y mapea una lista de números usando Streams.",
        "ex3_title": "REST Controller", "ex3_desc": "Define un @RestController simple en Spring Boot.",
        "doc_url": "https://docs.oracle.com/en/java/",
        "github_url": "https://github.com/openjdk/jdk",
        "extra_url": "https://www.baeldung.com/"
    },
    "csharp": {
        "title": "Guía de C# y .NET: De 0 a 100",
        "description": "Versatilidad total con .NET. Desde Unity a aplicaciones nativas.",
        "tags": ["csharp", "guia", "dotnet"],
        "intro": "C# es el lenguaje principal de Microsoft, diseñado para la plataforma .NET moderna.",
        "installation": "1. Instalar el SDK de .NET desde dotnet.microsoft.com.",
        "lang_code": "csharp",
        "hello_world": 'System.Console.WriteLine("Hola Mundo");',
        "basic_syntax": "Similar a Java pero con características modernas como LINQ y async/await nativo.",
        "framework_name": "ASP.NET Core",
        "framework_install": "dotnet new webapi",
        "framework_structure": "Sistema de inyección de dependencias integrado y middleware HTTP.",
        "ex1_title": "LINQ", "ex1_desc": "Realiza una consulta sobre una lista de objetos usando sintaxis fluida.",
        "ex2_title": "Enums", "ex2_desc": "Usa enumeraciones para definir estados de un pedido.",
        "ex3_title": "Dapper", "ex3_desc": "Acceso básico a base de datos usando este Micro-ORM.",
        "doc_url": "https://docs.microsoft.com/en-us/dotnet/csharp/",
        "github_url": "https://github.com/dotnet/csharplang",
        "extra_url": "https://dotnet.microsoft.com/learn"
    },
    "kotlin": {
        "title": "Guía de Kotlin: De 0 a 100",
        "description": "El lenguaje preferido para Android. Moderno, conciso y seguro.",
        "tags": ["kotlin", "guia", "mobile"],
        "intro": "Kotlin es totalmente interoperable con Java, eliminando errores de punteros nulos.",
        "installation": "1. Instalar IntelliJ IDEA o configurar el compilador `kotlinc`.",
        "lang_code": "kotlin",
        "hello_world": 'fun main() {\n    println("Hola Mundo")\n}',
        "basic_syntax": "Más conciso que Java. Null safety por defecto (?).",
        "framework_name": "Ktor",
        "framework_install": "Implementar plugin en Gradle",
        "framework_structure": "Basado en corrutinas de Kotlin para alta escalabilidad y ligereza.",
        "ex1_title": "Data Classes", "ex1_desc": "Define un modelo de datos en una sola línea.",
        "ex2_title": "Coroutines", "ex2_desc": "Lanza una tarea asíncrona suspendida.",
        "ex3_title": "Cálculo de Promedio", "ex3_desc": "Usa funciones de extensión sobre una lista.",
        "doc_url": "https://kotlinlang.org/docs/",
        "github_url": "https://github.com/JetBrains/kotlin",
        "extra_url": "https://play.kotlinlang.org/"
    },
    "swift": {
        "title": "Guía de Swift: De 0 a 100",
        "description": "Desarrollo nativo para el ecosistema Apple (iOS, macOS).",
        "tags": ["swift", "guia", "ios"],
        "intro": "Swift es un lenguaje rápido, seguro y moderno diseñado por Apple para sus plataformas.",
        "installation": "1. Instalar Xcode en macOS.\n2. Usar Swift Playgrounds.",
        "lang_code": "swift",
        "hello_world": 'print("Hola Mundo")',
        "basic_syntax": "Variables con `var` y constantes con `let`. Control de flujo potente.",
        "framework_name": "SwiftUI",
        "framework_install": "Incluido en Xcode",
        "framework_structure": "Declarativo, basado en vistas y estados persistentes.",
        "ex1_title": "Optionals", "ex1_desc": "Desempaqueta un valor opcional de forma segura con `if let`.",
        "ex2_title": "Struct vs Class", "ex2_desc": "Compara comportamientos de paso por valor y referencia.",
        "ex3_title": "View Simple", "ex3_desc": "Crea una interfaz básica con un texto y un botón en SwiftUI.",
        "doc_url": "https://developer.apple.com/documentation/swift",
        "github_url": "https://github.com/apple/swift",
        "extra_url": "https://swift.org/"
    },
    "php": {
        "title": "Guía de PHP: De 0 a 100",
        "description": "El veterano de la web que sigue moviendo el mundo (Laravel, WordPress).",
        "tags": ["php", "guia", "backend"],
        "intro": "PHP es un lenguaje de script del lado del servidor diseñado para el desarrollo web.",
        "installation": "1. Instalar XAMPP o PHP directo en Linux.\n2. Probar con `php -v`.",
        "lang_code": "php",
        "hello_world": '<?php echo "Hola Mundo"; ?>',
        "basic_syntax": "Variables empiezan por `$`. Débilmente tipado (aunque moderno permite tipos).",
        "framework_name": "Laravel",
        "framework_install": "composer global require laravel/installer",
        "framework_structure": "Patrón MVC elegante, Eloquent ORM y Blade como motor de plantillas.",
        "ex1_title": "Array Map", "ex1_desc": "Aplica una función a todos los elementos de un array.",
        "ex2_title": "Formulario", "ex2_desc": "Recibe datos de un POST y muéstralos por pantalla.",
        "ex3_title": "Migrations", "ex3_desc": "Define una tabla simple en Laravel usando migraciones.",
        "doc_url": "https://www.php.net/docs.php",
        "github_url": "https://github.com/php/php-src",
        "extra_url": "https://laracasts.com/"
    },
    "ruby": {
        "title": "Guía de Ruby: De 0 a 100",
        "description": "El lenguaje de la felicidad del programador. Ruby on Rails.",
        "tags": ["ruby", "guia", "backend"],
        "intro": "Ruby es un lenguaje dinámico y de código abierto enfocado en la simplicidad y la productividad.",
        "installation": "1. Usar rbenv o rvm para instalar Ruby.\n2. `ruby -v`.",
        "lang_code": "ruby",
        "hello_world": 'puts "Hola Mundo"',
        "basic_syntax": "Todo es un objeto. Bloques, procs y lambdas son muy comunes.",
        "framework_name": "Ruby on Rails",
        "framework_install": "gem install rails",
        "framework_structure": "Filosofía 'Convención sobre Configuración' (CoC) y DRY.",
        "ex1_title": "Iterador", "ex1_desc": "Usa `.each` para recorrer una lista de nombres.",
        "ex2_title": "Clase Persona", "ex2_desc": "Crea una clase con atributos y un método de saludo.",
        "ex3_title": "Scaffold", "ex3_desc": "Genera un CRUD completo en Rails con un solo comando.",
        "doc_url": "https://www.ruby-lang.org/en/documentation/",
        "github_url": "https://github.com/ruby/ruby",
        "extra_url": "https://rubyonrails.org/"
    },
    "dart": {
        "title": "Guía de Dart: De 0 a 100",
        "description": "Optimizado para interfaces de usuario fluidas. El corazón de Flutter.",
        "tags": ["dart", "guia", "mobile"],
        "intro": "Dart es un lenguaje centrado en el cliente para aplicaciones rápidas en cualquier plataforma.",
        "installation": "1. Descargar el SDK de Dart desde dart.dev.",
        "lang_code": "dart",
        "hello_world": 'void main() {\n  print("Hola Mundo");\n}',
        "basic_syntax": "AOT y JIT. Soporta clases, mixins y tipado fuerte opcional.",
        "framework_name": "Flutter",
        "framework_install": "Descargar Flutter SDK",
        "framework_structure": "Usa Widgets para todo. Arquitectura reactiva y árbol de renderizado rápido.",
        "ex1_title": "Asincronía", "ex1_desc": "Usa Future y await para simular una carga de datos.",
        "ex2_title": "Mixins", "ex2_desc": "Añade funcionalidad a una clase sin usar herencia múltiple.",
        "ex3_title": "Widget Básico", "ex3_desc": "Crea un botón personalizado en Flutter.",
        "doc_url": "https://dart.dev/guides",
        "github_url": "https://github.com/dart-lang/sdk",
        "extra_url": "https://dartpad.dev/"
    }
}

def generate():
    if not os.path.exists(POSTS_DIR): os.makedirs(POSTS_DIR)
    for slug, data in GUIDES.items():
        data['tags'] = json.dumps(data['tags'], ensure_ascii=False)
        content = TEMPLATE.safe_substitute(data)
        path = os.path.join(POSTS_DIR, f"guia-0-100-{slug}.mdx")
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ Generado: {path}")

if __name__ == "__main__":
    generate()
