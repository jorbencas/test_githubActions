/* cheatsheet.js — Render previews for cheatsheet items */
(function() {
  'use strict';

  const PREVIEWS = document.querySelectorAll('.md-preview[data-render]');
  if (!PREVIEWS.length) return;

  function getMd() {
    if (typeof markdownit === 'function') {
      return markdownit({ html: true, breaks: true, linkify: true, typographer: true });
    }
    if (window.markdownit) {
      return window.markdownit({ html: true, breaks: true, linkify: true, typographer: true });
    }
    return null;
  }

  function cleanCode(el) {
    const code = el.querySelector('code');
    if (!code) return '';
    let text = code.textContent;
    text = text.replace(/^```[\w]*\n?/, '').replace(/\n?```$/, '');
    return text.trim();
  }

  function renderAll() {
    const md = getMd();
    if (!md) {
      console.warn('cheatsheet.js: markdown-it not loaded');
      return;
    }

    PREVIEWS.forEach(function(preview) {
      const item = preview.closest('.cheat-item');
      if (!item) return;
      const codeBlock = item.querySelector('.cheat-code');
      if (!codeBlock) return;

      const raw = cleanCode(codeBlock);
      if (!raw) return;

      try {
        preview.innerHTML = md.render(raw);
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
