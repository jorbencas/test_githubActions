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

// Cozy homey eras: warm browns, amber, fire colors
const ERAS = [
  { name: 'medieval', range: [1970, 1979], bg: '#120c06', accent: '#d97706', accent2: '#92400e', smoke: [0.85, 0.45, 0.05], cardBg: 'rgba(25, 18, 8, 0.92)' },
  { name: 'retro70', range: [1980, 1989], bg: '#0f0a06', accent: '#c2410c', accent2: '#b45309', smoke: [0.76, 0.25, 0.05], cardBg: 'rgba(22, 14, 6, 0.92)' },
  { name: 'retro80', range: [1990, 1999], bg: '#0d0a08', accent: '#e67e22', accent2: '#f59e0b', smoke: [0.9, 0.5, 0.1], cardBg: 'rgba(20, 15, 10, 0.92)' },
  { name: 'digital90', range: [2000, 2009], bg: '#0a0d0a', accent: '#65a30d', accent2: '#4d7c0f', smoke: [0.4, 0.65, 0.1], cardBg: 'rgba(14, 18, 10, 0.92)' },
  { name: 'connected', range: [2010, 2019], bg: '#080a0f', accent: '#0ea5e9', accent2: '#0284c7', smoke: [0.06, 0.65, 0.9], cardBg: 'rgba(10, 14, 22, 0.92)' },
  { name: 'ai-home', range: [2020, 2025], bg: '#0d0810', accent: '#a78bfa', accent2: '#7c3aed', smoke: [0.65, 0.48, 0.98], cardBg: 'rgba(16, 10, 22, 0.92)' },
];

// Cozy parallax SVG elements per era
const ERA_ELEMENTS = {
  medieval: [
    { type: 'fire', x: 5, y: 55, size: 160, speed: 0.06 },
    { type: 'tree', x: 12, y: 20, size: 200, speed: 0.04 },
    { type: 'cabin', x: 25, y: 60, size: 180, speed: 0.08 },
    { type: 'logs', x: 38, y: 75, size: 140, speed: 0.03 },
    { type: 'tree', x: 48, y: 15, size: 170, speed: 0.05 },
    { type: 'fire', x: 60, y: 65, size: 130, speed: 0.07 },
    { type: 'cabin', x: 75, y: 25, size: 160, speed: 0.04 },
    { type: 'tree', x: 88, y: 55, size: 190, speed: 0.06 },
  ],
  retro70: [
    { type: 'vinyl', x: 8, y: 25, size: 150, speed: 0.07 },
    { type: 'lamp', x: 18, y: 60, size: 120, speed: 0.05 },
    { type: 'fire', x: 30, y: 50, size: 160, speed: 0.08 },
    { type: 'plant', x: 42, y: 18, size: 140, speed: 0.04 },
    { type: 'couch', x: 55, y: 65, size: 170, speed: 0.06 },
    { type: 'vinyl', x: 68, y: 30, size: 130, speed: 0.05 },
    { type: 'fire', x: 80, y: 55, size: 150, speed: 0.07 },
    { type: 'lamp', x: 90, y: 20, size: 110, speed: 0.04 },
  ],
  retro80: [
    { type: 'tv', x: 6, y: 30, size: 160, speed: 0.06 },
    { type: 'fire', x: 18, y: 60, size: 140, speed: 0.08 },
    { type: 'arcade', x: 30, y: 20, size: 150, speed: 0.05 },
    { type: 'cassette', x: 42, y: 65, size: 120, speed: 0.04 },
    { type: 'fire', x: 55, y: 45, size: 160, speed: 0.07 },
    { type: 'tv', x: 68, y: 25, size: 140, speed: 0.06 },
    { type: 'tree', x: 80, y: 60, size: 170, speed: 0.03 },
    { type: 'arcade', x: 90, y: 35, size: 130, speed: 0.05 },
  ],
  digital90: [
    { type: 'tree', x: 5, y: 25, size: 180, speed: 0.04 },
    { type: 'monitor', x: 15, y: 55, size: 150, speed: 0.07 },
    { type: 'fire', x: 28, y: 40, size: 140, speed: 0.06 },
    { type: 'cabin', x: 40, y: 70, size: 160, speed: 0.05 },
    { type: 'tree', x: 52, y: 18, size: 190, speed: 0.03 },
    { type: 'monitor', x: 65, y: 60, size: 140, speed: 0.08 },
    { type: 'fire', x: 78, y: 30, size: 130, speed: 0.06 },
    { type: 'cabin', x: 90, y: 55, size: 150, speed: 0.04 },
  ],
  connected: [
    { type: 'phone', x: 8, y: 28, size: 120, speed: 0.07 },
    { type: 'cloud', x: 20, y: 15, size: 180, speed: 0.04 },
    { type: 'fire', x: 32, y: 60, size: 140, speed: 0.06 },
    { type: 'tree', x: 45, y: 35, size: 170, speed: 0.05 },
    { type: 'phone', x: 58, y: 65, size: 110, speed: 0.08 },
    { type: 'cloud', x: 70, y: 20, size: 160, speed: 0.03 },
    { type: 'fire', x: 82, y: 50, size: 130, speed: 0.07 },
    { type: 'tree', x: 92, y: 30, size: 150, speed: 0.04 },
  ],
  'ai-home': [
    { type: 'brain', x: 6, y: 25, size: 170, speed: 0.06 },
    { type: 'fire', x: 18, y: 55, size: 150, speed: 0.08 },
    { type: 'neural', x: 30, y: 15, size: 200, speed: 0.04 },
    { type: 'cabin', x: 42, y: 65, size: 160, speed: 0.05 },
    { type: 'brain', x: 55, y: 30, size: 140, speed: 0.07 },
    { type: 'fire', x: 68, y: 55, size: 130, speed: 0.06 },
    { type: 'tree', x: 80, y: 20, size: 180, speed: 0.03 },
    { type: 'neural', x: 92, y: 60, size: 150, speed: 0.05 },
  ],
};

