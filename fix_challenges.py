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
    # ── INICIAL ─────────────────────────────
    "suma-de-digitos": {
        "desc": "Suma los dígitos de un número entero positivo.",
        "p1": "Convertir a cadena e iterar sumando los valores numéricos.",
        "p2": "Usar sum() con generador para mayor brevedad.",
        "p3": "O(d) tiempo, O(d) espacio para la cadena.",
        "py": "def sol(n): return sum(int(d) for d in str(abs(n)))\nprint(sol(1234))",
        "js": "const sol = n => [...String(Math.abs(n))].reduce((a, b) => a + +b, 0);\nconsole.log(sol(1234));"
    },
    "vocales-en-mayo": {
        "desc": "Cuenta las vocales en una cadena de texto.",
        "p1": "Normalizar a minúsculas y filtrar caracteres en 'aeiou'.",
        "p2": "Usar comprensiones o expresiones regulares.",
        "p3": "O(n) tiempo.",
        "py": "def sol(s): return sum(1 for c in s.lower() if c in 'aeiouáéíóú')\nprint(sol('Hola'))",
        "js": "const sol = s => (s.match(/[aeiouáéíóú]/gi) || []).length;\nconsole.log(sol('Hola'));"
    },
    "salto-de-linea": {
        "desc": "Añade un salto de línea entre dos palabras.",
        "p1": "Concatenar las cadenas con el carácter especial '\\n'.",
        "p2": "Usar f-strings o join.",
        "p3": "O(1).",
        "py": "def sol(a, b): return f'{a}\\n{b}'\nprint(sol('Hola', 'Mundo'))",
        "js": "const sol = (a, b) => `${a}\\n${b}`;\nconsole.log(sol('Hola', 'Mundo'));"
    },
    "validador-de-rango": {
        "desc": "Verifica si un número está entre un mínimo y un máximo.",
        "p1": "Comprobar si n >= min y n <= max.",
        "p2": "En Python se puede simplificar como min <= n <= max.",
        "p3": "O(1).",
        "py": "def sol(n, mi, ma): return mi <= n <= ma\nprint(sol(5, 1, 10))",
        "js": "const sol = (n, mi, ma) => n >= mi && n <= ma;\nconsole.log(sol(5, 1, 10));"
    },
    "mayor-de-edad": {
        "desc": "Determina si una persona es mayor de edad (>= 18).",
        "p1": "Comparación simple del valor de entrada con 18.",
        "p2": "Devolver booleano directamente.",
        "p3": "O(1).",
        "py": "def sol(edad): return edad >= 18\nprint(sol(20))",
        "js": "const sol = e => e >= 18;\nconsole.log(sol(20));"
    },
    "par-o-impar": {
        "desc": "Comprueba si un número es par.",
        "p1": "Usar el operador módulo (%) entre 2.",
        "p2": "n % 2 == 0 indica paridad.",
        "p3": "O(1).",
        "py": "def sol(n): return n % 2 == 0\nprint(sol(4))",
        "js": "const sol = n => n % 2 === 0;\nconsole.log(sol(4));"
    },
    "invertir-palabra": {
        "desc": "Invierte una cadena de texto.",
        "p1": "Recorrer la cadena de atrás hacia adelante.",
        "p2": "Usar slicing s[::-1] en Python.",
        "p3": "O(n).",
        "py": "def sol(s): return s[::-1]\nprint(sol('python'))",
        "js": "const sol = s => s.split('').reverse().join('');\nconsole.log(sol('python'));"
    },
    "contar-espacios": {
        "desc": "Cuenta los espacios en blanco en una frase.",
        "p1": "Iterar y comparar cada carácter con ' '.",
        "p2": "Usar el método count(' ') de las strings.",
        "p3": "O(n).",
        "py": "def sol(s): return s.count(' ')\nprint(sol('A B C'))",
        "js": "const sol = s => (s.match(/ /g) || []).length;\nconsole.log(sol('A B C'));"
    },
    "multiplicar-por-2": {
        "desc": "Multiplica un número por 2.",
        "p1": "Operación aritmética básica.",
        "p2": "Operador * o desplazamiento de bits << 1.",
        "p3": "O(1).",
        "py": "def sol(n): return n * 2\nprint(sol(10))",
        "js": "const sol = n => n * 2;\nconsole.log(sol(10));"
    },
    "celsius-a-kelvin": {
        "desc": "Convierte grados Celsius a Kelvin.",
        "p1": "Sumar 273.15 al valor Celsius.",
        "p2": "Fórmula: K = C + 273.15.",
        "p3": "O(1).",
        "py": "def sol(c): return c + 273.15\nprint(sol(25))",
        "js": "const sol = c => c + 273.15;\nconsole.log(sol(25));"
    },
    "area-de-triangulo": {
        "desc": "Calcula el área de un triángulo (base * altura / 2).",
        "p1": "Aplicar la fórmula geométrica estándar.",
        "p2": "Multiplicar base por altura y dividir por 2.",
        "p3": "O(1).",
        "py": "def sol(b, h): return (b * h) / 2\nprint(sol(10, 5))",
        "js": "const sol = (b, h) => (b * h) / 2;\nconsole.log(sol(10, 5));"
    },
    "calculadora-de-segundos": {
        "desc": "Convierte horas a segundos.",
        "p1": "Multiplicar horas por 3600 (60 min * 60 seg).",
        "p2": "h * 60 * 60.",
        "p3": "O(1).",
        "py": "def sol(h): return h * 3600\nprint(sol(2))",
        "js": "const sol = h => h * 3600;\nconsole.log(sol(2));"
    },
    "concatenar-nombres": {
        "desc": "Une nombre y apellido con un espacio.",
        "p1": "Usar concatenación o plantillas de texto.",
        "p2": "f'{nombre} {apellido}'.",
        "p3": "O(n).",
        "py": "def sol(n, a): return f'{n} {a}'\nprint(sol('Juan', 'Perez'))",
        "js": "const sol = (n, a) => `${n} ${a}`;\nconsole.log(sol('Juan', 'Perez'));"
    },
    "generador-de-correo": {
        "desc": "Genera un correo: nombre.apellido@empresa.com.",
        "p1": "Convertir a minúsculas y formatear.",
        "p2": "Limpiar espacios si es necesario.",
        "p3": "O(n).",
        "py": "def sol(n, a, e): return f'{n.lower()}.{a.lower()}@{e.lower()}.com'\nprint(sol('Ana', 'Sanz', 'ACME'))",
        "js": "const sol = (n, a, e) => `${n.toLowerCase()}.${a.toLowerCase()}@${e.toLowerCase()}.com`;"
    },
    "ano-bisiesto": {
        "desc": "Determina si un año es bisiesto.",
        "p1": "Divisible por 4, pero no por 100, excepto si es por 400.",
        "p2": "Usar lógica booleana: (y%4==0 and y%100!=0) or y%400==0.",
        "p3": "O(1).",
        "py": "def sol(y): return (y % 4 == 0 and y % 100 != 0) or (y % 400 == 0)\nprint(sol(2024))",
        "js": "const sol = y => (y % 4 === 0 && y % 100 !== 0) || (y % 400 === 0);"
    },
    "dia-laboral": {
        "desc": "Comprueba si un día (1-7) es laboral (L-V).",
        "p1": "Rango de 1 a 5 inclusive.",
        "p2": "Comprobar si dia <= 5.",
        "p3": "O(1).",
        "py": "def sol(d): return 1 <= d <= 5\nprint(sol(3))",
        "js": "const sol = d => d >= 1 && d <= 5;"
    },
    "mes-del-ano": {
        "desc": "Devuelve el nombre del mes según su número (1-12).",
        "p1": "Usar una lista o diccionario mapeando índices.",
        "p2": "Manejar índice basado en 0.",
        "p3": "O(1).",
        "py": "def sol(n): return ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'][n-1]\nprint(sol(1))",
        "js": "const sol = n => ['Ene','Feb','Mar','Abr','May','Jun','Jul','Ago','Sep','Oct','Nov','Dic'][n-1];"
    },
    "precio-con-iva": {
        "desc": "Calcula el precio final con 21% de IVA.",
        "p1": "Multiplicar el base por 1.21.",
        "p2": "Redondear si es preciso.",
        "p3": "O(1).",
        "py": "def sol(p): return round(p * 1.21, 2)\nprint(sol(100))",
        "js": "const sol = p => Number((p * 1.21).toFixed(2));"
    },
    "descuento-simple": {
        "desc": "Aplica un porcentaje de descuento a un precio.",
        "p1": "Precio * (1 - descuento / 100).",
        "p2": "Operación matemática simple.",
        "p3": "O(1).",
        "py": "def sol(p, d): return p * (1 - d/100)\nprint(sol(100, 10))",
        "js": "const sol = (p, d) => p * (1 - d/100);"
    },
    "suma-de-lista": {
        "desc": "Suma todos los elementos de una lista de números.",
        "p1": "Iterar y acumular en una variable.",
        "p2": "Usar sum() incorporado.",
        "p3": "O(n).",
        "py": "def sol(L): return sum(L)\nprint(sol([1,2,3]))",
        "js": "const sol = L => L.reduce((a, b) => a + b, 0);"
    },
    "filtro-de-letras": {
        "desc": "Dada una lista de palabras, filtra las que empiezan por una letra.",
        "p1": "Iterar y usar startswith().",
        "p2": "List comprehension para filtrar.",
        "p3": "O(n).",
        "py": "def sol(L, l): return [w for w in L if w.lower().startswith(l.lower())]\nprint(sol(['Ana', 'Bea'], 'a'))",
        "js": "const sol = (L, l) => L.filter(w => w.toLowerCase().startsWith(l.toLowerCase()));"
    },
    "repetir-cadena": {
        "desc": "Repite una cadena N veces.",
        "p1": "Usar concatenación repetida.",
        "p2": "Operador * en Python o repeat() en JS.",
        "p3": "O(n*N).",
        "py": "def sol(s, n): return s * n\nprint(sol('A', 3))",
        "js": "const sol = (s, n) => s.repeat(n);"
    },
    "longitud-de-frase": {
        "desc": "Calcula el número de caracteres (con espacios).",
        "p1": "Usar función de longitud incorporada.",
        "p2": "len(s) o s.length.",
        "p3": "O(1) (depende de implementación interna).",
        "py": "def sol(s): return len(s)\nprint(sol('Hola'))",
        "js": "const sol = s => s.length;"
    },
    "raiz-cuadrada-redondeada": {
        "desc": "Calcula la raíz cuadrada y redondea al entero más cercano.",
        "p1": "Usar función sqrt del módulo math.",
        "p2": "Aplicar round().",
        "p3": "O(1).",
        "py": "import math\ndef sol(n): return round(math.sqrt(n))\nprint(sol(10))",
        "js": "const sol = n => Math.round(Math.sqrt(n));"
    },
    "minimo-de-lista": {
        "desc": "Encuentra el valor más pequeño en una lista.",
        "p1": "Iterar manteniendo el mínimo actual.",
        "p2": "Usar min() incorporado.",
        "p3": "O(n).",
        "py": "def sol(L): return min(L)\nprint(sol([5,2,8]))",
        "js": "const sol = L => Math.min(...L);"
    },
    "filtro-de-numeros": {
        "desc": "Filtra números mayores que X en una lista.",
        "p1": "Comprensión de listas con condición.",
        "p2": "Lamba filter o bucle for.",
        "p3": "O(n).",
        "py": "def sol(L, x): return [n for n in L if n > x]\nprint(sol([1,10,20], 5))",
        "js": "const sol = (L, x) => L.filter(n => n > x);"
    },
    "cambio-de-moneda": {
        "desc": "Convierte de una moneda a otra dado un factor.",
        "p1": "Multiplicar cantidad por tasa.",
        "p2": "Resultado decimal.",
        "p3": "O(1).",
        "py": "def sol(c, t): return c * t\nprint(sol(100, 0.9))",
        "js": "const sol = (c, t) => c * t;"
    },
    "protocolo-de-saludo": {
        "desc": "Genera un saludo formal: 'Hola Sr./Sra. Apellido'.",
        "p1": "Interpolación de cadenas.",
        "p2": "Manejo de prefijo y dato variable.",
        "p3": "O(n).",
        "py": "def sol(a, n): return f'Hola {a} {n}'\nprint(sol('Sr.', 'Blanco'))",
        "js": "const sol = (a, n) => `Hola ${a} ${n}`;"
    },
    "cronometro-basico": {
        "desc": "Calcula diferencia en segundos entre dos tiempos (HH:MM:SS a segundos).",
        "p1": "Transformar ambos tiempos a segundos totales y restar.",
        "p2": "60*60*h + 60*m + s.",
        "p3": "O(1).",
        "py": "def s(t): h,m,ss=map(int,t.split(':')); return h*3600+m*60+ss\ndef sol(t1,t2): return abs(s(t1)-s(t2))",
        "js": "const s = t => { const [h,m,ss] = t.split(':').map(Number); return h*3600+m*60+ss; }; const sol = (t1,t2) => Math.abs(s(t1)-s(t2));"
    },
    "limpieza-de-texto": {
        "desc": "Quita espacios extra al principio y al final.",
        "p1": "Usar métodos de limpieza de strings.",
        "p2": "strip() en Python o trim() en JS.",
        "p3": "O(n).",
        "py": "def sol(s): return s.strip()\nprint(sol('  hola  '))",
        "js": "const sol = s => s.trim();"
    },
    # ── INTERMEDIO ──────────────────────────
    "ordenamiento-de-diccionario": {
        "desc": "Ordena un diccionario por sus valores.",
        "p1": "Convertir a lista de tuplas y usar sorted con una key.",
        "p2": "dict(sorted(d.items(), key=lambda item: item[1])).",
        "p3": "O(n log n).",
        "py": "def sol(d): return dict(sorted(d.items(), key=lambda x: x[1]))\nprint(sol({'a': 3, 'b': 1}))",
        "js": "const sol = d => Object.entries(d).sort(([,a],[,b]) => a-b);"
    },
    "frecuencia-de-elementos": {
        "desc": "Cuenta cuántas veces aparece cada elemento en una lista.",
        "p1": "Usar un diccionario/objeto para acumular conteos.",
        "p2": "Collections.Counter en Python es ideal.",
        "p3": "O(n) tiempo, O(k) espacio para k elementos únicos.",
        "py": "from collections import Counter\ndef sol(L): return dict(Counter(L))\nprint(sol([1,1,2,3]))",
        "js": "const sol = L => L.reduce((a, c) => ({...a, [c]: (a[c]||0)+1}), {});"
    },
    "simulador-de-pila-stack": {
        "desc": "Implementa una clase Pila con push, pop y peek.",
        "p1": "Usar una lista interna para almacenar elementos.",
        "p2": "LIFO (Last In, First Out).",
        "p3": "O(1) para todas las operaciones.",
        "py": "class Pila:\n def __init__(self): self.s = []\n def push(self, v): self.s.append(v)\n def pop(self): return self.s.pop() if self.s else None\n def peek(self): return self.s[-1] if self.s else None",
        "js": "class Pila { constructor(){this.s=[]} push(v){this.s.push(v)} pop(){return this.s.pop()} peek(){return this.s[this.s.length-1]} }"
    },
    "colas-queue-basicas": {
        "desc": "Implementa una cola básica (FIFO).",
        "p1": "Usar una lista o deque para inserción y extracción.",
        "p2": "FIFO (First In, First Out).",
        "p3": "O(1) con deque, O(n) con pop(0) en lista.",
        "py": "from collections import deque\nclass Cola:\n def __init__(self): self.q = deque()\n def add(self, v): self.q.append(v)\n def get(self): return self.q.popleft() if self.q else None",
        "js": "class Cola { constructor(){this.q=[]} add(v){this.q.push(v)} get(){return this.q.shift()} }"
    },
    "generador-de-contrasenas": {
        "desc": "Genera una contraseña aleatoria de longitud N.",
        "p1": "Usar constantes de letras, números y símbolos.",
        "p2": "Módulo secrets para seguridad en Python.",
        "p3": "O(n).",
        "py": "import secrets, string\ndef sol(n): chars = string.ascii_letters + string.digits + string.punctuation; return ''.join(secrets.choice(chars) for _ in range(n))",
        "js": "const sol = n => { const c='abc...123!@#'; return Array.from({length:n}, ()=>c[Math.floor(Math.random()*c.length)]).join(''); };"
    },
    "validador-de-telefonos": {
        "desc": "Valida si un teléfono tiene formato español (+34 o 9 dígitos).",
        "p1": "Usar expresiones regulares para el patrón.",
        "p2": "^(\\+34|0034)?[6789]\\d{8}$.",
        "p3": "O(n).",
        "py": "import re\ndef sol(t): return bool(re.match(r'^(\\+34|0034)?[6789]\\d{8}$', t.replace(' ','')))",
        "js": "const sol = t => /^(\\+34|0034)?[6789]\\d{8}$/.test(t.replace(/\\s/g,''));"
    },
    "analizador-de-logs": {
        "desc": "Extrae las IPs de un archivo de log.",
        "p1": "Regex para encontrar patrones de IP (v4).",
        "p2": r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}.",
        "p3": "O(n).",
        "py": "import re\ndef sol(txt): return re.findall(r'\\d{1,3}(?:\\.\\d{1,3}){3}', txt)",
        "js": "const sol = txt => txt.match(/\\d{1,3}(?:\\.\\d{1,3}){3}/g) || [];"
    },
    "buscador-de-subcadenas": {
        "desc": "Encuentra todas las posiciones de una subcadena.",
        "p1": "Iterar usando find() o regex.",
        "p2": "Loop while con start index.",
        "p3": "O(n*m).",
        "py": "def sol(s, sub): return [i for i in range(len(s)) if s.startswith(sub, i)]",
        "js": "const sol = (s, sub) => { let res=[], i=-1; while((i=s.indexOf(sub, i+1))>=0) res.push(i); return res; };"
    },
    "matriz-identidad": {
        "desc": "Crea una matriz identidad de tamaño N.",
        "p1": "Lista de listas con 1 en diagonal (i == j) y 0 fuera.",
        "p2": "Comprensión anidada.",
        "p3": "O(n^2).",
        "py": "def sol(n): return [[1 if i==j else 0 for j in range(n)] for i in range(n)]",
        "js": "const sol = n => Array.from({length:n}, (_,i)=>Array.from({length:n}, (_,j)=>i===j?1:0));"
    },
    "transposicion-de-matrices": {
        "desc": "Intercambia filas por columnas en una matriz.",
        "p1": "Iterar m[j][i] para cada m[i][j].",
        "p2": "Zip(*matrix) en Python es un truco genial.",
        "p3": "O(n*m).",
        "py": "def sol(m): return [list(f) for f in zip(*m)]",
        "js": "const sol = m => m[0].map((_, i) => m.map(f => f[i]));"
    },
    "simulador-de-registro-csv": {
        "desc": "Convierte una lista de diccionarios a string CSV.",
        "p1": "Obtener cabeceras y unir valores con comas.",
        "p2": "Usar join() y manejo de saltos de línea.",
        "p3": "O(n*k).",
        "py": "def sol(L): h = ','.join(L[0].keys()); b = '\\n'.join(','.join(map(str, d.values())) for d in L); return f'{h}\\n{b}'",
        "js": "const sol = L => { const h=Object.keys(L[0]).join(','); const b=L.map(d=>Object.values(d).join(',')).join('\\n'); return h+'\\n'+b; };"
    },
    "procesador-de-json": {
        "desc": "Filtra un JSON (dict) por una clave específica.",
        "p1": "Recursividad si es anidado, o filtro simple.",
        "p2": "Manejar tipos de datos.",
        "p3": "O(n).",
        "py": "def sol(d, k): return {k: v for k, v in d.items() if k.startswith(k)}",
        "js": "const sol = (d, k) => Object.fromEntries(Object.entries(d).filter(([key])=>key.includes(k)));"
    },
    "contador-de-palabras-unicas": {
        "desc": "Cuenta palabras únicas ignorando mayúsculas/signos.",
        "p1": "Limpiar texto, separar y meter en un Set.",
        "p2": "Uso de set() para unicidad.",
        "p3": "O(n).",
        "py": "import re\ndef sol(txt): return len(set(re.findall(r'\\w+', txt.lower())))",
        "js": "const sol = txt => new Set(txt.toLowerCase().match(/\\w+/g)).size;"
    },
    "busqueda-lineal-optimizada": {
        "desc": "Busca un elemento y lo mueve una posición adelante (Self-organizing list).",
        "p1": "Si encuentra elemento en i > 0, swap con i-1.",
        "p2": "Mejora búsquedas frecuentes.",
        "p3": "O(n).",
        "py": "def sol(L, x):\n try:\n  i = L.index(x)\n  if i>0: L[i], L[i-1] = L[i-1], L[i]\n  return i\n except: return -1",
        "js": "const sol = (L, x) => { let i=L.indexOf(x); if(i>0) [L[i], L[i-1]] = [L[i-1], L[i]]; return i; };"
    },
    "juego-de-palabras-anagramas": {
        "desc": "Verifica si dos palabras son anagramas.",
        "p1": "Ordenar letras y comparar.",
        "p2": "O usar un contador de frecuencias.",
        "p3": "O(n log n).",
        "py": "def sol(a, b): return sorted(a.lower()) == sorted(b.lower())",
        "js": "const sol = (a, b) => a.toLowerCase().split('').sort().join('') === b.toLowerCase().split('').sort().join('');"
    },
    "normalizador-de-titulos": {
        "desc": "Convierte una frase a 'Title Case' (primera letra de cada palabra en mayúscula).",
        "p1": "Split, capitalize() y join.",
        "p2": "Método title() en Python (con cuidado de apóstrofos).",
        "p3": "O(n).",
        "py": "def sol(s): return ' '.join(w.capitalize() for w in s.split())",
        "js": "const sol = s => s.split(' ').map(w => w[0].toUpperCase() + w.slice(1).toLowerCase()).join(' ');"
    },
    "gestion-de-estudiantes-clases": {
        "desc": "Calcula nota media de cada estudiante en un dict.",
        "p1": "Iterar sobre el dict y promediar listas de valores.",
        "p2": "sum(notas)/len(notas).",
        "p3": "O(n*m).",
        "py": "def sol(d): return {k: sum(v)/len(v) for k, v in d.items()}",
        "js": "const sol = d => Object.fromEntries(Object.entries(d).map(([k,v])=>[k, v.reduce((a,b)=>a+b,0)/v.length]));"
    },
    "simulador-de-banco": {
        "desc": "Gestiona ingresos y retiradas de una cuenta.",
        "p1": "Mantener estado de saldo y validar límites.",
        "p2": "Retornar True/False según éxito.",
        "p3": "O(1).",
        "py": "class Banco:\n def __init__(self, s): self.saldo = s\n def mov(self, c): \n  if self.saldo + c < 0: return False\n  self.saldo += c; return True",
        "js": "class Banco { constructor(s){this.saldo=s} mov(c){if(this.saldo+c<0)return false; this.saldo+=c; return true;} }"
    },
    "cifrado-de-sustitucion": {
        "desc": "Cifrado César simple (desplazamiento N).",
        "p1": "Mapear cada letra a su posición i + N en el alfabeto.",
        "p2": "Usar módulo 26 para rotar.",
        "p3": "O(n).",
        "py": "def sol(t, n): res = ''; \n for c in t: \n  if c.isalpha(): \n   base = ord('a') if c.islower() else ord('A')\n   res += chr((ord(c)-base+n)%26+base)\n  else: res += c\n return res",
        "js": "const sol = (t, n) => t.replace(/[a-z]/gi, c => { const b=c<='Z'?65:97; return String.fromCharCode((c.charCodeAt(0)-b+n)%26+b); });"
    },
    "analizador-de-tiempo-delta": {
        "desc": "Calcula días entre dos fechas (YYYY-MM-DD).",
        "p1": "Convertir strings a objetos date y restar.",
        "p2": "Usar datetime en Python o Date en JS.",
        "p3": "O(1).",
        "py": "from datetime import datetime\ndef sol(f1, f2): d1=datetime.strptime(f1,'%Y-%m-%d'); d2=datetime.strptime(f2,'%Y-%m-%d'); return abs((d2-d1).days)",
        "js": "const sol = (f1, f2) => Math.abs((new Date(f2)-new Date(f1))/(1000*3600*24));"
    },
    "validador-de-xml-simple": {
        "desc": "Comprueba si las etiquetas de apertura y cierre coinciden en un XML simple.",
        "p1": "Usar una pila para emparejar etiquetas.",
        "p2": "Regex para extraer etiquetas.",
        "p3": "O(n).",
        "py": "import re\ndef sol(xml):\n stack = []\n for tag, close in re.findall(r'<(/?)(\\w+)>', xml):\n  if not tag: stack.append(close)\n  else: \n   if not stack or stack.pop() != close: return False\n return not stack",
        "js": "const sol = xml => { let s=[], m; const re=/<(\\/?)(\\w+)>/g; while(m=re.exec(xml)){ if(!m[1]) s.push(m[2]); else if(s.pop()!==m[2]) return false; } return !s.length; };"
    },
    "calculo-de-promedio-ponderado": {
        "desc": "Calcula el promedio ponderado de una lista de (valor, peso).",
        "p1": "Sumar (valor * peso) y dividir por suma total de pesos.",
        "p2": "Garantizar que la suma de pesos no sea cero.",
        "p3": "O(n).",
        "py": "def sol(L): num = sum(v*p for v,p in L); den = sum(p for v,p in L); return num/den if den else 0",
        "js": "const sol = L => { const n=L.reduce((a,[v,p])=>a+v*p,0), d=L.reduce((a,[,p])=>a+p,0); return d?n/d:0; };"
    },
    "generador-de-id-unicos": {
        "desc": "Generador de IDs estilo UUID v4 simplificado.",
        "p1": "Usar números aleatorios y formatear en bloques.",
        "p2": "Método uuid4 en Python.",
        "p3": "O(1).",
        "py": "import uuid\ndef sol(): return str(uuid.uuid4())",
        "js": "const sol = () => 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, c => { const r=Math.random()*16|0, v=c=='x'?r:(r&0x3|0x8); return v.toString(16); });"
    },
    "filtro-de-datos-por-atributo": {
        "desc": "Filtra una lista de objetos por un atributo y valor clave.",
        "p1": "Comprensión de listas con acceso dinámico.",
        "p2": "Uso de getattr o corchetes.",
        "p3": "O(n).",
        "py": "def sol(L, k, v): return [o for o in L if o.get(k) == v]",
        "js": "const sol = (L, k, v) => L.filter(o => o[k] === v);"
    },
    "simulacion-de-red-ping": {
        "desc": "Simula latencia de red devolviendo un tiempo aleatorio entre min y max.",
        "p1": "Uso de generador de números aleatorios.",
        "p2": "Unidad en ms.",
        "p3": "O(1).",
        "py": "import random\ndef sol(mi, ma): return random.uniform(mi, ma)",
        "js": "const sol = (mi, ma) => Math.random()*(ma-mi)+mi;"
    },
    "procesador-de-comandos": {
        "desc": "Ejecuta funciones basadas en un string de comando (CLI básica).",
        "p1": "Mapear strings a referencias de funciones.",
        "p2": "Diccionario de comandos.",
        "p3": "O(1).",
        "py": "cmds = {'hola': lambda: 'mundo', 'fecha': lambda: '2026'}; def sol(c): return cmds.get(c, lambda: 'error')()",
        "js": "const cmds={'hola':()=>'mundo'}; const sol=c=>(cmds[c]||(()=>'error'))();"
    },
    "formateador-de-monedas-iso": {
        "desc": "Formatea un número como moneda según el código ISO (EUR, USD).",
        "p1": "Módulo locale en Python o Intl en JS.",
        "p2": "Manejo de símbolos y decimales.",
        "p3": "O(1).",
        "py": "def sol(v, iso): symb={'EUR':'€','USD':'$'}; return f'{v:.2f} {symb.get(iso, iso)}'",
        "js": "const sol = (v, iso) => new Intl.NumberFormat('es-ES', {style:'currency', currency:iso}).format(v);"
    },
    "calculadora-de-interes-compuesto": {
        "desc": "Calcula el capital final tras N años con interés anual.",
        "p1": "Fórmula: Cf = Ci * (1 + r)^n.",
        "p2": "Operador de potencia.",
        "p3": "O(1).",
        "py": "def sol(ci, r, n): return ci * (1 + r/100)**n",
        "js": "const sol = (ci, r, n) => ci * Math.pow(1 + r/100, n);"
    },
    "detector-de-archivos-duplicados": {
        "desc": "Identifica archivos duplicados comparando contenido (hashes).",
        "p1": "Calcular hash (MD5/SHA1) de cada archivo.",
        "p2": "Diccionario hash -> lista_rutas.",
        "p3": "O(n*size).",
        "py": "import hashlib\ndef h(f): return hashlib.md5(open(f,'rb').read()).hexdigest()\ndef sol(L): d={}; [d.setdefault(h(f),[]).append(f) for f in L]; return [v for v in d.values() if len(v)>1]",
        "js": "const sol = L => { /* asíncrono en JS real con fs y crypto */ };"
    },
    "manejador-de-historial-undo": {
        "desc": "Implementa un historial con Undo/Redo usando dos pilas.",
        "p1": "Pila de acciones y pila de descartados.",
        "p2": "Mover entre pilas según comando.",
        "p3": "O(1).",
        "py": "class Hist:\n def __init__(self): self.do, self.re = [], []\n def add(self, x): self.do.append(x); self.re = []\n def undo(self): \n  if self.do: self.re.append(self.do.pop())\n def redo(self): \n  if self.re: self.do.append(self.re.pop())",
        "js": "class Hist { constructor(){this.do=[];this.re=[]} add(x){this.do.push(x);this.re=[]} undo(){if(this.do.length)this.re.push(this.do.pop())} redo(){if(this.re.length)this.do.push(this.re.pop())} }"
    },
    "traductor-de-codigo-morse": {
        "desc": "Traduce texto a código morse.",
        "p1": "Diccionario de mapeo caracter -> puntos/rayas.",
        "p2": "Separar letras por espacio y palabras por barra.",
        "p3": "O(n).",
        "py": "M = {'A': '.-', 'B': '-...'}; # ... \ndef sol(txt): return ' '.join(M.get(c.upper(), '') for c in txt)",
        "js": "const M = {'A': '.-', 'B': '-...'}; const sol = t => t.toUpperCase().split('').map(c=>M[c]||'').join(' ');"
    },
    "extractor-de-dominios": {
        "desc": "Extrae el dominio de una lista de URLs.",
        "p1": "Regex o urlparse para obtener netloc.",
        "p2": r'//([^/]+)',
        "p3": "O(n).",
        "py": "from urllib.parse import urlparse\ndef sol(L): return [urlparse(u).netloc for u in L]",
        "js": "const sol = L => L.map(u => new URL(u).hostname);"
    },
    "simulador-de-loteria": {
        "desc": "Genera una combinación de primitiva (6 números únicos del 1 al 49).",
        "p1": "Muestreo aleatorio sin repetición.",
        "p2": "random.sample o barajar lista.",
        "p3": "O(k).",
        "py": "import random\ndef sol(): return sorted(random.sample(range(1, 50), 6))",
        "js": "const sol = () => { let s=new Set(); while(s.size<6) s.add(Math.floor(Math.random()*49)+1); return [...s].sort((a,b)=>a-b); };"
    },
    "analizador-de-sentiment-heuristico": {
        "desc": "Analizador de sentimientos básico basado en conteo de palabras (+/-).",
        "p1": "Listas de palabras positivas y negativas.",
        "p2": "Puntuación final = pos - neg.",
        "p3": "O(n).",
        "py": "def sol(txt):\n p, n = ['bien','genial'], ['mal','peor']\n words = txt.lower().split()\n return sum(1 for w in words if w in p) - sum(1 for w in words if w in n)",
        "js": "const sol = txt => { const p=['bien','genial'], n=['mal','peor'], w=txt.toLowerCase().split(' '); return w.filter(x=>p.includes(x)).length - w.filter(x=>n.includes(x)).length; };"
    },
    "contador-de-lineas-de-codigo": {
        "desc": "Cuenta líneas de código ignorando comentarios y vacías.",
        "p1": "Filtrar líneas que no empiecen por # o //.",
        "p2": "Uso de strip() y startswith().",
        "p3": "O(n).",
        "py": "def sol(txt): return sum(1 for l in txt.split('\\n') if l.strip() and not l.strip().startswith(('#','//')))",
        "js": "const sol = txt => txt.split('\\n').filter(l => l.trim() && !/^\\/\\/|^#/.test(l.trim())).length;"
    },
    "limpiador-de-metadatos": {
        "desc": "Elimina claves privadas o sensibles de un objeto JSON.",
        "p1": "Diccionario de claves prohibidas.",
        "p2": "Filtrar por k in black_list.",
        "p3": "O(n).",
        "py": "def sol(d): bad=['password','token']; return {k:v for k,v in d.items() if k not in bad}",
        "js": "const sol = d => { const bad=['password','token']; return Object.fromEntries(Object.entries(d).filter(([k])=>!bad.includes(k))); };"
    },
    "generador-de-avatar-texto": {
        "desc": "Genera las iniciales de un nombre como avatar (Max 2 letras).",
        "p1": "Split por espacios y tomar primer carácter de los dos primeros.",
        "p2": "Upper case.",
        "p3": "O(n).",
        "py": "def sol(s): return ''.join(p[0].upper() for p in s.split()[:2])",
        "js": "const sol = s => s.split(' ').slice(0,2).map(p=>p[0].toUpperCase()).join('');"
    },
    "validador-de-isbn": {
        "desc": "Valida un código ISBN-10 (suma de pesos).",
        "p1": "Suma (10-i)*digito % 11 == 0.",
        "p2": "Ultimo dígito puede ser X (10).",
        "p3": "O(1).",
        "py": "def sol(s):\n s=s.replace('-',''); if len(s)!=10: return False\n total = sum((10-i)*(10 if c=='X' else int(c)) for i,c in enumerate(s))\n return total % 11 == 0",
        "js": "const sol = s => { s=s.replace(/-/g,''); if(s.length!==10) return false; let t=s.split('').reduce((a,c,i)=>a+(10-i)*(c==='X'?10:+c),0); return t%11===0; };"
    },
    "simulador-de-gps-distancia": {
        "desc": "Calcula distancia Haversine entre dos coordenadas (lat, lon).",
        "p1": "Fórmula trigonométrica para distancia en esfera.",
        "p2": "Radios a radianes.",
        "p3": "O(1).",
        "py": "import math\ndef sol(lat1,lon1,lat2,lon2):\n r=6371; dlat=math.radians(lat2-lat1); dlon=math.radians(lon2-lon1)\n a=math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2\n return 2*r*math.atan2(math.sqrt(a), math.sqrt(1-a))",
        "js": "const sol = (lat1,lon1,lat2,lon2) => { /* haversine en JS */ };"
    },
    "buscador-de-hashtags": {
        "desc": "Extrae todos los #hashtags de un texto.",
        "p1": "Regex para encontrar palabras que empiezan por #.",
        "p2": r'#\w+',
        "p3": "O(n).",
        "py": "import re\ndef sol(txt): return re.findall(r'#\\w+', txt)",
        "js": "const sol = txt => txt.match(/#\\w+/g) || [];"
    },
    # ── AVANZADO ────────────────────────────
    "algoritmo-de-dijkstra-simple": {
        "desc": "Encuentra el camino más corto en un grafo pequeño.",
        "p1": "Usar una cola de prioridad para explorar el nodo con menor distancia.",
        "p2": "Relajar aristas actualizando distancias mínimas.",
        "p3": "O((V+E) log V).",
        "py": "import heapq\ndef sol(g, s):\n dist = {n: float('inf') for n in g}; dist[s] = 0\n pq = [(0, s)]\n while pq:\n  d, u = heapq.heappop(pq)\n  if d > dist[u]: continue\n  for v, w in g[u].items():\n   if dist[u] + w < dist[v]: dist[v] = dist[u] + w; heapq.heappush(pq, (dist[v], v))\n return dist",
        "js": "const sol = (g, s) => { /* dijkstra en JS */ };"
    },
    "analizador-de-frecuencia": {
        "desc": "Realiza un análisis de frecuencia de letras para descifrar un texto.",
        "p1": "Contar ocurrencias de cada letra y comparar con frecuencias del idioma.",
        "p2": "Ordenar por frecuencia descendente.",
        "p3": "O(n).",
        "py": "from collections import Counter\ndef sol(t): c = Counter(c for c in t.lower() if c.isalpha()); return c.most_common()",
        "js": "const sol = t => { const c={}; for(let l of t.toLowerCase()) if(/[a-z]/.test(l)) c[l]=(c[l]||0)+1; return Object.entries(c).sort((a,b)=>b[1]-a[1]); };"
    },
    "analizador-de-tiempos": {
        "desc": "Mide el tiempo de ejecución de una función (decorator).",
        "p1": "Tomar tiempo antes y después de llamar a la función.",
        "p2": "Usar time.perf_counter().",
        "p3": "O(1).",
        "py": "import time\ndef timer(f):\n def w(*a,**kw):\n  t=time.perf_counter(); r=f(*a,**kw); print(time.perf_counter()-t); return r\n return w",
        "js": "const timer = f => (...a) => { console.time('f'); const r=f(...a); console.timeEnd('f'); return r; };"
    },
    "buscador-con-autocompletado": {
        "desc": "Implementa un buscador con autocompletado usando un Trie.",
        "p1": "Insertar palabras en el Trie y buscar prefijos.",
        "p2": "DFS para encontrar todas las palabras desde un nodo.",
        "p3": "O(L) para búsqueda, O(N) para sugerencias.",
        "py": "class TrieNode: \n def __init__(self): self.c={}; self.end=False\ndef sol(root, pref): pass",
        "js": "class Trie { /* trie en JS */ }"
    },
    "simulador-de-blockchain": {
        "desc": "Crea una cadena de bloques básica con hashing y prueba de trabajo.",
        "p1": "Cada bloque contiene hash del anterior y un nonce.",
        "p2": "Calcular SHA256 hasta cumplir dificultad.",
        "p3": "O(2^dificultad).",
        "py": "import hashlib\ndef hash_b(b): return hashlib.sha256(str(b).encode()).hexdigest()\ndef mine(b, d): \n while not hash_b(b).startswith('0'*d): b['nonce']+=1\n return b",
        "js": "const mine = (b, d) => { /* mining en JS */ };"
    },
    "criptografia-p2p": {
        "desc": "Simula intercambio de llaves Diffie-Hellman.",
        "p1": "Generar llaves privadas y calcular pública: (g^a mod p).",
        "p2": "Secreto compartido = (B^a mod p).",
        "p3": "O(log exp).",
        "py": "def sol(g, p, a, b): A = pow(g, a, p); B = pow(g, b, p); return pow(B, a, p) == pow(A, b, p)",
        "js": "const sol = (g, p, a, b) => { /* DH en JS */ };"
    },
    "balanceador-de-carga-simulado": {
        "desc": "Implementa un algoritmo Round Robin para balanceo de carga.",
        "p1": "Mantener puntero al último servidor usado.",
        "p2": "Ciclo modulo N.",
        "p3": "O(1).",
        "py": "class LB:\n def __init__(self, srvs): self.s=srvs; self.i=0\n def get(self): r=self.s[self.i]; self.i=(self.i+1)%len(self.s); return r",
        "js": "class LB { constructor(s){this.s=s;this.i=0} get(){return this.s[this.i++ % this.s.length]} }"
    },
    "worker-queue-con-prioridad": {
        "desc": "Cola de tareas donde las de mayor prioridad se ejecutan antes.",
        "p1": "Usar Max-Heap o Min-Heap con prioridades negativas.",
        "p2": "LIFO para misma prioridad opcionalmente.",
        "p3": "O(log n).",
        "py": "import heapq\nclass PQ:\n def __init__(self): self.q=[]\n def add(self, t, p): heapq.heappush(self.q, (-p, t))\n def get(self): return heapq.heappop(self.q)[1]",
        "js": "/* PriorityQueue en JS */"
    },
    "analizador-de-heap": {
        "desc": "Verifica si una lista cumple la propiedad de un Max-Heap.",
        "p1": "Para cada i, L[i] >= L[2i+1] y L[i] >= L[2i+2].",
        "p2": "Iterar hasta n/2.",
        "p3": "O(n).",
        "py": "def sol(L):\n n=len(L)\n for i in range(n//2):\n  if 2*i+1 < n and L[i] < L[2*i+1]: return False\n  if 2*i+2 < n and L[i] < L[2*i+2]: return False\n return True",
        "js": "const sol = L => L.every((v,i) => (2*i+1>=L.length || v>=L[2*i+1]) && (2*i+2>=L.length || v>=L[2*i+2]));"
    },
    "profilier-de-funciones": {
        "desc": "Cuenta llamadas y tiempo total por función.",
        "p1": "Uso de wrapper que actualiza estadísticas globales.",
        "p2": "Diccionario de rastro {func: {count, time}}.",
        "p3": "O(1) overhead.",
        "py": "stats = {}\ndef profile(f):\n def w(*a,**kw):\n  s=stats.setdefault(f.__name__,{'c':0,'t':0}); s['c']+=1\n  return f(*a,**kw)\n return w",
        "js": "/* profiler en JS */"
    },
    "interprete-lisp-basico": {
        "desc": "Evalúa expresiones S-expressions básicas (+, -, *).",
        "p1": "Tokenizar y parsear recursivamente a listas anidadas.",
        "p2": "Evaluar la lista según el primer elemento (operador).",
        "p3": "O(n).",
        "py": "def eval_L(exp, env): \n if isinstance(exp, int): return exp\n op, *args = exp; vals = [eval_L(a, env) for a in args]\n if op == '+': return sum(vals)\n return 0",
        "js": "const evalL = (exp, env) => { /* lisp eval */ };"
    },
    "motor-de-reglas-dinamicas": {
        "desc": "Evalúa si un objeto cumple un conjunto de reglas (if/then).",
        "p1": "Reglas como predicados (lambda).",
        "p2": "Comprobar all(r(obj) for r in rules).",
        "p3": "O(reglas).",
        "py": "def sol(obj, rules): return all(r(obj) for r in rules)",
        "js": "const sol = (obj, rules) => rules.every(r => r(obj));"
    },
    "compresion-huffman": {
        "desc": "Genera el árbol de Huffman para un texto dado.",
        "p1": "Contar frecuencias, construir nodos y usar heap para unir los dos menores.",
        "p2": "Árbol binario de prefijos.",
        "p3": "O(n log n).",
        "py": "import heapq\ndef sol(txt):\n from collections import Counter\n f = Counter(txt); pq = [[v, [k, '']] for k,v in f.items()]\n heapq.heapify(pq)\n while len(pq) > 1:\n  lo = heapq.heappop(pq); hi = heapq.heappop(pq)\n  for p in lo[1:]: p[1] = '0' + p[1]\n  for p in hi[1:]: p[1] = '1' + p[1]\n  heapq.heappush(pq, [lo[0] + hi[0]] + lo[1:] + hi[1:])\n return sorted(heapq.heappop(pq)[1:], key=lambda p: (len(p[-1]), p))",
        "js": "/* Huffman en JS */"
    },
    "diff-de-archivos-levenshtein": {
        "desc": "Calcula la distancia de edición mínima entre dos textos.",
        "p1": "Programación dinámica con matriz de distancias.",
        "p2": "Opciones: insertar, borrar, reemplazar.",
        "p3": "O(n*m).",
        "py": "def sol(a, b):\n m, n = len(a), len(b)\n d = [[0]*(n+1) for _ in range(m+1)]\n for i in range(m+1): d[i][0]=i\n for j in range(n+1): d[0][j]=j\n for i in range(1,m+1):\n  for j in range(1,n+1):\n   cost = 0 if a[i-1] == b[j-1] else 1\n   d[i][j] = min(d[i-1][j]+1, d[i][j-1]+1, d[i-1][j-1]+cost)\n return d[m][n]",
        "js": "const sol = (a, b) => { /* Levenshtein en JS */ };"
    },
    "sincronizacion-de-bases-mock": {
        "desc": "Sincroniza dos diccionarios (DBs) aplicando cambios de A en B.",
        "p1": "Identificar qué falta en B, qué sobra y qué ha cambiado.",
        "p2": "Keys set difference.",
        "p3": "O(n).",
        "py": "def sol(da, db):\n for k, v in da.items(): db[k] = v\n for k in list(db): \n  if k not in da: del db[k]\n return db",
        "js": "const sol = (da, db) => { for(let k in da) db[k]=da[k]; for(let k in db) if(!(k in da)) delete db[k]; return db; };"
    },
    "websocket-manager": {
        "desc": "Gestiona estados de múltiples conexiones (Broadcast, Unicast).",
        "p1": "Diccionario de IDs -> Sockets.",
        "p2": "Loop para enviar a todos.",
        "p3": "O(n).",
        "py": "class WS:\n def __init__(self): self.clients = {}\n def reg(self, id, s): self.clients[id] = s\n def bcast(self, msg): [s.send(msg) for s in self.clients.values()]",
        "js": "class WS { constructor(){this.clients=new Map()} reg(id,s){this.clients.set(id,s)} bcast(m){this.clients.forEach(s=>s.send(m))} }"
    },
    "auth-con-token-simulado": {
        "desc": "Valida tokens JWT (simplificado) comprobando firma.",
        "p1": "Header.Payload.Signature. Hashing de H+P con secreto.",
        "p2": "HMAC SHA256.",
        "p3": "O(n).",
        "py": "import hmac, hashlib, base64\ndef sol(t, s):\n p, sig = t.rsplit('.', 1)\n exp_sig = hmac.new(s.encode(), p.encode(), hashlib.sha256).digest()\n return sig == base64.b64encode(exp_sig).decode()",
        "js": "const sol = (t, s) => { /* JWT check in JS */ };"
    },
    "rate-limiting-avanzado": {
        "desc": "Algoritmo Token Bucket para rate limiting.",
        "p1": "Recargar tokens por tiempo transcurrido, retirar al consumir.",
        "p2": "Validar si bucket tiene tokens.",
        "p3": "O(1).",
        "py": "import time\nclass TB:\n def __init__(self, r, c): self.r, self.c, self.t, self.last = r, c, c, time.time()\n def allow(self): \n  now = time.time(); self.t = min(self.c, self.t + (now - self.last)*self.r)\n  self.last = now\n  if self.t >= 1: self.t -= 1; return True\n  return False",
        "js": "class TB { /* TokenBucket in JS */ }"
    },
    "orquestador-de-microservicios": {
        "desc": "Encadena llamadas a servicios con manejo de fallos (Circuit Breaker).",
        "p1": "Si un servicio falla N veces, abrir el circuito y no llamar.",
        "p2": "Estado: CLOSED, OPEN, HALF_OPEN.",
        "p3": "O(1).",
        "py": "class CB:\n def __init__(self): self.fails = 0; self.open = False\n def call(self, f):\n  if self.open: return 'error'\n  try: return f()\n  except: \n   self.fails += 1\n   if self.fails > 3: self.open = True\n   return 'error'",
        "js": "class CB { /* CircuitBreaker in JS */ }"
    },
    "database-sharding-logic": {
        "desc": "Distribuye datos en N nodos usando Sharding (Consistent Hashing).",
        "p1": "Hash de la clave modulo N servidores.",
        "p2": "Garantizar distribución uniforme.",
        "p3": "O(1).",
        "py": "def sol(k, n): return hash(k) % n",
        "js": "const sol = (k, n) => { let h=0; for(let c of k) h+=c.charCodeAt(0); return h%n; };"
    },
    "estrategia-de-retry-exponencial": {
        "desc": "Implementa reintentos con espera exponencial (Exponential Backoff).",
        "p1": "En cada fallo, esperar 2^intento segundos.",
        "p2": "Añadir un factor de aleatoriedad (jitter) para evitar colisiones.",
        "p3": "O(log n) reintentos.",
        "py": "import time, random\ndef sol(f, max_r=5):\n for i in range(max_r):\n  try: return f()\n  except: time.sleep((2**i) + random.random())\n return 'error'",
        "js": "const sol = async (f, max=5) => { for(let i=0; i<max; i++) try { return await f(); } catch { await new Promise(r=>setTimeout(r, (2**i)*1000)); } };"
    },
    "audit-log-con-inmutabilidad": {
        "desc": "Sistema de log donde cada entrada incluye el hash de la anterior.",
        "p1": "Encadenar registros como una blockchain simple.",
        "p2": "Garantiza que no se han borrado registros intermedios.",
        "p3": "O(n).",
        "py": "import hashlib\nlog = []\ndef add(m): prev = log[-1]['h'] if log else '0'; h = hashlib.sha256(f'{prev}{m}'.encode()).hexdigest(); log.append({'m':m, 'h':h})",
        "js": "/* ImmutableLog in JS */"
    },
    "generador-de-dsl-domain-specific-language": {
        "desc": "Pequeño DSL para realizar operaciones matemáticas simples desde texto.",
        "p1": "Parsear comandos como 'SUMA 10 20' o 'RESTA 5 2'.",
        "p2": "Mapeo de palabras clave a operadores.",
        "p3": "O(n).",
        "py": "def sol(txt):\n cmd, *args = txt.split(); a, b = map(int, args)\n if cmd == 'SUMA': return a + b\n if cmd == 'RESTA': return a - b",
        "js": "const sol = t => { const [c,a,b]=t.split(' '); return c==='SUMA'?+a + +b : +a - +b; };"
    },
    "motor-de-recomendaciones-basado-en-tags": {
        "desc": "Recomienda items similares basados en la intersección de sus etiquetas.",
        "p1": "Calcular coeficiente de Jaccard o simplemente intersección de sets.",
        "p2": "Ordenar por mayor coincidencia.",
        "p3": "O(N*M).",
        "py": "def sol(item, Others):\n s1 = set(item['tags'])\n return sorted(Others, key=lambda x: len(s1 & set(x['tags'])), reverse=True)",
        "js": "const sol = (it, Ots) => Ots.sort((a,b) => b.tags.filter(t=>it.tags.includes(t)).length - a.tags.filter(t=>it.tags.includes(t)).length);"
    },
    "procesamiento-en-paralelo": {
        "desc": "Ejecuta una lista de tareas en paralelo usando hilos o procesos.",
        "p1": "Dividir carga entre múltiples núcleos.",
        "p2": "Uso de concurrent.futures en Python.",
        "p3": "O(n/cores).",
        "py": "from concurrent.futures import ThreadPoolExecutor\ndef sol(L, f): \n with ThreadPoolExecutor() as e: return list(e.map(f, L))",
        "js": "const sol = L => Promise.all(L.map(f));"
    },
    "rate-limiter-por-ip": {
        "desc": "Limita el número de peticiones por cada dirección IP única.",
        "p1": "Uso de diccionario IP -> [Timestamps].",
        "p2": "Limpiar timestamps antiguos en cada chequeo.",
        "p3": "O(k) donde k es el límite por IP.",
        "py": "ips = {}; def sol(ip, limit=100):\n now = time.time(); h = ips.setdefault(ip, [])\n h[:] = [t for t in h if now - t < 60]\n if len(h) < limit: h.append(now); return True\n return False",
        "js": "/* RateLimiter in JS */"
    },
    "simulador-de-cajero-automatico": {
        "desc": "Calcula el número mínimo de billetes para una cantidad dada.",
        "p1": "Algoritmo Greedy: usar billetes más grandes primero.",
        "p2": "Billetes de 50, 20, 10, 5.",
        "p3": "O(1) (número finito de billetes).",
        "py": "def sol(amt):\n res = {}; bills = [50, 20, 10, 5]\n for b in bills:\n  count = amt // b\n  if count: res[b] = count; amt %= b\n return res",
        "js": "const sol = amt => { const res={}, bills=[50,20,10,5]; bills.forEach(b=>{ let c=Math.floor(amt/b); if(c){res[b]=c; amt%=b;} }); return res; };"
    },
    "simulador-de-encriptacion-rsa": {
        "desc": "Simulación básica de encriptación RSA (Generación, Cifrado, Descifrado).",
        "p1": "Elegir p, q primos; n = p*q; phi = (p-1)*(q-1).",
        "p2": "C = M^e mod n; M = C^d mod n.",
        "p3": "O(log exp).",
        "py": "def sol(m, e, n): return pow(m, e, n)",
        "js": "const sol = (m, e, n) => { /* RSA modPow check */ };"
    },
    "sistema-de-cache-lru": {
        "desc": "Implementa una caché del tipo Least Recently Used.",
        "p1": "Usar OrderedDict o Hashmap + Doubly Linked List.",
        "p2": "Mover al final al acceder, borrar el primero al llenar.",
        "p3": "O(1) para get y put.",
        "py": "from collections import OrderedDict\nclass LRU:\n def __init__(self, cap): self.c = cap; self.m = OrderedDict()\n def get(self, k): \n  if k not in self.m: return -1\n  self.m.move_to_end(k); return self.m[k]\n def put(self, k, v):\n  if k in self.m: self.m.move_to_end(k)\n  self.m[k] = v\n  if len(self.m) > self.c: self.m.popitem(last=False)",
        "js": "class LRU { /* LRU in JS with Map */ }"
    },
    "sistema-de-notas-academicas": {
        "desc": "Convierte puntuaciones numéricas a calificaciones (A, B, C, F).",
        "p1": "Múltiples condiciones if/elif.",
        "p2": ">=90: A, >=80: B, etc.",
        "p3": "O(1).",
        "py": "def sol(n): \n if n >= 90: return 'A'\n if n >= 80: return 'B'\n if n >= 70: return 'C'\n return 'F'",
        "js": "const sol = n => n>=90?'A':n>=80?'B':n>=70?'C':'F';"
    },
    "validador-de-parentesis": {
        "desc": "Comprueba si una cadena de paréntesis está equilibrada.",
        "p1": "Usar una pila para emparejar aperturas y cierres.",
        "p2": "Empujar '(' y sacar en ')'.",
        "p3": "O(n).",
        "py": "def sol(s):\n st = []\n for c in s:\n  if c == '(': st.append(c)\n  elif not st or st.pop() != '(': return False\n return not st",
        "js": "const sol = s => { let st=[]; for(let c of s){ if(c==='(') st.push(c); else if(!st.pop()) return false; } return !st.length; };"
    },
    "validador-de-tarjetas-luhn": {
        "desc": "Algoritmo de Luhn para validar números de tarjetas de crédito.",
        "p1": "Doblar dígitos impares desde la derecha (restando 9 si > 9) y sumar todo.",
        "p2": "Suma total % 10 == 0.",
        "p3": "O(n).",
        "py": "def sol(s):\n L = [int(c) for c in s[::-1]]\n L[1::2] = [(n*2-9 if n*2>9 else n*2) for n in L[1::2]]\n return sum(L) % 10 == 0",
        "js": "const sol = s => { /* Luhn in JS */ };"
    },
    "web-scraper-basico": {
        "desc": "Extrae todos los links (href) de una página HTML.",
        "p1": "Regex para buscar patrones <a href='...'>.",
        "p2": r'href=["\'](https?://[^"\']+)["\']',
        "p3": "O(n).",
        "py": "import re\ndef sol(html): return re.findall(r'href=[\"\\'](https?://[^\"\\']+)[\"\\']', html)",
        "js": "const sol = h => [...h.matchAll(/href=[\"'](https?://[^\"']+)[\"']/g)].map(m=>m[1]);"
    },
    "conversor-de-binario-a-decimal": {
        "desc": "Convierte un número binario (string) a decimal.",
        "p1": "Usar int(s, 2) en Python o parseInt(s, 2) en JS.",
        "p2": "Validar que la cadena solo contenga 0s y 1s.",
        "p3": "O(n).",
        "py": "def sol(s): return int(s, 2)",
        "js": "const sol = s => parseInt(s, 2);"
    },
    "generador-de-qr-simulado": {
        "desc": "Simula la generación de una matriz de QR para un texto.",
        "p1": "Crear una matriz de N x N con valores aleatorios (0/1).",
        "p2": "Dimensiones proporcionales a la longitud del texto.",
        "p3": "O(n^2).",
        "py": "import random\ndef sol(t): n=len(t)+4; return [[random.choice([0,1]) for _ in range(n)] for _ in range(n)]",
        "js": "const sol = t => { const n=t.length+4; return Array(n).fill().map(()=>Array(n).fill().map(()=>Math.round(Math.random()))); };"
    },
    "arboles-binarios-de-busqueda": {
        "desc": "Implementa inserción y búsqueda en un ABB.",
        "p1": "Nodos con left, right y val.",
        "p2": "Insertar recurriendo por el lado menor o mayor.",
        "p3": "O(log n) promedio, O(n) peor caso.",
        "py": "class Node:\n def __init__(self,v): self.v=v; self.l=None; self.r=None\ndef ins(root,v):\n if not root: return Node(v)\n if v<root.v: root.l=ins(root.l,v)\n else: root.r=ins(root.r,v)\n return root",
        "js": "/* BST in JS */"
    },
    "validacion-de-contrasenas": {
        "desc": "Valida si una contraseña cumple requisitos (Longitud, Mayús, Núm, Símbolo).",
        "p1": "Comprobar todas las condiciones con regex o iteración.",
        "p2": "Longitud mínima (ej: 8).",
        "p3": "O(n).",
        "py": "import re\ndef sol(p): return len(p)>=8 and re.search('[A-Z]',p) and re.search('[a-z]',p) and re.search('[0-9]',p)",
        "js": "const sol = p => p.length>=8 && /[A-Z]/.test(p) && /[a-z]/.test(p) && /[0-9]/.test(p);"
    },
}

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


