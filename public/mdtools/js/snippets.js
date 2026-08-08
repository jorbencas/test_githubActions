/* snippets.js: Extracción de snippets de código */
(function () {
  const mdInput = document.getElementById('mdInput');
  const preview = document.getElementById('preview');
  const btnLoadExample = document.getElementById('btnLoadExample');
  const btnClear = document.getElementById('btnClear');
  const btnCopyAll = document.getElementById('btnCopyAll');

  if (!mdInput) return;

  const parserWorker = new Worker('/mdtools/js/parser-worker.js');
  parserWorker.addEventListener('message', (e) => {
    if (e.data.id === 1) {
      const tmp = document.createElement('div');
      tmp.innerHTML = e.data.html;
      const pres = tmp.querySelectorAll('pre code');
      if (!pres.length) {
        preview.innerHTML = '<p class="output-placeholder">No se encontraron bloques de código.</p>';
        return;
      }
      let html = '';
      pres.forEach((code, i) => {
        const lang = (code.className.match(/language-(\w+)/) || [])[1] || '';
        const lines = code.textContent.split('\n');
        const numbered = lines.map((l, j) => `<span class="line-num">${String(j + 1).padStart(3)}</span> ${l.replace(/</g, '&lt;')}`).join('\n');
        html += `<div class="snippet-block">
          <div class="snippet-header"><span class="snippet-lang">${lang || 'code'}</span><span class="snippet-lines">${lines.length} líneas</span></div>
          <pre><code>${numbered}</code></pre>
        </div>`;
      });
      preview.innerHTML = html;
    }
  });

  function render() {
    const blocks = mdInput.value.match(/```[\s\S]*?```/g);
    if (!blocks) { preview.innerHTML = '<p class="output-placeholder">Pega Markdown con bloques de código.</p>'; return; }
    parserWorker.postMessage({ id: 1, markdown: mdInput.value });
  }

  mdInput.addEventListener('input', render);

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', () => {
      mdInput.value = `# Ejemplo de Snippets

\`\`\`python
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
\`\`\`

\`\`\`javascript
const greet = (name) => {
  console.log(\`¡Hola, \${name}!\`);
};
greet("Mundo");
\`\`\`

\`\`\`rust
fn main() {
    println!("¡Hola desde Rust!");
}
\`\`\``;
      render();
    });
  }

  if (btnClear) btnClear.addEventListener('click', () => { mdInput.value = ''; preview.innerHTML = ''; });

  if (btnCopyAll) {
    btnCopyAll.addEventListener('click', () => {
      const blocks = mdInput.value.match(/```[\s\S]*?```/g) || [];
      const allCode = blocks.map(b => b.replace(/```\w*\n?/g, '').replace(/```$/g, '').trim()).join('\n\n---\n\n');
      if (allCode) navigator.clipboard.writeText(allCode).then(() => { btnCopyAll.textContent = 'Copiado!'; setTimeout(() => btnCopyAll.textContent = 'Copiar todos', 1500); });
    });
  }
})();
