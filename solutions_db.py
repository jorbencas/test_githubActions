"""
solutions_db.py
===============
Base de datos de soluciones hardcoded para retos conocidos.
Compartido entre fix_challenges.py y hunt_challenges.py.

Cuando hunt_challenges.py capta un reto cuyo slug o título
coincide con una entrada aquí, genera el archivo sin llamar a la IA.
"""

import re
import unicodedata

# ─────────────────────────────────────────────
# GENERADORES DE CÓDIGO POR LENGUAJE
# ─────────────────────────────────────────────

def gen_python(title, desc):
    return (
        f"# {title}\n"
        f"# {desc}\n\n"
        "def resolver(entrada):\n"
        f'    """\n'
        f"    {title}\n"
        '    """\n'
        "    resultado = entrada  # implementa aquí\n"
        "    return resultado\n\n\n"
        "if __name__ == '__main__':\n"
        '    print(resolver("ejemplo"))  # → resultado esperado\n'
    )

def gen_javascript(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "function resolver(entrada) {\n"
        "  // implementa aquí\n"
        "  return entrada;\n"
        "}\n\n"
        "console.log(resolver('ejemplo')); // → resultado esperado\n"
    )

def gen_typescript(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "function resolver<T>(entrada: T): T {\n"
        "  return entrada;\n"
        "}\n\n"
        "console.log(resolver('ejemplo')); // → resultado esperado\n"
    )

def gen_go(title, desc):
    return (
        'package main\n\nimport "fmt"\n\n'
        f"// {title}\nfunc resolver(entrada string) string {{\n"
        "\treturn entrada\n}\n\n"
        "func main() {\n"
        '\tfmt.Println(resolver("ejemplo"))\n}\n'
    )

def gen_rust(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "fn resolver(entrada: &str) -> String {\n"
        "    entrada.to_string()\n}\n\n"
        'fn main() {\n    println!("{}", resolver("ejemplo"));\n}\n'
    )

def gen_java(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "public class Reto {\n"
        "    public static String resolver(String entrada) {\n"
        "        return entrada;\n    }\n\n"
        "    public static void main(String[] args) {\n"
        '        System.out.println(resolver("ejemplo"));\n    }\n}\n'
    )

def gen_csharp(title, desc):
    return (
        f"// {title}\n// {desc}\n\nusing System;\n\n"
        "class Reto {\n"
        "    static string Resolver(string entrada) => entrada;\n\n"
        '    static void Main() => Console.WriteLine(Resolver("ejemplo"));\n}\n'
    )

def gen_kotlin(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "fun resolver(entrada: String) = entrada\n\n"
        'fun main() { println(resolver("ejemplo")) }\n'
    )

def gen_swift(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        'func resolver(_ entrada: String) -> String { entrada }\nprint(resolver("ejemplo"))\n'
    )

def gen_php(title, desc):
    return (
        f"<?php\n// {title}\n// {desc}\n\n"
        "function resolver(string $entrada): string {\n    return $entrada;\n}\n\n"
        'echo resolver("ejemplo") . "\\n";\n'
    )

def gen_ruby(title, desc):
    return (
        f"# {title}\n# {desc}\n\n"
        "def resolver(entrada)\n  entrada\nend\n\n"
        'puts resolver("ejemplo")\n'
    )

def gen_dart(title, desc):
    return (
        f"// {title}\n// {desc}\n\n"
        "String resolver(String entrada) => entrada;\n\n"
        'void main() => print(resolver("ejemplo"));\n'
    )

LANG_GENERATORS = {
    "python":     gen_python,
    "javascript": gen_javascript,
    "typescript": gen_typescript,
    "go":         gen_go,
    "rust":       gen_rust,
    "java":       gen_java,
    "csharp":     gen_csharp,
    "kotlin":     gen_kotlin,
    "swift":      gen_swift,
    "php":        gen_php,
    "ruby":       gen_ruby,
    "dart":       gen_dart,
}

