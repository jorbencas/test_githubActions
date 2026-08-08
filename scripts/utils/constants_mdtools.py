MDTOOLS_NAV_HTML = """<nav class="main-nav" id="mainNav">
  <div class="nav-inner">
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
      <p>Referencia rápida de syntax, emojis, shortcodes y más.</p>
    </section>

    <section class="cheatsheet-grid">
      <div class="cheat-section">
        <h2>Encabezados</h2>
        <pre><code># H1
## H2
### H3
#### H4
##### H5
###### H6</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Texto</h2>
        <pre><code>**negrita**
*cursiva*
~~tachado~~
`código inline`
> bloque de cita</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Listas</h2>
        <pre><code>- Elemento 1
- Elemento 2
  - Sub-elemento

1. Primero
2. Segundo
3. Tercero</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Enlaces e Imágenes</h2>
        <pre><code>[texto](https://url.com)
![alt](imagen.png)
[tooltip](https://url.com "título")</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Tablas</h2>
        <pre><code>| Col 1 | Col 2 | Col 3 |
|-------|:-----:|------:|
| izq   | centro| derecha |</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Bloques de Código</h2>
        <pre><code>```python
def hello():
    print("Hello!")
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Emojis</h2>
        <pre><code>:rocket:  → 🚀
:fire:    → 🔥
:check:   → ✅
:warning: → ⚠️
:star:    → ⭐
:heart:   → ❤️
:bug:     → 🐛
:sparkles:→ ✨</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Horizontal Rule</h2>
        <pre><code>---
***
___</code></pre>
      </div>
    </section>"""

MDTOOLS_JS_CONFIG = """const MDTOOLS_CONFIG = {
  "TOOLS_BASE": "/mdtools",
  "DASHBOARD_URL": "http://jorbencasdownloaderdocument.surge.sh",
  "SLIDE_THEMES": ["default", "dark", "mono"],
  "PDF_PAGE_SIZES": ["a4", "letter", "legal"],
  "SNIPPET_LANGUAGES": ["python", "javascript", "typescript", "rust", "go", "java", "c", "html", "css", "sql", "bash"],
};"""