class SmokeParticle {
  constructor(canvas, era) { this.canvas = canvas; this.reset(era, true); }
  reset(era, initial = false) {
    this.x = Math.random() * this.canvas.width;
    this.y = initial ? Math.random() * this.canvas.height : this.canvas.height + 20;
    this.size = Math.random() * 140 + 60;
    this.speedX = (Math.random() - 0.5) * 0.25;
    this.speedY = -(Math.random() * 0.35 + 0.1);
    this.opacity = Math.random() * 0.1 + 0.02;
    this.life = 0;
    this.maxLife = Math.random() * 500 + 250;
    const c = era.smoke; this.r = c[0]; this.g = c[1]; this.b = c[2];
  }
  update(era) {
    this.x += this.speedX; this.y += this.speedY; this.life++;
    this.speedX += (Math.random() - 0.5) * 0.015;
    const c = era.smoke;
    this.r += (c[0] - this.r) * 0.008;
    this.g += (c[1] - this.g) * 0.008;
    this.b += (c[2] - this.b) * 0.008;
    if (this.life > this.maxLife || this.y < -this.size) this.reset(era);
  }
  draw(ctx) {
    const p = this.life / this.maxLife;
    const a = this.opacity * (p < 0.15 ? p / 0.15 : p > 0.75 ? (1 - p) / 0.25 : 1);
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
    g.addColorStop(0, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},${a})`);
    g.addColorStop(1, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},0)`);
    ctx.fillStyle = g;
    ctx.fillRect(this.x - this.size, this.y - this.size, this.size * 2, this.size * 2);
  }
}

class EmberParticle {
  constructor(canvas, era) { this.canvas = canvas; this.reset(era); }
  reset(era) {
    this.x = Math.random() * this.canvas.width;
    this.y = this.canvas.height + 10;
    this.size = Math.random() * 3 + 1;
    this.speedX = (Math.random() - 0.5) * 0.8;
    this.speedY = -(Math.random() * 1.5 + 0.5);
    this.opacity = Math.random() * 0.8 + 0.2;
    this.life = 0;
    this.maxLife = Math.random() * 200 + 100;
    this.wobble = Math.random() * Math.PI * 2;
  }
  update() {
    this.x += this.speedX + Math.sin(this.wobble) * 0.3;
    this.y += this.speedY;
    this.wobble += 0.05;
    this.life++;
    this.speedY *= 0.998;
    if (this.life > this.maxLife || this.y < -10) this.reset();
  }
  draw(ctx) {
    const p = this.life / this.maxLife;
    const a = this.opacity * (1 - p);
    const r = 230 + Math.random() * 25;
    const g = 80 + Math.random() * 60;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * (1 - p * 0.5), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${r},${g},10,${a})`;
    ctx.fill();
    // Glow
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * 3 * (1 - p * 0.5), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${r},${g},10,${a * 0.15})`;
    ctx.fill();
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
    this.embers = [];
    this.parallaxEls = { back: [], mid: [], front: [] };
    this.scrollLeft = 0;