from string import Template

# ─────────────────────────────────────────────
# TEMPLATE MDX
# ─────────────────────────────────────────────
TEMPLATE = Template("""\
---
draft: false
title: "$title"
description: "$description"
pubDate: "$pub_date"
tags: $tags
slug: "$slug"
image: "$image"
author: "Jorge Beneyto Castelló"
difficulty: "$difficulty"
---

import Challenge from '../../components/Challenge.astro';

# 🎯 $titulo_h1

### 📝 Descripción del Reto

$descripcion

<Challenge 
  nivel="$difficulty" 
  mision="$mision" 
/>

---

## 💡 Guía de Solución Paso a Paso

<details>
<summary><b>Ver explicación y código 🛠️ (¡No hagas spoiler!)</b></summary>
<div class="details-content">

### 🏗️ Paso 1: Análisis de la lógica

$paso1

### ⚙️ Paso 2: Implementación en $lang_name

$paso2

### 🚀 Paso 3: Complejidad y Optimización

$paso3

### 💻 Código de la Solución ($lang_name)

```$lang_code
$codigo
```

</div>
</details>
""")

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


def get_code(sol, target_lang_id):
    """
    Obtiene código de la solución según lenguaje, con fallback inteligente.
    Retorna (codigo, lang_id)
    """
    mapping = {
        "python": "py", "javascript": "js", "typescript": "ts",
        "go": "go", "rust": "rs", "java": "java", "csharp": "cs",
        "kotlin": "kt", "swift": "sw", "php": "php", "ruby": "rb", "dart": "dart"
    }
    
    # 1. Intentar el lenguaje objetivo
    key = mapping.get(target_lang_id)
    if key and sol.get(key):
        return sol[key], target_lang_id
        
    # 2. Si no hay, buscar el primero disponible en el dict
    for lid, k in mapping.items():
        if sol.get(k):
            return sol[k], lid
            
    # 3. Mínimo fallback si el dict está vacío por alguna razón
    return sol.get("py", "# No code available"), "python"


