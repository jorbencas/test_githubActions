MDTOOLS_NAV_HTML = """<nav class="main-nav" id="mainNav">
  <div class="nav-inner">
    <a href="/" class="nav-back">← Dashboard</a>
    <a href="/mdtools/" class="nav-brand">Markdown Tools</a>
    <button class="nav-toggle" id="navToggle" aria-label="Abrir menú">
      <span></span><span></span><span></span>
    </button>
    <div class="nav-links" id="navLinks">
      <a href="/mdtools/" class="{active_home}">Inicio</a>
      <a href="/mdtools/pdf.html" class="{active_pdf}">PDF</a>
      <a href="/mdtools/slides.html" class="{active_slides}">Diapositivas</a>
      <a href="/mdtools/table.html" class="{active_table}">Tabla</a>
      <a href="/mdtools/snippets.html" class="{active_snippets}">Snippets</a>
      <a href="/mdtools/cheatsheet.html" class="{active_cheatsheet}">Cheatsheet</a>
    </div>
  </div>
</nav>"""

MDTOOLS_TOOLS_SUBNAV_HTML = """<div class="tools-subnav" id="toolsSubnav">
  <div class="subnav-inner">
    <a href="#editor">Editor</a>
    <a href="#preview">Preview</a>
    <a href="#output">Resultado</a>
  </div>
</div>"""

MDTOOLS_BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} | Markdown Tools</title>
  <meta name="description" content="{description}">
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><text y='.9em' font-size='90'>📝</text></svg>">
  <link rel="stylesheet" href="/mdtools/css/base.css">
  <link rel="stylesheet" href="/mdtools/css/nav.css">
  <link rel="stylesheet" href="/mdtools/css/editor.css">
  <link rel="stylesheet" href="/mdtools/css/tools.css">
  <link rel="stylesheet" href="/mdtools/css/dark-theme.css">
  <link rel="stylesheet" href="/mdtools/css/responsive.css">
  {extra_head}
</head>
<body>
{nav}

  <main class="main-content">
{content}
  </main>

  <footer class="site-footer">
    <p>Markdown Tools &mdash; Herramientas offline para convertir y transformar Markdown</p>
  </footer>

  <script src="/mdtools/js/nav.js"></script>
  {extra_scripts}
