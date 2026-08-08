/* parser-worker.js: markdown-it como Web Worker */
let md;
self.addEventListener('message', (e) => {
  const { id, markdown } = e.data;
  if (!md) {
    try {
      importScripts('https://cdnjs.cloudflare.com/ajax/libs/markdown-it/14.1.0/markdown-it.min.js');
      md = self.markdownit({ html: true, linkify: true, typographer: true });
    } catch (err) {
      self.postMessage({ id, html: '<p>Error al cargar el parser Markdown.</p>', error: true });
      return;
    }
  }
  try {
    self.postMessage({ id, html: md.render(markdown) });
  } catch (err) {
    self.postMessage({ id, html: '<p>Error al renderizar Markdown.</p>', error: true });
  }
});
