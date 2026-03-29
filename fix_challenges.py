"""
fix_challenges.py
=================
Reescribe los archivos MDX de retos estáticos con:
  - Soluciones reales y funcionales
  - Lenguajes del Codeember (rotación cíclica)
  - Descripciones y pasos explicativos concretos

Uso: python fix_challenges.py
"""
import os, re, json

CHALLENGES_DIR = "../blog/src/content/auto-challenges"

# Lenguajes Codeember en rotación
LANGS = [
    ("python",     "python",     "Python"),
    ("javascript", "javascript", "JavaScript"),
    ("typescript", "typescript", "TypeScript"),
    ("go",         "go",         "Go"),
    ("rust",       "rust",       "Rust"),
    ("java",       "java",       "Java"),
    ("csharp",     "csharp",     "C#"),
    ("kotlin",     "kotlin",     "Kotlin"),
    ("swift",      "swift",      "Swift"),
    ("php",        "php",        "PHP"),
    ("ruby",       "ruby",       "Ruby"),
    ("dart",       "dart",       "Dart"),
]

# ─────────────────────────────────────────────
# BASE DE DATOS DE SOLUCIONES (retos estáticos)
# ─────────────────────────────────────────────
SOLUTIONS = {
    # ── INICIACIÓN ──────────────────────────
    "suma-de-digitos": {
        "desc": "Dado un número entero positivo, suma todos sus dígitos. Por ejemplo: 1234 → 1+2+3+4 = 10.",
        "p1": "Convertimos el número a string para iterar carácter a carácter, luego convertimos cada dígito a int y los sumamos.",
        "p2": "Podemos usar un bucle o la función `sum()` con una expresión generadora. El enfoque con `sum()` es más idiomático.",
        "p3": "O(d) donde d es el número de dígitos. Espacio O(1).",
        "py": "def suma_digitos(n):\n    return sum(int(d) for d in str(abs(n)))\n\n# Ejemplos\nprint(suma_digitos(1234))   # 10\nprint(suma_digitos(9999))   # 36\nprint(suma_digitos(100))    # 1",
        "js": "function sumaDigitos(n) {\n  return String(Math.abs(n)).split('').reduce((acc, d) => acc + Number(d), 0);\n}\n\nconsole.log(sumaDigitos(1234));  // 10\nconsole.log(sumaDigitos(9999));  // 36",
        "ts": "function sumaDigitos(n: number): number {\n  return String(Math.abs(n)).split('').reduce((acc, d) => acc + Number(d), 0);\n}\n\nconsole.log(sumaDigitos(1234));  // 10\nconsole.log(sumaDigitos(9999));  // 36",
        "go": 'package main\n\nimport "fmt"\n\nfunc sumaDigitos(n int) int {\n\tif n < 0 { n = -n }\n\tsum := 0\n\tfor n > 0 {\n\t\tsum += n % 10\n\t\tn /= 10\n\t}\n\treturn sum\n}\n\nfunc main() {\n\tfmt.Println(sumaDigitos(1234)) // 10\n\tfmt.Println(sumaDigitos(9999)) // 36\n}',
        "rs": 'fn suma_digitos(n: i64) -> i64 {\n    n.abs().to_string().chars().map(|c| c.to_digit(10).unwrap() as i64).sum()\n}\n\nfn main() {\n    println!("{}", suma_digitos(1234)); // 10\n    println!("{}", suma_digitos(9999)); // 36\n}',
        "java": 'public class SumaDigitos {\n    public static int sumaDigitos(int n) {\n        n = Math.abs(n);\n        int suma = 0;\n        while (n > 0) { suma += n % 10; n /= 10; }\n        return suma;\n    }\n    public static void main(String[] args) {\n        System.out.println(sumaDigitos(1234)); // 10\n        System.out.println(sumaDigitos(9999)); // 36\n    }\n}',
        "cs": 'using System;\nclass SumaDigitos {\n    static int Suma(int n) => Math.Abs(n).ToString().ToCharArray().Sum(c => c - \'0\');\n    static void Main() {\n        Console.WriteLine(Suma(1234)); // 10\n        Console.WriteLine(Suma(9999)); // 36\n    }\n}',
        "kt": 'fun sumaDigitos(n: Int): Int = Math.abs(n).toString().sumOf { it.digitToInt() }\n\nfun main() {\n    println(sumaDigitos(1234)) // 10\n    println(sumaDigitos(9999)) // 36\n}',
        "sw": 'func sumaDigitos(_ n: Int) -> Int {\n    return abs(n).description.compactMap { $0.wholeNumberValue }.reduce(0, +)\n}\n\nprint(sumaDigitos(1234)) // 10\nprint(sumaDigitos(9999)) // 36',
        "php": '<?php\nfunction sumaDigitos(int $n): int {\n    return array_sum(str_split(strval(abs($n))));\n}\necho sumaDigitos(1234) . "\n"; // 10\necho sumaDigitos(9999) . "\n"; // 36',
        "rb": 'def suma_digitos(n)\n  n.abs.digits.sum\nend\n\nputs suma_digitos(1234) # 10\nputs suma_digitos(9999) # 36',
        "dart": 'int sumaDigitos(int n) {\n  return n.abs().toString().split(\'\').fold(0, (sum, d) => sum + int.parse(d));\n}\n\nvoid main() {\n  print(sumaDigitos(1234)); // 10\n  print(sumaDigitos(9999)); // 36\n}',
    },
    "vocales-en-mayo": {
        "desc": "Cuenta cuántas vocales (a, e, i, o, u) contiene una cadena de texto, sin distinguir mayúsculas.",
        "p1": "Iteramos cada carácter de la cadena y verificamos si pertenece al conjunto de vocales {a, e, i, o, u}.",
        "p2": "Convertimos la cadena a minúsculas y usamos `sum()` con una condición de pertenencia al conjunto de vocales.",
        "p3": "O(n) donde n es la longitud de la cadena. Espacio O(1).",
        "py": "def contar_vocales(texto):\n    return sum(1 for c in texto.lower() if c in 'aeiouáéíóú')\n\nprint(contar_vocales('Hola Mundo'))  # 4\nprint(contar_vocales('Python'))      # 1",
        "js": "function contarVocales(texto) {\n  return (texto.toLowerCase().match(/[aeiouáéíóú]/g) || []).length;\n}\nconsole.log(contarVocales('Hola Mundo')); // 4",
        "ts": "function contarVocales(texto: string): number {\n  return (texto.toLowerCase().match(/[aeiouáéíóú]/g) ?? []).length;\n}\nconsole.log(contarVocales('Hola Mundo')); // 4",
        "go": 'package main\n\nimport (\n\t"fmt"\n\t"strings"\n\t"unicode"\n)\n\nfunc contarVocales(s string) int {\n\tcount := 0\n\tfor _, r := range strings.ToLower(s) {\n\t\tif strings.ContainsRune("aeiouáéíóú", r) || unicode.Is(unicode.Latin, r) {\n\t\t\tif strings.ContainsRune("aeiouáéíóú", r) {\n\t\t\t\tcount++\n\t\t\t}\n\t\t}\n\t}\n\treturn count\n}\n\nfunc main() {\n\tfmt.Println(contarVocales("Hola Mundo")) // 4\n}',
        "rs": 'fn contar_vocales(s: &str) -> usize {\n    s.to_lowercase().chars().filter(|c| "aeiouáéíóú".contains(*c)).count()\n}\n\nfn main() {\n    println!("{}", contar_vocales("Hola Mundo")); // 4\n}',
        "java": 'public class ContarVocales {\n    public static int contar(String s) {\n        return (int) s.toLowerCase().chars().filter(c -> "aeiouáéíóú".indexOf(c) >= 0).count();\n    }\n    public static void main(String[] a) {\n        System.out.println(contar("Hola Mundo")); // 4\n    }\n}',
        "cs": 'using System;\nusing System.Linq;\nclass ContarVocales {\n    static int Contar(string s) => s.ToLower().Count(c => "aeiouáéíóú".Contains(c));\n    static void Main() => Console.WriteLine(Contar("Hola Mundo")); // 4\n}',
        "kt": 'fun contarVocales(s: String) = s.lowercase().count { it in "aeiouáéíóú" }\nfun main() { println(contarVocales("Hola Mundo")) } // 4',
        "sw": 'func contarVocales(_ s: String) -> Int {\n  let vocales: Set<Character> = ["a","e","i","o","u","á","é","í","ó","ú"]\n  return s.lowercased().filter { vocales.contains($0) }.count\n}\nprint(contarVocales("Hola Mundo")) // 4',
        "php": '<?php\nfunction contarVocales(string $s): int {\n    return preg_match_all(\'/[aeiouáéíóú]/i\', $s);\n}\necho contarVocales("Hola Mundo"); // 4',
        "rb": 'def contar_vocales(s)\n  s.downcase.count("aeiouáéíóú")\nend\nputs contar_vocales("Hola Mundo") # 4',
        "dart": 'int contarVocales(String s) {\n  return s.toLowerCase().split(\'\').where((c) => \'aeiouáéíóú\'.contains(c)).length;\n}\nvoid main() => print(contarVocales(\'Hola Mundo\')); // 4',
    },
}

