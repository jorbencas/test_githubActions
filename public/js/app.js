const YEAR_MIN = 1970;
const YEAR_MAX = 2025;

const CAT_COLORS = {
  languages: { bg: '#0ea5e922', text: '#0ea5e9', emoji: '💻' },
  frameworks: { bg: '#8b5cf622', text: '#8b5cf6', emoji: '🛠️' },
  tools: { bg: '#10b98122', text: '#10b981', emoji: '🔧' },
  ai: { bg: '#f59e0b22', text: '#f59e0b', emoji: '🤖' },
  hardware: { bg: '#ef444422', text: '#ef4444', emoji: '🖥️' },
  internet: { bg: '#3b82f622', text: '#3b82f6', emoji: '🌐' },
  companies: { bg: '#ec489922', text: '#ec4899', emoji: '🏢' },
  opensource: { bg: '#14b8a622', text: '#14b8a6', emoji: '📖' },
  news: { bg: '#f9731622', text: '#f97316', emoji: '📰' },
};

const CAT_GRADIENTS = {
  languages: 'linear-gradient(135deg, #0ea5e9, #0369a1)',
  frameworks: 'linear-gradient(135deg, #8b5cf6, #6d28d9)',
  tools: 'linear-gradient(135deg, #10b981, #047857)',
  ai: 'linear-gradient(135deg, #f59e0b, #b45309)',
  hardware: 'linear-gradient(135deg, #ef4444, #991b1b)',
  internet: 'linear-gradient(135deg, #3b82f6, #1d4ed8)',
  companies: 'linear-gradient(135deg, #ec4899, #9d174d)',
  opensource: 'linear-gradient(135deg, #14b8a6, #0f766e)',
  news: 'linear-gradient(135deg, #f97316, #c2410c)',
};

class App {
  constructor() {
    this.container = document.getElementById('timeline-container');
    this.track = document.getElementById('timeline-track');
    this.yearDisplay = document.getElementById('year-display');
    this.yearBarInner = document.getElementById('year-bar-inner');
    this.scrollHint = document.getElementById('scroll-hint');
    this.loadingEl = document.getElementById('loading');

    this.currentYear = YEAR_MIN;
    this.events = [];

    this._bindScroll();
    this._bindButtons();
    this._loadData();
  }

