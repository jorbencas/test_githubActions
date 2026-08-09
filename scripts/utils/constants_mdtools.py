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
        <p>Referencia completa de Markdown y MDX con preview en vivo de cada ejemplo.</p>
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
      <h1>Cheatsheet de Markdown</h1>
      <p>Referencia completa de Markdown y MDX con preview en vivo.</p>
    </section>

    <section class="cheatsheet-grid" id="cheatsheet">

      <div class="cheat-item">
        <h3>Encabezados</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code># H1
## H2
### H3
#### H4
##### H5
###### H6</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Texto enriquecido</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>**negrita** y *cursiva*

***negrita y cursiva***

~~tachado~~  `código inline`

==resaltado==

superíndice: x^2^

subíndice: H~2~O</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Listas</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>- Elemento 1
- Elemento 2
  - Subelemento
  - Subelemento 2

1. Primero
2. Segundo
3. Tercero</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Tareas</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>- [x] Completado
- [ ] Pendiente
- [ ] Otra tarea</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Enlaces e Imágenes</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>[Google](https://google.com)

[Con tooltip](https://url.com "título")

![Logo](https://via.placeholder.com/120x60?text=Image)</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Tablas</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>| Lenguaje | Año | Tipo |
|----------|:---:|-----:|
| Python | 1991 | Script |
| Rust | 2015 | Systems |
| TypeScript | 2012 | JS+ |</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Código</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>```python
def greet(name):
    return f"Hello, {name}!"
```</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Citas</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&gt; Cita simple multilinea

&gt; Cita con **formato**

&gt; "Autor" — Nombre</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Horizontal Rule</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>Texto antes

---

Texto después</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Footnotes</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>Texto con nota[^1].

[^1]: Nota al pie breve.</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Definition Lists</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>Markdown
: Lenguaje de escritura ligero

HTML
: Lenguaje de marcado para web</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Emojis</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>:rocket: :fire: :tada: :star:

:white_check_mark: :warning: :bug:

:sparkles: :zap: :trophy: :bulb:

:memo: :gear: :package: :globe:</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Badges</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>![v1.0](https://img.shields.io/badge/version-1.0-blue)
![MIT](https://img.shields.io/badge/license-MIT-green)
![build](https://img.shields.io/badge/build-passing-brightgreen)</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Alerts (GitHub)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&gt; [!NOTE]
&gt; Información importante

&gt; [!TIP]
&gt; Consejo útil

&gt; [!WARNING]
&gt; Advertencia</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Anclas</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>## Mi Sección {#custom-id}

Ir a [sección](#mi-sección)

Ir a [custom](#custom-id)</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Frontmatter</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>---
title: Mi Post
author: Jorge
date: 2026-08-09
tags: [markdown, tutorial]
draft: false
---

Contenido del post aquí.</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Math / LaTeX</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>Inline: $E = mc^2$

Bloque:

$$
\\sum_{i=1}^{n} x_i
$$

Fracción: $\\frac{a}{b}$</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Mermaid</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>```mermaid
graph LR
  A[Inicio] --&gt; B{¿OK?}
  B --|Sí| C[Fin]
  B --|No| D[Error]
```</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Símbolos</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>→ ← ↑ ↓  ⇒ ⇐  ↗ ↘

✓ ✗ ☑ ☐  ★ ☆  ◆ ◇

∑ π θ λ  ∞ ≠ ≈  √ ∫</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>HTML embebido</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&lt;kbd&gt;Ctrl&lt;/kbd&gt;+&lt;kbd&gt;S&lt;/kbd&gt;

&lt;mark&gt;resaltado&lt;/mark&gt;

&lt;del&gt;eliminado&lt;/del&gt;

&lt;details&gt;
  &lt;summary&gt;Ver más&lt;/summary&gt;
  Contenido oculto aquí
&lt;/details&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Colores</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&lt;font color="red"&gt;Rojo&lt;/font&gt;

&lt;font color="#3b82f6"&gt;Azul&lt;/font&gt;

&lt;font color="rgb(34,197,94)"&gt;
  Verde
&lt;/font&gt;

&lt;span style="color:purple"&gt;
  Púrpura
&lt;/span&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Centrar / Alinear</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&lt;div align="center"&gt;

# Título centrado

![Logo](https://via.placeholder.com/80x30?text=Logo)

&lt;/div&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Progress</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>&lt;progress value="70" max="100"&gt;
  70%
&lt;/progress&gt;

█████████░░░░░ 70%

████████████░░ 90%</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Commit Conventional</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>feat: nueva funcionalidad
fix: corrección de bug
docs: documentación
style: formato
refactor: reestructurar
test: pruebas
chore: mantenimiento

feat(auth): login OAuth
fix(api): timeout requests</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Imports (MDX)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>import Componente from './Comp'
import { Image } from 'astro:assets'
import * as prismic from '@prismicio/client'

# Uso en el contenido

&lt;Componente prop="valor" /&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Exports (MDX)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>---
title: Mi post
---

export const metadata = {
  author: "Jorge"
}

function customFn() {
  return "usable en MDX"
}</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>JSX en MDX</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code># Texto normal

&lt;div style={{background:'#f0f0f0',padding:'1rem'}}&gt;
  Bloque JSX con estilo inline
&lt;/div&gt;

Más texto markdown aquí.</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Componentes (MDX)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>import { Callout } from '../components'

# Título del post

&lt;Callout type="tip"&gt;
  Este es un consejo útil
&lt;/Callout&gt;

Texto después del componente.</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Props (MDX)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>import Button from '../components/Button'

# Demo de props

&lt;Button
  text="Click me"
  color="blue"
  size="lg"
/&gt;

&lt;Button {...props} /&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Expresiones JS (MDX)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>import { items } from '../data'

# Lista dinámica

{items.map(item =&gt; (
  &lt;div key={item.id}&gt;
    {item.name} - {item.price}
  &lt;/div&gt;
))}

{items.length &gt; 0 &amp;&amp; (
  &lt;p&gt;Hay {items.length} elementos&lt;/p&gt;
)}</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Content Collections (Astro)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>// src/content/config.ts
import { defineCollection } from 'astro:content'

const posts = defineCollection({
  type: 'content',
  schema: ({ z }) =&gt; ({
    title: z.string(),
    date: z.date(),
    tags: z.array(z.string())
  })
})

export const collections = { posts }</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Loop de posts (Astro)</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>---
import { getCollection } from 'astro:content'
const posts = await getCollection('posts')
---

{posts.map(post =&gt; (
  &lt;article&gt;
    &lt;h2&gt;{post.data.title}&lt;/h2&gt;
    &lt;time&gt;{post.data.date}&lt;/time&gt;
    &lt;a href={`/blog/${post.slug}`}&gt;
      Leer más
    &lt;/a&gt;
  &lt;/article&gt;
))}</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>React Islands</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>---
import Counter from '../components/Counter'
---

# Mi post interactivo

&lt;Counter client:load /&gt;

// client:load    - inmediato
// client:visible - cuando visible
// client:idle    - cuando idle
// client:only    - solo cliente</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>Svelte en MDX</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>---
import Alert from '../components/Alert.svelte'
---

# Post con Svelte

&lt;Alert type="info" /&gt;

&lt;script&gt;
  let count = $state(0)
&lt;/script&gt;

&lt;button onclick={() =&gt; count++}&gt;
  Count: {count}
&lt;/button&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

      <div class="cheat-item">
        <h3>MDX Pitfalls</h3>
        <div class="cheat-row">
          <div class="cheat-code"><pre><code>// ❌ NO usar HTML entities
&lt;div&gt; &amp;lt; &amp;gt; &lt;/div&gt;

// ❌ NO mezclar JSX con MD
&lt;p&gt;**negrita**&lt;/p&gt;

// ✅ Sí usar JSX para HTML
&lt;p&gt;&lt;strong&gt;texto&lt;/strong&gt;&lt;/p&gt;

// ✅ O Markdown fuera de JSX
**negrita**
&lt;div&gt;texto&lt;/div&gt;</code></pre></div>
          <div class="cheat-preview md-preview" data-render></div>
        </div>
      </div>

    </section>"""

MDTOOLS_JS_CONFIG = """const MDTOOLS_CONFIG = {
  "TOOLS_BASE": "/mdtools",
  "DASHBOARD_URL": "https://jorbencasdownloaderdocument.surge.sh",
  "SLIDE_THEMES": ["default", "dark", "mono"],
  "PDF_PAGE_SIZES": ["a4", "letter", "legal"],
  "SNIPPET_LANGUAGES": ["python", "javascript", "typescript", "rust", "go", "java", "c", "html", "css", "sql", "bash"],
};"""