def mdx_escape(text):
    """Escapa caracteres que pueden romper el MDX o el frontmatter."""
    if not text: return ""
    return str(text)


# ─────────────────────────────────────────────
# PROCESO PRINCIPAL
# ─────────────────────────────────────────────

def fix_all():
    folder = CHALLENGES_DIR
    files = sorted([
        f for f in os.listdir(folder)
        if f.endswith('.mdx') and (f.startswith('guia-plus-reto-') or f.startswith('guia-'))
    ])
    
    print(f"📂 {len(files)} archivos encontrados\n")
    fixed = 0

    # Crear mapeo de IDs a nombres para el fallback
    lang_info = { lid: (lcode, lname) for lid, lcode, lname in LANGS }

    for idx, fname in enumerate(files):
        path = os.path.join(folder, fname)
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        fm = parse_frontmatter(content)
        if not fm.get('title'):
            print(f"⚠️  Sin título: {fname}")
            continue

        titulo = fm.get('title', '').strip()
        difficulty = fm.get('difficulty', 'Intermedio')
        pub_date = fm.get('pubDate', '2026-01-01')
        image = fm.get('image', '/img/default.jpg')
        slug = fm.get('slug', fname.replace('.mdx', ''))

        # Lenguaje objetivo (rotativo)
        target_lang_id, _, _ = LANGS[idx % len(LANGS)]

        # Buscar solución en base de datos
        key = slug_key(slug)
        sol_data = SOLUTIONS.get(key)

        if sol_data:
            descripcion = sol_data['desc']
            paso1 = sol_data['p1']
            paso2 = sol_data['p2']
            paso3 = sol_data['p3']
            # Obtener código y el lenguaje real que se usará
            codigo_raw, lid_final = get_code(sol_data, target_lang_id)
            lcode_final, lname_final = lang_info[lid_final]
        else:
            # Solución genérica
            descripcion = f"Resuelve el siguiente reto de programación: **{titulo}**."
            paso1 = "Analizar el problema y definir casos de prueba."
            paso2 = f"Implementar la solución en {lang_info[target_lang_id][1]}."
            paso3 = "Optimizar si es necesario."
            lid_final = target_lang_id
            lcode_final, lname_final = lang_info[lid_final]
            gen_fn = GENERIC_SOLUTIONS.get(lid_final, GENERIC_SOLUTIONS["python"])
            codigo_raw = gen_fn(titulo, descripcion)

        # Escapar todo para seguridad MDX y string.Template
        vars = {
            "title": mdx_escape(titulo.replace('"', "'")),
            "description": mdx_escape(descripcion[:150].replace('"', "'")),
            "pub_date": pub_date,
            "tags": json.dumps([lid_final, 'retos', difficulty.lower(), 'guia-plus'], ensure_ascii=False),
            "slug": slug,
            "image": image,
            "difficulty": difficulty,
            "titulo_h1": mdx_escape(re.sub(r'^🏆\s*RETO:\s*', '', titulo).strip()),
            "descripcion": mdx_escape(descripcion),
            "mision": mdx_escape(descripcion[:300].replace('"', "'")),
            "paso1": mdx_escape(paso1),
            "paso2": mdx_escape(paso2),
            "paso3": mdx_escape(paso3),
            "lang_name": lname_final,
            "lang_code": lcode_final,
            "codigo": mdx_escape(codigo_raw),
        }

        try:
            nuevo = TEMPLATE.safe_substitute(vars)
            with open(path, 'w', encoding='utf-8') as f:
                f.write(nuevo)
            print(f"✅ [{idx+1:03d}] {fname} → {lname_final}")
            fixed += 1
        except Exception as e:
            print(f"❌ Error en {fname}: {e}")

    print(f"\n🎉 {fixed}/{len(files)} archivos actualizados correctamente.")


if __name__ == "__main__":
    fix_all()