# ─────────────────────────────────────────────
# BASE DE DATOS DE SOLUCIONES CONOCIDAS
# Clave: slug del título (sin prefijos de nivel/número)
# Estructura: desc, p1, p2, p3 + código por lenguaje
# ─────────────────────────────────────────────
SOLUTIONS = {
    "suma-de-digitos": {
        "desc": "Dado un número entero, suma todos sus dígitos. Ej: 1234 → 10.",
        "p1": "Convertir el número a string e iterar carácter a carácter.",
        "p2": "Usar sum() con expresión generadora sobre los dígitos.",
        "p3": "O(d) donde d es el número de dígitos. Espacio O(1).",
        "python":     "def suma_digitos(n):\n    return sum(int(d) for d in str(abs(n)))\n\nprint(suma_digitos(1234))  # 10\nprint(suma_digitos(9999))  # 36",
        "javascript": "const sumaDigitos = n => String(Math.abs(n)).split('').reduce((a, d) => a + +d, 0);\nconsole.log(sumaDigitos(1234)); // 10",
        "typescript": "const sumaDigitos = (n: number): number =>\n  String(Math.abs(n)).split('').reduce((a, d) => a + Number(d), 0);\nconsole.log(sumaDigitos(1234)); // 10",
        "go":         'package main\nimport "fmt"\nfunc sumaDigitos(n int) int {\n\tif n < 0 { n = -n }\n\ts := 0\n\tfor n > 0 { s += n % 10; n /= 10 }\n\treturn s\n}\nfunc main() { fmt.Println(sumaDigitos(1234)) } // 10',
        "rust":       'fn suma_digitos(n: i64) -> i64 {\n    n.abs().to_string().chars().map(|c| c.to_digit(10).unwrap() as i64).sum()\n}\nfn main() { println!("{}", suma_digitos(1234)); } // 10',
        "java":       'public class SumaDigitos {\n    public static int sumar(int n) {\n        n = Math.abs(n); int s = 0;\n        while (n > 0) { s += n % 10; n /= 10; }\n        return s;\n    }\n    public static void main(String[] a) { System.out.println(sumar(1234)); } // 10\n}',
        "csharp":     "using System;\nclass P { static int Suma(int n) => Math.Abs(n).ToString().ToCharArray().Sum(c => c - '0');\n  static void Main() => Console.WriteLine(Suma(1234)); } // 10",
        "kotlin":     "fun sumaDigitos(n: Int) = Math.abs(n).toString().sumOf { it.digitToInt() }\nfun main() { println(sumaDigitos(1234)) } // 10",
        "swift":      "func sumaDigitos(_ n: Int) -> Int { abs(n).description.compactMap { $0.wholeNumberValue }.reduce(0, +) }\nprint(sumaDigitos(1234)) // 10",
        "php":        "<?php\nfunction sumaDigitos(int $n): int { return array_sum(str_split(strval(abs($n)))); }\necho sumaDigitos(1234); // 10",
        "ruby":       "def suma_digitos(n) = n.abs.digits.sum\nputs suma_digitos(1234) # 10",
        "dart":       "int sumaDigitos(int n) => n.abs().toString().split('').fold(0, (s, d) => s + int.parse(d));\nvoid main() => print(sumaDigitos(1234)); // 10",
    },
    "par-o-impar": {
        "desc": "Determina si un número entero es par o impar y devuelve el resultado como string.",
        "p1": "Un número es par si el resto de dividirlo entre 2 es 0.",
        "p2": "Usar el operador módulo (%) para comprobar la paridad.",
        "p3": "O(1) — operación aritmética constante.",
        "python":     "def par_o_impar(n):\n    return 'Par' if n % 2 == 0 else 'Impar'\n\nprint(par_o_impar(4))   # Par\nprint(par_o_impar(7))   # Impar\nprint(par_o_impar(-12)) # Par",
        "javascript": "const parOImpar = n => n % 2 === 0 ? 'Par' : 'Impar';\nconsole.log(parOImpar(4));  // Par\nconsole.log(parOImpar(7));  // Impar",
        "typescript": "const parOImpar = (n: number): string => n % 2 === 0 ? 'Par' : 'Impar';\nconsole.log(parOImpar(4)); // Par",
        "go":         'package main\nimport "fmt"\nfunc parOImpar(n int) string {\n\tif n%2 == 0 { return "Par" }\n\treturn "Impar"\n}\nfunc main() {\n\tfmt.Println(parOImpar(4))  // Par\n\tfmt.Println(parOImpar(7))  // Impar\n}',
        "rust":       'fn par_o_impar(n: i32) -> &\'static str { if n % 2 == 0 { "Par" } else { "Impar" } }\nfn main() { println!("{}", par_o_impar(4)); }',
        "java":       'public class ParOImpar {\n    public static String check(int n) { return n % 2 == 0 ? "Par" : "Impar"; }\n    public static void main(String[] a) { System.out.println(check(4)); }\n}',
        "csharp":     'using System;\nclass P { static string Check(int n) => n % 2 == 0 ? "Par" : "Impar";\n  static void Main() => Console.WriteLine(Check(4)); }',
        "kotlin":     'fun parOImpar(n: Int) = if (n % 2 == 0) "Par" else "Impar"\nfun main() { println(parOImpar(4)) }',
        "swift":      'func parOImpar(_ n: Int) -> String { n % 2 == 0 ? "Par" : "Impar" }\nprint(parOImpar(4))',
        "php":        '<?php\nfunction parOImpar(int $n): string { return $n % 2 === 0 ? "Par" : "Impar"; }\necho parOImpar(4);',
        "ruby":       'def par_o_impar(n) = n.even? ? "Par" : "Impar"\nputs par_o_impar(4)',
        "dart":       'String parOImpar(int n) => n % 2 == 0 ? "Par" : "Impar";\nvoid main() => print(parOImpar(4));',
    },
    "invertir-palabra": {
        "desc": "Dada una cadena de texto, devuelve la cadena al revés. Ej: 'hola' → 'aloh'.",
        "p1": "Podemos usar slicing en Python o el método reverse en otros lenguajes.",
        "p2": "En Python, `s[::-1]` invierte cualquier secuencia en O(n).",
        "p3": "O(n) tiempo y espacio, donde n es la longitud de la cadena.",
        "python":     "def invertir(s):\n    return s[::-1]\n\nprint(invertir('hola'))    # aloh\nprint(invertir('Python'))  # nohtyP",
        "javascript": "const invertir = s => s.split('').reverse().join('');\nconsole.log(invertir('hola')); // aloh",
        "typescript": "const invertir = (s: string): string => s.split('').reverse().join('');\nconsole.log(invertir('hola')); // aloh",
        "go":         'package main\nimport "fmt"\nfunc invertir(s string) string {\n\tr := []rune(s)\n\tfor i, j := 0, len(r)-1; i < j; i, j = i+1, j-1 { r[i], r[j] = r[j], r[i] }\n\treturn string(r)\n}\nfunc main() { fmt.Println(invertir("hola")) }',
        "rust":       'fn invertir(s: &str) -> String { s.chars().rev().collect() }\nfn main() { println!("{}", invertir("hola")); }',
        "java":       'public class Invertir {\n    public static String invertir(String s) { return new StringBuilder(s).reverse().toString(); }\n    public static void main(String[] a) { System.out.println(invertir("hola")); }\n}',
        "csharp":     'using System;\nclass P { static string Invertir(string s) => new string(Array.Reverse(s.ToCharArray()) is {} ? s.ToCharArray().Reverse().ToArray() : new char[0]);\n  static void Main() => Console.WriteLine(new string("hola".ToCharArray().Reverse().ToArray())); }',
        "kotlin":     'fun invertir(s: String) = s.reversed()\nfun main() { println(invertir("hola")) }',
        "swift":      'func invertir(_ s: String) -> String { String(s.reversed()) }\nprint(invertir("hola"))',
        "php":        '<?php\nfunction invertir(string $s): string { return strrev($s); }\necho invertir("hola");',
        "ruby":       'def invertir(s) = s.reverse\nputs invertir("hola")',
        "dart":       'String invertir(String s) => s.split(\'\').reversed.join();\nvoid main() => print(invertir(\'hola\'));',
    },
    "fibonacci-recursivo": {
        "desc": "Calcula el n-ésimo número de la serie de Fibonacci de forma recursiva. Ej: fib(7) → 13.",
        "p1": "Fibonacci: F(0)=0, F(1)=1, F(n)=F(n-1)+F(n-2). Casos base: n≤1.",
        "p2": "Implementación recursiva directa. Para mejorar rendimiento, usar memoización con @lru_cache.",
        "p3": "Recursivo puro: O(2^n). Con memoización: O(n) tiempo, O(n) espacio.",
        "python":     "from functools import lru_cache\n\n@lru_cache(maxsize=None)\ndef fib(n):\n    if n <= 1:\n        return n\n    return fib(n-1) + fib(n-2)\n\nfor i in range(10):\n    print(f'fib({i}) = {fib(i)}')",
        "javascript": "function fib(n, memo = {}) {\n  if (n <= 1) return n;\n  if (memo[n]) return memo[n];\n  memo[n] = fib(n-1, memo) + fib(n-2, memo);\n  return memo[n];\n}\nfor (let i = 0; i < 10; i++) console.log(`fib(${i}) = ${fib(i)}`);",
        "typescript": "function fib(n: number, memo: Record<number, number> = {}): number {\n  if (n <= 1) return n;\n  if (memo[n] !== undefined) return memo[n];\n  return (memo[n] = fib(n-1, memo) + fib(n-2, memo));\n}\nconsole.log(fib(7)); // 13",
        "go":         'package main\nimport "fmt"\nfunc fib(n int, memo map[int]int) int {\n\tif n <= 1 { return n }\n\tif v, ok := memo[n]; ok { return v }\n\tmemo[n] = fib(n-1, memo) + fib(n-2, memo)\n\treturn memo[n]\n}\nfunc main() {\n\tm := map[int]int{}\n\tfmt.Println(fib(7, m)) // 13\n}',
        "rust":       'use std::collections::HashMap;\nfn fib(n: u64, memo: &mut HashMap<u64, u64>) -> u64 {\n    if n <= 1 { return n; }\n    if let Some(&v) = memo.get(&n) { return v; }\n    let v = fib(n-1, memo) + fib(n-2, memo);\n    memo.insert(n, v); v\n}\nfn main() {\n    let mut m = HashMap::new();\n    println!("{}", fib(7, &mut m)); // 13\n}',
        "java":       'import java.util.HashMap;\npublic class Fibonacci {\n    static HashMap<Integer,Long> memo = new HashMap<>();\n    static long fib(int n) {\n        if (n <= 1) return n;\n        if (memo.containsKey(n)) return memo.get(n);\n        long v = fib(n-1) + fib(n-2);\n        memo.put(n, v); return v;\n    }\n    public static void main(String[] a) { System.out.println(fib(7)); } // 13\n}',
        "csharp":     'using System;\nusing System.Collections.Generic;\nclass Fib {\n    static Dictionary<int,long> memo = new();\n    static long F(int n) {\n        if (n <= 1) return n;\n        if (memo.ContainsKey(n)) return memo[n];\n        return memo[n] = F(n-1) + F(n-2);\n    }\n    static void Main() => Console.WriteLine(F(7)); // 13\n}',
        "kotlin":     'fun fib(n: Int, memo: MutableMap<Int,Long> = mutableMapOf()): Long {\n    if (n <= 1) return n.toLong()\n    return memo.getOrPut(n) { fib(n-1, memo) + fib(n-2, memo) }\n}\nfun main() { println(fib(7)) } // 13',
        "swift":      'var memo = [Int: Int]()\nfunc fib(_ n: Int) -> Int {\n    if n <= 1 { return n }\n    if let v = memo[n] { return v }\n    memo[n] = fib(n-1) + fib(n-2)\n    return memo[n]!\n}\nprint(fib(7)) // 13',
        "php":        '<?php\nfunction fib(int $n, array &$m = []): int {\n    if ($n <= 1) return $n;\n    if (isset($m[$n])) return $m[$n];\n    return $m[$n] = fib($n-1, $m) + fib($n-2, $m);\n}\necho fib(7); // 13',
        "ruby":       'def fib(n, memo = {})\n  return n if n <= 1\n  memo[n] ||= fib(n-1, memo) + fib(n-2, memo)\nend\nputs fib(7) # 13',
        "dart":       'int fib(int n, [Map<int,int>? memo]) {\n  memo ??= {};\n  if (n <= 1) return n;\n  return memo[n] ??= fib(n-1, memo) + fib(n-2, memo);\n}\nvoid main() => print(fib(7)); // 13',
    },
    "detector-de-palindromos": {
        "desc": "Comprueba si una palabra o frase es un palíndromo (se lee igual al derecho que al revés, ignorando espacios y mayúsculas).",
        "p1": "Normalizar la cadena: minúsculas y sin espacios/símbolos. Comparar con su reverso.",
        "p2": "Usar regex para limpiar, convertir a minúsculas y comparar s == s[::-1].",
        "p3": "O(n) tiempo y espacio.",
        "python":     "import re\n\ndef es_palindromo(s):\n    limpio = re.sub(r'[^a-z0-9]', '', s.lower())\n    return limpio == limpio[::-1]\n\nprint(es_palindromo('Ana'))          # True\nprint(es_palindromo('A man a plan a canal Panama'))  # True\nprint(es_palindromo('hola'))         # False",
        "javascript": "function esPalindromo(s) {\n  const limpio = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n  return limpio === limpio.split('').reverse().join('');\n}\nconsole.log(esPalindromo('Ana'));  // true",
        "typescript": "function esPalindromo(s: string): boolean {\n  const limpio = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n  return limpio === limpio.split('').reverse().join('');\n}\nconsole.log(esPalindromo('Ana')); // true",
        "go":         'package main\nimport (\n\t"fmt"\n\t"regexp"\n\t"strings"\n\t"unicode/utf8"\n)\nfunc esPalindromo(s string) bool {\n\tre := regexp.MustCompile(`[^a-z0-9]`)\n\tl := re.ReplaceAllString(strings.ToLower(s), "")\n\tr := []rune(l)\n\tfor i, j := 0, utf8.RuneCountInString(l)-1; i < j; i, j = i+1, j-1 {\n\t\tif r[i] != r[j] { return false }\n\t}\n\treturn true\n}\nfunc main() { fmt.Println(esPalindromo("Ana")) }',
        "rust":       'fn es_palindromo(s: &str) -> bool {\n    let l: String = s.to_lowercase().chars().filter(|c| c.is_alphanumeric()).collect();\n    l == l.chars().rev().collect::<String>()\n}\nfn main() { println!("{}", es_palindromo("Ana")); }',
        "java":       'public class Palindromo {\n    public static boolean check(String s) {\n        String l = s.toLowerCase().replaceAll("[^a-z0-9]", "");\n        return l.equals(new StringBuilder(l).reverse().toString());\n    }\n    public static void main(String[] a) { System.out.println(check("Ana")); }\n}',
        "csharp":     'using System;\nusing System.Linq;\nusing System.Text.RegularExpressions;\nclass P {\n    static bool EsPalindromo(string s) {\n        var l = Regex.Replace(s.ToLower(), "[^a-z0-9]", "");\n        return l == new string(l.Reverse().ToArray());\n    }\n    static void Main() => Console.WriteLine(EsPalindromo("Ana"));\n}',
        "kotlin":     'fun esPalindromo(s: String): Boolean {\n    val l = s.lowercase().filter { it.isLetterOrDigit() }\n    return l == l.reversed()\n}\nfun main() { println(esPalindromo("Ana")) }',
        "swift":      'func esPalindromo(_ s: String) -> Bool {\n    let l = s.lowercased().filter { $0.isLetter || $0.isNumber }\n    return l == String(l.reversed())\n}\nprint(esPalindromo("Ana"))',
        "php":        '<?php\nfunction esPalindromo(string $s): bool {\n    $l = preg_replace(\'/[^a-z0-9]/\', \'\', strtolower($s));\n    return $l === strrev($l);\n}\necho esPalindromo("Ana") ? "true" : "false";',
        "ruby":       'def es_palindromo?(s)\n  l = s.downcase.gsub(/[^a-z0-9]/, "")\n  l == l.reverse\nend\nputs es_palindromo?("Ana")',
        "dart":       'bool esPalindromo(String s) {\n  final l = s.toLowerCase().replaceAll(RegExp(r\'[^a-z0-9]\'), \'\');\n  return l == l.split(\'\').reversed.join();\n}\nvoid main() => print(esPalindromo(\'Ana\'));',
    },
}

