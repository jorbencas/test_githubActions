/**
 * Tech Pulse Dashboard — News Dashboard JavaScript
 * Renders news from JSON with lazy loading, infinite scroll, and filtering.
 */
(function () {
  'use strict';

  var BATCH_SIZE = 50;
  var NEWS_JSON_URL = '/data/news.json';

  var allNews = [];
  var filteredNews = [];
  var renderedCount = 0;
  var isLoading = false;
  var activeChannels = [];
  var dataLoaded = false;

  var newsList = document.getElementById('news-list');
  var newsLoading = document.getElementById('news-loading');
  var newsLoadMore = document.getElementById('news-load-more');
  var newsEnd = document.getElementById('news-end');
  var newsSearch = document.getElementById('news-search');
  var statsBar = document.getElementById('stats-bar');

  function esc(s) {
    if (!s) return '';
    var d = document.createElement('div');
    d.textContent = s;
    return d.innerHTML;
  }

  function formatDate(raw) {
    if (!raw) return '';
    try {
      var dt = new Date(raw);
      if (isNaN(dt)) return raw;
      var meses = ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'];
      return dt.getDate() + ' de ' + meses[dt.getMonth()] + ' de ' + dt.getFullYear();
    } catch (_) { return raw; }
  }

  function buildItemHTML(item) {
    var badgeTech = item.b === 'Tech' ? '<span class="badge-tech">Tech</span>' : '';
    var tipoBadge;
    if (item.o === 'rss') {
      tipoBadge = '<span class="badge-rss">&#x1F4E1; RSS</span>';
    } else if (item.tp === 'herramienta') {
      tipoBadge = '<span class="badge-tool">&#x1F527; Herramienta</span>';
    } else {
      tipoBadge = '<span class="badge-news">&#x1F4C4; Noticia</span>';
    }
    var fecha = formatDate(item.fp);

    return '<li class="news-item" data-source="' + esc(item.fn) + '" data-category="' + esc(item.c) + '" data-ts="' + esc(item.ts) + '">'
      + '<a href="' + esc(item.e) + '" target="_blank" rel="noopener">'
      + '<img class="favicon" src="' + esc(item.ic) + '" alt="' + esc(item.f) + '" width="20" height="20" loading="lazy">'
      + '<div class="news-text">'
      + '<span class="news-title">' + esc(item.t) + '</span>'
      + '<span class="news-meta">' + tipoBadge + badgeTech + esc(item.f) + ' &middot; ' + esc(fecha) + ' <span class="badge-cat">' + esc(item.c) + '</span></span>'
      + '</div></a></li>';
  }

  function renderBatch(start, count) {
    var fragment = document.createDocumentFragment();
    var end = Math.min(start + count, filteredNews.length);
    for (var i = start; i < end; i++) {
      var temp = document.createElement('div');
      temp.innerHTML = buildItemHTML(filteredNews[i]);
      if (temp.firstChild) fragment.appendChild(temp.firstChild);
    }
    return fragment;
  }

  function updateLoadMoreVisibility() {
    if (renderedCount >= filteredNews.length && filteredNews.length > 0) {
      newsLoadMore.style.display = 'none';
      newsEnd.style.display = 'block';
    } else if (renderedCount < filteredNews.length) {
      newsLoadMore.style.display = 'inline-block';
      newsEnd.style.display = 'none';
    }
  }

  function appendNews() {
    if (isLoading || renderedCount >= filteredNews.length) return;
    isLoading = true;
    newsLoading.style.display = 'block';
    newsLoadMore.style.display = 'none';

    setTimeout(function () {
      var fragment = renderBatch(renderedCount, BATCH_SIZE);
      newsList.appendChild(fragment);
      renderedCount += BATCH_SIZE;
      isLoading = false;
      newsLoading.style.display = 'none';
      updateLoadMoreVisibility();
    }, 80);
  }

  function resetAndRender() {
    newsList.innerHTML = '';
    renderedCount = 0;
    newsEnd.style.display = 'none';
    appendNews();
  }

  function applyFilters() {
    var query = newsSearch ? newsSearch.value.toLowerCase() : '';
    filteredNews = allNews.filter(function (item) {
      var matchesQuery = !query
        || (item.t && item.t.toLowerCase().indexOf(query) !== -1)
        || (item.f && item.f.toLowerCase().indexOf(query) !== -1)
        || (item.c && item.c.toLowerCase().indexOf(query) !== -1);

      var matchesChannel = activeChannels.length === 0
        || activeChannels.indexOf(item.fn) !== -1;

      return matchesQuery && matchesChannel;
    });

    updateStats();
    resetAndRender();
  }

  function updateStats() {
    if (!statsBar) return;
    var total = filteredNews.length;
    var techCount = 0;
    for (var i = 0; i < filteredNews.length; i++) {
      if (filteredNews[i].b === 'Tech') techCount++;
    }
    statsBar.innerHTML =
      '<div class="stat-card"><b>' + allNews.length + '</b><span>Total</span></div>'
      + '<div class="stat-card"><b>' + techCount + '</b><span>Tech</span></div>'
      + '<div class="stat-card"><b>' + total + '</b><span>Mostrando</span></div>';
  }

  // ── Load news JSON ──
  function loadNews() {
    if (dataLoaded) return;
    dataLoaded = true;
    newsLoading.style.display = 'block';

    fetch(NEWS_JSON_URL)
      .then(function (res) { return res.json(); })
      .then(function (data) {
        allNews = data;
        filteredNews = data.slice();
        updateStats();
        newsLoading.style.display = 'none';
        appendNews();
      })
      .catch(function (err) {
        console.error('Error loading news:', err);
        newsLoading.style.display = 'none';
        newsEnd.textContent = 'Error al cargar noticias.';
        newsEnd.style.display = 'block';
      });
  }

  // ── Theme toggle ──
  var themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    var savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    themeToggle.textContent = savedTheme === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';

    themeToggle.addEventListener('click', function () {
      var current = document.documentElement.getAttribute('data-theme');
      var next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
      localStorage.setItem('theme', next);
      themeToggle.textContent = next === 'dark' ? '\u2600\uFE0F' : '\uD83C\uDF19';
    });
  }

  // ── News search (debounced) ──
  if (newsSearch) {
    var searchTimer;
    newsSearch.addEventListener('input', function () {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(applyFilters, 200);
    });
  }

  // ── Channel chip filters ──
  var chipContainers = document.querySelectorAll('.chip-container');
  chipContainers.forEach(function (container) {
    var chips = container.querySelectorAll('.chip');
    chips.forEach(function (chip) {
      chip.addEventListener('click', function () {
        var channel = chip.dataset.channel;

        if (channel === 'all') {
          activeChannels = [];
          chips.forEach(function (c) { c.classList.remove('active'); });
          chip.classList.add('active');
        } else {
          var allBtn = container.querySelector('.chip[data-channel="all"]');
          if (allBtn) allBtn.classList.remove('active');
          chip.classList.toggle('active');
          activeChannels = [];
          chips.forEach(function (c) {
            if (c.classList.contains('active') && c.dataset.channel !== 'all') {
              activeChannels.push(c.dataset.channel);
            }
          });
          if (activeChannels.length === 0 && allBtn) {
            allBtn.classList.add('active');
          }
        }
        applyFilters();
      });
    });
  });

  // ── Load more button ──
  if (newsLoadMore) {
    newsLoadMore.addEventListener('click', function () {
      appendNews();
    });
  }

  // ── Infinite scroll with IntersectionObserver ──
  if ('IntersectionObserver' in window) {
    var scrollSentinel = document.createElement('div');
    scrollSentinel.id = 'scroll-sentinel';
    scrollSentinel.style.height = '1px';
    scrollSentinel.style.marginTop = '200px';
    newsList.parentNode.insertBefore(scrollSentinel, newsLoadMore);

    var scrollObserver = new IntersectionObserver(function (entries) {
      if (entries[0].isIntersecting && dataLoaded && !isLoading && renderedCount < filteredNews.length) {
        appendNews();
      }
    }, { rootMargin: '400px' });
    scrollObserver.observe(scrollSentinel);
  }

  // ── Video search ──
  var videoSearch = document.getElementById('video-search');
  if (videoSearch) {
    videoSearch.addEventListener('input', function (e) {
      var query = e.target.value.toLowerCase();
      document.querySelectorAll('.video-card').forEach(function (card) {
        var title = (card.querySelector('.video-title') || {}).textContent || '';
        var meta = (card.querySelector('.video-meta') || {}).textContent || '';
        var match = title.toLowerCase().indexOf(query) !== -1 || meta.toLowerCase().indexOf(query) !== -1;
        card.style.display = match ? '' : 'none';
      });
    });
  }

  // ── Multimedia tabs ──
  var multimediaTabs = document.querySelectorAll('#multimedia-tabs .chip');
  multimediaTabs.forEach(function (tab) {
    tab.addEventListener('click', function () {
      multimediaTabs.forEach(function (t) { t.classList.remove('active'); });
      tab.classList.add('active');
      var tabType = tab.dataset.tab;
      document.querySelectorAll('.video-card').forEach(function (card) {
        if (tabType === 'all') {
          card.style.display = '';
        } else {
          card.style.display = card.dataset.type === tabType ? '' : 'none';
        }
      });
    });
  });

  // ── GitHub filter ──
  var githubFilter = document.getElementById('github-filter');
  if (githubFilter) {
    githubFilter.addEventListener('input', function (e) {
      var query = e.target.value.toLowerCase();
      document.querySelectorAll('.github-item').forEach(function (item) {
        var name = (item.querySelector('.github-name') || {}).textContent || '';
        var desc = (item.querySelector('.github-desc') || {}).textContent || '';
        var lang = (item.dataset.lang || '').toLowerCase();
        var match = name.toLowerCase().indexOf(query) !== -1
          || desc.toLowerCase().indexOf(query) !== -1
          || lang.indexOf(query) !== -1;
        item.style.display = match ? '' : 'none';
      });
    });
  }

  // ── Smooth scroll ──
  document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
    anchor.addEventListener('click', function (e) {
      e.preventDefault();
      var target = document.querySelector(this.getAttribute('href'));
      if (target) target.scrollIntoView({ behavior: 'smooth' });
    });
  });

  // ── Image lazy loading fallback ──
  if ('IntersectionObserver' in window) {
    var imageObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          var img = entry.target;
          if (img.dataset.src) {
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
          }
          imageObserver.unobserve(img);
        }
      });
    });
    document.querySelectorAll('img[data-src]').forEach(function (img) {
      imageObserver.observe(img);
    });
  }

  // ── Init: load news on DOM ready ──
  loadNews();
})();