    this._resizeCanvas();
    this._initSmoke();
    this._initEmbers();
    this._buildParallaxElements(ERAS[0]);
    this._bindScroll();
    this._startMusic();
    this._loadData();
    this._animate();

    window.addEventListener('resize', () => {
      this._resizeCanvas();
      this._buildParallaxElements(this.currentEra);
    });
  }

  _resizeCanvas() {
    this.fxCanvas.width = window.innerWidth;
    this.fxCanvas.height = window.innerHeight;
  }

  _initSmoke() {
    for (let i = 0; i < 20; i++) this.smokeParticles.push(new SmokeParticle(this.fxCanvas, this.currentEra));
  }

  _initEmbers() {
    for (let i = 0; i < 30; i++) this.embers.push(new EmberParticle(this.fxCanvas, this.currentEra));
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

    elems.forEach((el) => {
      const layerIdx = el.speed < 0.05 ? 0 : el.speed < 0.07 ? 1 : 2;
      const layer = layers[layerIdx];
      const name = layerNames[layerIdx];

      const div = document.createElement('div');
      div.className = 'parallax-el';
      div.dataset.speed = el.speed;
      div.style.left = `${el.x}%`;
      div.style.top = `${el.y}%`;
      div.style.width = `${el.size}px`;
      div.style.height = `${el.size}px`;

      div.innerHTML = this._cozySVG(el);
      layer.appendChild(div);
      this.parallaxEls[name].push(div);
    });
  }

  _cozySVG(el) {
    const s = el.size;
    const o = 0.07; // opacity
    const oc = '230,126,34'; // orange fire color
    const wood = '139,90,43';
    const leaf = '60,100,40';
    const stone = '120,110,100';

    switch (el.type) {
      case 'fire':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <path d="M${s*0.5} ${s*0.1} Q${s*0.35} ${s*0.3} ${s*0.3} ${s*0.5} Q${s*0.25} ${s*0.7} ${s*0.5} ${s*0.9} Q${s*0.75} ${s*0.7} ${s*0.7} ${s*0.5} Q${s*0.65} ${s*0.3} ${s*0.5} ${s*0.1}" fill="rgba(${oc},0.3)" stroke="rgba(${oc},0.5)" stroke-width="1"/>
            <path d="M${s*0.5} ${s*0.25} Q${s*0.4} ${s*0.4} ${s*0.38} ${s*0.55} Q${s*0.45} ${s*0.65} ${s*0.5} ${s*0.7} Q${s*0.55} ${s*0.65} ${s*0.62} ${s*0.55} Q${s*0.6} ${s*0.4} ${s*0.5} ${s*0.25}" fill="rgba(255,200,50,0.2)"/>
            <rect x="${s*0.35}" y="${s*0.82}" width="${s*0.3}" height="${s*0.06}" rx="2" fill="rgba(${wood},0.4)"/>
            <rect x="${s*0.3}" y="${s*0.88}" width="${s*0.4}" height="${s*0.05}" rx="2" fill="rgba(${wood},0.3)"/>
          </g>
        </svg>`;
      case 'tree':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.46}" y="${s*0.6}" width="${s*0.08}" height="${s*0.35}" fill="rgba(${wood},0.5)"/>
            <polygon points="${s*0.5},${s*0.05} ${s*0.2},${s*0.45} ${s*0.8},${s*0.45}" fill="rgba(${leaf},0.3)" stroke="rgba(${leaf},0.4)" stroke-width="1"/>
            <polygon points="${s*0.5},${s*0.15} ${s*0.25},${s*0.55} ${s*0.75},${s*0.55}" fill="rgba(${leaf},0.2)"/>
            <polygon points="${s*0.5},${s*0.28} ${s*0.3},${s*0.62} ${s*0.7},${s*0.62}" fill="rgba(${leaf},0.15)"/>
          </g>
        </svg>`;
      case 'cabin':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.15}" y="${s*0.4}" width="${s*0.7}" height="${s*0.5}" fill="rgba(${wood},0.3)" stroke="rgba(${wood},0.4)" stroke-width="1"/>
            <polygon points="${s*0.1},${s*0.42} ${s*0.5},${s*0.1} ${s*0.9},${s*0.42}" fill="rgba(${wood},0.4)" stroke="rgba(${wood},0.3)" stroke-width="1"/>
            <rect x="${s*0.4}" y="${s*0.55}" width="${s*0.2}" height="${s*0.35}" fill="rgba(40,25,10,0.5)" rx="1"/>
            <rect x="${s*0.22}" y="${s*0.5}" width="${s*0.15}" height="${s*0.15}" fill="rgba(${oc},0.2)" rx="1"/>
            <rect x="${s*0.63}" y="${s*0.5}" width="${s*0.15}" height="${s*0.15}" fill="rgba(${oc},0.15)" rx="1"/>
            <line x1="${s*0.5}" y1="${s*0.1}" x2="${s*0.5}" y2="${s*0.02}" stroke="rgba(80,80,80,0.3)" stroke-width="2"/>
          </g>
        </svg>`;
      case 'logs':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.5}">
          <g opacity="${o}">
            <ellipse cx="${s*0.3}" cy="${s*0.35}" rx="${s*0.35}" ry="${s*0.08}" fill="rgba(${wood},0.3)" stroke="rgba(${wood},0.4)" stroke-width="1"/>
            <ellipse cx="${s*0.5}" cy="${s*0.28}" rx="${s*0.4}" ry="${s*0.07}" fill="rgba(${wood},0.25)" stroke="rgba(${wood},0.35)" stroke-width="1"/>
            <ellipse cx="${s*0.4}" cy="${s*0.42}" rx="${s*0.38}" ry="${s*0.06}" fill="rgba(${wood},0.2)" stroke="rgba(${wood},0.3)" stroke-width="1"/>
            <circle cx="${s*0.05}" cy="${s*0.35}" r="${s*0.06}" fill="rgba(${wood},0.35)"/>
            <circle cx="${s*0.75}" cy="${s*0.28}" r="${s*0.05}" fill="rgba(${wood},0.3)"/>
          </g>
        </svg>`;
      case 'vinyl':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <circle cx="${s/2}" cy="${s/2}" r="${s*0.45}" fill="none" stroke="rgba(60,50,40,0.4)" stroke-width="1"/>
            <circle cx="${s/2}" cy="${s/2}" r="${s*0.35}" fill="none" stroke="rgba(60,50,40,0.3)" stroke-width="0.5"/>
            <circle cx="${s/2}" cy="${s/2}" r="${s*0.25}" fill="none" stroke="rgba(60,50,40,0.25)" stroke-width="0.5"/>
            <circle cx="${s/2}" cy="${s/2}" r="${s*0.15}" fill="rgba(${oc},0.15)" stroke="rgba(${oc},0.3)" stroke-width="1"/>
            <circle cx="${s/2}" cy="${s/2}" r="${s*0.03}" fill="rgba(${oc},0.3)"/>
          </g>
        </svg>`;
      case 'lamp':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.5}" height="${s}">
          <g opacity="${o}">
            <polygon points="${s*0.25},${s*0.05} ${s*0.05},${s*0.35} ${s*0.45},${s*0.35}" fill="rgba(${oc},0.2)" stroke="rgba(${oc},0.3)" stroke-width="1"/>
            <rect x="${s*0.22}" y="${s*0.35}" width="${s*0.06}" height="${s*0.4}" fill="rgba(${wood},0.3)"/>
            <ellipse cx="${s*0.25}" cy="${s*0.78}" rx="${s*0.12}" ry="${s*0.03}" fill="rgba(${wood},0.3)"/>
            <circle cx="${s*0.25}" cy="${s*0.2}" r="${s*0.04}" fill="rgba(255,220,100,0.2)"/>
          </g>
        </svg>`;
      case 'couch':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.5}">
          <g opacity="${o}">
            <rect x="${s*0.1}" y="${s*0.15}" width="${s*0.8}" height="${s*0.25}" rx="8" fill="rgba(${wood},0.3)" stroke="rgba(${wood},0.35)" stroke-width="1"/>
            <rect x="${s*0.05}" y="${s*0.1}" width="${s*0.15}" height="${s*0.35}" rx="4" fill="rgba(${wood},0.25)"/>
            <rect x="${s*0.8}" y="${s*0.1}" width="${s*0.15}" height="${s*0.35}" rx="4" fill="rgba(${wood},0.25)"/>
            <rect x="${s*0.15}" y="${s*0.38}" width="${s*0.1}" height="${s*0.08}" rx="2" fill="rgba(${wood},0.2)"/>
            <rect x="${s*0.75}" y="${s*0.38}" width="${s*0.1}" height="${s*0.08}" rx="2" fill="rgba(${wood},0.2)"/>
          </g>
        </svg>`;
      case 'tv':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.15}" y="${s*0.1}" width="${s*0.7}" height="${s*0.5}" rx="4" fill="rgba(40,35,30,0.4)" stroke="rgba(80,70,60,0.4)" stroke-width="1.5"/>
            <rect x="${s*0.2}" y="${s*0.15}" width="${s*0.55}" height="${s*0.38}" fill="rgba(${oc},0.08)"/>
            <circle cx="${s*0.82}" cy="${s*0.25}" r="${s*0.03}" fill="rgba(${oc},0.2)"/>
            <circle cx="${s*0.82}" cy="${s*0.35}" r="${s*0.03}" fill="rgba(100,100,100,0.2)"/>
            <rect x="${s*0.35}" y="${s*0.62}" width="${s*0.3}" height="${s*0.06}" rx="1" fill="rgba(${wood},0.3)"/>
            <line x1="${s*0.3}" y1="${s*0.68}" x2="${s*0.2}" y2="${s*0.78}" stroke="rgba(${wood},0.2)" stroke-width="1"/>
            <line x1="${s*0.7}" y1="${s*0.68}" x2="${s*0.8}" y2="${s*0.78}" stroke="rgba(${wood},0.2)" stroke-width="1"/>
          </g>
        </svg>`;
      case 'arcade':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.6}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.1}" y="${s*0.05}" width="${s*0.4}" height="${s*0.65}" rx="4" fill="rgba(30,25,40,0.4)" stroke="rgba(${oc},0.3)" stroke-width="1"/>
            <rect x="${s*0.13}" y="${s*0.1}" width="${s*0.34}" height="${s*0.3}" fill="rgba(${oc},0.1)"/>
            <circle cx="${s*0.2}" cy="${s*0.5}" r="${s*0.04}" fill="rgba(200,50,50,0.3)"/>
            <circle cx="${s*0.35}" cy="${s*0.5}" r="${s*0.04}" fill="rgba(50,50,200,0.3)"/>
            <rect x="${s*0.15}" y="${s*0.56}" width="${s*0.3}" height="${s*0.12}" rx="2" fill="rgba(60,50,40,0.3)"/>
            <rect x="${s*0.08}" y="${s*0.72}" width="${s*0.44}" height="${s*0.22}" fill="rgba(40,35,30,0.3)"/>
          </g>
        </svg>`;
      case 'cassette':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.6}">
          <g opacity="${o}">
            <rect x="${s*0.1}" y="${s*0.1}" width="${s*0.8}" height="${s*0.4}" rx="4" fill="rgba(40,35,30,0.4)" stroke="rgba(80,70,60,0.3)" stroke-width="1"/>
            <circle cx="${s*0.35}" cy="${s*0.3}" r="${s*0.08}" fill="none" stroke="rgba(${wood},0.3)" stroke-width="1"/>
            <circle cx="${s*0.65}" cy="${s*0.3}" r="${s*0.08}" fill="none" stroke="rgba(${wood},0.3)" stroke-width="1"/>
            <line x1="${s*0.43}" y1="${s*0.3}" x2="${s*0.57}" y2="${s*0.3}" stroke="rgba(${wood},0.2)" stroke-width="0.5"/>
            <rect x="${s*0.25}" y="${s*0.42}" width="${s*0.5}" height="${s*0.04}" rx="1" fill="rgba(${wood},0.2)"/>
          </g>
        </svg>`;
      case 'monitor':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.1}" y="${s*0.05}" width="${s*0.8}" height="${s*0.55}" rx="4" fill="rgba(35,30,25,0.4)" stroke="rgba(80,70,60,0.3)" stroke-width="1.5"/>
            <rect x="${s*0.15}" y="${s*0.1}" width="${s*0.65}" height="${s*0.4}" fill="rgba(100,200,100,0.06)"/>
            <rect x="${s*0.35}" y="${s*0.62}" width="${s*0.3}" height="${s*0.08}" rx="1" fill="rgba(${wood},0.25)"/>
            <line x1="${s*0.25}" y1="${s*0.7}" x2="${s*0.15}" y2="${s*0.82}" stroke="rgba(${wood},0.2)" stroke-width="1"/>
            <line x1="${s*0.75}" y1="${s*0.7}" x2="${s*0.85}" y2="${s*0.82}" stroke="rgba(${wood},0.2)" stroke-width="1"/>
          </g>
        </svg>`;
      case 'phone':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.5}" height="${s}">
          <g opacity="${o}">
            <rect x="${s*0.08}" y="${s*0.05}" width="${s*0.34}" height="${s*0.7}" rx="6" fill="rgba(30,28,35,0.4)" stroke="rgba(100,100,120,0.3)" stroke-width="1"/>
            <rect x="${s*0.12}" y="${s*0.12}" width="${s*0.26}" height="${s*0.45}" fill="rgba(${oc},0.06)"/>
            <circle cx="${s*0.25}" cy="${s*0.67}" r="${s*0.03}" fill="rgba(100,100,100,0.2)"/>
          </g>
        </svg>`;
      case 'cloud':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.5}">
          <g opacity="${o}">
            <path d="M${s*0.2} ${s*0.35} Q${s*0.1} ${s*0.35} ${s*0.1} ${s*0.25} Q${s*0.1} ${s*0.12} ${s*0.25} ${s*0.12} Q${s*0.3} ${s*0.02} ${s*0.5} ${s*0.02} Q${s*0.7} ${s*0.02} ${s*0.75} ${s*0.12} Q${s*0.9} ${s*0.12} ${s*0.9} ${s*0.25} Q${s*0.9} ${s*0.35} ${s*0.8} ${s*0.35} Z" fill="rgba(180,200,220,0.15)" stroke="rgba(180,200,220,0.2)" stroke-width="1"/>
          </g>
        </svg>`;
      case 'brain':
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}">
          <g opacity="${o}">
            <path d="M${s*0.5} ${s*0.12} Q${s*0.3} ${s*0.08} ${s*0.25} ${s*0.22} Q${s*0.15} ${s*0.3} ${s*0.2} ${s*0.45} Q${s*0.15} ${s*0.6} ${s*0.3} ${s*0.65} Q${s*0.4} ${s*0.78} ${s*0.5} ${s*0.85}" stroke="rgba(${oc},0.4)" fill="none" stroke-width="1.5"/>
            <path d="M${s*0.5} ${s*0.12} Q${s*0.7} ${s*0.08} ${s*0.75} ${s*0.22} Q${s*0.85} ${s*0.3} ${s*0.8} ${s*0.45} Q${s*0.85} ${s*0.6} ${s*0.7} ${s*0.65} Q${s*0.6} ${s*0.78} ${s*0.5} ${s*0.85}" stroke="rgba(${oc},0.4)" fill="none" stroke-width="1.5"/>
            <path d="M${s*0.35} ${s*0.3} Q${s*0.5} ${s*0.35} ${s*0.65} ${s*0.3}" stroke="rgba(${oc},0.2)" fill="none" stroke-width="0.8"/>
            <path d="M${s*0.3} ${s*0.5} Q${s*0.5} ${s*0.55} ${s*0.7} ${s*0.5}" stroke="rgba(${oc},0.2)" fill="none" stroke-width="0.8"/>
          </g>
        </svg>`;
      case 'neural':
        const nodes = [];
        for (let i = 0; i < 10; i++) nodes.push([Math.random()*s*0.8+s*0.1, Math.random()*s*0.8+s*0.1]);
        const lines = [];
        for (let i = 0; i < nodes.length; i++) for (let j = i+1; j < nodes.length; j++) {
          const dx = nodes[i][0]-nodes[j][0], dy = nodes[i][1]-nodes[j][1];
          if (Math.sqrt(dx*dx+dy*dy) < s*0.4) lines.push(`<line x1="${nodes[i][0]}" y1="${nodes[i][1]}" x2="${nodes[j][0]}" y2="${nodes[j][1]}" stroke="rgba(${oc},0.15)" stroke-width="0.5"/>`);
        }
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}">${lines.join('')}${nodes.map(([x,y])=>`<circle cx="${x}" cy="${y}" r="3" fill="rgba(${oc},0.25)"/>`).join('')}</g></svg>`;
      default:
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><circle cx="${s/2}" cy="${s/2}" r="${s/2-2}" stroke="rgba(${oc},0.3)" fill="none" stroke-width="1"/></svg>`;
    }
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
    this.bgGradient.style.background = `radial-gradient(ellipse at 25% 75%, rgba(230,126,34,0.08) 0%, transparent 50%), radial-gradient(ellipse at 75% 25%, rgba(211,84,0,0.05) 0%, transparent 40%)`;
    document.getElementById('header').style.background = `linear-gradient(180deg, ${era.bg}ee 0%, transparent 100%)`;
    document.getElementById('year-bar').style.background = `linear-gradient(0deg, ${era.bg}ee 0%, transparent 100%)`;
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
      // Deep warm drone
      makeOsc(55, 'sine', 0.025);
      makeOsc(82.5, 'sine', 0.018);
      makeOsc(110, 'sine', 0.012);
      // Warm shimmer
      const shimmer = makeOsc(220, 'triangle', 0.005);
      const lfo = ctx.createOscillator(); const lfoG = ctx.createGain();
      lfo.type = 'sine'; lfo.frequency.value = 0.06; lfoG.gain.value = 0.004;
      lfo.connect(lfoG); lfoG.connect(shimmer.gain.gain); lfo.start();
      // Crackle (very subtle noise)
      const bufSize = ctx.sampleRate * 2;
      const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.003;
      const noise = ctx.createBufferSource();
      noise.buffer = buf; noise.loop = true;
      const noiseFilter = ctx.createBiquadFilter();
      noiseFilter.type = 'bandpass'; noiseFilter.frequency.value = 800; noiseFilter.Q.value = 0.5;
      const noiseGain = ctx.createGain(); noiseGain.gain.value = 0.4;
      noise.connect(noiseFilter); noiseFilter.connect(noiseGain); noiseGain.connect(ctx.destination);
      noise.start();
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
      group.className = 'year-group'; group.dataset.year = year;
      const label = document.createElement('div');
      label.className = 'year-label'; label.textContent = year;
      group.appendChild(label);
      const dot = document.createElement('div');
      dot.className = 'year-dot'; group.appendChild(dot);
      const cardsRow = document.createElement('div');
      cardsRow.className = 'year-cards';
      yearEvents.sort((a, b) => (a.importance || 0) - (b.importance || 0));
      yearEvents.forEach(ev => cardsRow.appendChild(this._createCard(ev)));
      group.appendChild(cardsRow);
      this.track.appendChild(group);
    }
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
    const ctx = this.fxCtx;
    const w = this.fxCanvas.width, h = this.fxCanvas.height;
    ctx.clearRect(0, 0, w, h);

    // Smoke
    for (const p of this.smokeParticles) { p.update(this.currentEra); p.draw(ctx); }
    // Embers
    for (const e of this.embers) { e.update(); e.draw(ctx); }

    // Parallax scroll
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll > 0) {
      const scrollProgress = this.scrollLeft / maxScroll;
      ['back', 'mid', 'front'].forEach(layerName => {
        const layer = layerName === 'back' ? this.parallaxBack : layerName === 'mid' ? this.parallaxMid : this.parallaxFront;
        const speed = layerName === 'back' ? 0.08 : layerName === 'mid' ? 0.2 : 0.4;
        layer.style.transform = `translateX(${-scrollProgress * w * speed}px)`;
      });

      // Float parallax elements
      const time = performance.now() * 0.001;
      Object.values(this.parallaxEls).flat().forEach((el, i) => {
        const floatY = Math.sin(time * 0.4 + i * 0.8) * 6;
        const floatX = Math.cos(time * 0.25 + i * 1.2) * 3;
        el.style.transform = `translate(${floatX}px, ${floatY}px)`;
        el.style.opacity = 0.05 + Math.sin(time * 0.15 + i) * 0.02;
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
      setTimeout(() => this.loadingEl.classList.add('hidden'), 500);
    } catch (err) {
      console.error('Failed to load events:', err);
      const sub = this.loadingEl.querySelector('.loader-sub');
      if (sub) { sub.textContent = 'Error. Reintentando...'; sub.style.color = '#ef4444'; }
      setTimeout(() => this._loadData(), 3000);
    }
  }
}

new App();
