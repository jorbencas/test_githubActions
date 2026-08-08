/* pdf.js: Lógica de generación PDF */
(function () {
  const mdInput = document.getElementById('mdInput');
  const preview = document.getElementById('preview');
  const btnGenerate = document.getElementById('btnGenerate');
  const btnLoadExample = document.getElementById('btnLoadExample');
  const btnClear = document.getElementById('btnClear');
  const pdfOutput = document.getElementById('pdfOutput');
  const pdfTheme = document.getElementById('pdfTheme');

  if (!mdInput) return;

  let md = null;
  let pdfReady = false;

  function initMarkdown() {
    if (typeof window.markdownit !== 'undefined') {
      md = window.markdownit({ html: true, linkify: true, typographer: true });
      return true;
    }
    if (typeof self !== 'undefined' && typeof self.markdownit !== 'undefined') {
      md = self.markdownit({ html: true, linkify: true, typographer: true });
      return true;
    }
    return false;
  }

  function initPdfMake() {
    if (typeof pdfMake !== 'undefined') {
      pdfReady = true;
      return true;
    }
    return false;
  }

  function updatePreview() {
    if (!md && !initMarkdown()) {
      preview.innerHTML = '<p class="output-placeholder">Cargando parser Markdown...</p>';
      return;
    }
    try {
      preview.innerHTML = md.render(mdInput.value);
    } catch (err) {
      preview.innerHTML = '<p class="output-placeholder">Error al renderizar Markdown.</p>';
    }
  }

  mdInput.addEventListener('input', updatePreview);

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', () => {
      mdInput.value = `# Título Principal\n\n## Subtítulo\n\nPárrafo de ejemplo con **negrita** y *cursiva*.\n\n### Lista\n- Elemento 1\n- Elemento 2\n- Elemento 3\n\n### Tabla\n| Nombre | Tipo | Descripción |\n|--------|------|-------------|\n| Alpha  | Tool | Primera herramienta |\n| Beta   | Lib  | Librería util |\n| Gamma  | API  | Endpoint REST |\n\n### Código\n\`\`\`python\ndef hello():\n    print("¡Hola desde Markdown!")\n\`\`\`\n\n> Cita de ejemplo: "El código es poesía."`;
      updatePreview();
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', () => {
      mdInput.value = '';
      preview.innerHTML = '';
      pdfOutput.innerHTML = '<p class="output-placeholder">Haz clic en "Generar PDF" para ver el resultado.</p>';
    });
  }

  if (btnGenerate) {
    btnGenerate.addEventListener('click', () => {
      if (!initPdfMake()) {
        pdfOutput.innerHTML = '<p class="output-placeholder">pdfmake no se ha cargado. Verifica tu conexión a internet.</p>';
        return;
      }

      const theme = pdfTheme?.value || 'default';
      const colors = {
        default: { bg: '#ffffff', text: '#0f172a', accent: '#2563eb' },
        dark: { bg: '#0f172a', text: '#e2e8f0', accent: '#3b82f6' },
        mono: { bg: '#ffffff', text: '#1a1a1a', accent: '#333333' },
      }[theme];

      const lines = mdInput.value.split('\n');
      const content = [];
      let inCode = false;
      let codeBuffer = [];

      for (const line of lines) {
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
        if (line.startsWith('# ')) { content.push({ text: line.slice(2), style: 'h1', margin: [0, 16, 0, 8] }); }
        else if (line.startsWith('## ')) { content.push({ text: line.slice(3), style: 'h2', margin: [0, 12, 0, 6] }); }
        else if (line.startsWith('### ')) { content.push({ text: line.slice(4), style: 'h3', margin: [0, 8, 0, 4] }); }
        else if (line.startsWith('> ')) { content.push({ text: line.slice(2), style: 'quote', margin: [16, 4, 0, 4] }); }
        else if (line.startsWith('- ') || line.startsWith('* ')) { content.push({ text: '  •  ' + line.slice(2), margin: [8, 2, 0, 2] }); }
        else if (/^\d+\.\s/.test(line)) { content.push({ text: '  ' + line, margin: [8, 2, 0, 2] }); }
        else if (line.startsWith('|')) {
          const cells = line.split('|').filter(c => c.trim()).map(c => c.trim());
          if (!cells.some(c => /^[-:]+$/.test(c))) {
            content.push({ text: cells.join('  |  '), style: 'tableRow', margin: [0, 2, 0, 2] });
          }
        }
        else if (line.trim()) { content.push({ text: line, margin: [0, 4, 0, 4] }); }
      }

      const docDefinition = {
        content: [{ text: 'Documento Markdown', style: 'title', margin: [0, 0, 0, 20] }, ...content],
        defaultStyle: { color: colors.text, font: 'Roboto' },
        styles: {
          title: { fontSize: 22, bold: true, color: colors.accent },
          h1: { fontSize: 18, bold: true, color: colors.accent },
          h2: { fontSize: 15, bold: true },
          h3: { fontSize: 13, bold: true },
          code: { font: 'Courier', fontSize: 9, background: '#f1f5f9' },
          quote: { italics: true, color: '#64748b', margin: [20, 4, 0, 4] },
          tableRow: { font: 'Courier', fontSize: 9 },
        },
        info: { title: 'Documento Markdown' },
        pageMargins: [40, 40, 40, 40],
      };

      pdfOutput.innerHTML = '<p style="color: var(--text-muted); text-align: center;">Generando PDF...</p>';

      try {
        pdfMake.createPdf(docDefinition).download('documento.pdf');
        pdfOutput.innerHTML = '<p style="color: var(--accent); text-align: center;">✓ PDF descargado</p>';
      } catch (err) {
        pdfOutput.innerHTML = '<p style="color: #ef4444;">Error: ' + err.message + '</p>';
      }
    });
  }
})();
