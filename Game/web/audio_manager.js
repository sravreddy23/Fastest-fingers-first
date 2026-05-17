export class AudioManager {
  constructor() {
    this.audioContext = null;
    this.musicNode = null;
    this.musicGain = null;
    this.musicEnabled = true;
    this.musicVolume = 0.45;
  }

  ensureContext() {
    if (!this.audioContext) {
      const AudioContextClass = window.AudioContext || window.webkitAudioContext;
      this.audioContext = new AudioContextClass();
    }
    if (this.audioContext.state === "suspended") {
      this.audioContext.resume();
    }
    return this.audioContext;
  }

  setVolume(value) {
    this.musicVolume = Math.max(0, Math.min(1, value));
    if (this.musicGain) {
      this.musicGain.gain.value = this.musicEnabled ? this.musicVolume : 0;
    }
  }

  toggleMusic() {
    this.musicEnabled = !this.musicEnabled;
    if (this.musicGain) {
      this.musicGain.gain.value = this.musicEnabled ? this.musicVolume : 0;
    }
    return this.musicEnabled;
  }

  startMusic() {
    const ctx = this.ensureContext();
    if (this.musicNode) return;

    this.musicGain = ctx.createGain();
    this.musicGain.gain.value = this.musicEnabled ? this.musicVolume : 0;
    this.musicGain.connect(ctx.destination);

    const oscillators = [220, 277.18, 329.63, 440];
    oscillators.forEach((frequency, index) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = index % 2 === 0 ? "sine" : "triangle";
      osc.frequency.value = frequency;
      gain.gain.value = 0.04 / (index + 1);
      osc.connect(gain).connect(this.musicGain);
      osc.start();
      this.musicNode = osc;
    });
  }

  stopMusic() {
    if (this.musicNode) {
      try {
        this.musicNode.stop();
      } catch {
        // ignore
      }
      this.musicNode = null;
    }
  }

  _tone(frequency, duration, type = "sine", volume = 0.18) {
    const ctx = this.ensureContext();
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillator.type = type;
    oscillator.frequency.value = frequency;
    gain.gain.value = volume * this.musicVolume;
    oscillator.connect(gain).connect(ctx.destination);
    oscillator.start();
    gain.gain.exponentialRampToValueAtTime(0.0001, ctx.currentTime + duration);
    oscillator.stop(ctx.currentTime + duration);
  }

  playCorrect() {
    this._tone(880, 0.14, "sine", 0.18);
    this._tone(1320, 0.08, "triangle", 0.08);
  }

  playWrong() {
    this._tone(180, 0.16, "square", 0.15);
  }

  playGameOver() {
    this._tone(220, 0.24, "triangle", 0.18);
    this._tone(140, 0.28, "sawtooth", 0.12);
  }
}
