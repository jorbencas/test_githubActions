export class Controls {
  constructor(app) {
    this.app = app;
    this.targetX = 0;
    this.targetY = 8;
    this.targetZ = 25;
    this.lookAtY = 6;
    this.minX = -5;
    this.maxX = 120;
    this.velocity = 0;
    this.friction = 0.92;
    this.sensitivity = 1.5;
    this.zoomLevel = 1;
    this.minZoom = 0.4;
    this.maxZoom = 2.2;
  }

  setBounds(minX, maxX) {
    this.minX = minX - 5;
    this.maxX = maxX + 5;
  }

  onWheel(e) {
    const delta = e.deltaY * 0.008;
    this.velocity += delta * this.sensitivity;
  }

  onDrag(dx) {
    this.velocity -= dx * this.sensitivity;
  }

  onZoom(delta) {
    this.zoomLevel = Math.max(this.minZoom, Math.min(this.maxZoom, this.zoomLevel + delta));
    this.targetZ = 25 / this.zoomLevel;
  }

  update(dt) {
    this.targetX += this.velocity;
    this.velocity *= this.friction;
    if (Math.abs(this.velocity) < 0.001) this.velocity = 0;
    this.targetX = Math.max(this.minX, Math.min(this.maxX, this.targetX));
    this.targetY = 8 / this.zoomLevel;
    this.lookAtY = 6 / this.zoomLevel;
  }
}
