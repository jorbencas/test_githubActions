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

const ERAS = [
  { name: 'mainframes', range: [1970, 1979], bg: '#1a1208', accent: '#d97706', accent2: '#92400e', smoke: [0.85, 0.45, 0.05], cardBg: 'rgba(30, 20, 5, 0.88)' },
  { name: 'pc-revolution', range: [1980, 1989], bg: '#0a0818', accent: '#a855f7', accent2: '#ec4899', smoke: [0.65, 0.33, 0.97], cardBg: 'rgba(15, 10, 30, 0.88)' },
  { name: 'internet-boom', range: [1990, 1999], bg: '#040f1a', accent: '#38bdf8', accent2: '#22d3ee', smoke: [0.22, 0.74, 0.97], cardBg: 'rgba(5, 15, 30, 0.88)' },
  { name: 'web2', range: [2000, 2009], bg: '#0f0a04', accent: '#f59e0b', accent2: '#f97316', smoke: [0.96, 0.62, 0.04], cardBg: 'rgba(20, 15, 5, 0.88)' },
  { name: 'mobile-cloud', range: [2010, 2019], bg: '#040f0a', accent: '#10b981', accent2: '#14b8a6', smoke: [0.06, 0.73, 0.51], cardBg: 'rgba(5, 20, 12, 0.88)' },
  { name: 'ai-era', range: [2020, 2025], bg: '#0a0418', accent: '#8b5cf6', accent2: '#6366f1', smoke: [0.55, 0.36, 0.97], cardBg: 'rgba(12, 5, 25, 0.88)' },
];

// Parallax decorative elements per era
const ERA_ELEMENTS = {
  mainframes: [
    { type: 'circle', x: 8, y: 20, size: 300, color: '#d97706', speed: 0.08 },
    { type: 'rect', x: 15, y: 65, size: 180, color: '#92400e', speed: 0.12 },
    { type: 'circle', x: 30, y: 35, size: 120, color: '#d97706', speed: 0.05 },
    { type: 'grid', x: 5, y: 80, size: 400, color: '#d97706', speed: 0.03 },
    { type: 'circle', x: 50, y: 15, size: 200, color: '#92400e', speed: 0.1 },
    { type: 'rect', x: 70, y: 70, size: 150, color: '#d97706', speed: 0.07 },
  ],
  'pc-revolution': [
    { type: 'monitor', x: 10, y: 25, size: 160, color: '#a855f7', speed: 0.09 },
    { type: 'circle', x: 25, y: 60, size: 250, color: '#ec4899', speed: 0.06 },
    { type: 'rect', x: 55, y: 20, size: 140, color: '#a855f7', speed: 0.11 },
    { type: 'circle', x: 75, y: 50, size: 180, color: '#ec4899', speed: 0.04 },
    { type: 'grid', x: 40, y: 75, size: 350, color: '#a855f7', speed: 0.02 },
  ],
  'internet-boom': [
    { type: 'circle', x: 5, y: 30, size: 280, color: '#38bdf8', speed: 0.07 },
    { type: 'globe', x: 20, y: 55, size: 200, color: '#22d3ee', speed: 0.1 },
    { type: 'circle', x: 45, y: 15, size: 160, color: '#38bdf8', speed: 0.04 },
    { type: 'wave', x: 60, y: 70, size: 500, color: '#22d3ee', speed: 0.03 },
    { type: 'circle', x: 80, y: 40, size: 220, color: '#38bdf8', speed: 0.08 },
  ],
  web2: [
    { type: 'rect', x: 8, y: 20, size: 200, color: '#f59e0b', speed: 0.06 },
    { type: 'circle', x: 30, y: 50, size: 260, color: '#f97316', speed: 0.09 },
    { type: 'rect', x: 50, y: 15, size: 150, color: '#f59e0b', speed: 0.04 },
    { type: 'grid', x: 65, y: 65, size: 380, color: '#f97316', speed: 0.02 },
    { type: 'circle', x: 85, y: 30, size: 190, color: '#f59e0b', speed: 0.07 },
  ],
  'mobile-cloud': [
    { type: 'phone', x: 10, y: 25, size: 130, color: '#10b981', speed: 0.1 },
    { type: 'circle', x: 25, y: 55, size: 240, color: '#14b8a6', speed: 0.05 },
    { type: 'cloud', x: 50, y: 18, size: 220, color: '#10b981', speed: 0.08 },
    { type: 'circle', x: 70, y: 60, size: 170, color: '#14b8a6', speed: 0.04 },
    { type: 'rect', x: 85, y: 35, size: 140, color: '#10b981', speed: 0.06 },
  ],
  'ai-era': [
    { type: 'brain', x: 8, y: 30, size: 200, color: '#8b5cf6', speed: 0.09 },
    { type: 'circle', x: 25, y: 55, size: 280, color: '#6366f1', speed: 0.04 },
    { type: 'neural', x: 50, y: 20, size: 300, color: '#8b5cf6', speed: 0.07 },
    { type: 'circle', x: 72, y: 50, size: 180, color: '#6366f1', speed: 0.06 },
    { type: 'rect', x: 88, y: 70, size: 160, color: '#8b5cf6', speed: 0.11 },
  ],
};

