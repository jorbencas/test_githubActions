/* table.js: Generación de tablas Markdown */
(function () {
  const dataInput = document.getElementById('dataInput');
  const preview = document.getElementById('preview');
  const btnLoadExample = document.getElementById('btnLoadExample');
  const btnCopy = document.getElementById('btnCopy');
  const inputFormat = document.getElementById('inputFormat');
  const alignment = document.getElementById('alignment');

  if (!dataInput) return;

  function parseInput(text, fmt) {
    const lines = text.trim().split('\n').filter(Boolean);
    if (!lines.length) return [];
    if (fmt === 'json') {
      try { return JSON.parse(text); } catch { return []; }
    }
    const sep = fmt === 'csv' ? ',' : '\t';
    return lines.map(line => line.split(sep).map(c => c.trim()));
  }

  function generateTable(data, align) {
    if (!data.length || !data[0].length) return '';
    const cols = data[0].length;
    const sep = align === 'center' ? ':---:' : align === 'right' ? '---:' : '---';
    const header = '| ' + data[0].join(' | ') + ' |';
    const divider = '| ' + Array(cols).fill(sep).join(' | ') + ' |';
    const rows = data.slice(1).map(r => '| ' + r.join(' | ') + ' |');
    return [header, divider, ...rows].join('\n');
  }

  function render() {
    const data = parseInput(dataInput.value, inputFormat?.value || 'tsv');
    const md = generateTable(data, alignment?.value || 'left');
    if (!md) { preview.innerHTML = '<p class="output-placeholder">Pega datos tabulares para generar una tabla.</p>'; return; }
    preview.innerHTML = `<pre style="white-space: pre-wrap; font-size: 0.85rem;">${md.replace(/</g, '&lt;').replace(/>/g, '&gt;')}</pre>
    <p style="margin-top: 12px; color: var(--text-muted); font-size: 0.8rem;">${data.length - 1} filas × ${data[0]?.length || 0} columnas</p>`;
    preview.dataset.markdown = md;
  }

  dataInput.addEventListener('input', render);

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', () => {
      dataInput.value = `Nombre\tTipo\tLenguaje\tEstrellas
React\tLibrería\tTypeScript\t220k
Next.js\tFramework\tTypeScript\t128k
Vue\tFramework\tJavaScript\t208k
Svelte\tFramework\tJavaScript\t82k
Astro\tFramework\tTypeScript\t49k`;
      render();
    });
  }

  if (btnCopy) {
    btnCopy.addEventListener('click', () => {
      const md = preview.dataset.markdown;
      if (md) navigator.clipboard.writeText(md).then(() => { btnCopy.textContent = 'Copiado!'; setTimeout(() => btnCopy.textContent = 'Copiar', 1500); });
    });
  }

  if (inputFormat) inputFormat.addEventListener('change', render);
  if (alignment) alignment.addEventListener('change', render);
})();
