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

// Era definitions: colors, smoke colors, SVG patterns
const ERAS = [
  {
    name: 'mainframes', range: [1970, 1979],
    bg: '#1a1208', accent: '#d97706', accent2: '#92400e',
    smoke: [0.85, 0.45, 0.05], // RGB 0-1
    cardBg: 'rgba(30, 20, 5, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><rect x='10' y='10' width='60' height='40' rx='3' stroke='%23d97706' fill='none' opacity='0.06' stroke-width='1'/><line x1='20' y1='60' x2='60' y2='60' stroke='%23d97706' opacity='0.04' stroke-width='1'/><circle cx='25' cy='30' r='3' fill='%23d97706' opacity='0.05'/><circle cx='40' cy='30' r='3' fill='%23d97706' opacity='0.05'/><circle cx='55' cy='30' r='3' fill='%23d97706' opacity='0.05'/></svg>`
  },
  {
    name: 'pc-revolution', range: [1980, 1989],
    bg: '#0a0818', accent: '#a855f7', accent2: '#ec4899',
    smoke: [0.65, 0.33, 0.97],
    cardBg: 'rgba(15, 10, 30, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><rect x='15' y='15' width='50' height='35' rx='2' stroke='%23a855f7' fill='none' opacity='0.06' stroke-width='1'/><rect x='20' y='55' width='40' height='8' rx='1' stroke='%23a855f7' fill='none' opacity='0.04' stroke-width='1'/><rect x='25' y='22' width='30' height='18' fill='%23a855f7' opacity='0.03'/></svg>`
  },
  {
    name: 'internet-boom', range: [1990, 1999],
    bg: '#040f1a', accent: '#38bdf8', accent2: '#22d3ee',
    smoke: [0.22, 0.74, 0.97],
    cardBg: 'rgba(5, 15, 30, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><circle cx='40' cy='40' r='25' stroke='%2338bdf8' fill='none' opacity='0.05' stroke-width='1'/><circle cx='40' cy='40' r='15' stroke='%2338bdf8' fill='none' opacity='0.04' stroke-width='1'/><line x1='40' y1='15' x2='40' y2='65' stroke='%2338bdf8' opacity='0.03' stroke-width='1'/><line x1='15' y1='40' x2='65' y2='40' stroke='%2338bdf8' opacity='0.03' stroke-width='1'/></svg>`
  },
  {
    name: 'web2', range: [2000, 2009],
    bg: '#0f0a04', accent: '#f59e0b', accent2: '#f97316',
    smoke: [0.96, 0.62, 0.04],
    cardBg: 'rgba(20, 15, 5, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><rect x='10' y='20' width='25' height='25' rx='5' stroke='%23f59e0b' fill='none' opacity='0.06' stroke-width='1'/><rect x='45' y='20' width='25' height='25' rx='5' stroke='%23f59e0b' fill='none' opacity='0.06' stroke-width='1'/><rect x='28' y='45' width='25' height='25' rx='5' stroke='%23f59e0b' fill='none' opacity='0.06' stroke-width='1'/></svg>`
  },
  {
    name: 'mobile-cloud', range: [2010, 2019],
    bg: '#040f0a', accent: '#10b981', accent2: '#14b8a6',
    smoke: [0.06, 0.73, 0.51],
    cardBg: 'rgba(5, 20, 12, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><rect x='28' y='10' width='24' height='45' rx='4' stroke='%2310b981' fill='none' opacity='0.06' stroke-width='1'/><circle cx='40' cy='48' r='3' stroke='%2310b981' fill='none' opacity='0.04' stroke-width='1'/><path d='M20 65 Q40 55 60 65' stroke='%2310b981' fill='none' opacity='0.04' stroke-width='1'/></svg>`
  },
  {
    name: 'ai-era', range: [2020, 2025],
    bg: '#0a0418', accent: '#8b5cf6', accent2: '#6366f1',
    smoke: [0.55, 0.36, 0.97],
    cardBg: 'rgba(12, 5, 25, 0.88)',
    svg: `<svg xmlns='http://www.w3.org/2000/svg' width='80' height='80'><circle cx='40' cy='25' r='8' stroke='%238b5cf6' fill='none' opacity='0.06' stroke-width='1'/><circle cx='25' cy='50' r='8' stroke='%238b5cf6' fill='none' opacity='0.06' stroke-width='1'/><circle cx='55' cy='50' r='8' stroke='%238b5cf6' fill='none' opacity='0.06' stroke-width='1'/><line x1='40' y1='33' x2='25' y2='42' stroke='%238b5cf6' opacity='0.04' stroke-width='1'/><line x1='40' y1='33' x2='55' y2='42' stroke='%238b5cf6' opacity='0.04' stroke-width='1'/><line x1='25' y1='58' x2='55' y2='58' stroke='%238b5cf6' opacity='0.04' stroke-width='1'/></svg>`
  }
];

