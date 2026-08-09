/* slides.js: Presentaciones — sin Worker, directo */
(function () {
  'use strict';

  var mdInput = document.getElementById('mdInput');
  var preview = document.getElementById('preview');
  var btnLoadExample = document.getElementById('btnLoadExample');
  var btnClear = document.getElementById('btnClear');
  var btnPrev = document.getElementById('btnPrev');
  var btnNext = document.getElementById('btnNext');
  var btnFullscreen = document.getElementById('btnFullscreen');
  var btnDownload = document.getElementById('btnDownload');
  var slideCounter = document.getElementById('slideCounter');

  if (!mdInput || !preview) return;

  var slides = [];
  var current = 0;
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

  function parseAndRender() {
    var parser = getMd();
    if (!parser) {
      preview.innerHTML = '<div class="slide"><p>Cargando parser…</p></div>';
      setTimeout(parseAndRender, 200);
      return;
    }
    try {
      var html = parser.render(mdInput.value || '');
      slides = html.split(/<hr\s*\/?>/i).map(function (s) { return s.trim(); }).filter(Boolean);
      if (!slides.length) slides = ['<p>Escribe algo…</p>'];
    } catch (e) {
      slides = ['<p>Error al renderizar</p>'];
    }
    current = 0;
    renderSlide();
  }

  function renderSlide() {
    preview.innerHTML = '<div class="slide">' + slides[current] + '</div>';
    if (slideCounter) slideCounter.textContent = (current + 1) + ' / ' + slides.length;
  }

  if (btnPrev) btnPrev.addEventListener('click', function () { current = Math.max(0, current - 1); renderSlide(); });
  if (btnNext) btnNext.addEventListener('click', function () { current = Math.min(slides.length - 1, current + 1); renderSlide(); });
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', function () {
      if (preview.requestFullscreen) preview.requestFullscreen();
      else if (preview.webkitRequestFullscreen) preview.webkitRequestFullscreen();
    });
  }

  document.addEventListener('keydown', function (e) {
    if (e.target === mdInput) return;
    if (e.key === 'ArrowRight' || e.key === ' ') { current = Math.min(slides.length - 1, current + 1); renderSlide(); }
    if (e.key === 'ArrowLeft') { current = Math.max(0, current - 1); renderSlide(); }
  });

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', function () {
      mdInput.value = '# Bienvenido a Slides\n\nPresentación de ejemplo\n\n---\n\n## Diapositiva 2\n\n- Punto A\n- Punto B\n- Punto C\n\n---\n\n## Diapositiva 3\n\n> Cita inspiradora\n\nCódigo:\n\n```python\nprint("Hello Slides!")\n```';
      parseAndRender();
    });
  }

  if (btnClear) {
    btnClear.addEventListener('click', function () {
      mdInput.value = '';
      slides = [];
      current = 0;
      preview.innerHTML = '';
      if (slideCounter) slideCounter.textContent = '1 / 1';
    });
  }

  mdInput.addEventListener('input', parseAndRender);

  if (btnDownload) {
    btnDownload.addEventListener('click', function () {
      if (!slides.length) return;
      var allSlides = slides.map(function (s) {
        return '<section>' + s + '</section>';
      }).join('\n');
      var html = '<!DOCTYPE html>\n<html lang="es">\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n<title>Presentación</title>\n<style>\n*{margin:0;padding:0;box-sizing:border-box}\nbody{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;display:flex;align-items:center;justify-content:center;min-height:100vh}\n.slide{max-width:900px;width:90%;padding:40px 60px;background:#1e293b;border-radius:12px;min-height:400px;display:flex;flex-direction:column;justify-content:center}\n.slide h1,.slide h2,.slide h3{margin-bottom:16px}\n.slide h1{font-size:2.2rem;color:#3b82f6}\n.slide h2{font-size:1.6rem}\n.slide p,.slide li{font-size:1.1rem;line-height:1.6;margin-bottom:8px}\n.slide ul,.slide ol{padding-left:24px}\n.slide blockquote{border-left:3px solid #3b82f6;padding-left:16px;color:#94a3b8;margin:16px 0}\n.slide pre{background:#0f172a;padding:16px;border-radius:8px;overflow-x:auto;margin:12px 0}\n.slide code{font-family:monospace;font-size:0.9rem}\n.slide table{width:100%;border-collapse:collapse;margin:12px 0}\n.slide th,.slide td{border:1px solid #334155;padding:8px 12px;text-align:left}\n.slide th{background:#1e293b}\n</style>\n</head>\n<body>\n' + allSlides + '\n</body>\n</html>';
      var blob = new Blob([html], { type: 'text/html' });
      var url = URL.createObjectURL(blob);
      var a = document.createElement('a');
      a.href = url;
      a.download = 'presentacion.html';
      a.click();
      URL.revokeObjectURL(url);
    });
  }
})();