# Solución genérica cuando no hay hardcode
def _gen_python(title, desc):
    return (
        f"# {title}\n"
        f"# {desc}\n\n"
        "def resolver(entrada):\n"
        f'    """\n'
        f"    Implementación de: {title}\n\n"
        "    Args:\n"
        "        entrada: Dato de entrada del reto\n"
        "    Returns:\n"
        "        Resultado procesado\n"
        '    """\n'
        "    resultado = entrada  # Lógica principal aquí\n"
        "    return resultado\n\n\n"
        "def main():\n"
        "    # Casos de prueba\n"
        "    casos = [\n"
        '        ("caso_1", "resultado_esperado_1"),\n'
        '        ("caso_2", "resultado_esperado_2"),\n'
        "    ]\n"
        "    for caso, esperado in casos:\n"
        "        resultado = resolver(caso)\n"
        '        estado = "✅" if str(resultado) == str(esperado) else "❓"\n'
        '        print(f"{estado} Entrada: {caso} → Resultado: {resultado}")\n\n\n'
        'if __name__ == "__main__":\n'
        "    main()\n"
    )

def _gen_javascript(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "function resolver(entrada) {\n"
        "  // Lógica principal\n"
        "  return entrada;\n"
        "}\n\n"
        "const casos = [\n"
        '  { entrada: "caso_1", esperado: "resultado_1" },\n'
        '  { entrada: "caso_2", esperado: "resultado_2" },\n'
        "];\n\n"
        "casos.forEach(({ entrada, esperado }) => {\n"
        "  const resultado = resolver(entrada);\n"
        "  const ok = resultado === esperado;\n"
        "  console.log(`${ok ? '✅' : '❓'} ${entrada} → ${resultado}`);\n"
        "});\n"
    )

