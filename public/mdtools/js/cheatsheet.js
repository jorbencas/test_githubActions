/* cheatsheet.js: Preview en vivo — robusto */
(function () {
  'use strict';

  var PREVIEWS = document.querySelectorAll('.md-preview[data-render]');
  if (!PREVIEWS.length) return;

  var md = null;

  function getMd() {
    if (md) return md;
    try {
      if (typeof markdownit === 'function') {
        md = markdownit({ html: true, breaks: true, linkify: true, typographer: true });
      } else if (window.markdownit) {
        md = window.markdownit({ html: true, breaks: true, linkify: true, typographer: true });
      } else {
        return null;
      }
      return md;
    } catch (e) {
      return null;
    }
  }

  function cleanCode(el) {
    var code = el.querySelector('code');
    if (!code) return '';
    var text = code.textContent;
    text = text.replace(/^```[\w]*\n?/, '').replace(/\n?```$/, '');
    return text.trim();
  }

  function renderAll() {
    var parser = getMd();
    if (!parser) {
      setTimeout(renderAll, 200);
      return;
    }

    PREVIEWS.forEach(function (preview) {
      var item = preview.closest('.cheat-item');
      if (!item) return;
      var codeBlock = item.querySelector('.cheat-code');
      if (!codeBlock) return;

      var raw = cleanCode(codeBlock);
      if (!raw) return;

      try {
        preview.innerHTML = parser.render(raw);
      } catch (e) {
        preview.textContent = raw;
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderAll);
  } else {
    renderAll();
  }
})();
