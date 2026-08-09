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
})();