</body>
</html>"""

MDTOOLS_HOME_CONTENT = """    <section class="hero">
      <h1>Markdown Tools</h1>
      <p class="hero-subtitle">Herramientas offline para convertir y transformar Markdown</p>
    </section>

    <section class="tools-grid">
      <a href="/mdtools/pdf.html" class="tool-card">
        <div class="tool-icon">📄</div>
        <h3>Markdown a PDF</h3>
        <p>Convierte Markdown a PDF con soporte de tablas, listas, bloques de código y encabezados estilizados.</p>
        <span class="tool-tag">Cliente-side</span>
      </a>
      <a href="/mdtools/slides.html" class="tool-card">
        <div class="tool-icon">🎞️</div>
        <h3>Diapositivas</h3>
        <p>Crea presentaciones estilo Reveal.js directamente desde Markdown.</p>
        <span class="tool-tag">Cliente-side</span>
      </a>
      <a href="/mdtools/table.html" class="tool-card">
        <div class="tool-icon">📊</div>
        <h3>Tabla Markdown</h3>
        <p>Genera tablas Markdown con alineación configurable a partir de datos tabulares.</p>
        <span class="tool-tag">Cliente-side</span>
      </a>
      <a href="/mdtools/snippets.html" class="tool-card">
        <div class="tool-icon">✂️</div>
        <h3>Snippets de Código</h3>
        <p>Extrae y formatea fragmentos de código con numeración de líneas y syntax highlighting.</p>
        <span class="tool-tag">Cliente-side</span>
      </a>
      <a href="/mdtools/cheatsheet.html" class="tool-card">
        <div class="tool-icon">📋</div>
        <h3>Cheatsheet</h3>
        <p>Referencia rápida de Markdown: syntax, emojis, shortcodes y más.</p>
        <span class="tool-tag">Referencia</span>
      </a>
    </section>"""

MDTOOLS_PDF_CONTENT = """    <section class="tool-header">
      <h1>📄 Markdown a PDF</h1>
      <p>Convierte Markdown a PDF directamente en el navegador.</p>
    </section>

    <section class="tool-layout">
      <div class="editor-pane">
        <div class="pane-header">
          <h3>Markdown</h3>
          <div class="pane-actions">
            <button class="btn-sm" id="btnLoadExample">Ejemplo</button>
            <button class="btn-sm" id="btnClear">Limpiar</button>
          </div>
        </div>
        <textarea id="mdInput" class="editor-textarea" placeholder="Escribe o pega tu Markdown aquí..."></textarea>
      </div>

      <div class="preview-pane">
        <div class="pane-header">
          <h3>Preview</h3>
          <div class="pane-actions">
            <select id="pdfTheme">
              <option value="default">Tema claro</option>
              <option value="dark">Tema oscuro</option>
              <option value="mono">Monocromático</option>
            </select>
          </div>
        </div>
        <div id="preview" class="preview-content"></div>
      </div>
    </section>

    <section class="output-section">
      <div class="output-header">
        <h3>Resultado</h3>
        <button class="btn-primary" id="btnGenerate">Generar PDF</button>
      </div>
      <div id="pdfOutput" class="output-content">
        <p class="output-placeholder">Haz clic en "Generar PDF" para ver el resultado.</p>
      </div>
    </section>

    <section class="limitations-section">
      <h3>Limitaciones conocidas</h3>
      <ul>
        <li><strong>Páginas máximas:</strong> 50 (limitación de pdfmake)</li>
        <li><strong>Tabla:</strong> máx. 500 filas por tabla</li>
        <li><strong>Syntax highlighting:</strong> no soportado en PDF (se renderiza como texto plano)</li>
        <li><strong>Mermaid / SVG:</strong> se inserta como imagen estática capturada del preview</li>
      </ul>
    </section>"""

MDTOOLS_SLIDES_CONTENT = """    <section class="tool-header">
      <h1>🎞️ Diapositivas desde Markdown</h1>
      <p>Crea presentaciones estilo Reveal.js directamente en el navegador.</p>
    </section>

    <section class="tool-layout">
      <div class="editor-pane">
        <div class="pane-header">
          <h3>Markdown</h3>
          <div class="pane-actions">
            <button class="btn-sm" id="btnLoadExample">Ejemplo</button>
            <button class="btn-sm" id="btnClear">Limpiar</button>
          </div>
        </div>
        <textarea id="mdInput" class="editor-textarea" placeholder="Separa diapositivas con --- (tres guiones)"></textarea>
      </div>

      <div class="preview-pane">
        <div class="pane-header">
          <h3>Preview</h3>
          <div class="pane-actions">
            <button class="btn-sm" id="btnPrev">◀</button>
            <span id="slideCounter" class="slide-counter">1 / 1</span>
            <button class="btn-sm" id="btnNext">▶</button>
            <button class="btn-sm" id="btnFullscreen">⛶</button>
          </div>
        </div>
        <div id="preview" class="preview-content slide-preview"></div>
      </div>
    </section>"""

MDTOOLS_TABLE_CONTENT = """    <section class="tool-header">
      <h1>📊 Tabla Markdown</h1>
      <p>Genera tablas Markdown a partir de datos tabulares.</p>
    </section>

    <section class="tool-layout">
      <div class="editor-pane">
        <div class="pane-header">
          <h3>Datos de entrada</h3>
          <div class="pane-actions">
            <select id="inputFormat">
              <option value="tsv">Tab-separated</option>
              <option value="csv">CSV</option>
              <option value="json">JSON</option>
            </select>
            <button class="btn-sm" id="btnLoadExample">Ejemplo</button>
          </div>
        </div>
        <textarea id="dataInput" class="editor-textarea" placeholder="Pega datos tabulares aquí..."></textarea>
      </div>

      <div class="preview-pane">
        <div class="pane-header">
          <h3>Resultado</h3>
          <div class="pane-actions">
            <select id="alignment">
              <option value="left">Izquierda</option>
              <option value="center">Centro</option>
              <option value="right">Derecha</option>
            </select>
            <button class="btn-sm" id="btnCopy">Copiar</button>
          </div>
        </div>
        <div id="preview" class="preview-content"></div>
      </div>
    </section>"""

MDTOOLS_SNIPPETS_CONTENT = """    <section class="tool-header">
      <h1>✂️ Snippets de Código</h1>
      <p>Extrae y formatea fragmentos de código Markdown.</p>
    </section>

    <section class="tool-layout">
      <div class="editor-pane">
        <div class="pane-header">
          <h3>Markdown de entrada</h3>
          <div class="pane-actions">
            <button class="btn-sm" id="btnLoadExample">Ejemplo</button>
            <button class="btn-sm" id="btnClear">Limpiar</button>
          </div>
        </div>
        <textarea id="mdInput" class="editor-textarea" placeholder="Pega Markdown con bloques de código..."></textarea>
      </div>

      <div class="preview-pane">
        <div class="pane-header">
          <h3>Snippets extraídos</h3>
          <div class="pane-actions">
            <button class="btn-sm" id="btnCopyAll">Copiar todos</button>
          </div>
        </div>
        <div id="preview" class="preview-content"></div>
      </div>
    </section>"""

MDTOOLS_CHEATSHEET_CONTENT = """    <section class="tool-header">
      <h1>📋 Cheatsheet de Markdown</h1>
      <p>Referencia completa de syntax, emojis, shortcodes, HTML embebido y más.</p>
    </section>

    <section class="cheatsheet-grid">
      <div class="cheat-section">
        <h2>Encabezados</h2>
        <pre><code># H1
