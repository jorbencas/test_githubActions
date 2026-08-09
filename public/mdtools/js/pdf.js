/* pdf.js: Markdown a PDF — sin Worker, directo */
(function () {
  'use strict';

  const mdInput = document.getElementById('mdInput');
  const preview = document.getElementById('preview');
  const btnGenerate = document.getElementById('btnGenerate');
  const btnLoadExample = document.getElementById('btnLoadExample');
  const btnClear = document.getElementById('btnClear');
  const pdfOutput = document.getElementById('pdfOutput');
  const pdfTheme = document.getElementById('pdfTheme');
  const btnDownloadPdf = document.getElementById('btnDownloadPdf');

  if (!mdInput || !preview) return;

  let md = null;
  let lastDocDef = null;

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

  function updatePreview() {
    var parser = getMd();
    if (!parser) {
      preview.innerHTML = '<p class="output-placeholder">⏳ Cargando parser Markdown…</p>';
      setTimeout(updatePreview, 200);
      return;
    }
    try {
      preview.innerHTML = parser.render(mdInput.value || '');
    } catch (err) {
      preview.innerHTML = '<p class="output-placeholder">Error al renderizar: ' + err.message + '</p>';
    }
  }

  mdInput.addEventListener('input', updatePreview);

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', function () {
      mdInput.value = '# Título Principal\n\n## Subtítulo\n\nPárrafo de ejemplo con **negrita** y *cursiva*.\n\n### Lista\n- Elemento 1\n- Elemento 2\n- Elemento 3\n\n### Tabla\n| Nombre | Tipo | Descripción |\n|--------|------|-------------|\n| Alpha  | Tool | Primera herramienta |\n| Beta   | Lib  | Librería útil |\n| Gamma  | API  | Endpoint REST |\n\n### Código\n\n```python\ndef hello():\n    print("¡Hola desde Markdown!")\n```\n\n> Cita de ejemplo: "El código es poesía."';
      updatePreview();
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', function () {
      mdInput.value = '';
      preview.innerHTML = '';
      if (pdfOutput) pdfOutput.innerHTML = '<p class="output-placeholder">Haz clic en "Generar PDF" para ver el resultado.</p>';
    });
  }

  if (btnGenerate) {
    btnGenerate.addEventListener('click', function () {
      if (typeof pdfMake === 'undefined') {
        pdfOutput.innerHTML = '<p class="output-placeholder">⚠️ pdfmake no se ha cargado. Verifica tu conexión.</p>';
        return;
      }

      var theme = pdfTheme ? pdfTheme.value : 'default';
      var colors = {
        default: { bg: '#ffffff', text: '#0f172a', accent: '#2563eb' },
        dark: { bg: '#0f172a', text: '#e2e8f0', accent: '#3b82f6' },
        mono: { bg: '#ffffff', text: '#1a1a1a', accent: '#333333' }
      }[theme] || colors.default;

      var lines = mdInput.value.split('\n');
      var content = [];
      var inCode = false;
      var codeBuffer = [];

      for (var i = 0; i < lines.length; i++) {
        var line = lines[i];
        if (line.startsWith('```')) {
          if (inCode) {
            content.push({ text: codeBuffer.join('\n'), style: 'code', margin: [0, 4, 0, 8] });
            codeBuffer = [];
            inCode = false;
          } else {
            inCode = true;
          }
          continue;
        }
        if (inCode) { codeBuffer.push(line); continue; }
        if (line.startsWith('# ')) content.push({ text: line.slice(2), style: 'h1', margin: [0, 16, 0, 8] });
        else if (line.startsWith('## ')) content.push({ text: line.slice(3), style: 'h2', margin: [0, 12, 0, 6] });
        else if (line.startsWith('### ')) content.push({ text: line.slice(4), style: 'h3', margin: [0, 8, 0, 4] });
        else if (line.startsWith('> ')) content.push({ text: line.slice(2), style: 'quote', margin: [16, 4, 0, 4] });
        else if (line.startsWith('- ') || line.startsWith('* ')) content.push({ text: '  •  ' + line.slice(2), margin: [8, 2, 0, 2] });
        else if (/^\d+\.\s/.test(line)) content.push({ text: '  ' + line, margin: [8, 2, 0, 2] });
        else if (line.startsWith('|')) {
          var cells = line.split('|').filter(function (c) { return c.trim(); }).map(function (c) { return c.trim(); });
          if (!cells.some(function (c) { return /^[-:]+$/.test(c); })) {
            content.push({ text: cells.join('  |  '), style: 'tableRow', margin: [0, 2, 0, 2] });
          }
        }
        else if (line.trim()) content.push({ text: line, margin: [0, 4, 0, 4] });
      }

      var docDefinition = {
        content: [{ text: 'Documento Markdown', style: 'title', margin: [0, 0, 0, 20] }].concat(content),
        defaultStyle: { color: colors.text, font: 'Roboto' },
        styles: {
          title: { fontSize: 22, bold: true, color: colors.accent },
          h1: { fontSize: 18, bold: true, color: colors.accent },
          h2: { fontSize: 15, bold: true },
          h3: { fontSize: 13, bold: true },
          code: { font: 'Courier', fontSize: 9, background: '#f1f5f9' },
          quote: { italics: true, color: '#64748b', margin: [20, 4, 0, 4] },
          tableRow: { font: 'Courier', fontSize: 9 }
        },
        info: { title: 'Documento Markdown' },
        pageMargins: [40, 40, 40, 40]
      };

      pdfOutput.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Generando PDF…</p>';
      try {
        lastDocDef = docDefinition;
        pdfMake.createPdf(docDefinition).download('documento.pdf');
        pdfOutput.innerHTML = '<p style="color: var(--accent); text-align: center;">✓ PDF descargado</p>';
        if (btnDownloadPdf) btnDownloadPdf.style.display = '';
      } catch (err) {
        pdfOutput.innerHTML = '<p style="color: #ef4444;">Error: ' + err.message + '</p>';
      }
    });
  }

  if (btnDownloadPdf) {
    btnDownloadPdf.addEventListener('click', function () {
      if (!lastDocDef) return;
      try {
        pdfMake.createPdf(lastDocDef).download('documento.pdf');
      } catch (err) {}
    });
  }
})();
