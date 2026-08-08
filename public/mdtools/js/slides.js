/* slides.js: Presentaciones desde Markdown */
(function () {
  const mdInput = document.getElementById('mdInput');
  const preview = document.getElementById('preview');
  const btnLoadExample = document.getElementById('btnLoadExample');
  const btnClear = document.getElementById('btnClear');
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnFullscreen = document.getElementById('btnFullscreen');
  const slideCounter = document.getElementById('slideCounter');

  if (!mdInput || !preview) return;

  let slides = [];
  let current = 0;

  const parserWorker = new Worker('/mdtools/js/parser-worker.js');
  parserWorker.addEventListener('message', (e) => {
    if (e.data.id === 0) {
      slides = e.data.html.split('<hr>').map(s => s.trim()).filter(Boolean);
      if (!slides.length) slides = ['<p>Escribe algo...</p>'];
      current = 0;
      renderSlide();
    }
  });

  function parseAndRender() {
    parserWorker.postMessage({ id: 0, markdown: mdInput.value });
  }

  function renderSlide() {
    preview.innerHTML = `<div class="slide">${slides[current]}</div>`;
    if (slideCounter) slideCounter.textContent = `${current + 1} / ${slides.length}`;
  }

  if (btnPrev) btnPrev.addEventListener('click', () => { current = Math.max(0, current - 1); renderSlide(); });
  if (btnNext) btnNext.addEventListener('click', () => { current = Math.min(slides.length - 1, current + 1); renderSlide(); });
  if (btnFullscreen) {
    btnFullscreen.addEventListener('click', () => {
      const el = preview;
      if (el.requestFullscreen) el.requestFullscreen();
      else if (el.webkitRequestFullscreen) el.webkitRequestFullscreen();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.target === mdInput) return;
    if (e.key === 'ArrowRight' || e.key === ' ') { current = Math.min(slides.length - 1, current + 1); renderSlide(); }
    if (e.key === 'ArrowLeft') { current = Math.max(0, current - 1); renderSlide(); }
  });

  if (btnLoadExample) {
    btnLoadExample.addEventListener('click', () => {
      mdInput.value = `# Bienvenido a Slides\n\nPresentación de ejemplo\n\n---\n\n## Diapositiva 2\n\n- Punto A\n- Punto B\n- Punto C\n\n---\n\n## Diapositiva 3\n\n> Cita inspiradora\n\nCódigo:\n\`\`\`python\nprint("Hello Slides!")\n\`\`\``;
      parseAndRender();
    });
  }

  if (btnClear) btnClear.addEventListener('click', () => { mdInput.value = ''; slides = []; current = 0; preview.innerHTML = ''; if (slideCounter) slideCounter.textContent = '1 / 1'; });

  mdInput.addEventListener('input', parseAndRender);
})();
