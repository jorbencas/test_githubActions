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
      <a href="/mdtools/md.html" class="{active_md}">MD</a>
      <a href="/mdtools/cheatsheet.html" class="{active_cheatsheet}">MDX</a>
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
      <h1>📋 Cheatsheet de MDX</h1>
      <p>Referencia completa de MDX: Markdown + JSX, componentes, Astro y más.</p>
    </section>

    <section class="cheatsheet-grid">
      <div class="cheat-section">
        <h2>MDX vs Markdown</h2>
        <pre><code>MD = solo texto formateado
MDX = Markdown + JSX/React

// MDX permite:
import Componente from './Comp'
export const meta = { title: "Hi" }

# Esto es MDX
&lt;Componente nombre="Jorge" /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Imports en MDX</h2>
        <pre><code>import Button from '../components/Button'
import { Chart } from 'recharts'
import heroImg from './hero.png'

# Uso
&lt;Button color="blue"&gt;Click&lt;/Button&gt;

![Hero](heroImg)</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Exports en MDX</h2>
        <pre><code>export const metadata = {
  title: "Mi Post",
  author: "Jorge",
  date: "2026-08-09"
}

export function CustomPara({ children }) {
  return &lt;p className="fancy"&gt;{children}&lt;/p&gt;
}</code></pre>
      </div>

      <div class="cheat-section">
        <h2>JSX en Markdown</h2>
        <pre><code># Título con JSX

&lt;div className="alert"&gt;
  **Atención**: esto es JSX
&lt;/div&gt;

Texto normal con &lt;mark&gt;resaltado&lt;/mark&gt;