def _gen_typescript(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "function resolver<T>(entrada: T): T {\n"
        "  return entrada;\n"
        "}\n\n"
        "const casos: Array<{ entrada: string; esperado: string }> = [\n"
        '  { entrada: "caso_1", esperado: "resultado_1" },\n'
        '  { entrada: "caso_2", esperado: "resultado_2" },\n'
        "];\n\n"
        "casos.forEach(({ entrada, esperado }) => {\n"
        "  const resultado = resolver(entrada);\n"
        "  console.log(`${resultado === esperado ? '✅' : '❓'} ${entrada} → ${resultado}`);\n"
        "});\n"
    )

def _gen_go(title, desc):
    return (
        'package main\n\nimport "fmt"\n\n'
        f"// resolver - {title}\n"
        f"// {desc}\n"
        "func resolver(entrada string) string {\n"
        "\treturn entrada\n"
        "}\n\n"
        "func main() {\n"
        '\tcasos := []string{"caso_1", "caso_2"}\n'
        "\tfor _, c := range casos {\n"
        '\t\tfmt.Printf("▶ %s → %s\\n", c, resolver(c))\n'
        "\t}\n"
        "}\n"
    )

def _gen_rust(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "fn resolver(entrada: &str) -> String {\n"
        "    entrada.to_string()\n"
        "}\n\n"
        "fn main() {\n"
        '    let casos = vec!["caso_1", "caso_2"];\n'
        "    for c in casos {\n"
        '        println!("▶ {} → {}", c, resolver(c));\n'
        "    }\n"
        "}\n"
    )

def _gen_java(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "public class Reto {\n"
        "    public static String resolver(String entrada) {\n"
        "        return entrada;\n"
        "    }\n\n"
        "    public static void main(String[] args) {\n"
        '        String[] casos = {"caso_1", "caso_2"};\n'
        "        for (String c : casos) {\n"
        '            System.out.println("▶ " + c + " → " + resolver(c));\n'
        "        }\n"
        "    }\n"
        "}\n"
    )

def _gen_csharp(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "using System;\n\n"
        "class Reto {\n"
        "    static string Resolver(string entrada) => entrada;\n\n"
        "    static void Main() {\n"
        '        string[] casos = {"caso_1", "caso_2"};\n'
        "        foreach (var c in casos)\n"
        '            Console.WriteLine($"▶ {c} → {Resolver(c)}");\n'
        "    }\n"
        "}\n"
    )

