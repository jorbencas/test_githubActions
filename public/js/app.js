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

// Each era: real images, distinct mood, parallax elements
const ERAS = [
  {
    name: 'mainframes', range: [1970, 1979],
    label: 'La Edad de los Mainframes',
    bg: '#120c06',
    accent: '#d97706', accent2: '#92400e',
    smoke: [0.85, 0.45, 0.05],
    overlay: 'linear-gradient(180deg, rgba(18,12,6,0.7) 0%, rgba(18,12,6,0.4) 50%, rgba(18,12,6,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1920&q=80', // circuit board
      'https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=1920&q=80', // server room
    ],
    parallax: [
      { type: 'circuit', x: 5, y: 20, size: 300, speed: 0.04, opacity: 0.06 },
      { type: 'chip', x: 20, y: 60, size: 180, speed: 0.07, opacity: 0.05 },
      { type: 'circuit', x: 45, y: 15, size: 250, speed: 0.03, opacity: 0.04 },
      { type: 'chip', x: 70, y: 55, size: 200, speed: 0.06, opacity: 0.05 },
      { type: 'circuit', x: 90, y: 30, size: 220, speed: 0.05, opacity: 0.04 },
    ]
  },
  {
    name: 'pc-revolution', range: [1980, 1989],
    label: 'La Revolución del PC',
    bg: '#0f0a06',
    accent: '#c2410c', accent2: '#b45309',
    smoke: [0.76, 0.25, 0.05],
    overlay: 'linear-gradient(180deg, rgba(15,10,6,0.7) 0%, rgba(15,10,6,0.35) 50%, rgba(15,10,6,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=1920&q=80', // retro computer
      'https://images.unsplash.com/photo-1550745165-9bc0b252726f?w=1920&q=80', // retro gaming
    ],
    parallax: [
      { type: 'floppy', x: 8, y: 25, size: 160, speed: 0.05, opacity: 0.06 },
      { type: 'monitor', x: 25, y: 55, size: 200, speed: 0.08, opacity: 0.05 },
      { type: 'floppy', x: 50, y: 18, size: 140, speed: 0.04, opacity: 0.04 },
      { type: 'monitor', x: 72, y: 60, size: 180, speed: 0.06, opacity: 0.05 },
      { type: 'floppy', x: 88, y: 30, size: 150, speed: 0.07, opacity: 0.04 },
    ]
  },
  {
    name: 'internet-boom', range: [1990, 1999],
    label: 'El Boom de Internet',
    bg: '#0a0d12',
    accent: '#38bdf8', accent2: '#0ea5e9',
    smoke: [0.22, 0.74, 0.97],
    overlay: 'linear-gradient(180deg, rgba(10,13,18,0.7) 0%, rgba(10,13,18,0.35) 50%, rgba(10,13,18,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=1920&q=80', // internet/tech
      'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=1920&q=80', // network cables
    ],
    parallax: [
      { type: 'globe', x: 6, y: 22, size: 240, speed: 0.04, opacity: 0.06 },
      { type: 'wave', x: 28, y: 58, size: 300, speed: 0.07, opacity: 0.05 },
      { type: 'globe', x: 52, y: 15, size: 200, speed: 0.03, opacity: 0.04 },
      { type: 'wave', x: 75, y: 52, size: 280, speed: 0.06, opacity: 0.05 },
      { type: 'globe', x: 92, y: 28, size: 180, speed: 0.05, opacity: 0.04 },
    ]
  },
  {
    name: 'web2', range: [2000, 2009],
    label: 'La Era Web 2.0',
    bg: '#0d0a06',
    accent: '#f59e0b', accent2: '#d97706',
    smoke: [0.96, 0.62, 0.04],
    overlay: 'linear-gradient(180deg, rgba(13,10,6,0.7) 0%, rgba(13,10,6,0.35) 50%, rgba(13,10,6,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=1920&q=80', // laptop coding
      'https://images.unsplash.com/photo-1504868584819-f8e8b4b6d7e3?w=1920&q=80', // dashboard
    ],
    parallax: [
      { type: 'window', x: 7, y: 20, size: 180, speed: 0.05, opacity: 0.06 },
      { type: 'code', x: 30, y: 55, size: 220, speed: 0.08, opacity: 0.05 },
      { type: 'window', x: 55, y: 18, size: 160, speed: 0.04, opacity: 0.04 },
      { type: 'code', x: 78, y: 58, size: 200, speed: 0.06, opacity: 0.05 },
      { type: 'window', x: 93, y: 25, size: 170, speed: 0.07, opacity: 0.04 },
    ]
  },
  {
    name: 'mobile-cloud', range: [2010, 2019],
    label: 'La Era Móvil y la Nube',
    bg: '#060a0d',
    accent: '#10b981', accent2: '#059669',
    smoke: [0.06, 0.73, 0.51],
    overlay: 'linear-gradient(180deg, rgba(6,10,13,0.7) 0%, rgba(6,10,13,0.35) 50%, rgba(6,10,13,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?w=1920&q=80', // smartphone
      'https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1920&q=80', // cloud/data
    ],
    parallax: [
      { type: 'phone', x: 8, y: 22, size: 140, speed: 0.06, opacity: 0.06 },
      { type: 'cloud', x: 30, y: 50, size: 260, speed: 0.04, opacity: 0.05 },
      { type: 'phone', x: 55, y: 18, size: 130, speed: 0.07, opacity: 0.04 },
      { type: 'cloud', x: 78, y: 55, size: 240, speed: 0.05, opacity: 0.05 },
      { type: 'phone', x: 94, y: 28, size: 120, speed: 0.08, opacity: 0.04 },
    ]
  },
  {
    name: 'ai-era', range: [2020, 2025],
    label: 'La Era de la Inteligencia Artificial',
    bg: '#0d0814',
    accent: '#a78bfa', accent2: '#7c3aed',
    smoke: [0.65, 0.48, 0.98],
    overlay: 'linear-gradient(180deg, rgba(13,8,20,0.7) 0%, rgba(13,8,20,0.35) 50%, rgba(13,8,20,0.8) 100%)',
    images: [
      'https://images.unsplash.com/photo-1677442136019-21780ecad995?w=1920&q=80', // AI brain
      'https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1920&q=80', // AI robot
    ],
    parallax: [
      { type: 'brain', x: 6, y: 20, size: 220, speed: 0.05, opacity: 0.06 },
      { type: 'neural', x: 28, y: 55, size: 280, speed: 0.08, opacity: 0.05 },
      { type: 'brain', x: 52, y: 15, size: 200, speed: 0.04, opacity: 0.04 },
      { type: 'neural', x: 76, y: 52, size: 260, speed: 0.06, opacity: 0.05 },
      { type: 'brain', x: 94, y: 25, size: 180, speed: 0.07, opacity: 0.04 },
    ]
  },
];

