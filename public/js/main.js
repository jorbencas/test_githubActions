import * as THREE from 'three';
import { Timeline } from './timeline.js';
import { Controls } from './controls.js';
import { UI } from './ui.js';
import { Particles } from './particles.js';
import { AmbientMusic } from './music.js';

const YEAR_MIN = 1970;
const YEAR_MAX = 2025;
const UNITS_PER_YEAR = 2;

class App {
  constructor() {
    this.canvas = document.getElementById('timeline-canvas');
    this.loadingEl = document.getElementById('loading');
    this.yearDisplay = document.getElementById('year-display');
    this.scrollHint = document.getElementById('scroll-hint');
    this.statTotal = document.getElementById('stat-total');
    this.statVisible = document.getElementById('stat-visible');
    this.statYear = document.getElementById('stat-year');

    this.clock = new THREE.Clock();
    this.mouse = new THREE.Vector2(-999, -999);
    this.raycaster = new THREE.Raycaster();

    this.activeFilter = 'all';
    this.currentYear = YEAR_MIN;
    this.hoveredMesh = null;
    this.selectedEvent = null;

    this._dragStartX = 0;
    this._dragStartY = 0;
    this._isDragging = false;
    this._dragDistance = 0;

    this._initRenderer();
    this._initScene();
    this._initLights();
    this._initMaterials();

    this.controls = new Controls(this);
    this.ui = new UI(this);
    this.particles = new Particles(this);
    this.music = new AmbientMusic();

    this._bindEvents();
    this._bindMusicButton();
    this._loadData();
  }