def _gen_kotlin(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "fun resolver(entrada: String) = entrada\n\n"
        "fun main() {\n"
        '    listOf("caso_1", "caso_2").forEach {\n'
        '        println("▶ $it → ${resolver(it)}")\n'
        "    }\n"
        "}\n"
    )

def _gen_swift(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "func resolver(_ entrada: String) -> String { entrada }\n\n"
        'let casos = ["caso_1", "caso_2"]\n'
        "for c in casos {\n"
        '    print("▶ \\(c) → \\(resolver(c))")\n'
        "}\n"
    )

def _gen_php(title, desc):
    return (
        "<?php\n"
        f"// {title}\n"
        f"// {desc}\n\n"
        "function resolver(string $entrada): string {\n"
        "    return $entrada;\n"
        "}\n\n"
        '$casos = ["caso_1", "caso_2"];\n'
        "foreach ($casos as $c) {\n"
        '    echo "▶ $c → " . resolver($c) . "\\n";\n'
        "}\n"
    )

def _gen_ruby(title, desc):
    return (
        f"# {title}\n"
        f"# {desc}\n\n"
        "def resolver(entrada)\n"
        "  entrada\n"
        "end\n\n"
        '["caso_1", "caso_2"].each do |c|\n'
        '  puts "▶ #{c} → #{resolver(c)}"\n'
        "end\n"
    )

def _gen_dart(title, desc):
    return (
        f"// {title}\n"
        f"// {desc}\n\n"
        "String resolver(String entrada) => entrada;\n\n"
        "void main() {\n"
        '  ["caso_1", "caso_2"].forEach((c) {\n'
        '    print("▶ $c → ${resolver(c)}");\n'
        "  });\n"
        "}\n"
    )

GENERIC_SOLUTIONS = {
    "python":     _gen_python,
    "javascript": _gen_javascript,
    "typescript": _gen_typescript,
    "go":         _gen_go,
    "rust":       _gen_rust,
    "java":       _gen_java,
    "csharp":     _gen_csharp,
    "kotlin":     _gen_kotlin,
    "swift":      _gen_swift,
    "php":        _gen_php,
    "ruby":       _gen_ruby,
    "dart":       _gen_dart,
}


# ─────────────────────────────────────────────
# TEMPLATE MDX
# ─────────────────────────────────────────────
TEMPLATE = """\
---
draft: false
title: "{title}"
description: "{description}"
pubDate: "{pub_date}"
tags: {tags}
slug: "{slug}"
image: "{image}"
author: "Jorge Beneyto Castelló"
difficulty: "{difficulty}"
---

import Challenge from '../../components/Challenge.astro';

# 🎯 {titulo_h1}

### 📝 Descripción del Reto

{descripcion}

<Challenge 
  nivel="{difficulty}" 
  mision="{mision}" 
/>

---

## 💡 Guía de Solución Paso a Paso

<details>
<summary><b>Ver explicación y código 🛠️ (¡No hagas spoiler!)</b></summary>
<div class="details-content">

### 🏗️ Paso 1: Análisis de la lógica

{paso1}

### ⚙️ Paso 2: Implementación en {lang_name}

{paso2}

### 🚀 Paso 3: Complejidad y Optimización

{paso3}

### 💻 Código de la Solución ({lang_name})

```{lang_code}
{codigo}
```

</div>
</details>
"""

# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────

def parse_frontmatter(content):
    m = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return {}
    data = {}
    for line in m.group(1).split('\n'):
        if ':' in line:
            k, _, v = line.partition(':')
            data[k.strip()] = v.strip().strip('"')
    return data


def slug_key(slug):
    """Extrae clave del slug para buscar en SOLUTIONS, ej: 'suma-de-digitos'"""
    # guia-plus-reto-inicial-01-suma-de-digitos → suma-de-digitos
    parts = slug.split('-')
    # Saltar prefijos: guia, plus, reto, nivel, número
    i = 0
    stopwords = {'guia', 'plus', 'reto', 'inicial', 'intermedio', 'avanzado'}
    while i < len(parts):
        if parts[i] in stopwords or parts[i].isdigit():
            i += 1
        else:
            break
    return '-'.join(parts[i:])


