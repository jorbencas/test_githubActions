export class AmbientMusic {
  constructor() {
    this.ctx = null;
    this.isPlaying = false;
    this.nodes = [];
    this.masterGain = null;
  }

  init() {
    if (this.ctx) return;
    this.ctx = new (window.AudioContext || window.webkitAudioContext)();
    this.masterGain = this.ctx.createGain();
    this.masterGain.gain.value = 0;
    this.masterGain.connect(this.ctx.destination);
  }

  toggle() {
    this.init();
    if (this.isPlaying) {
      this.stop();
    } else {
      this.start();
    }
    return this.isPlaying;
  }

  start() {
    if (this.isPlaying) return;
    if (this.ctx.state === 'suspended') this.ctx.resume();

    const now = this.ctx.currentTime;

    const pad = this._createPad(110, 0.08);
    const pad2 = this._createPad(165, 0.05);
    const pad3 = this._createPad(220, 0.04);
    const bass = this._createBass(55, 0.06);

    this._startLFO(pad.gain, 0.06, 0.1, 0.08, now);
    this._startLFO(pad2.gain, 0.03, 0.07, 0.05, now + 1);
    this._startLFO(pad3.gain, 0.02, 0.09, 0.04, now + 2);
    this._startLFO(bass.gain, 0.04, 0.05, 0.06, now);

    this.masterGain.gain.linearRampToValueAtTime(0.7, now + 2);
    this.isPlaying = true;
  }

  stop() {
    if (!this.isPlaying) return;
    const now = this.ctx.currentTime;
    this.masterGain.gain.linearRampToValueAtTime(0, now + 1);
    setTimeout(() => {
      this.nodes.forEach(n => { try { n.stop(); } catch(e) {} });
      this.nodes = [];
    }, 1200);
    this.isPlaying = false;
  }

  _createPad(freq, vol) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();

    osc.type = 'sine';
    osc.frequency.value = freq;

    filter.type = 'lowpass';
    filter.frequency.value = 800;
    filter.Q.value = 1;

    gain.gain.value = vol;

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);
    osc.start();
    this.nodes.push(osc);
    return gain;
  }

  _createBass(freq, vol) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    const filter = this.ctx.createBiquadFilter();

    osc.type = 'triangle';
    osc.frequency.value = freq;

    filter.type = 'lowpass';
    filter.frequency.value = 200;

    gain.gain.value = vol;

    osc.connect(filter);
    filter.connect(gain);
    gain.connect(this.masterGain);
    osc.start();
    this.nodes.push(osc);
    return gain;
  }

  _startLFO(param, base, depth, rate, startTime) {
    const osc = this.ctx.createOscillator();
    const gain = this.ctx.createGain();
    osc.type = 'sine';
    osc.frequency.value = rate;
    gain.gain.value = depth;
    osc.connect(gain);
    gain.connect(param);
    param.value = base;
    osc.start(startTime);
    this.nodes.push(osc);
  }
}