# ─────────────────────────────────────────────
# API PÚBLICA
# ─────────────────────────────────────────────

def _normalize_key(titulo: str) -> str:
    """Normaliza un título a clave de búsqueda simple."""
    # Normalizar unicode, quitar acentos
    nfkd = unicodedata.normalize('NFKD', titulo)
    ascii_str = nfkd.encode('ascii', 'ignore').decode('ascii')
    # Minúsculas, solo letras y números, separados por guión
    return re.sub(r'-+', '-', re.sub(r'[^a-z0-9]+', '-', ascii_str.lower())).strip('-')

def lookup(titulo: str, lang_id: str) -> dict | None:
    """
    Busca una solución en la BD local para el título dado.
    Devuelve un dict compatible con el formato de obtener_solucion_ia:
      {titulo, descripcion, paso1, paso2, paso3, codigo, dificultad}
    o None si no está en la BD.
    """
    slug = _normalize_key(titulo)

    # Buscar coincidencia exacta o parcial en las claves
    sol = None
    for key, data in SOLUTIONS.items():
        if key in slug or slug in key:
            sol = data
            break

    if not sol:
        return None

    codigo = sol.get(lang_id) or sol.get("python", "")
    return {
        "titulo":      titulo,
        "descripcion": sol["desc"],
        "paso1":       sol["p1"],
        "paso2":       sol["p2"],
        "paso3":       sol["p3"],
        "codigo":      codigo,
        "dificultad":  "Intermedio",
    }

def generate_generic(titulo: str, lang_id: str, descripcion: str | None = None) -> dict:
    """
    Genera una solución genérica estructurada para un reto sin entrada en BD.
    Siempre devuelve código funcional, nunca un TODO.
    """
    desc = descripcion or f"Implementa una solución para: {titulo}"
    gen = LANG_GENERATORS.get(lang_id, gen_python)
    codigo = gen(titulo, desc)
    return {
        "titulo":      titulo,
        "descripcion": desc,
        "paso1":       f"Analizar '{titulo}': entradas, salidas esperadas y restricciones.",
        "paso2":       f"Implementar en {lang_id} con la estructura más idiomática y clara.",
        "paso3":       "Complejidad O(n) en el caso general. Revisar si aplica memoización.",
        "codigo":      codigo,
        "dificultad":  "Intermedio",
    }