## H2
### H3
#### H4
##### H5
###### H6

H1 alternativo
==============

H2 alternativo
--------------</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Texto</h2>
        <pre><code>**negrita**
*cursiva*
***negrita y cursiva***
~~tachado~~
`código inline`
==resaltado==
_subíndice~2~_
super^índice^2^</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Listas</h2>
        <pre><code>- Elemento 1
- Elemento 2
  - Sub-elemento
  - Sub-elemento 2

1. Primero
2. Segundo
3. Tercero

* Elemento con asterisco
+ Elemento con más</code></pre>
      </div>

      <div class="cheat-section">
        <h2> Listas de Tareas</h2>
        <pre><code>- [x] Tarea completada
- [ ] Tarea pendiente
- [ ] Otra tarea

1. [x] Paso 1 hecho
2. [ ] Paso 2 pendiente</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Enlaces e Imágenes</h2>
        <pre><code>[texto](https://url.com)
[tooltip](https://url.com "título")
![alt](imagen.png)
![alt](imagen.png "tooltip")

 referencia: [ref][1]
 [1]: https://url.com

Enlace directo: &lt;https://url.com&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Tablas</h2>
        <pre><code>| Col 1 | Col 2 | Col 3 |
|-------|:-----:|------:|
| izq   | centro| derecha |
| celda | celda | celda  |

| Sin alinear |
|-------------|
| defecto     |</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Bloques de Código</h2>
        <pre><code>```python
def hello():
    print("Hello!")
```

    código con 4 espacios

```javascript
// código en línea
const x = 42;
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Citas</h2>
        <pre><code>&gt; Cita simple
&gt; multilinea

&gt; Cita con **formato**
&gt; y *cursiva*

&gt; Cita
&gt;&gt; Anidada</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Footnotes</h2>
        <pre><code>Texto con nota[^1].

Otra nota[^long].

[^1]: Nota al pie breve.
[^long]: Nota más extensa
    con varias líneas.</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Listas de Definición</h2>
        <pre><code>Término
: Definición del término

Otro término
: Primera definición
: Segunda definición</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Abreviaturas</h2>
        <pre><code>*[HTML]: HyperText Markup Language
*[CSS]: Cascading Style Sheets

Esto es HTML y esto es CSS.</code></pre>
      </div>

      <div class="cheat-section">
        <h2>HTML embebido</h2>
        <pre><code>&lt;sub&gt;subíndice&lt;/sub&gt;
&lt;sup&gt;superíndice&lt;/sup&gt;
&lt;mark&gt;resaltado&lt;/mark&gt;
&lt;kbd&gt;Ctrl&lt;/kbd&gt;+S
&lt;del&gt;eliminado&lt;/del&gt;
&lt;ins&gt;insertado&lt;/ins&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Bloques Expandibles</h2>
        <pre><code>&lt;details&gt;
&lt;summary&gt;Click para ver&lt;/summary&gt;

Contenido oculto aquí.

&lt;/details&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Math / LaTeX</h2>
        <pre><code>Inline: $E = mc^2$

Bloque:
$$
\\sum_{i=1}^{n} x_i = x_1 + x_2
$$

Fracción: $\\frac{a}{b}$</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Diagrams (Mermaid)</h2>
        <pre><code>```mermaid
graph LR
  A[Inicio] --> B{¿OK?}
  B -->|Sí| C[Fin]
  B -->|No| D[Error]
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Badges (Shields.io)</h2>
        <pre><code>![Badge](https://img.shields.io/badge/
  -label-color)

![Status](https://img.shields.io/
  badge/status-passing-brightgreen)

![Version](https://img.shields.io/
  badge/v1.0.0-blue)</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Alerts (GitHub)</h2>
        <pre><code>&gt; [!NOTE]
&gt; Nota informativa

&gt; [!TIP]
&gt; Consejo útil

&gt; [!WARNING]
&gt; Advertencia

&gt; [!CAUTION]
&gt; Precaución</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Horizontal Rule</h2>
        <pre><code>---
***
___

(Se recomienda usar ---)</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Escaping</h2>
        <pre><code>\\*no cursiva\\*
\\# no encabezado
\\[no link\\]
\\`no code\\`
\\{no brace\\}</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Emojis</h2>
        <pre><code>:rocket:  → 🚀    :fire:    → 🔥
:white_check_mark: → ✅
:warning: → ⚠️    :star:    → ⭐
:heart:   → ❤️    :bug:     → 🐛
:sparkles:→ ✨    :zap:     → ⚡
:trophy:  → 🏆    :bulb:    → 💡
:memo:    → 📝    :gear:    → ⚙️
:package: → 📦    :globe:   → 🌍</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Ancoras / Links internos</h2>
        <pre><code>## Mi Sección {#custom-id}

[Ir a sección](#mi-sección)
[Ir a custom](#custom-id)

Elemento con
scroll-margin-top</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Frontmatter (YAML)</h2>
        <pre><code>---
title: Mi Post
author: Jorge
date: 2026-08-09
tags: [markdown, tutorial]
draft: true
---

Contenido del post aquí.</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Colores (HTML)</h2>
        <pre><code>&lt;font color="red"&gt;Rojo&lt;/font&gt;
&lt;font color="#3b82f6"&gt;Azul&lt;/font&gt;
&lt;font color="rgb(34,197,94)"&gt;
  Verde
&lt;/font&gt;
&lt;span style="color:purple"&gt;
  Púrpura
&lt;/span&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Centrar / Alinear</h2>
        <pre><code>&lt;div align="center"&gt;

# Título centrado

[![Logo](img.png)](url)

&lt;/div&gt;

&lt;div align="right"&gt;
Texto a la derecha
&lt;/div&gt;

&lt;p align="left"&gt;
  Texto a la izquierda
&lt;/p&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Imágenes con tamaño</h2>
        <pre><code>&lt;img src="img.png" width="200"&gt;

&lt;img src="img.png"
     width="50%"
     alt="MIT License"&gt;

&lt;p align="center"&gt;
  &lt;img src="banner.png"
       width="80%"&gt;
&lt;/p&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Video / Audio embed</h2>
        <pre><code>&lt;video src="video.mp4"
       width="100%"
       controls&gt;
&lt;/video&gt;

&lt;iframe width="560"
  height="315"
  src="https://youtube.com/..."
  frameborder="0"
  allowfullscreen&gt;
&lt;/iframe&gt;

&lt;audio src="audio.mp3"
       controls&gt;
&lt;/audio&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Col layout (HTML)</h2>
        <pre><code>&lt;table&gt;&lt;tr&gt;
&lt;td width="50%"&gt;

### Columna 1
Contenido izquierda.

&lt;/td&gt;
&lt;td width="50%"&gt;

### Columna 2
Contenido derecha.

&lt;/td&gt;
&lt;/tr&gt;&lt;/table&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Superscript / Subscript</h2>
        <pre><code>H&lt;sub&gt;2&lt;/sub&gt;O
x&lt;sup&gt;2&lt;/sup&gt; + y&lt;sup&gt;2&lt;/sup&gt;
E = mc&lt;sup&gt;2&lt;/sup&gt;

X&lt;sup&gt;n&lt;/sup&gt; + Y&lt;sub&gt;n&lt;/sub&gt;

H&lt;sub&gt;2&lt;/sub&gt;SO&lt;sub&gt;4&lt;/sub&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Cita con atribución</h2>
        <pre><code>&gt; "El código es poesía."
&gt;
&gt; — **Autor Unknown**

---

&gt; "La simplicidad es la
&gt;  sofisticación suprema."
&gt;
&gt; — *Leonardo da Vinci*</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Tablas avanzadas</h2>
        <pre><code>| Feature | Status | Priority |
|:--------|:------:|----------:|
| Auth    | ✅ Done | 🔴 High  |
| API     | 🔄 WIP  | 🟡 Med   |
| Docs    | ⏳ Todo | 🟢 Low   |

| **Negrita** | *Cursiva* |
|:-----------:|:---------:|
| centrado    | centrado  |</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Keyboard / Kbd</h2>
        <pre><code>&lt;kbd&gt;Ctrl&lt;/kbd&gt;+&lt;kbd&gt;C&lt;/kbd&gt;
&lt;kbd&gt;Ctrl&lt;/kbd&gt;+&lt;kbd&gt;V&lt;/kbd&gt;
&lt;kbd&gt;Cmd&lt;/kbd&gt;+&lt;kbd&gt;Shift&lt;/kbd&gt;+P

&lt;kbd&gt;Alt&lt;/kbd&gt;+&lt;kbd&gt;F4&lt;/kbd&gt;
&lt;kbd&gt;F12&lt;/kbd&gt;
&lt;kbd&gt;Esc&lt;/kbd&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Progreso / Progress</h2>
        <pre><code>&lt;progress value="70"
          max="100"&gt;
  70%
&lt;/progress&gt;

█████████░░░░░ 70%
████████████░░ 90%
██░░░░░░░░░░░░ 15%</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Math símbolos</h2>
        <pre><code>∑ σ μ π θ λ Δ δ
∞ ≠ ≈ ≤ ≥ ± × ÷
√ ∛ ∫ ∬ ∂ ∇ ∝
∈ ∉ ⊂ ⊃ ∪ ∩ ∅
→ ← ↑ ↓ ↔ ⇒ ⇔</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Flechas y Símbolos</h2>
        <pre><code>→ ← ↑ ↓ ↔ ↕
⇒ ⇐ ⇑ ⇓ ⇔ ⇏
⟶ ⟵ ⟶ ⟵
↗ ↘ ↙ ↖ ↴ ↵
➤ ➜ ► ▸ ◆ ◇ ★ ☆
✓ ✗ ☑ ☐ ⬜ ⬛</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Bloques de código avanzados</h2>
        <pre><code>```python title="main.py"
# filename visible
def main():
    pass
```

```diff
- código eliminado
+ código agregado
  código sin cambio
```

```markdown
**esto es markdown**
dentro de un bloque
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Plantillas de Commit</h2>
        <pre><code>feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato
refactor: reestructurar
test: pruebas añadidas
chore: mantenimiento

feat(auth): login con OAuth
fix(api): timeout en requests
docs(readme): actualizar badges</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Markdown en la naturaleza</h2>
        <pre><code>GFM: GitHub Flavored MD
MDX: MD + JSX (componentes)
Astro: .mdx en content/
RST: reStructuredText (Python)
AsciiDoc: docs técnicas
Pandock: conversor universal

Extensiones comunes:
markdown-it, remark,Unified</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Recetas comunes</h2>
        <pre><code>Centrar imagen:
&lt;p align="center"&gt;
  &lt;img src="img.png"&gt;
&lt;/p&gt;

 Badge combo:
![![badge](url)][url2]

 separador y centrar:
&lt;div align="center"&gt;
  ---
&lt;/div&gt;</code></pre>
      </div>
    </section>"""

MDTOOLS_JS_CONFIG = """const MDTOOLS_CONFIG = {
  "TOOLS_BASE": "/mdtools",
  "DASHBOARD_URL": "https://jorbencasdownloaderdocument.surge.sh",
  "SLIDE_THEMES": ["default", "dark", "mono"],
  "PDF_PAGE_SIZES": ["a4", "letter", "legal"],
  "SNIPPET_LANGUAGES": ["python", "javascript", "typescript", "rust", "go", "java", "c", "html", "css", "sql", "bash"],
};"""
