import * as THREE from 'three';

const YEAR_MIN = 1970;
const UNITS_PER_YEAR = 2;

export class Timeline {
  constructor(app, data) {
    this.app = app;
    this.events = data.events;
    this.categories = data.categories;
    this.group = new THREE.Group();
    this.meshes = [];
    this.meshMap = new Map();
    this.categoryGroups = {};

    this._buildSpine();
    this._buildCategoryLabels();
    this._buildEvents();
  }

  _buildSpine() {
    const totalYears = 2025 - YEAR_MIN;
    const totalWidth = totalYears * UNITS_PER_YEAR;

    const points = [
      new THREE.Vector3(-2, 0, 0),
      new THREE.Vector3(totalWidth + 2, 0, 0)
    ];
    const lineGeo = new THREE.BufferGeometry().setFromPoints(points);
    const lineMat = new THREE.LineBasicMaterial({
      color: 0x1a1a2e,
      transparent: true,
      opacity: 0.6
    });
    this.group.add(new THREE.Line(lineGeo, lineMat));

    for (let y = YEAR_MIN; y <= 2025; y += 10) {
      const x = (y - YEAR_MIN) * UNITS_PER_YEAR;
      const tickPoints = [
        new THREE.Vector3(x, -0.5, 0),
        new THREE.Vector3(x, 0.5, 0)
      ];
      const tickGeo = new THREE.BufferGeometry().setFromPoints(tickPoints);
      const tickMat = new THREE.LineBasicMaterial({
        color: y % 50 === 0 ? 0x333355 : 0x222244,
        transparent: true,
        opacity: y % 50 === 0 ? 0.8 : 0.4
      });
      this.group.add(new THREE.Line(tickGeo, tickMat));

      if (y % 50 === 0) {
        const canvas = document.createElement('canvas');
        canvas.width = 128;
        canvas.height = 48;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = '#555570';
        ctx.font = '600 28px Inter, sans-serif';
        ctx.textAlign = 'center';
        ctx.fillText(String(y), 64, 34);

        const tex = new THREE.CanvasTexture(canvas);
        const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.6 });
        const sprite = new THREE.Sprite(spriteMat);
        sprite.position.set(x, -1.5, 0);
        sprite.scale.set(3, 1.1, 1);
        this.group.add(sprite);
      }
    }
  }

  _buildCategoryLabels() {
    for (const [key, cat] of Object.entries(this.categories)) {
      const canvas = document.createElement('canvas');
      canvas.width = 256;
      canvas.height = 40;
      const ctx = canvas.getContext('2d');
      ctx.fillStyle = cat.color;
      ctx.font = '600 22px Inter, sans-serif';
      ctx.textAlign = 'left';
      ctx.fillText(cat.label, 10, 28);

      const tex = new THREE.CanvasTexture(canvas);
      const spriteMat = new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.5 });
      const sprite = new THREE.Sprite(spriteMat);
      sprite.position.set(-4, cat.yOffset, 0);
      sprite.scale.set(5, 0.8, 1);
      this.group.add(sprite);
    }
  }

  _buildEvents() {
    const sorted = [...this.events].sort((a, b) => a.year - b.year);
    const yearBuckets = {};

    for (const ev of sorted) {
      if (!yearBuckets[ev.year]) yearBuckets[ev.year] = [];
      yearBuckets[ev.year].push(ev);
    }

    const SEGMENTS = window.innerWidth < 768 ? 6 : 8;
    const RING_SEGMENTS = window.innerWidth < 768 ? 12 : 16;

    for (const ev of sorted) {
      const cat = this.categories[ev.category];
      if (!cat) continue;

      const x = (ev.year - YEAR_MIN) * UNITS_PER_YEAR;
      const bucket = yearBuckets[ev.year];
      const indexInYear = bucket.indexOf(ev);
      const jitter = (indexInYear - (bucket.length - 1) / 2) * 0.5;
      const y = cat.yOffset + jitter;

      const radius = 0.12 + (ev.importance || 1) * 0.08;

      const geo = new THREE.SphereGeometry(radius, SEGMENTS, SEGMENTS);
      const mat = this.app.eventMaterials[ev.category].clone();
      const mesh = new THREE.Mesh(geo, mat);
      mesh.position.set(x, y, 0);
      mesh.userData.event = ev;
      mesh.userData.baseY = y;
      mesh.userData.baseScale = radius;

      const glowGeo = new THREE.SphereGeometry(radius * 2.2, SEGMENTS, SEGMENTS);
      const glowMat = new THREE.MeshBasicMaterial({
        color: mat.color,
        transparent: true,
        opacity: 0.08,
        depthWrite: false
      });
      const glow = new THREE.Mesh(glowGeo, glowMat);
      glow.visible = false;
      mesh.add(glow);
      mesh.userData.glow = glow;

      if (ev.importance >= 3) {
        const ringGeo = new THREE.RingGeometry(radius * 1.3, radius * 1.5, RING_SEGMENTS);
        const ringMat = new THREE.MeshBasicMaterial({
          color: mat.color,
          transparent: true,
          opacity: 0.15,
          side: THREE.DoubleSide,
          depthWrite: false
        });
        const ring = new THREE.Mesh(ringGeo, ringMat);
        ring.rotation.x = -Math.PI / 2;
        mesh.add(ring);
        mesh.userData.ring = ring;
      }

      this.group.add(mesh);
      this.meshes.push(mesh);
      this.meshMap.set(ev.id, mesh);

      if (!this.categoryGroups[ev.category]) {
        this.categoryGroups[ev.category] = [];
      }
      this.categoryGroups[ev.category].push(mesh);
    }
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

      mesh.position.y = baseY + Math.sin(elapsed * 0.8 + baseY * 2) * 0.06;

      const visible = ev.year <= this.app.currentYear;
      const catMatch = this.app.activeFilter === 'all' || ev.category === this.app.activeFilter;
      const targetOpacity = (visible && catMatch) ? 0.9 : 0.05;
      const targetScale = (visible && catMatch) ? 1 : 0.3;

      mesh.material.opacity += (targetOpacity - mesh.material.opacity) * 0.06;

      const s = mesh.scale.x;
      const ts = targetScale;
      const ns = s + (ts - s) * 0.06;
      mesh.scale.setScalar(ns / mesh.userData.baseScale);

      const ring = mesh.userData.ring;
      if (ring) {
        if (visible && catMatch) {
          ring.rotation.z = elapsed * 0.5;
          ring.material.opacity = 0.1 + Math.sin(elapsed * 2 + baseY) * 0.05;
        }
      }
    }
  }
}