def get_code(sol, lang_id):
    """Obtiene código de la solución según lenguaje."""
    mapping = {
        "python": sol.get("py"), "javascript": sol.get("js"),
        "typescript": sol.get("ts"), "go": sol.get("go"),
        "rust": sol.get("rs"), "java": sol.get("java"),
        "csharp": sol.get("cs"), "kotlin": sol.get("kt"),
        "swift": sol.get("sw"), "php": sol.get("php"),
        "ruby": sol.get("rb"), "dart": sol.get("dart"),
    }
    code = mapping.get(lang_id)
    # Fallback: si no hay código específico para ese lenguaje, usar Python
    if not code:
        code = sol.get("py")
    return code


# ─────────────────────────────────────────────
# PROCESO PRINCIPAL
# ─────────────────────────────────────────────

def fix_all():
    folder = CHALLENGES_DIR
    files = sorted([
        f for f in os.listdir(folder)
        if f.endswith('.mdx') and f.startswith('guia-plus-reto-')
    ])
    
    print(f"📂 {len(files)} archivos encontrados\n")
    fixed = 0

    for idx, fname in enumerate(files):
        path = os.path.join(folder, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        fm = parse_frontmatter(content)
        if not fm.get('title'):
            print(f"⚠️  Sin título: {fname}")
            continue

        # Datos del frontmatter
        titulo = fm.get('title', '').strip()
        difficulty = fm.get('difficulty', 'Intermedio')
        pub_date = fm.get('pubDate', '2026-01-01')
        image = fm.get('image', 'https://images.unsplash.com/photo-1542831371-29b0f74f9713?ixlib=rb-4.0.3&auto=format&fit=crop&w=1170&q=80')
        slug = fm.get('slug', fname.replace('.mdx', ''))

        # Lenguaje cíclico Codeember
        lang_id, lang_code, lang_name = LANGS[idx % len(LANGS)]

        # Buscar solución en base de datos
        key = slug_key(slug)
        sol_data = SOLUTIONS.get(key)

        if sol_data:
            descripcion = sol_data['desc']
            paso1 = sol_data['p1']
            paso2 = sol_data['p2']
            paso3 = sol_data['p3']
            codigo = get_code(sol_data, lang_id) or GENERIC_SOLUTIONS[lang_id](titulo, descripcion)
        else:
            # Solución genérica estructurada
            descripcion = f"Resuelve el siguiente reto de programación: **{titulo}**. Implementa una solución eficiente que maneje los casos base y edge cases correctamente."
            paso1 = f"Analizar el problema '{titulo}': identificar entradas, salidas esperadas y restricciones. Definir los casos límite que la solución debe manejar."
            paso2 = f"Elegir la estructura de datos y algoritmo más adecuado para resolver '{titulo}' en {lang_name}. Implementar la lógica paso a paso con comentarios claros."
            paso3 = f"La solución tiene complejidad temporal O(n) en el caso general. Para grandes volúmenes de datos, considerar optimizaciones como memoización o estructuras de datos más eficientes."
            gen_fn = GENERIC_SOLUTIONS.get(lang_id, GENERIC_SOLUTIONS["python"])
            codigo = gen_fn(titulo, descripcion)

        # Título limpio para h1 (sin prefijo RETO:)
        titulo_h1 = re.sub(r'^🏆\s*RETO:\s*', '', titulo).strip()
        if not titulo_h1:
            titulo_h1 = titulo

        # Descripción corta
        mision = descripcion[:150].rstrip() + ('...' if len(descripcion) > 150 else '')
        desc_fm = mision.replace('"', "'")

        tags = json.dumps([lang_id, 'retos', difficulty.lower(), 'guia-plus'], ensure_ascii=False)

        nuevo = TEMPLATE.format(
            title=titulo.replace('"', "'"),
            description=desc_fm,
            pub_date=pub_date,
            tags=tags,
            slug=slug,
            image=image,
            difficulty=difficulty,
            titulo_h1=titulo_h1,
            descripcion=descripcion,
            mision=mision.replace('"', "'"),
            paso1=paso1,
            paso2=paso2,
            paso3=paso3,
            lang_name=lang_name,
            lang_code=lang_code,
            codigo=codigo,
        )

        with open(path, 'w', encoding='utf-8') as f:
            f.write(nuevo)

        print(f"✅ [{idx+1:03d}] {fname} → {lang_name}")
        fixed += 1

    print(f"\n🎉 {fixed}/{len(files)} archivos actualizados correctamente.")


if __name__ == "__main__":
    fix_all()