  _initRenderer() {
    this.renderer = new THREE.WebGLRenderer({
      canvas: this.canvas,
      antialias: window.innerWidth >= 768,
      alpha: false,
      powerPreference: 'high-performance'
    });
    this.renderer.setSize(window.innerWidth, window.innerHeight);
    this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, window.innerWidth < 768 ? 1.5 : 2));
    this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
    this.renderer.toneMappingExposure = 1.4;
  }

  _initScene() {
    this.scene = new THREE.Scene();
    this.scene.background = new THREE.Color(0xf0f4f8);
    this.scene.fog = new THREE.FogExp2(0xf0f4f8, 0.012);

    const aspect = window.innerWidth / window.innerHeight;
    this.camera = new THREE.PerspectiveCamera(60, aspect, 0.1, 500);
    this.camera.position.set(0, 8, 25);
    this.camera.lookAt(0, 6, 0);
  }

  _initLights() {
    this.scene.add(new THREE.AmbientLight(0xffffff, 0.9));

    const dir = new THREE.DirectionalLight(0xffffff, 1.0);
    dir.position.set(10, 30, 20);
    this.scene.add(dir);

    const point1 = new THREE.PointLight(0x3182ce, 1.0, 80);
    point1.position.set(0, 12, 10);
    this.scene.add(point1);

    const point2 = new THREE.PointLight(0x8b5cf6, 0.8, 60);
    point2.position.set(-20, 10, -5);
    this.scene.add(point2);
  }

  _initMaterials() {
    this.eventMaterials = {};
    const cats = {
      languages: 0x0ea5e9, frameworks: 0x8b5cf6, tools: 0x10b981,
      ai: 0xf59e0b, hardware: 0xef4444, internet: 0x3b82f6,
      companies: 0xec4899, opensource: 0x14b8a6, news: 0xf97316
    };
    for (const [cat, hex] of Object.entries(cats)) {
      this.eventMaterials[cat] = new THREE.MeshStandardMaterial({
        color: hex,
        emissive: hex,
        emissiveIntensity: 0.3,
        metalness: 0.1,
        roughness: 0.5,
        transparent: true,
        opacity: 0.9
      });
    }
  }

  _bindEvents() {
    window.addEventListener('resize', () => this._onResize());
    window.addEventListener('mousemove', (e) => this._onMouseMove(e));

    this.canvas.addEventListener('wheel', (e) => {
      e.preventDefault();
      this.controls.onWheel(e);
      this._hideScrollHint();
    }, { passive: false });

    let touchStartX = 0;
    let pinchStart = 0;
    this.canvas.addEventListener('touchstart', (e) => {
      if (e.touches.length === 1) {
        touchStartX = e.touches[0].clientX;
        this._dragStartX = e.touches[0].clientX;
        this._dragStartY = e.touches[0].clientY;
        this._dragDistance = 0;
        this._isDragging = true;
      } else if (e.touches.length === 2) {
        pinchStart = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
      }
    }, { passive: true });

    this.canvas.addEventListener('touchmove', (e) => {
      if (e.touches.length === 1 && this._isDragging) {
        const dx = e.touches[0].clientX - touchStartX;
        touchStartX = e.touches[0].clientX;
        this.controls.onDrag(dx * 0.05);
        this._dragDistance += Math.abs(dx);
        this._hideScrollHint();
      } else if (e.touches.length === 2) {
        const dist = Math.hypot(
          e.touches[0].clientX - e.touches[1].clientX,
          e.touches[0].clientY - e.touches[1].clientY
        );
        const delta = pinchStart - dist;
        pinchStart = dist;
        this.controls.onZoom(delta * 0.01);
      }
    }, { passive: true });

    this.canvas.addEventListener('touchend', (e) => {
      if (this._isDragging && this._dragDistance < 10) {
        this._handleClick(this._dragStartX, this._dragStartY);
      }
      this._isDragging = false;
    });

    let mouseDownX = 0;
    let mouseDownY = 0;
    let mouseDownTime = 0;

    this.canvas.addEventListener('mousedown', (e) => {
      mouseDownX = e.clientX;
      mouseDownY = e.clientY;
      mouseDownTime = Date.now();
      this._isDragging = true;
    });

    window.addEventListener('mouseup', (e) => {
      if (this._isDragging) {
        const dx = Math.abs(e.clientX - mouseDownX);
        const dy = Math.abs(e.clientY - mouseDownY);
        const dt = Date.now() - mouseDownTime;
        if (dx < 5 && dy < 5 && dt < 300) {
          this._handleClick(mouseDownX, mouseDownY);
        }
      }
      this._isDragging = false;
    });

    window.addEventListener('mousemove', (e) => {
      if (this._isDragging) {
        const dx = e.movementX || 0;
        this.controls.onDrag(-dx * 0.05);
        this._hideScrollHint();
      }
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight') this.controls.velocity += 2;
      if (e.key === 'ArrowLeft') this.controls.velocity -= 2;
    });
  }

  _handleClick(clientX, clientY) {
    if (this.ui.isUIElement(clientX, clientY)) return;

    this.mouse.x = (clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = -(clientY / window.innerHeight) * 2 + 1;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const meshes = this.timeline ? this.timeline.getMeshes() : [];
    const hits = this.raycaster.intersectObjects(meshes, false);

    if (hits.length > 0) {
      const mesh = hits[0].object;
      const event = mesh.userData.event;
      if (event) {
        this.selectedEvent = event;
        this.ui.showPanel(event);
        this.particles.burstAt(mesh.position.clone(), mesh.material.color);
      }
    } else {
      this.selectedEvent = null;
      this.ui.hidePanel();
    }
  }

  _onResize() {
    const w = window.innerWidth;
    const h = window.innerHeight;
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.renderer.setSize(w, h);
  }

  _onMouseMove(e) {
    this.mouse.x = (e.clientX / window.innerWidth) * 2 - 1;
    this.mouse.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  _updateRaycast() {
    if (this._isDragging) return;

    this.raycaster.setFromCamera(this.mouse, this.camera);
    const meshes = this.timeline ? this.timeline.getMeshes() : [];
    const hits = this.raycaster.intersectObjects(meshes, false);

    if (hits.length > 0) {
      const mesh = hits[0].object;
      if (this.hoveredMesh !== mesh) {
        if (this.hoveredMesh) this._unhover(this.hoveredMesh);
        this.hoveredMesh = mesh;
        this._hover(mesh);
        this.canvas.style.cursor = 'pointer';
      }
    } else {
      if (this.hoveredMesh) {
        this._unhover(this.hoveredMesh);
        this.hoveredMesh = null;
        this.canvas.style.cursor = 'grab';
      }
    }
  }

  _hover(mesh) {
    mesh.userData.origScale = mesh.scale.clone();
    mesh.scale.multiplyScalar(1.6);
    mesh.material.emissiveIntensity = 0.7;
    if (mesh.userData.glow) mesh.userData.glow.visible = true;
  }

  _unhover(mesh) {
    if (mesh.userData.origScale) mesh.scale.copy(mesh.userData.origScale);
    mesh.material.emissiveIntensity = 0.3;
    if (mesh.userData.glow) mesh.userData.glow.visible = false;
  }

  _updateCamera() {
    const t = this.controls;
    this.camera.position.x += (t.targetX - this.camera.position.x) * 0.08;
    this.camera.position.y += (t.targetY - this.camera.position.y) * 0.08;
    this.camera.position.z += (t.targetZ - this.camera.position.z) * 0.08;
    this.camera.lookAt(t.targetX, t.lookAtY, 0);
  }

  _updateYearDisplay() {
    const x = this.camera.position.x;
    const year = Math.round(YEAR_MIN + x / UNITS_PER_YEAR);
    const clamped = Math.max(YEAR_MIN, Math.min(YEAR_MAX, year));
    if (clamped !== this.currentYear) {
      this.currentYear = clamped;
      this.yearDisplay.textContent = clamped;
      this.statYear.textContent = clamped;
      this.yearDisplay.classList.add('active');
      clearTimeout(this._yearTimeout);
      this._yearTimeout = setTimeout(() => {
        this.yearDisplay.classList.remove('active');
      }, 600);
    }
  }

  _updateStats() {
    if (!this.timeline) return;
    const total = this.timeline.events.length;
    const visible = this.timeline.getVisibleCount(this.currentYear, this.activeFilter);
    this.statTotal.textContent = `${total} eventos`;
    this.statVisible.textContent = `${visible} visibles`;
  }

  _hideScrollHint() {
    if (this.scrollHint && !this.scrollHint.classList.contains('hidden')) {
      this.scrollHint.classList.add('hidden');
    }
  }

  _bindMusicButton() {
    const btn = document.getElementById('btn-music');
    if (!btn) return;
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const playing = this.music.toggle();
      btn.classList.toggle('active', playing);
    });
  }

  async _loadData() {
    try {
      const resp = await fetch('data/events.json');
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      this.timeline = new Timeline(this, data);
      this.scene.add(this.timeline.group);

      this.particles.init(data);

      this.statTotal.textContent = `${data.events.length} eventos`;
      this.statVisible.textContent = `${data.events.length} visibles`;

      const totalWidth = (YEAR_MAX - YEAR_MIN) * UNITS_PER_YEAR;
      this.controls.setBounds(0, totalWidth);

      setTimeout(() => {
        this.loadingEl.classList.add('hidden');
        this._animate();
      }, 600);
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

  _animate() {
    requestAnimationFrame(() => this._animate());
    const dt = Math.min(this.clock.getDelta(), 0.1);
    const elapsed = this.clock.elapsedTime;

    this.controls.update(dt);
    this._updateCamera();
    this._updateYearDisplay();
    this._updateRaycast();
    this._updateStats();

    if (this.timeline) this.timeline.update(elapsed, dt);
    this.particles.update(elapsed, dt);

    this.renderer.render(this.scene, this.camera);
  }
}

new App();