// Smoke particle class
class SmokeParticle {
  constructor(canvas, era) {
    this.canvas = canvas;
    this.reset(era, true);
  }

  reset(era, initial = false) {
    this.x = Math.random() * this.canvas.width;
    this.y = initial ? Math.random() * this.canvas.height : this.canvas.height + 20;
    this.size = Math.random() * 120 + 60;
    this.speedX = (Math.random() - 0.5) * 0.3;
    this.speedY = -(Math.random() * 0.4 + 0.15);
    this.opacity = Math.random() * 0.12 + 0.03;
    this.life = 0;
    this.maxLife = Math.random() * 400 + 200;
    const c = era.smoke;
    this.r = c[0]; this.g = c[1]; this.b = c[2];
  }

  update(era) {
    this.x += this.speedX;
    this.y += this.speedY;
    this.life++;
    this.speedX += (Math.random() - 0.5) * 0.02;

    const c = era.smoke;
    this.r += (c[0] - this.r) * 0.01;
    this.g += (c[1] - this.g) * 0.01;
    this.b += (c[2] - this.b) * 0.01;

    if (this.life > this.maxLife || this.y < -this.size) {
      this.reset(era);
    }
  }

  draw(ctx) {
    const progress = this.life / this.maxLife;
    const alpha = this.opacity * (progress < 0.2 ? progress / 0.2 : progress > 0.8 ? (1 - progress) / 0.2 : 1);
    const gradient = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
    gradient.addColorStop(0, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},${alpha})`);
    gradient.addColorStop(1, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},0)`);
    ctx.fillStyle = gradient;
    ctx.fillRect(this.x - this.size, this.y - this.size, this.size * 2, this.size * 2);
  }
}

class App {
  constructor() {
    this.container = document.getElementById('timeline-container');
    this.track = document.getElementById('timeline-track');
    this.yearDisplay = document.getElementById('year-display');
    this.yearBarInner = document.getElementById('year-bar-inner');
    this.yearBarDot = document.getElementById('year-bar-dot');
    this.scrollHint = document.getElementById('scroll-hint');
    this.loadingEl = document.getElementById('loading');
    this.bgGradient = document.getElementById('bg-gradient');
    this.fxCanvas = document.getElementById('fx-canvas');
    this.fxCtx = this.fxCanvas.getContext('2d');

    this.currentYear = YEAR_MIN;
    this.currentEra = ERAS[0];
    this.events = [];
    this.smokeParticles = [];

    this._resizeCanvas();
    this._initSmoke();
    this._bindScroll();
    this._startMusic();
    this._loadData();
    this._animate();

    window.addEventListener('resize', () => this._resizeCanvas());
  }

  _resizeCanvas() {
    this.fxCanvas.width = window.innerWidth;
    this.fxCanvas.height = window.innerHeight;
  }

  _initSmoke() {
    for (let i = 0; i < 25; i++) {
      this.smokeParticles.push(new SmokeParticle(this.fxCanvas, this.currentEra));
    }
  }

