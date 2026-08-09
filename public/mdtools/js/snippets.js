/* snippets.js: Extracción de snippets — sin Worker, directo */
(function () {
  'use strict';

  var mdInput = document.getElementById('mdInput');
  var preview = document.getElementById('preview');
  var btnLoadExample = document.getElementById('btnLoadExample');
  var btnClear = document.getElementById('btnClear');
  var btnCopyAll = document.getElementById('btnCopyAll');

  if (!mdInput || !preview) return;

  var md = null;

  function getMd() {
    if (md) return md;
    try {
      if (typeof markdownit === 'function') {
        md = markdownit({ html: true, linkify: true, typographer: true });
      } else if (window.markdownit) {
        md = window.markdownit({ html: true, linkify: true, typographer: true });
      } else {
        return null;
      }
      return md;
    } catch (e) {
      return null;
    }
  }

  function render() {
    var blocks = mdInput.value.match(/```[\s\S]*?```/g);
    if (!blocks) {
      preview.innerHTML = '<p class="output-placeholder">Pega Markdown con bloques de código.</p>';
      return;
    }

    var parser = getMd();
    if (!parser) {
      preview.innerHTML = '<p class="output-placeholder">⏳ Cargando parser…</p>';
      setTimeout(render, 200);
      return;
    }

    try {
      var html = parser.render(mdInput.value);
      var tmp = document.createElement('div');
      tmp.innerHTML = html;
      var pres = tmp.querySelectorAll('pre code');
      if (!pres.length) {
        preview.innerHTML = '<p class="output-placeholder">No se encontraron bloques de código.</p>';
        return;
      }
      var out = '';
      pres.forEach(function (code) {
        var lang = (code.className.match(/language-(\w+)/) || [])[1] || '';
        var lines = code.textContent.split('\n');
        var numbered = lines.map(function (l, j) {
          return '<span class="line-num">' + String(j + 1).padStart(3) + '</span> ' + l.replace(/</g, '&lt;');
        }).join('\n');
        out += '<div class="snippet-block">' +
          '<div class="snippet-header"><span class="snippet-lang">' + (lang || 'code') + '</span><span class="snippet-lines">' + lines.length + ' líneas</span></div>' +
          '<pre><code>' + numbered + '</code></pre></div>';
      });
      preview.innerHTML = out;
    } catch (e) {
      preview.innerHTML = '<p class="output-placeholder">Error: ' + e.message + '</p>';
    }
  }

  mdInput.addEventListener('input', render);

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', function () {
      mdInput.value = '# Ejemplo de Snippets\n\n```python\ndef fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)\n```\n\n```javascript\nconst greet = (name) => {\n  console.log(`¡Hola, ${name}!`);\n};\ngreet("Mundo");\n```\n\n```rust\nfn main() {\n    println!("¡Hola desde Rust!");\n}\n```';
      render();
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', function () {
      mdInput.value = '';
      preview.innerHTML = '';
    });
  }

  if (btnCopyAll) {
    btnCopyAll.addEventListener('click', function () {
      var blocks = mdInput.value.match(/```[\s\S]*?```/g) || [];
      var allCode = blocks.map(function (b) {
        return b.replace(/```\w*\n?/g, '').replace(/```$/g, '').trim();
      }).join('\n\n---\n\n');
      if (allCode) {
        navigator.clipboard.writeText(allCode).then(function () {
          btnCopyAll.textContent = 'Copiado!';
          setTimeout(function () { btnCopyAll.textContent = 'Copiar todos'; }, 1500);
        });
      }
    });
  }
})();
