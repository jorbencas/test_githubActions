export class UI {
  constructor(app) {
    this.app = app;
    this.panel = document.getElementById('event-panel');
    this.panelClose = document.getElementById('panel-close');
    this.panelCategory = this.panel.querySelector('.panel-category');
    this.panelTitle = this.panel.querySelector('.panel-title');
    this.panelYear = this.panel.querySelector('.panel-year');
    this.panelDescription = this.panel.querySelector('.panel-description');
    this.panelLink = this.panel.querySelector('.panel-link');
    this.filtersEl = document.getElementById('filters');
    this.filterBtns = document.querySelectorAll('.filter-btn');
    this.mobileToggle = document.getElementById('mobile-filters-toggle');

    this._bindFilters();
    this._bindPanel();
    this._bindMobileToggle();
    this._bindKeyboard();
  }

  _bindFilters() {
    this.filterBtns.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.filterBtns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        this.app.activeFilter = btn.dataset.category;
      });
    });
  }

  _bindPanel() {
    this.panelClose.addEventListener('click', (e) => {
      e.stopPropagation();
      this.hidePanel();
      this.app.selectedEvent = null;
    });
  }

  _bindMobileToggle() {
    if (!this.mobileToggle) return;
    this.mobileToggle.addEventListener('click', (e) => {
      e.stopPropagation();
      this.filtersEl.classList.toggle('visible');
      this.mobileToggle.classList.toggle('active');
    });
  }

  _bindKeyboard() {
    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        this.hidePanel();
        this.app.selectedEvent = null;
        if (this.filtersEl.classList.contains('visible')) {
          this.filtersEl.classList.remove('visible');
          if (this.mobileToggle) this.mobileToggle.classList.remove('active');
        }
      }
      if (e.key === 'ArrowUp') {
        this.app.controls.zoomLevel = Math.min(2.2, this.app.controls.zoomLevel + 0.1);
        this.app.controls.targetZ = 25 / this.app.controls.zoomLevel;
      }
      if (e.key === 'ArrowDown') {
        this.app.controls.zoomLevel = Math.max(0.4, this.app.controls.zoomLevel - 0.1);
        this.app.controls.targetZ = 25 / this.app.controls.zoomLevel;
      }

      const keyMap = {
        '1': 'all', '2': 'languages', '3': 'frameworks', '4': 'tools',
        '5': 'ai', '6': 'hardware', '7': 'internet', '8': 'companies', '9': 'opensource'
      };
      if (keyMap[e.key]) {
        this.app.activeFilter = keyMap[e.key];
        this.filterBtns.forEach(b => {
          b.classList.toggle('active', b.dataset.category === keyMap[e.key]);
        });
      }
    });
  }

  isUIElement(clientX, clientY) {
    const els = document.elementsFromPoint(clientX, clientY);
    for (const el of els) {
      if (el.closest('#filters') || el.closest('#event-panel') ||
          el.closest('#header') || el.closest('#stats') ||
          el.closest('#mobile-filters-toggle')) {
        return true;
      }
    }
    return false;
  }

  showPanel(event) {
    const cat = this.app.timeline.categories[event.category];
    this.panelCategory.textContent = cat ? cat.label : event.category;
    this.panelCategory.style.background = `${cat ? cat.color : '#00d4ff'}22`;
    this.panelCategory.style.color = cat ? cat.color : '#00d4ff';
    this.panelTitle.textContent = event.title;
    this.panelYear.textContent = event.year;
    this.panelDescription.textContent = event.description;
    this.panelLink.href = event.url || '#';
    this.panelLink.style.display = event.url ? 'inline-flex' : 'none';
    this.panel.classList.remove('hidden');
  }

  hidePanel() {
    this.panel.classList.add('hidden');
  }
}