class SmokeParticle {
  constructor(canvas, era) { this.canvas = canvas; this.reset(era, true); }
  reset(era, initial = false) {
    this.x = Math.random() * this.canvas.width;
    this.y = initial ? Math.random() * this.canvas.height : this.canvas.height + 20;
    this.size = Math.random() * 150 + 70;
    this.speedX = (Math.random() - 0.5) * 0.2;
    this.speedY = -(Math.random() * 0.3 + 0.08);
    this.opacity = Math.random() * 0.08 + 0.01;
    this.life = 0;
    this.maxLife = Math.random() * 600 + 300;
    const c = era.smoke; this.r = c[0]; this.g = c[1]; this.b = c[2];
  }
  update(era) {
    this.x += this.speedX; this.y += this.speedY; this.life++;
    this.speedX += (Math.random() - 0.5) * 0.01;
    const c = era.smoke;
    this.r += (c[0] - this.r) * 0.005;
    this.g += (c[1] - this.g) * 0.005;
    this.b += (c[2] - this.b) * 0.005;
    if (this.life > this.maxLife || this.y < -this.size) this.reset(era);
  }
  draw(ctx) {
    const p = this.life / this.maxLife;
    const a = this.opacity * (p < 0.1 ? p / 0.1 : p > 0.7 ? (1 - p) / 0.3 : 1);
    const g = ctx.createRadialGradient(this.x, this.y, 0, this.x, this.y, this.size);
    g.addColorStop(0, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},${a})`);
    g.addColorStop(1, `rgba(${Math.round(this.r*255)},${Math.round(this.g*255)},${Math.round(this.b*255)},0)`);
    ctx.fillStyle = g;
    ctx.fillRect(this.x - this.size, this.y - this.size, this.size * 2, this.size * 2);
  }
}

class EmberParticle {
  constructor(canvas) { this.canvas = canvas; this.reset(); }
  reset() {
    this.x = Math.random() * this.canvas.width;
    this.y = this.canvas.height + 10;
    this.size = Math.random() * 3 + 1;
    this.speedX = (Math.random() - 0.5) * 0.6;
    this.speedY = -(Math.random() * 1.2 + 0.4);
    this.opacity = Math.random() * 0.7 + 0.3;
    this.life = 0;
    this.maxLife = Math.random() * 250 + 120;
    this.wobble = Math.random() * Math.PI * 2;
  }
  update() {
    this.x += this.speedX + Math.sin(this.wobble) * 0.25;
    this.y += this.speedY;
    this.wobble += 0.04;
    this.life++;
    this.speedY *= 0.999;
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
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.size * 3 * (1 - p * 0.5), 0, Math.PI * 2);
    ctx.fillStyle = `rgba(${r},${g},10,${a * 0.12})`;
    ctx.fill();
  }
}

class App {
  constructor() {
    this.container = document.getElementById('timeline-container');
    this.track = document.getElementById('timeline-track');
    this.yearDisplay = document.getElementById('year-display');
    this.eraLabel = document.getElementById('era-label');
    this.yearBarInner = document.getElementById('year-bar-inner');
    this.yearBarDot = document.getElementById('year-bar-dot');
    this.scrollHint = document.getElementById('scroll-hint');
    this.loadingEl = document.getElementById('loading');
    this.eraBg = document.getElementById('era-bg');
    this.eraOverlay = document.getElementById('era-overlay');
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
    this.bgImages = {};
    this.bgLoaded = {};

    this._resizeCanvas();
    this._initSmoke();
    this._initEmbers();
    this._preloadEraImages();
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
    for (let i = 0; i < 18; i++) this.smokeParticles.push(new SmokeParticle(this.fxCanvas, this.currentEra));
  }

  _initEmbers() {
    for (let i = 0; i < 25; i++) this.embers.push(new EmberParticle(this.fxCanvas));
  }

  _preloadEraImages() {
    ERAS.forEach(era => {
      era.images.forEach(url => {
        const img = new Image();
        img.src = url;
        img.onload = () => { this.bgLoaded[url] = true; };
      });
    });
  }

  _getEra(year) {
    for (const era of ERAS) { if (year >= era.range[0] && year <= era.range[1]) return era; }
    return ERAS[ERAS.length - 1];
  }

  _buildParallaxElements(era) {
    [this.parallaxBack, this.parallaxMid, this.parallaxFront].forEach(el => el.innerHTML = '');
    this.parallaxEls = { back: [], mid: [], front: [] };

    era.parallax.forEach(el => {
      const layerIdx = el.speed < 0.05 ? 0 : el.speed < 0.07 ? 1 : 2;
      const layer = [this.parallaxBack, this.parallaxMid, this.parallaxFront][layerIdx];
      const name = ['back', 'mid', 'front'][layerIdx];

      const div = document.createElement('div');
      div.className = 'parallax-el';
      div.dataset.speed = el.speed;
      div.style.left = `${el.x}%`;
      div.style.top = `${el.y}%`;
      div.style.width = `${el.size}px`;
      div.style.height = `${el.size}px`;
      div.style.opacity = el.opacity;
      div.innerHTML = this._eraSVG(el, era);
      layer.appendChild(div);
      this.parallaxEls[name].push(div);
    });
  }

  _eraSVG(el, era) {
    const s = el.size;
    const c = era.accent;
    const o = el.opacity || 0.06;
    const types = {
      circuit: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><rect x="${s*0.1}" y="${s*0.1}" width="${s*0.8}" height="${s*0.8}" rx="4" stroke="${c}" fill="none" stroke-width="1"/><line x1="${s*0.1}" y1="${s*0.3}" x2="${s*0.9}" y2="${s*0.3}" stroke="${c}" stroke-width="0.5"/><line x1="${s*0.1}" y1="${s*0.5}" x2="${s*0.9}" y2="${s*0.5}" stroke="${c}" stroke-width="0.5"/><line x1="${s*0.1}" y1="${s*0.7}" x2="${s*0.9}" y2="${s*0.7}" stroke="${c}" stroke-width="0.5"/><line x1="${s*0.3}" y1="${s*0.1}" x2="${s*0.3}" y2="${s*0.9}" stroke="${c}" stroke-width="0.5"/><line x1="${s*0.5}" y1="${s*0.1}" x2="${s*0.5}" y2="${s*0.9}" stroke="${c}" stroke-width="0.5"/><line x1="${s*0.7}" y1="${s*0.1}" x2="${s*0.7}" y2="${s*0.9}" stroke="${c}" stroke-width="0.5"/><circle cx="${s*0.3}" cy="${s*0.3}" r="${s*0.04}" fill="${c}"/><circle cx="${s*0.7}" cy="${s*0.5}" r="${s*0.04}" fill="${c}"/><circle cx="${s*0.5}" cy="${s*0.7}" r="${s*0.04}" fill="${c}"/></g></svg>`,
      chip: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><rect x="${s*0.2}" y="${s*0.2}" width="${s*0.6}" height="${s*0.6}" rx="3" stroke="${c}" fill="none" stroke-width="1.5"/><rect x="${s*0.3}" y="${s*0.3}" width="${s*0.4}" height="${s*0.4}" fill="${c}" opacity="0.15"/><line x1="${s*0.35}" y1="${s*0.2}" x2="${s*0.35}" y2="${s*0.05}" stroke="${c}" stroke-width="1"/><line x1="${s*0.5}" y1="${s*0.2}" x2="${s*0.5}" y2="${s*0.05}" stroke="${c}" stroke-width="1"/><line x1="${s*0.65}" y1="${s*0.2}" x2="${s*0.65}" y2="${s*0.05}" stroke="${c}" stroke-width="1"/><line x1="${s*0.35}" y1="${s*0.8}" x2="${s*0.35}" y2="${s*0.95}" stroke="${c}" stroke-width="1"/><line x1="${s*0.5}" y1="${s*0.8}" x2="${s*0.5}" y2="${s*0.95}" stroke="${c}" stroke-width="1"/><line x1="${s*0.65}" y1="${s*0.8}" x2="${s*0.65}" y2="${s*0.95}" stroke="${c}" stroke-width="1"/></g></svg>`,
      floppy: `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.7}" height="${s}"><g opacity="${o}"><rect x="${s*0.05}" y="${s*0.05}" width="${s*0.6}" height="${s*0.9}" rx="3" stroke="${c}" fill="none" stroke-width="1.5"/><rect x="${s*0.15}" y="${s*0.05}" width="${s*0.4}" height="${s*0.25}" rx="1" stroke="${c}" fill="none" stroke-width="1"/><rect x="${s*0.15}" y="${s*0.55}" width="${s*0.4}" height="${s*0.35}" rx="1" stroke="${c}" fill="none" stroke-width="0.8"/><circle cx="${s*0.52}" cy="${s*0.42}" r="${s*0.03}" fill="${c}"/></g></svg>`,
      monitor: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><rect x="${s*0.1}" y="${s*0.05}" width="${s*0.8}" height="${s*0.55}" rx="4" stroke="${c}" fill="none" stroke-width="1.5"/><rect x="${s*0.15}" y="${s*0.1}" width="${s*0.65}" height="${s*0.4}" fill="${c}" opacity="0.08"/><rect x="${s*0.35}" y="${s*0.62}" width="${s*0.3}" height="${s*0.08}" rx="1" stroke="${c}" fill="none" stroke-width="0.8"/><line x1="${s*0.25}" y1="${s*0.7}" x2="${s*0.15}" y2="${s*0.82}" stroke="${c}" stroke-width="0.8"/><line x1="${s*0.75}" y1="${s*0.7}" x2="${s*0.85}" y2="${s*0.82}" stroke="${c}" stroke-width="0.8"/></g></svg>`,
      globe: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><circle cx="${s/2}" cy="${s/2}" r="${s*0.42}" stroke="${c}" fill="none" stroke-width="1"/><ellipse cx="${s/2}" cy="${s/2}" rx="${s*0.2}" ry="${s*0.42}" stroke="${c}" fill="none" stroke-width="0.8"/><line x1="${s*0.08}" y1="${s/2}" x2="${s*0.92}" y2="${s/2}" stroke="${c}" stroke-width="0.8"/><path d="M${s*0.12} ${s*0.3} Q${s*0.5} ${s*0.35} ${s*0.88} ${s*0.3}" stroke="${c}" fill="none" stroke-width="0.5"/><path d="M${s*0.12} ${s*0.7} Q${s*0.5} ${s*0.65} ${s*0.88} ${s*0.7}" stroke="${c}" fill="none" stroke-width="0.5"/></g></svg>`,
      wave: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.3}"><g opacity="${o}"><path d="M0 ${s*0.15} Q${s*0.1} ${s*0.05} ${s*0.2} ${s*0.15} T${s*0.4} ${s*0.15} T${s*0.6} ${s*0.15} T${s*0.8} ${s*0.15} T${s} ${s*0.15}" stroke="${c}" fill="none" stroke-width="1.5"/><path d="M0 ${s*0.2} Q${s*0.1} ${s*0.12} ${s*0.2} ${s*0.2} T${s*0.4} ${s*0.2} T${s*0.6} ${s*0.2} T${s*0.8} ${s*0.2} T${s} ${s*0.2}" stroke="${c}" fill="none" stroke-width="0.8" opacity="0.5"/></g></svg>`,
      window: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><rect x="${s*0.1}" y="${s*0.1}" width="${s*0.8}" height="${s*0.7}" rx="4" stroke="${c}" fill="none" stroke-width="1.5"/><line x1="${s*0.1}" y1="${s*0.25}" x2="${s*0.9}" y2="${s*0.25}" stroke="${c}" stroke-width="0.8"/><circle cx="${s*0.18}" cy="${s*0.18}" r="${s*0.025}" fill="${c}"/><circle cx="${s*0.25}" cy="${s*0.18}" r="${s*0.025}" fill="${c}"/><circle cx="${s*0.32}" cy="${s*0.18}" r="${s*0.025}" fill="${c}"/><rect x="${s*0.15}" y="${s*0.32}" width="${s*0.35}" height="${s*0.03}" rx="1" fill="${c}" opacity="0.3"/><rect x="${s*0.15}" y="${s*0.4}" width="${s*0.5}" height="${s*0.03}" rx="1" fill="${c}" opacity="0.2"/><rect x="${s*0.15}" y="${s*0.48}" width="${s*0.4}" height="${s*0.03}" rx="1" fill="${c}" opacity="0.15"/></g></svg>`,
      code: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><text x="${s*0.1}" y="${s*0.2}" font-family="monospace" font-size="${s*0.08}" fill="${c}" opacity="0.4">&lt;div&gt;</text><text x="${s*0.15}" y="${s*0.32}" font-family="monospace" font-size="${s*0.08}" fill="${c}" opacity="0.3">&lt;span&gt;</text><text x="${s*0.2}" y="${s*0.44}" font-family="monospace" font-size="${s*0.08}" fill="${c}" opacity="0.25">hello</text><text x="${s*0.15}" y="${s*0.56}" font-family="monospace" font-size="${s*0.08}" fill="${c}" opacity="0.3">&lt;/span&gt;</text><text x="${s*0.1}" y="${s*0.68}" font-family="monospace" font-size="${s*0.08}" fill="${c}" opacity="0.4">&lt;/div&gt;</text></g></svg>`,
      phone: `<svg xmlns="http://www.w3.org/2000/svg" width="${s*0.5}" height="${s}"><g opacity="${o}"><rect x="${s*0.08}" y="${s*0.05}" width="${s*0.34}" height="${s*0.7}" rx="8" stroke="${c}" fill="none" stroke-width="1.5"/><rect x="${s*0.12}" y="${s*0.12}" width="${s*0.26}" height="${s*0.45}" fill="${c}" opacity="0.08"/><circle cx="${s*0.25}" cy="${s*0.67}" r="${s*0.03}" stroke="${c}" fill="none" stroke-width="0.8"/></g></svg>`,
      cloud: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s*0.5}"><g opacity="${o}"><path d="M${s*0.2} ${s*0.35} Q${s*0.1} ${s*0.35} ${s*0.1} ${s*0.25} Q${s*0.1} ${s*0.12} ${s*0.25} ${s*0.12} Q${s*0.3} ${s*0.02} ${s*0.5} ${s*0.02} Q${s*0.7} ${s*0.02} ${s*0.75} ${s*0.12} Q${s*0.9} ${s*0.12} ${s*0.9} ${s*0.25} Q${s*0.9} ${s*0.35} ${s*0.8} ${s*0.35} Z" stroke="${c}" fill="${c}" fill-opacity="0.08" stroke-width="1"/></g></svg>`,
      brain: `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}"><path d="M${s*0.5} ${s*0.1} Q${s*0.28} ${s*0.06} ${s*0.22} ${s*0.22} Q${s*0.12} ${s*0.32} ${s*0.18} ${s*0.48} Q${s*0.12} ${s*0.62} ${s*0.28} ${s*0.68} Q${s*0.38} ${s*0.8} ${s*0.5} ${s*0.88}" stroke="${c}" fill="none" stroke-width="1.5"/><path d="M${s*0.5} ${s*0.1} Q${s*0.72} ${s*0.06} ${s*0.78} ${s*0.22} Q${s*0.88} ${s*0.32} ${s*0.82} ${s*0.48} Q${s*0.88} ${s*0.62} ${s*0.72} ${s*0.68} Q${s*0.62} ${s*0.8} ${s*0.5} ${s*0.88}" stroke="${c}" fill="none" stroke-width="1.5"/><path d="M${s*0.32} ${s*0.28} Q${s*0.5} ${s*0.34} ${s*0.68} ${s*0.28}" stroke="${c}" fill="none" stroke-width="0.8"/><path d="M${s*0.28} ${s*0.48} Q${s*0.5} ${s*0.54} ${s*0.72} ${s*0.48}" stroke="${c}" fill="none" stroke-width="0.8"/><path d="M${s*0.32} ${s*0.65} Q${s*0.5} ${s*0.7} ${s*0.68} ${s*0.65}" stroke="${c}" fill="none" stroke-width="0.8"/></g></svg>`,
      neural: (() => {
        const nodes = [];
        for (let i = 0; i < 12; i++) nodes.push([Math.random()*0.8+0.1, Math.random()*0.8+0.1]);
        const lines = [];
        for (let i = 0; i < nodes.length; i++) for (let j = i+1; j < nodes.length; j++) {
          const dx = (nodes[i][0]-nodes[j][0])*s, dy = (nodes[i][1]-nodes[j][1])*s;
          if (Math.sqrt(dx*dx+dy*dy) < s*0.35) lines.push(`<line x1="${nodes[i][0]*s}" y1="${nodes[i][1]*s}" x2="${nodes[j][0]*s}" y2="${nodes[j][1]*s}" stroke="${c}" stroke-width="0.5"/>`);
        }
        return `<svg xmlns="http://www.w3.org/2000/svg" width="${s}" height="${s}"><g opacity="${o}">${lines.join('')}${nodes.map(([x,y])=>`<circle cx="${x*s}" cy="${y*s}" r="3" fill="${c}" opacity="0.4"/>`).join('')}</g></svg>`;
      })(),
    };
    return types[el.type] || types.circuit;
  }

  _applyEra(era, instant = false) {
    if (era === this.currentEra && !instant) return;
    this.currentEra = era;

    // Background image
    const imgUrl = era.images[Math.floor(Math.random() * era.images.length)];
    this.eraBg.style.transition = instant ? 'none' : 'background-image 1.5s ease, opacity 1.5s';
    this.eraBg.style.opacity = '0';
    setTimeout(() => {
      this.eraBg.style.backgroundImage = `url(${imgUrl})`;
      this.eraBg.style.opacity = '1';
      this.eraBg.classList.add('active');
    }, instant ? 0 : 300);

    // Overlay
    this.eraOverlay.style.background = era.overlay;

    // Colors
    document.documentElement.style.setProperty('--accent', era.accent);
    this.yearDisplay.style.color = era.accent;
    this.eraLabel.style.color = era.accent;
    this.eraLabel.textContent = era.label;
    this.yearBarDot.style.background = era.accent;

    // Parallax
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
      scrollTimeout = setTimeout(() => this._updateYearFromScroll(), 80);
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
      const shimmer = makeOsc(220, 'triangle', 0.004);
      const lfo = ctx.createOscillator(); const lfoG = ctx.createGain();
      lfo.type = 'sine'; lfo.frequency.value = 0.06; lfoG.gain.value = 0.003;
      lfo.connect(lfoG); lfoG.connect(shimmer.gain.gain); lfo.start();
      // Fire crackle
      const bufSize = ctx.sampleRate * 2;
      const buf = ctx.createBuffer(1, bufSize, ctx.sampleRate);
      const data = buf.getChannelData(0);
      for (let i = 0; i < bufSize; i++) data[i] = (Math.random() * 2 - 1) * 0.002;
      const noise = ctx.createBufferSource(); noise.buffer = buf; noise.loop = true;
      const filt = ctx.createBiquadFilter(); filt.type = 'bandpass'; filt.frequency.value = 900; filt.Q.value = 0.6;
      const ng = ctx.createGain(); ng.gain.value = 0.35;
      noise.connect(filt); filt.connect(ng); ng.connect(ctx.destination); noise.start();
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
      this._highlightYearTick(closestYear);
      this._applyEra(this._getEra(closestYear));
    }
  }

  _updateDot() {
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll <= 0) return;
    const progress = this.scrollLeft / maxScroll;
    this.yearBarDot.style.left = `${40 + progress * (window.innerWidth - 80)}px`;
  }

  _highlightYearTick(year) {
    this.yearBarInner.querySelectorAll('.year-tick').forEach(t => {
      t.classList.toggle('active', parseInt(t.dataset.year) === year);
    });
  }

  _hideScrollHint() {
    if (this.scrollHint && !this.scrollHint.classList.contains('hidden')) this.scrollHint.classList.add('hidden');
  }

  _createCard(event, index) {
    const cat = CAT_COLORS[event.category] || CAT_COLORS.news;
    const gradient = CAT_GRADIENTS[event.category] || CAT_GRADIENTS.news;
    const card = document.createElement('div');
    card.className = 'card';
    card.style.transitionDelay = `${(index % 8) * 0.08}s`;
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

    let cardIndex = 0;
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
      yearEvents.forEach(ev => { cardsRow.appendChild(this._createCard(ev, cardIndex)); cardIndex++; });
      group.appendChild(cardsRow);
      this.track.appendChild(group);
    }

    const line = document.createElement('div');
    line.className = 'timeline-line';
    line.innerHTML = '<div class="timeline-line-inner"></div>';
    this.track.appendChild(line);

    // Setup scroll observers for animations
    this._setupScrollAnimations();
  }

  _setupScrollAnimations() {
    const options = { root: this.container, threshold: 0.1, rootMargin: '0px 100px 0px 100px' };

    // Year groups observer
    const groupObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, options);

    this.track.querySelectorAll('.year-group').forEach(g => groupObserver.observe(g));

    // Cards observer
    const cardObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) entry.target.classList.add('visible');
      });
    }, { root: this.container, threshold: 0.05, rootMargin: '0px 200px 0px 200px' });

    this.track.querySelectorAll('.card').forEach(c => cardObserver.observe(c));
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
    ctx.clearRect(0, 0, this.fxCanvas.width, this.fxCanvas.height);

    for (const p of this.smokeParticles) { p.update(this.currentEra); p.draw(ctx); }
    for (const e of this.embers) { e.update(); e.draw(ctx); }

    // Parallax scroll movement
    const maxScroll = this.container.scrollWidth - this.container.clientWidth;
    if (maxScroll > 0) {
      const scrollProgress = this.scrollLeft / maxScroll;
      const w = this.fxCanvas.width;

      ['back', 'mid', 'front'].forEach(layerName => {
        const layer = layerName === 'back' ? this.parallaxBack : layerName === 'mid' ? this.parallaxMid : this.parallaxFront;
        const speed = layerName === 'back' ? 0.08 : layerName === 'mid' ? 0.2 : 0.4;
        layer.style.transform = `translateX(${-scrollProgress * w * speed}px)`;
      });

      // Float animation
      const time = performance.now() * 0.001;
      Object.values(this.parallaxEls).flat().forEach((el, i) => {
        const floatY = Math.sin(time * 0.35 + i * 0.9) * 5;
        const floatX = Math.cos(time * 0.2 + i * 1.3) * 3;
        el.style.transform = `translate(${floatX}px, ${floatY}px)`;
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
      this._applyEra(this._getEra(YEAR_MIN), true);
      setTimeout(() => this.loadingEl.classList.add('hidden'), 600);
    } catch (err) {
      console.error('Failed to load events:', err);
      const sub = this.loadingEl.querySelector('.loader-sub');
      if (sub) { sub.textContent = 'Error. Reintentando...'; sub.style.color = '#ef4444'; }
      setTimeout(() => this._loadData(), 3000);
    }
  }
}

new App();