class SmokeParticle {
  constructor(canvas, era) { this.canvas = canvas; this.reset(era, true); }
  reset(era, initial = false) {
    this.x = Math.random() * this.canvas.width;
    this.y = initial ? Math.random() * this.canvas.height : this.canvas.height + 20;
    this.size = Math.random() * 120 + 60;
    this.speedX = (Math.random() - 0.5) * 0.3;
    this.speedY = -(Math.random() * 0.4 + 0.15);
    this.opacity = Math.random() * 0.12 + 0.03;
    this.life = 0;
    this.maxLife = Math.random() * 400 + 200;
    const c = era.smoke; this.r = c[0]; this.g = c[1]; this.b = c[2];
  }
  update(era) {
    this.x += this.speedX; this.y += this.speedY; this.life++;
    this.speedX += (Math.random() - 0.5) * 0.02;
    const c = era.smoke;
    this.r += (c[0] - this.r) * 0.01;
    this.g += (c[1] - this.g) * 0.01;
    this.b += (c[2] - this.b) * 0.01;
    if (this.life > this.maxLife || this.y < -this.size) this.reset(era);
  }
  draw(ctx) {
    const p = this.life / this.maxLife;
    const a = this.opacity * (p < 0.2 ? p / 0.2 : p > 0.8 ? (1 - p) / 0.2 : 1);
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
    g.addColorStop(0, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},${a})`);
    g.addColorStop(1, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},0)`);
    ctx.fillStyle = g;
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
    this.parallaxBack = document.getElementById('parallax-back');
    this.parallaxMid = document.getElementById('parallax-mid');
    this.parallaxFront = document.getElementById('parallax-front');

    this.currentYear = YEAR_MIN;
    this.currentEra = ERAS[0];
    this.events = [];
    this.smokeParticles = [];
    this.parallaxEls = { back: [], mid: [], front: [] };
    this.scrollLeft = 0;
    this.targetScrollLeft = 0;

    this._resizeCanvas();
    this._initSmoke();
    this._buildParallaxElements(ERAS[0]);
    this._bindScroll();
    this._startMusic();
    this._loadData();
    this._animate();

    window.addEventListener('resize', () => {
      this._resizeCanvas();
      this._rebuildParallax();
    });
  }

  _resizeCanvas() {
    this.fxCanvas.width = window.innerWidth;
    this.fxCanvas.height = window.innerHeight;
  }

  _initSmoke() {
    for (let i = 0; i < 25; i++) this.smokeParticles.push(new SmokeParticle(this.fxCanvas, this.currentEra));
  }

  _getEra(year) {
    for (const era of ERAS) { if (year >= era.range[0] && year <= era.range[1]) return era; }
    return ERAS[ERAS.length - 1];
  }

  _buildParallaxElements(era) {
    [this.parallaxBack, this.parallaxMid, this.parallaxFront].forEach(el => el.innerHTML = '');
    this.parallaxEls = { back: [], mid: [], front: [] };

    const elems = ERA_ELEMENTS[era.name] || [];
    const layers = [this.parallaxBack, this.parallaxMid, this.parallaxFront];
    const layerNames = ['back', 'mid', 'front'];

    elems.forEach((el, i) => {
      const layerIdx = el.speed < 0.05 ? 0 : el.speed < 0.08 ? 1 : 2;
      const layer = layers[layerIdx];
      const name = layerNames[layerIdx];

      const div = document.createElement('div');
      div.className = 'parallax-el';
      div.dataset.speed = el.speed;
      div.dataset.baseX = el.x;
      div.style.left = `${el.x}%`;
      div.style.top = `${el.y}%`;
      div.style.width = `${el.size}px`;
      div.style.height = `${el.size}px`;

      const svg = this._createParallaxSVG(el);
      div.innerHTML = svg;
      layer.appendChild(div);
      this.parallaxEls[name].push(div);
    });
  }

  _createParallaxSVG(el) {
    const s = el.size;
    const c = el.color;
    const opacity = 0.06;
    switch (el.type) {
      case 'circle':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><circle cx="${s/2}" cy="${s/2}" r="${s/2-2}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
      case 'rect':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><rect x="4" y="4" width="${s-8}" height="${s-8}" rx="6" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
      case 'grid':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">${Array.from({length:5},(_,i)=>`<line x1="${(i+1)*s/6}" y1="0" x2="${(i+1)*s/6}" y2="${s}" stroke="${c}" opacity="${opacity*0.5}" stroke-width="0.5"/>`).join('')}${Array.from({length:5},(_,i)=>`<line x1="0" y1="${(i+1)*s/6}" x2="${s}" y2="${(i+1)*s/6}" stroke="${c}" opacity="${opacity*0.5}" stroke-width="0.5"/>`).join('')}</svg>`;
      case 'monitor':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><rect x="${s*0.1}" y="${s*0.05}" width="${s*0.8}" height="${s*0.55}" rx="4" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1.5"/><rect x="${s*0.35}" y="${s*0.62}" width="${s*0.3}" height="${s*0.1}" stroke="${c}" fill="none" opacity="${opacity*0.6}" stroke-width="1"/><line x1="${s*0.25}" y1="${s*0.75}" x2="${s*0.75}" y2="${s*0.75}" stroke="${c}" opacity="${opacity*0.4}" stroke-width="1"/></svg>`;
      case 'globe':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><circle cx="${s/2}" cy="${s/2}" r="${s/2-4}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/><ellipse cx="${s/2}" cy="${s/2}" rx="${s*0.2}" ry="${s/2-4}" stroke="${c}" fill="none" opacity="${opacity*0.5}" stroke-width="0.8"/><line x1="4" y1="${s/2}" x2="${s-4}" y2="${s/2}" stroke="${c}" opacity="${opacity*0.4}" stroke-width="0.8"/></svg>`;
      case 'wave':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.3}"><path d="M0 ${s*0.15} Q${s*0.125} ${s*0.05} ${s*0.25} ${s*0.15} T${s*0.5} ${s*0.15} T${s*0.75} ${s*0.15} T${s} ${s*0.15}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
      case 'phone':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.5}" height="${s}"><rect x="2" y="2" width="${s*0.5-4}" height="${s-4}" rx="8" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1.5"/><line x1="${s*0.2}" y1="${s-12}" x2="${s*0.3}" y2="${s-12}" stroke="${c}" opacity="${opacity*0.5}" stroke-width="1"/></svg>`;
      case 'cloud':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.6}"><path d="M${s*0.2} ${s*0.4} Q${s*0.1} ${s*0.4} ${s*0.1} ${s*0.3} Q${s*0.1} ${s*0.15} ${s*0.25} ${s*0.15} Q${s*0.3} ${s*0.05} ${s*0.5} ${s*0.05} Q${s*0.7} ${s*0.05} ${s*0.75} ${s*0.15} Q${s*0.9} ${s*0.15} ${s*0.9} ${s*0.3} Q${s*0.9} ${s*0.4} ${s*0.8} ${s*0.4} Z" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
      case 'brain':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><path d="M${s*0.5} ${s*0.15} Q${s*0.3} ${s*0.1} ${s*0.25} ${s*0.25} Q${s*0.15} ${s*0.3} ${s*0.2} ${s*0.45} Q${s*0.15} ${s*0.6} ${s*0.3} ${s*0.65} Q${s*0.4} ${s*0.75} ${s*0.5} ${s*0.8}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/><path d="M${s*0.5} ${s*0.15} Q${s*0.7} ${s*0.1} ${s*0.75} ${s*0.25} Q${s*0.85} ${s*0.3} ${s*0.8} ${s*0.45} Q${s*0.85} ${s*0.6} ${s*0.7} ${s*0.65} Q${s*0.6} ${s*0.75} ${s*0.5} ${s*0.8}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
      case 'neural':
        const nodes = Array.from({length:8}, () => [Math.random()*s*0.8+s*0.1, Math.random()*s*0.8+s*0.1]);
        const lines = [];
        for (let i = 0; i < nodes.length; i++) for (let j = i+1; j < nodes.length; j++) {
          const dx = nodes[i][0]-nodes[j][0], dy = nodes[i][1]-nodes[j][1];
          if (Math.sqrt(dx*dx+dy*dy) < s*0.5) lines.push(`<line x1="${nodes[i][0]}" y1="${nodes[i][1]}" x2="${nodes[j][0]}" y2="${nodes[j][1]}" stroke="${c}" opacity="${opacity*0.6}" stroke-width="0.5"/>`);
        }
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">${lines.join('')}${nodes.map(([x,y])=>`<circle cx="${x}" cy="${y}" r="3" fill="${c}" opacity="${opacity}"/>`).join('')}</svg>`;
      default:
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><circle cx="${s/2}" cy="${s/2}" r="${s/2-2}" stroke="${c}" fill="none" opacity="${opacity}" stroke-width="1"/></svg>`;
    }
  }

  _rebuildParallax() {
    this._buildParallaxElements(this.currentEra);
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
    this.bgGradient.style.background = `radial-gradient(ellipse at 20% 50%, ${era.accent}15 0%, transparent 60%), radial-gradient(ellipse at 80% 30%, ${era.accent2}10 0%, transparent 50%)`;
    document.getElementById('header').style.background = `linear-gradient(180deg, ${era.bg} 40%, transparent 100%)`;
    document.getElementById('year-bar').style.background = `linear-gradient(0deg, ${era.bg} 60%, transparent 100%)`;

    // Rebuild parallax for new era
    this._buildParallaxElements(era);
  }

  _bindScroll() {
    let scrollTimeout;
    this.container.addEventListener('scroll', () => {
      this.scrollLeft = this.container.scrollLeft;
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
      const makeOsc = (freq, type, gainVal) => {
        const osc = ctx.createOscillator(); const gain = ctx.createGain();
        osc.type = type; osc.frequency.value = freq; gain.gain.value = gainVal;
        osc.connect(gain); gain.connect(ctx.destination); osc.start();
        return { osc, gain };
      };
      makeOsc(55, 'sine', 0.022);
      makeOsc(82.5, 'sine', 0.015);
      makeOsc(110, 'sine', 0.01);
      const shimmer = makeOsc(330, 'triangle', 0.004);
      const lfo = ctx.createOscillator(); const lfoG = ctx.createGain();
      lfo.type = 'sine'; lfo.frequency.value = 0.07; lfoG.gain.value = 0.003;
      lfo.connect(lfoG); lfoG.connect(shimmer.gain.gain); lfo.start();
    } catch (e) {}
  }

  _updateYearFromScroll() {
    const containerWidth = this.container.clientWidth;
    const center = this.scrollLeft + containerWidth / 2;
    const groups = this.track.querySelectorAll('.year-group');
    let closestYear = YEAR_MIN, closestDist = Infinity;

    groups.forEach(grp => {
      const rect = grp.getBoundingClientRect();
      const containerRect = this.container.getBoundingClientRect();
      const grpCenter = rect.left + rect.width / 2 - containerRect.left + this.scrollLeft;
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
    const progress = this.scrollLeft / maxScroll;
    const lineWidth = window.innerWidth - 80;
    this.yearBarDot.style.left = `${40 + progress * lineWidth}px`;
  }

  _highlightYearTick(year) {
    this.yearBarInner.querySelectorAll('.year-tick').forEach(t => {
      t.classList.toggle('active', parseInt(t.dataset.year) === year);
    });
  }

  _hideScrollHint() {
    if (this.scrollHint && !this.scrollHint.classList.contains('hidden')) this.scrollHint.classList.add('hidden');
  }

  _createCard(event) {
    const cat = CAT_COLORS[event.category] || CAT_COLORS.news;
    const gradient = CAT_GRADIENTS[event.category] || CAT_GRADIENTS.news;
    const card = document.createElement('div');
    card.className = 'card';
    let imgHTML;
    if (event.image) {
      imgHTML = `<img class="card-img" src="${event.image}" alt="${event.title}" loading="lazy" onerror="this.style.display='none';this.nextElementSibling.style.display='flex'"><div class="card-img-placeholder" style="display:none;background:${gradient}"><span>${cat.emoji}</span></div>`;
    } else {
      imgHTML = `<div class="card-img-placeholder" style="background:${gradient}"><span>${cat.emoji}</span></div>`;
    }
    const link = event.url ? `<a class="card-link" href="${event.url}" target="_blank" rel="noopener" onclick="event.stopPropagation()">Saber más →</a>` : '';
    card.innerHTML = `${imgHTML}<div class="card-body"><div class="card-category" style="background:${cat.bg};color:${cat.text}">${cat.emoji} ${event.category}</div><div class="card-title">${event.title}</div><div class="card-desc">${event.description || ''}</div>${link}</div>`;
    return card;
  }

  _buildTimeline() {
    this.track.innerHTML = '';
    const byYear = {};
    this.events.forEach(ev => { if (!byYear[ev.year]) byYear[ev.year] = []; byYear[ev.year].push(ev); });

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

      const dot = document.createElement('div');
      dot.className = 'year-dot';
      group.appendChild(dot);

      const cardsRow = document.createElement('div');
      cardsRow.className = 'year-cards';
      yearEvents.sort((a, b) => (a.importance || 0) - (b.importance || 0));
      yearEvents.forEach(ev => cardsRow.appendChild(this._createCard(ev)));
      group.appendChild(cardsRow);

      this.track.appendChild(group);
    }

    // Add the connecting line
    const line = document.createElement('div');
    line.className = 'timeline-line';
    line.innerHTML = '<div class="timeline-line-inner"></div>';
    this.track.appendChild(line);
  }

  _buildYearBar() {
    this.yearBarInner.innerHTML = '';
    for (let y = YEAR_MIN; y <= YEAR_MAX; y += 5) {
      const tick = document.createElement('div');
      tick.className = 'year-tick'; tick.dataset.year = y; tick.textContent = y;
      tick.addEventListener('click', () => this._scrollToYear(y));
      this.yearBarInner.appendChild(tick);
    }
    if (YEAR_MAX % 5 !== 0) {
      const tick = document.createElement('div');
      tick.className = 'year-tick'; tick.dataset.year = YEAR_MAX; tick.textContent = YEAR_MAX;
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

    // Smooth scroll interpolation
    this.scrollLeft += (this.container.scrollLeft - this.scrollLeft) * 0.1;

    // Smoke
    const ctx = this.fxCtx;
    ctx.clearRect(0, 0, this.fxCanvas.width, this.fxCanvas.height);
    for (const p of this.smokeParticles) { p.update(this.currentEra); p.draw(ctx); }

    // Parallax movement - theater stage effect
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll > 0) {
      const scrollProgress = this.scrollLeft / maxScroll;

      // Move parallax layers at different speeds
      ['back', 'mid', 'front'].forEach(layerName => {
        const layer = layerName === 'back' ? this.parallaxBack : layerName === 'mid' ? this.parallaxMid : this.parallaxFront;
        const speed = layerName === 'back' ? 0.1 : layerName === 'mid' ? 0.25 : 0.5;
        const offset = -scrollProgress * window.innerWidth * speed;
        layer.style.transform = `translateX(${offset}px)`;
      });

      // Animate individual parallax elements with subtle float
      const time = performance.now() * 0.001;
      Object.values(this.parallaxEls).flat().forEach((el, i) => {
        const baseSpeed = parseFloat(el.dataset.speed);
        const floatY = Math.sin(time * 0.5 + i * 0.7) * 8;
        const floatX = Math.cos(time * 0.3 + i * 1.1) * 4;
        el.style.transform = `translate(${floatX}px, ${floatY}px)`;
        el.style.opacity = 0.04 + Math.sin(time * 0.2 + i) * 0.02;
      });
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