  _getEra(year) {
    for (const era of ERAS) {
      if (year >= era.range[0] && year <= era.range[1]) return era;
    }
    return ERAS[ERAS.length - 1];
  }

  _applyEra(era) {
    if (era === this.currentEra) return;
    this.currentEra = era;

    document.body.style.background = era.bg;
    document.documentElement.style.setProperty('--accent', era.accent);
    document.documentElement.style.setProperty('--accent2', era.accent2);
    document.documentElement.style.setProperty('--bg-card', era.cardBg);

    this.yearDisplay.style.color = era.accent;
    this.yearBarDot.style.background = era.accent;

    this.bgGradient.style.background = `
      radial-gradient(ellipse at 20% 50%, ${era.accent}15 0%, transparent 60%),
      radial-gradient(ellipse at 80% 30%, ${era.accent2}10 0%, transparent 50%)
    `;

    const headerGrad = `linear-gradient(180deg, ${era.bg} 40%, transparent 100%)`;
    document.getElementById('header').style.background = headerGrad;
    document.getElementById('year-bar').style.background = `linear-gradient(0deg, ${era.bg} 60%, transparent 100%)`;
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
      const ctx = new (window.AudioContext || window.webkitAudioContext)();
      this.audioCtx = ctx;

      const makeOsc = (freq, type, gainVal) => {
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = type; osc.frequency.value = freq;
        gain.gain.value = gainVal;
        osc.connect(gain); gain.connect(ctx.destination);
        osc.start();
        return { osc, gain };
      };

      makeOsc(55, 'sine', 0.022);
      makeOsc(82.5, 'sine', 0.015);
      makeOsc(110, 'sine', 0.01);

      const shimmer = makeOsc(330, 'triangle', 0.004);
      const lfo = ctx.createOscillator();
      const lfoG = ctx.createGain();
      lfo.type = 'sine'; lfo.frequency.value = 0.07;
      lfoG.gain.value = 0.003;
      lfo.connect(lfoG);
      lfoG.connect(shimmer.gain.gain);
      lfo.start();
    } catch (e) {}
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
      if (dist < closestDist) { closestDist = dist; closestYear = year; }
    });

    if (closestYear !== this.currentYear) {
      this.currentYear = closestYear;
      this.yearDisplay.textContent = closestYear;
      this.yearDisplay.classList.add('active');
      clearTimeout(this._yearTimeout);
      this._yearTimeout = setTimeout(() => this.yearDisplay.classList.remove('active'), 500);
      this._highlightYearTick(closestYear);
      this._applyEra(this._getEra(closestYear));
    }
  }

  _updateDot() {
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll <= 0) return;
    const progress = this.container.scrollLeft / maxScroll;
    const lineLeft = 40;
    const barWidth = window.innerWidth;
    const lineWidth = barWidth - 80;
    this.yearBarDot.style.left = `${lineLeft + progress * lineWidth}px`;
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

    card.innerHTML = `${imgHTML}<div class="card-body"><div class="card-category" style="background:${cat.bg};color:${cat.text}">${cat.emoji} ${event.category}</div><div class="card-title">${event.title}</div><div class="card-desc">${desc}</div>${link}</div>`;
    return card;
  }

  _buildTimeline() {
    this.track.innerHTML = '';
    const byYear = {};
    this.events.forEach(ev => {
      if (!byYear[ev.year]) byYear[ev.year] = [];
      byYear[ev.year].push(ev);
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

  _animate() {
    requestAnimationFrame(() => this._animate());
    const ctx = this.fxCtx;
    const w = this.fxCanvas.width;
    const h = this.fxCanvas.height;

    ctx.clearRect(0, 0, w, h);

    for (const p of this.smokeParticles) {
      p.update(this.currentEra);
      p.draw(ctx);
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
      this._applyEra(this._getEra(YEAR_MIN));

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
