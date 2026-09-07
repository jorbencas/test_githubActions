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
    this.yearBarDot = document.getElementById('year-bar-dot');
    this.scrollHint = document.getElementById('scroll-hint');
    this.loadingEl = document.getElementById('loading');
    this.bgLayer = document.getElementById('bg-layer');

    this.currentYear = YEAR_MIN;
    this.events = [];

    this._bindScroll();
    this._startMusic();
    this._loadData();
  }

  _bindScroll() {
    let scrollTimeout;
    this.container.addEventListener('scroll', () => {
      this._updateYearFromScroll();
      this._updateDot();
      this._hideScrollHint();
      clearTimeout(scrollTimeout);
      scrollTimeout = setTimeout(() => this._updateYearFromScroll(), 100);
    }, { passive: true });
  }

  _startMusic() {
    try {
      this.audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      const ctx = this.audioCtx;

      // Pad layer 1 - deep drone
      const osc1 = ctx.createOscillator();
      const gain1 = ctx.createGain();
      osc1.type = 'sine'; osc1.frequency.value = 55;
      gain1.gain.value = 0.025;
      osc1.connect(gain1); gain1.connect(ctx.destination);
      osc1.start();

      // Pad layer 2 - fifth
      const osc2 = ctx.createOscillator();
      const gain2 = ctx.createGain();
      osc2.type = 'sine'; osc2.frequency.value = 82.5;
      gain2.gain.value = 0.018;
      osc2.connect(gain2); gain2.connect(ctx.destination);
      osc2.start();

      // Pad layer 3 - octave
      const osc3 = ctx.createOscillator();
      const gain3 = ctx.createGain();
      osc3.type = 'sine'; osc3.frequency.value = 110;
      gain3.gain.value = 0.012;
      osc3.connect(gain3); gain3.connect(ctx.destination);
      osc3.start();

      // LFO for movement
      const lfo = ctx.createOscillator();
      const lfoGain = ctx.createGain();
      lfo.type = 'sine'; lfo.frequency.value = 0.05;
      lfoGain.gain.value = 8;
      lfo.connect(lfoGain);
      lfoGain.connect(osc1.frequency);
      lfoGain.connect(osc2.frequency);
      lfo.start();

      // High shimmer
      const osc4 = ctx.createOscillator();
      const gain4 = ctx.createGain();
      const filter = ctx.createBiquadFilter();
      osc4.type = 'triangle'; osc4.frequency.value = 440;
      filter.type = 'lowpass'; filter.frequency.value = 800; filter.Q.value = 2;
      gain4.gain.value = 0.006;
      osc4.connect(filter); filter.connect(gain4); gain4.connect(ctx.destination);
      osc4.start();

      // LFO for shimmer volume
      const lfo2 = ctx.createOscillator();
      const lfo2Gain = ctx.createGain();
      lfo2.type = 'sine'; lfo2.frequency.value = 0.08;
      lfo2Gain.gain.value = 0.004;
      lfo2.connect(lfo2Gain);
      lfo2Gain.connect(gain4.gain);
      lfo2.start();
    } catch (e) {
      console.warn('Audio failed:', e);
    }
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
      this._yearTimeout = setTimeout(() => this.yearDisplay.classList.remove('active'), 500);
      this._highlightYearTick(closestYear);
    }
  }

  _updateDot() {
    const scrollLeft = this.container.scrollLeft;
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll <= 0) return;

    const bar = document.querySelector('.year-bar');
    const barRect = bar.getBoundingClientRect();
    const lineLeft = 40;
    const lineRight = barRect.width - 40;
    const lineWidth = lineRight - lineLeft;

    const progress = scrollLeft / maxScroll;
    const dotX = lineLeft + progress * lineWidth;

    this.yearBarDot.style.left = `${dotX}px`;
  }

  _highlightYearTick(year) {
    this.yearBarInner.querySelectorAll('.year-tick').forEach(t => {
      t.classList.toggle('active', parseInt(t.dataset.year) === year);
    });
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

    const byYear = {};
    this.events.forEach(ev => {
      const y = ev.year;
      if (!byYear[y]) byYear[y] = [];
      byYear[y].push(ev);
    });

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
      yearEvents.forEach(ev => cardsRow.appendChild(this._createCard(ev)));

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
    if (grp) grp.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
  }

  async _loadData() {
    try {
      const resp = await fetch('data/events.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();
      this.events = data.events || [];

      this._buildTimeline();
      this._buildYearBar();

      setTimeout(() => this.loadingEl.classList.add('hidden'), 400);
    } catch (err) {
      console.error('Failed to load events:', err);
      const sub = this.loadingEl.querySelector('.loader-sub');
      if (sub) { sub.textContent = 'Error. Reintentando...'; sub.style.color = '#ef4444'; }
      setTimeout(() => this._loadData(), 3000);
    }
  }
}

new App();