&lt;span style={{color: "red"&gt;
  Texto rojo
&lt;/span&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Componentes inline</h2>
        <pre><code>import Callout from '@/components/Callout'

&lt;Callout type="info"&gt;
  Esto es un callout informativo
&lt;/Callout&gt;

&lt;Callout type="warning"&gt;
  ¡Cuidado con esto!
&lt;/Callout&gt;

&lt;Callout emoji="🚀"&gt;
  Texto con emoji custom
&lt;/Callout&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Props en MDX</h2>
        <pre><code>import Card from './Card'

// Props como JSX
&lt;Card title="Mi post" /&gt;

// Props con children
&lt;Card title="Hola"&gt;
  Contenido del card
&lt;/Card&gt;

// Spread props
const props = { title: "Hi" }
&lt;Card {...props} /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Expresiones JS</h2>
        <pre><code>const items = ['A', 'B', 'C']

# Lista dinámica

{items.map(item =&gt; (
  &lt;li key={item}&gt;{item}&lt;/li&gt;
))}

# Condicional
{isDev && &lt;p&gt;Modo dev&lt;/p&gt;}

# Ternario
{user ? &lt;p&gt;Hola&lt;/p&gt; : &lt;p&gt;Bye&lt;/p&gt;}</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Componentes reutilizables</h2>
        <pre><code>// components/Button.tsx
export function Button({ children, color }) {
  return (
    &lt;button style={{
      background: color
    }}&gt;
      {children}
    &lt;/button&gt;
  )
}

// En MDX:
import { Button } from './Button'
&lt;Button color="#3b82f6"&gt;
  Click me
&lt;/Button&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Frontmatter (Astro)</h2>
        <pre><code>---
layout: ../../layouts/BlogPost.astro
title: "Mi Post MDX"
description: "Descripción"
pubDate: 2026-08-09
author: "Jorge"
tags: ["mdx", "astro"]
image: "/images/cover.png"
draft: false
---

# Contenido del post</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Layouts en Astro</h2>
        <pre><code>---
// Pagina.astro
import BlogPost from '../layouts/BlogPost.astro'
import Content from '../content/post.mdx'
---

&lt;BlogPost title="Mi Post"&gt;
  &lt;Content /&gt;
&lt;/BlogPost&gt;

// En MDX no necesitas layout
// Astro lo resuelve solo</code></pre>
      </div>

      <div class="cheat-section">
        <h2>HTML + MDX híbrido</h2>
        <pre><code># Markdown normal

&lt;div className="custom"&gt;
  ## JSX dentro de HTML
  - Lista dentro de div
  - **negrita** funciona
&lt;/div&gt;

# Vuelve Markdown normal

&lt;section id="seccion"&gt;
  &lt;h2&gt;Título JSX&lt;/h2&gt;
  &lt;p&gt;Párrafo normal&lt;/p&gt;
&lt;/section&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Clases y Estilos</h2>
        <pre><code># Con className (JSX)
&lt;div className="container"&gt;
  Texto
&lt;/div&gt;

# Con style object
&lt;p style={{fontSize: "1.2em",
           color: "#3b82f6"}}&gt;
  Texto azul grande
&lt;/p&gt;

# Tailwind en MDX
&lt;div className="flex gap-4 p-6"&gt;
  &lt;span className="text-blue-500"&gt;
    Tailwind funciona
  &lt;/span&gt;
&lt;/div&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Eventos en MDX</h2>
        <pre><code>import { useState } from 'react'

# Counter en MDX

export function Counter() {
  const [count, setCount] = useState(0)
  return (
    &lt;button onClick={() =&gt;
      setCount(c =&gt; c + 1)}&gt;
      Clicks: {count}
    &lt;/button&gt;
  )
}

&lt;Counter /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Tablas con componentes</h2>
        <pre><code>import Table from './Table'

const data = [
  { name: "React", stars: "220k" },
  { name: "Vue", stars: "208k" }
]

&lt;Table columns={["Name", "Stars"]}
        data={data} /&gt;

# O tabla Markdown normal
| Name | Stars |
|------|-------|
| React| 220k  |</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Imágenes en MDX</h2>
        <pre><code># Markdown normal
![Alt text](./image.png)

# Con componente Image (Astro)
import { Image } from 'astro:assets'
import hero from './hero.png'

&lt;Image src={hero}
       alt="Hero"
       width={800}
       quality="high" /&gt;

# HTML normal
&lt;img src="/img.png" width="100%" /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Code en MDX</h2>
        <pre><code># Código inline
Usa `npm install` para instalar

# Bloque de código
```jsx
function App() {
  return &lt;h1&gt;Hello&lt;/h1&gt;
}
```

# Code con título
```python title="app.py"
print("Hello MDX")
```

# Diff
```diff
- const old = "code"
+ const newer = "code"</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Remark / Rehype plugins</h2>
        <pre><code>// astro.config.mjs
import mdx from '@astrojs/mdx'

export default {
  integrations: [mdx()],
  markdown: {
    remarkPlugins: [],
    rehypePlugins: []
  }
}

// Plugins populares:
// remark-gfm (tablas, tasks)
// rehype-slug (ancoras)
// rehype-autolink-headings</code></pre>
      </div>

      <div class="cheat-section">
        <h2>MDX en Astro Content</h2>
        <pre><code>// src/content/config.ts
import { defineCollection } from 'astro:content'

const posts = defineCollection({
  type: 'content',
  schema: ({ z }) =&gt; ({
    title: z.string(),
    date: z.date(),
    tags: z.array(z.string())
  })
})

export const collections = { posts }</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Loop de posts (Astro)</h2>
        <pre><code>---
import { getCollection } from 'astro:content'
const posts = await getCollection('posts')
---

{posts.map(post =&gt; (
  &lt;article&gt;
    &lt;h2&gt;{post.data.title}&lt;/h2&gt;
    &lt;time&gt;{post.data.date}&lt;/time&gt;
    &lt;p&gt;{post.data.description}&lt;/p&gt;
    &lt;a href={`/blog/${post.slug}`}&gt;
      Leer más
    &lt;/a&gt;
  &lt;/article&gt;
))}</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Render MDX dinámico</h2>
        <pre><code>---
import { getEntry } from 'astro:content'
const entry = await getEntry('posts', 'mi-post')
const { Content } = await entry.render()
---

&lt;Content /&gt;

// Con props
const { Content } = await entry.render()
&lt;Content customProp="valor" /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>MDX con React islands</h2>
        <pre><code>---
import Counter from '../components/Counter'
import Chat from '../components/Chat'
---

# Mi post con interactividad

&lt;Counter client:load /&gt;

&lt;Chat client:visible /&gt;

# client directives:
// client:load    - carga inmediata
// client:visible - cuando es visible
// client:idle    - cuando idle
// client:only    - solo en cliente</code></pre>
      </div>

      <div class="cheat-section">
        <h2>MDX con Svelte</h2>
        <pre><code>---
import Alert from '../components/Alert.svelte'
---

# Post con Svelte

&lt;Alert type="info" /&gt;

// Svelte components en MDX
// funcionan igual que React

&lt;script&gt;
  let count = $state(0)
&lt;/script&gt;

&lt;button onclick={() =&gt; count++}&gt;
  Count: {count}
&lt;/button&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Patrones comunes MDX</h2>
        <pre><code>// Callout reutilizable
import { Callout } from 'components'

&lt;Callout type="tip"&gt;
  Consejo útil aquí
&lt;/Callout&gt;

// YouTube embed
import YouTube from 'astro-embed'

&lt;YouTube id="dQw4w9WgXcQ" /&gt;

// GitHub Gist
import Gist from 'gist-embed'

&lt;Gist gistId="user/id" /&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>MDX pitfalls</h2>
        <pre><code>// ❌ NO usar HTML entities
&lt;div&gt; &amp;lt; &amp;gt; &lt;/div&gt;

// ❌ NO mezclar JSX con MD
&lt;p&gt;**negrita**&lt;/p&gt; // no renderiza

// ✅ SÍ usar JSX para HTML
&lt;p&gt;&lt;strong&gt;texto&lt;/strong&gt;&lt;/p&gt;

// ✅ O Markdown fuera de JSX
**negrita**
&lt;div&gt;texto&lt;/div&gt;</code></pre>
      </div>
    </section>"""

MDTOOLS_MD_CONTENT = """    <section class="tool-header">
      <h1>📋 Cheatsheet de Markdown</h1>
      <p>Referencia completa de Markdown puro: syntax, tablas, listas, código y más.</p>
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

superíndice: x^2^
subíndice: H~2~O</code></pre>
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

* Con asterisco
+ Con más</code></pre>
      </div>

      <div class="cheat-section">
        <h2>✅ Listas de Tareas</h2>
        <pre><code>- [x] Tarea completada
- [ ] Tarea pendiente
- [ ] Otra tarea

1. [x] Paso 1 hecho
2. [ ] Paso 2 pendiente</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Enlaces</h2>
        <pre><code>[texto](https://url.com)
[tooltip](https://url.com "título")

 referencia: [ref][1]
 [1]: https://url.com

Enlace directo: &lt;https://url.com&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Imágenes</h2>
        <pre><code>![alt text](imagen.png)
![alt](imagen.png "tooltip")

Con tamaño (HTML):
&lt;img src="img.png" width="200"&gt;

Centrada:
&lt;p align="center"&gt;
  &lt;img src="img.png"&gt;
&lt;/p&gt;</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Tablas</h2>
        <pre><code>| Col 1 | Col 2 | Col 3 |
|-------|:-----:|------:|
| izq   | centro| derecha |
| celda | celda | celda  |

| Sin alinear |
|-------------|
| defecto     |

| Feature | Status |
|:--------|:------:|
| Auth    | ✅ Done |
| API     | 🔄 WIP  |</code></pre>
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
```

```diff
- código eliminado
+ código agregado
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Citas</h2>
        <pre><code>&gt; Cita simple
&gt; multilinea

&gt; Cita con **formato**
&gt; y *cursiva*

&gt; Cita
&gt;&gt; Anidada

&gt; "Autor"
&gt; — Nombre</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Horizontal Rule</h2>
        <pre><code>---
***
___

(Se recomienda usar ---)</code></pre>
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
        <h2>Definition Lists</h2>
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
*[MD]: Markdown

Esto es HTML con MD y CSS.</code></pre>
      </div>

      <div class="cheat-section">
        <h2>HTML embebido</h2>
        <pre><code>&lt;sub&gt;subíndice&lt;/sub&gt;
&lt;sup&gt;superíndice&lt;/sup&gt;
&lt;mark&gt;resaltado&lt;/mark&gt;
&lt;kbd&gt;Ctrl&lt;/kbd&gt;+S
&lt;del&gt;eliminado&lt;/del&gt;
&lt;ins&gt;insertado&lt;/ins&gt;
&lt;details&gt;&lt;summary&gt;Ver&lt;/summary&gt;
  Contenido
&lt;/details&gt;</code></pre>
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
        <h2>Escaping</h2>
        <pre><code>\\*no cursiva\\*
\\# no encabezado
\\[no link\\]
\\`no code\\`
\\{no brace\\}
\\(no paren\\)
\\|no pipe\\</code></pre>
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
:package: → 📦    :globe:   → 🌍
:rocket:  → 🚀    :tada:    → 🎉</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Badges (Shields.io)</h2>
        <pre><code>![Badge](https://img.shields.io/badge/
  -label-color)

![Status](https://img.shields.io/
  badge/status-passing-brightgreen)

![Version](https://img.shields.io/
  badge/v1.0.0-blue)

![License](https://img.shields.io/
  badge/license-MIT-blue)</code></pre>
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
        <h2>Math / LaTeX</h2>
        <pre><code>Inline: $E = mc^2$

Bloque:
$$
\\sum_{i=1}^{n} x_i = x_1 + x_2
$$

Fracción: $\\frac{a}{b}$
Raíz: $\\sqrt{x}$</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Mermaid Diagrams</h2>
        <pre><code>```mermaid
graph LR
  A[Inicio] --> B{¿OK?}
  B -->|Sí| C[Fin]
  B -->|No| D[Error]
```

```mermaid
pie title Lenguajes
  "JS" : 40
  "Python" : 30
  "Rust" : 20
```</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Anclas / Links internos</h2>
        <pre><code>## Mi Sección {#custom-id}

[Ir a sección](#mi-sección)
[Ir a custom](#custom-id)</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Frontmatter</h2>
        <pre><code>---
title: Mi Post
author: Jorge
date: 2026-08-09
tags: [markdown, tutorial]
draft: true
image: /cover.png
---

Contenido del post aquí.</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Símbolos y Flechas</h2>
        <pre><code>→ ← ↑ ↓ ↔ ↕
⇒ ⇐ ⇑ ⇓ ⇔ ⇏
↗ ↘ ↙ ↖ ↴ ↵
➤ ➜ ► ▸ ◆ ◇ ★ ☆
✓ ✗ ☑ ☐ ⬜ ⬛

∑ σ μ π θ λ Δ δ
∞ ≠ ≈ ≤ ≥ ± × ÷
√ ∛ ∫ ∬ ∂ ∇ ∝
∈ ∉ ⊂ ⊃ ∪ ∩ ∅</code></pre>
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
        <pre><code>&lt;progress value="70" max="100"&gt;
  70%
&lt;/progress&gt;

█████████░░░░░ 70%
████████████░░ 90%
██░░░░░░░░░░░░ 15%</code></pre>
      </div>

      <div class="cheat-section">
        <h2>Video / Audio</h2>
        <pre><code>&lt;video src="video.mp4"
       width="100%" controls&gt;
&lt;/video&gt;

&lt;iframe width="560" height="315"
  src="https://youtube.com/..."
  frameborder="0"
  allowfullscreen&gt;
&lt;/iframe&gt;

&lt;audio src="audio.mp3"
       controls&gt;
&lt;/audio&gt;</code></pre>
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
        <h2>Variantes de Markdown</h2>
        <pre><code>GFM: GitHub Flavored MD
  - Tablas, tasks, alerts
CommonMark: Estándar
MDX: MD + JSX (React/Astro)
RST: reStructuredText (Python)
AsciiDoc: docs técnicas
Pandoc: conversor universal

Editores: VS Code, Obsidian,
HackMD, Notion, Typora</code></pre>
      </div>
    </section>"""

MDTOOLS_JS_CONFIG = """const MDTOOLS_CONFIG = {
  "TOOLS_BASE": "/mdtools",
  "DASHBOARD_URL": "https://jorbencasdownloaderdocument.surge.sh",
  "SLIDE_THEMES": ["default", "dark", "mono"],
  "PDF_PAGE_SIZES": ["a4", "letter", "legal"],
  "SNIPPET_LANGUAGES": ["python", "javascript", "typescript", "rust", "go", "java", "c", "html", "css", "sql", "bash"],
};"""