  _bindScroll() {
    let scrollTimeout;
    this.container.addEventListener('scroll', () => {
      this._updateYearFromScroll();
      this._hideScrollHint();
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => this._highlightNearestYear(), 100);
    }, { passive: true });
  }

  _bindButtons() {
    const btnMusic = document.getElementById('btn-music');
    if (btnMusic) {
      btnMusic.addEventListener('click', (e) => {
        e.stopPropagation();
        this._toggleMusic(btnMusic);
      });
    }
  }

  _toggleMusic(btn) {
    if (!this.audioCtx) {
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      this._startAmbient();
      btn.classList.add('active');
    } else if (this.audioCtx.state === 'running') {
      this.audioCtx.suspend();
      btn.classList.remove('active');
    } else {
      this.audioCtx.resume();
      btn.classList.add('active');
    }
  }

  _startAmbient() {
    const ctx = this.audioCtx;
    const osc1 = ctx.createOscillator();
    const osc2 = ctx.createOscillator();
    const gain = ctx.createGain();
    const lfo = ctx.createOscillator();
    const lfoGain = ctx.createGain();

    osc1.type = 'sine'; osc1.frequency.value = 110;
    osc2.type = 'sine'; osc2.frequency.value = 165;
    lfo.type = 'sine'; lfo.frequency.value = 0.1;
    lfoGain.gain.value = 15;
    gain.gain.value = 0.03;

    lfo.connect(lfoGain);
    lfoGain.connect(osc1.frequency);
    osc1.connect(gain);
    osc2.connect(gain);
    gain.connect(ctx.destination);

    osc1.start(); osc2.start(); lfo.start();
  }

  _updateYearFromScroll() {
    const scrollLeft = this.container.scrollLeft;
    const containerWidth = this.container.clientWidth;
    const center = scrollLeft + containerWidth / 2;

    const groups = this.track.querySelectorAll('.year-group');
    let closestYear = YEAR_MIN;
    let closestDist = Infinity;

    groups.forEach(grp => {
      const rect = grp.getBoundingClientRect();
      const containerRect = this.container.getBoundingClientRect();
      const grpCenter = rect.left + rect.width / 2 - containerRect.left + scrollLeft;
      const dist = Math.abs(grpCenter - center);
      const year = parseInt(grp.dataset.year);
      if (dist < closestDist) {
        closestDist = dist;
        closestYear = year;
      }
    });

    if (closestYear !== this.currentYear) {
      this.currentYear = closestYear;
      this.yearDisplay.textContent = closestYear;
      this.yearDisplay.classList.add('active');
      clearTimeout(this._yearTimeout);
      this._yearTimeout = setTimeout(() => this.yearDisplay.classList.remove('active'), 600);
      this._highlightYearTick(closestYear);
    }
  }

  _highlightYearTick(year) {
    this.yearBarInner.querySelectorAll('.year-tick').forEach(t => {
      t.classList.toggle('active', parseInt(t.dataset.year) === year);
    });
  }

  _highlightNearestYear() {
    this._updateYearFromScroll();
  }

  _hideScrollHint() {
    if (this.scrollHint && !this.scrollHint.classList.contains('hidden')) {
      this.scrollHint.classList.add('hidden');
    }
  }

  _createCard(event) {
    const cat = CAT_COLORS[event.category] || CAT_COLORS.news;
    const gradient = CAT_GRADIENTS[event.category] || CAT_GRADIENTS.news;

    const card = document.createElement('div');
    card.className = 'card';

    let imgHTML;
    if (event.image) {
      imgHTML = `<img class="card-img" src="${event.image}" alt="${event.title}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'">`;
      imgHTML += `<div class="card-img-placeholder" style="display:none;background:${gradient}"><span>${cat.emoji}</span></div>`;
    } else {
      imgHTML = `<div class="card-img-placeholder" style="background:${gradient}"><span>${cat.emoji}</span></div>`;
    }

    const desc = event.description || '';
    const link = event.url ? `<a class="card-link" href="${event.url}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Saber más →</a>` : '';

    card.innerHTML = `
      ${imgHTML}
      <div class="card-body">
        <div class="card-category" style="background:${cat.bg};color:${cat.text}">${cat.emoji} ${event.category}</div>
        <div class="card-title">${event.title}</div>
        <div class="card-desc">${desc}</div>
        ${link}
      </div>
    `;

    return card;
  }

  _buildTimeline() {
    this.track.innerHTML = '';

    // Group events by year
    const byYear = {};
    this.events.forEach(ev => {
      const y = ev.year;
      if (!byYear[y]) byYear[y] = [];
      byYear[y].push(ev);
    });

    // Create year groups
    for (let year = YEAR_MIN; year <= YEAR_MAX; year++) {
      const yearEvents = byYear[year] || [];
      if (yearEvents.length === 0) continue;

      const group = document.createElement('div');
      group.className = 'year-group';
      group.dataset.year = year;

      const label = document.createElement('div');
      label.className = 'year-label';
      label.textContent = year;
      group.appendChild(label);

      const cardsRow = document.createElement('div');
      cardsRow.className = 'year-cards';

      yearEvents.sort((a, b) => (a.importance || 0) - (b.importance || 0));
      yearEvents.forEach(ev => {
        cardsRow.appendChild(this._createCard(ev));
      });

      group.appendChild(cardsRow);
      this.track.appendChild(group);
    }
  }

  _buildYearBar() {
    this.yearBarInner.innerHTML = '';
    for (let y = YEAR_MIN; y <= YEAR_MAX; y += 5) {
      const tick = document.createElement('div');
      tick.className = 'year-tick';
      tick.dataset.year = y;
      tick.textContent = y;
      tick.addEventListener('click', () => this._scrollToYear(y));
      this.yearBarInner.appendChild(tick);
    }
    if (YEAR_MAX % 5 !== 0) {
      const tick = document.createElement('div');
      tick.className = 'year-tick';
      tick.dataset.year = YEAR_MAX;
      tick.textContent = YEAR_MAX;
      tick.addEventListener('click', () => this._scrollToYear(YEAR_MAX));
      this.yearBarInner.appendChild(tick);
    }
  }

  _scrollToYear(year) {
    const grp = this.track.querySelector(`[data-year="${year}"]`);
    if (grp) {
      grp.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
    }
  }

  async _loadData() {
    try {
      const resp = await fetch('data/events.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      this.events = data.events || [];

      this._buildTimeline();
      this._buildYearBar();

      setTimeout(() => {
        this.loadingEl.classList.add('hidden');
      }, 400);
    } catch (err) {
      console.error('Failed to load events:', err);
      const sub = this.loadingEl.querySelector('.loader-sub');
      if (sub) {
        sub.textContent = 'Error al cargar. Reintentando...';
        sub.style.color = '#ef4444';
      }
      setTimeout(() => this._loadData(), 3000);
    }
  }
}

new App();
