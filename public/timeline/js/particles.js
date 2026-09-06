import * as THREE from 'three';

export class Particles {
  constructor(app) {
    this.app = app;
    this.group = new THREE.Group();
    this.ambientParticles = null;
    this.trails = [];
    this.bursts = [];
  }

  init(data) {
    this.app.scene.add(this.group);
    this._createAmbient();
    this._createTrails(data);
  }

  _createAmbient() {
    const isMobile = window.innerWidth < 768;
    const count = isMobile ? 200 : 400;
    const positions = new Float32Array(count * 3);
    const colors = new Float32Array(count * 3);

    const palette = [
      new THREE.Color(0x00d4ff),
      new THREE.Color(0xa855f7),
      new THREE.Color(0x10b981),
      new THREE.Color(0xf59e0b),
      new THREE.Color(0x3b82f6)
    ];

    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 200;
      positions[i * 3 + 1] = Math.random() * 20 - 2;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 40 - 5;

      const c = palette[Math.floor(Math.random() * palette.length)];
      colors[i * 3] = c.r;
      colors[i * 3 + 1] = c.g;
      colors[i * 3 + 2] = c.b;
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3));

    const mat = new THREE.PointsMaterial({
      size: 0.06,
      vertexColors: true,
      transparent: true,
      opacity: 0.35,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true
    });

    this.ambientParticles = new THREE.Points(geo, mat);
    this.group.add(this.ambientParticles);
  }

  _createTrails(data) {
    const catColors = {
      languages: 0x00d4ff, frameworks: 0xa855f7, tools: 0x10b981,
      ai: 0xf59e0b, hardware: 0xef4444, internet: 0x3b82f6,
      companies: 0xec4899, opensource: 0x14b8a6
    };

    const YEAR_MIN = 1970;
    const UNITS_PER_YEAR = 2;

    const byCat = {};
    for (const ev of data.events) {
      if (!byCat[ev.category]) byCat[ev.category] = [];
      byCat[ev.category].push(ev);
    }

    for (const [cat, events] of Object.entries(byCat)) {
      if (events.length < 2) continue;

      const sorted = events.sort((a, b) => a.year - b.year);
      const pts = sorted.map(ev => {
        const x = (ev.year - YEAR_MIN) * UNITS_PER_YEAR;
        const catInfo = data.categories[cat];
        return new THREE.Vector3(x, catInfo.yOffset, 0);
      });

      const curve = new THREE.CatmullRomCurve3(pts, false, 'catmullrom', 0.3);
      const curvePts = curve.getPoints(Math.min(sorted.length * 6, 100));

      const geo = new THREE.BufferGeometry().setFromPoints(curvePts);
      const mat = new THREE.LineBasicMaterial({
        color: catColors[cat] || 0xffffff,
        transparent: true,
        opacity: 0.06,
        depthWrite: false
      });

      const line = new THREE.Line(geo, mat);
      this.group.add(line);
      this.trails.push({ line, cat });
    }
  }

  burstAt(position, color) {
    const count = 20;
    const positions = new Float32Array(count * 3);
    const velocities = [];
    const c = color || new THREE.Color(0x00d4ff);

    for (let i = 0; i < count; i++) {
      positions[i * 3] = position.x;
      positions[i * 3 + 1] = position.y;
      positions[i * 3 + 2] = position.z;

      const theta = Math.random() * Math.PI * 2;
      const phi = Math.random() * Math.PI;
      const speed = 0.5 + Math.random() * 1.5;
      velocities.push({
        x: Math.sin(phi) * Math.cos(theta) * speed,
        y: Math.sin(phi) * Math.sin(theta) * speed,
        z: Math.cos(phi) * speed
      });
    }

    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

    const mat = new THREE.PointsMaterial({
      color: c,
      size: 0.1,
      transparent: true,
      opacity: 1,
      depthWrite: false,
      blending: THREE.AdditiveBlending,
      sizeAttenuation: true
    });

    const points = new THREE.Points(geo, mat);
    this.group.add(points);
    this.bursts.push({ points, velocities, life: 1.0 });

    if (this.bursts.length > 5) {
      const old = this.bursts.shift();
      this.group.remove(old.points);
      old.points.geometry.dispose();
      old.points.material.dispose();
    }
  }

  update(elapsed, dt) {
    if (this.ambientParticles) {
      const pos = this.ambientParticles.geometry.attributes.position.array;
      for (let i = 0; i < pos.length; i += 3) {
        pos[i + 1] += Math.sin(elapsed * 0.3 + pos[i] * 0.1) * 0.001;
        pos[i] += Math.cos(elapsed * 0.2 + pos[i + 2] * 0.1) * 0.0005;
      }
      this.ambientParticles.geometry.attributes.position.needsUpdate = true;
    }

    for (const trail of this.trails) {
      trail.line.material.opacity = 0.04 + Math.sin(elapsed * 0.5) * 0.02;
    }

    for (let i = this.bursts.length - 1; i >= 0; i--) {
      const burst = this.bursts[i];
      burst.life -= dt * 1.5;
      burst.points.material.opacity = Math.max(0, burst.life);

      const pos = burst.points.geometry.attributes.position.array;
      for (let j = 0; j < burst.velocities.length; j++) {
        const v = burst.velocities[j];
        pos[j * 3] += v.x * dt;
        pos[j * 3 + 1] += v.y * dt;
        pos[j * 3 + 2] += v.z * dt;
        v.y -= 1.5 * dt;
      }
      burst.points.geometry.attributes.position.needsUpdate = true;

      if (burst.life <= 0) {
        this.group.remove(burst.points);
        burst.points.geometry.dispose();
        burst.points.material.dispose();
        this.bursts.splice(i, 1);
      }
    }
  }
}
