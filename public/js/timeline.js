import * as THREE from 'three';

const YEAR_MIN = 1970;
const UNITS_PER_YEAR = 2;
const LANE_HEIGHT = 2.5;

export class Timeline {
  constructor(app, data) {
    this.app = app;
    this.events = data.events;
    this.categories = data.categories;
    this.group = new THREE.Group();
    this.meshes = [];
    this.meshMap = new Map();
    this.isMobile = window.innerWidth < 768;

    this._buildSpine();
    this._buildCategoryLabels();
    this._buildEvents();
  }

  _buildSpine() {
    const totalYears = 2025 - YEAR_MIN;
    const totalWidth = totalYears * UNITS_PER_YEAR;

    const pts = [new THREE.Vector3(-3, 0, 0), new THREE.Vector3(totalWidth + 3, 0, 0)];
    const geo = new THREE.BufferGeometry().setFromPoints(pts);
    const mat = new THREE.LineBasicMaterial({ color: 0xcccccc, transparent: true, opacity: 0.5 });
    this.group.add(new THREE.Line(geo, mat));

    for (let y = YEAR_MIN; y <= 2025; y++) {
      const x = (y - YEAR_MIN) * UNITS_PER_YEAR;
      const major = y % 10 === 0;
      const mid = y % 5 === 0;

      if (major || mid) {
        const h = major ? 0.8 : 0.4;
        const tickPts = [new THREE.Vector3(x, -h, 0), new THREE.Vector3(x, h, 0)];
        const tickGeo = new THREE.BufferGeometry().setFromPoints(tickPts);
        const tickMat = new THREE.LineBasicMaterial({
          color: major ? 0x999999 : 0xdddddd,
          transparent: true,
          opacity: major ? 0.6 : 0.3
        });
        this.group.add(new THREE.Line(tickGeo, tickMat));
      }

      if (major) {
        const canvas = document.createElement('canvas');
        canvas.width = 100;
        canvas.height = 36;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#666666';
        ctx.font = '700 24px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(String(y), 50, 28);

        const tex = new THREE.CanvasTexture(canvas);
        const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.5 });
        const sprite = new THREE.Sprite(spriteMat);
        sprite.position.set(x, -1.8, 0);
        sprite.scale.set(2.5, 0.9, 1);
        this.group.add(sprite);
      }
    }
  }

  _buildCategoryLabels() {
    for (const [key, cat] of Object.entries(this.categories)) {
      const canvas = document.createElement('canvas');
      canvas.width = 200;
      canvas.height = 32;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = cat.color;
      ctx.font = '700 18px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(cat.label, 8, 22);

      const tex = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.45 });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.position.set(-5, cat.yOffset, 0);
      sprite.scale.set(4, 0.6, 1);
      this.group.add(sprite);
    }
  }

  _buildEvents() {
    const sorted = [...this.events].sort((a, b) => a.year - b.year || a.category.localeCompare(b.category));

    const catKeys = Object.keys(this.categories);
    const catIndex = {};
    catKeys.forEach((k, i) => catIndex[k] = i);

    const SEGMENTS = this.isMobile ? 6 : 8;

    const placed = [];

    for (const ev of sorted) {
      const cat = this.categories[ev.category];
      if (!cat) continue;

      const x = (ev.year - YEAR_MIN) * UNITS_PER_YEAR;
      const baseY = cat.yOffset;

      let y = baseY;
      let attempt = 0;
      const minDist = this.isMobile ? 0.55 : 0.45;

      while (attempt < 20) {
        let collision = false;
        for (const p of placed) {
          const dx = Math.abs(x - p.x);
          const dy = Math.abs(y - p.y);
          if (dx < minDist && dy < minDist * 0.8) {
            collision = true;
            break;
          }
        }
        if (!collision) break;
        y += (attempt % 2 === 0 ? 1 : -1) * (Math.ceil(attempt / 2) * 0.35);
        attempt++;
      }

      placed.push({ x, y });

      const radius = this._getRadius(ev);

      const geo = new THREE.SphereGeometry(radius, SEGMENTS, SEGMENTS);
      const mat = this.app.eventMaterials[ev.category].clone();
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(x, y, 0);
      mesh.userData.event = ev;
      mesh.userData.baseY = y;
      mesh.userData.baseScale = radius;
      mesh.userData.radius = radius;

      if (ev.importance >= 3 && !this.isMobile) {
        const glowGeo = new THREE.SphereGeometry(radius * 1.8, SEGMENTS, SEGMENTS);
        const glowMat = new THREE.MeshBasicMaterial({
          color: mat.color,
          transparent: true,
          opacity: 0.1,
          depthWrite: false
        });
        const glow = new THREE.Mesh(glowGeo, glowMat);
        glow.visible = false;
        mesh.add(glow);
        mesh.userData.glow = glow;
      }

      if (ev.importance >= 3) {
        const lineH = Math.abs(y) + 0.5;
        const linePts = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -y, 0)];
        const lineGeo = new THREE.BufferGeometry().setFromPoints(linePts);
        const lineMat = new THREE.LineBasicMaterial({
          color: mat.color,
          transparent: true,
          opacity: 0.1
        });
        mesh.add(new THREE.Line(lineGeo, lineMat));
      }

      this.group.add(mesh);
      this.meshes.push(mesh);
      this.meshMap.set(ev.id, mesh);
    }
  }

  _getRadius(ev) {
    const base = this.isMobile ? 0.08 : 0.1;
    const imp = ev.importance || 1;
    return base + imp * 0.05;
  }

  getMeshes() {
    return this.meshes;
  }

  getVisibleCount(currentYear, filter) {
    let count = 0;
    for (const mesh of this.meshes) {
      const ev = mesh.userData.event;
      if (filter !== 'all' && ev.category !== filter) continue;
      if (ev.year <= currentYear) count++;
    }
    return count;
  }

  update(elapsed, dt) {
    for (const mesh of this.meshes) {
      const ev = mesh.userData.event;
      const baseY = mesh.userData.baseY;

      mesh.position.y = baseY + Math.sin(elapsed * 0.6 + baseY * 1.5) * 0.04;

      const visible = ev.year <= this.app.currentYear;
      const catMatch = this.app.activeFilter === 'all' || ev.category === this.app.activeFilter;
      const targetOpacity = (visible && catMatch) ? 0.85 : 0.06;
      const targetScale = (visible && catMatch) ? 1 : 0.2;

      mesh.material.opacity += (targetOpacity - mesh.material.opacity) * 0.08;

      const s = mesh.scale.x;
      const ns = s + (targetScale - s) * 0.08;
      mesh.scale.setScalar(ns / mesh.userData.baseScale);
    }
  }
}
