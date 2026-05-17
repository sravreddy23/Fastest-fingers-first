import { PlayerStats } from "./player_stats.js";
import { WordManager, MODE_SETTINGS } from "./word_manager.js";
import { UIManager } from "./ui_manager.js";
import { LeaderboardManager } from "./leaderboard_manager.js";
import { AudioManager } from "./audio_manager.js";

const WORDS_URL = "words.txt";
const GAME_STATE = {
  START: "start",
  COUNTDOWN: "countdown",
  PLAYING: "playing",
  PAUSED: "paused",
  GAME_OVER: "game_over",
};

const COLORS = {
  Easy: "#50f0ff",
  Medium: "#17f5a6",
  Hard: "#ff667f",
};

function $(id) {
  return document.getElementById(id);
}

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatLeaderboardEntry(entry, rank) {
  return `
    <div class="leaderboard-item">
      <div>
        <strong>#${rank} ${entry.name || "Player"}</strong>
        <span>${entry.mode || "Mode"}</span>
      </div>
      <div>
        <strong>${entry.score ?? 0}</strong>
        <span>${Number(entry.wpm ?? 0).toFixed(1)} WPM · ${Number(entry.accuracy ?? 0).toFixed(1)}%</span>
      </div>
    </div>
  `;
}

export class Game {
  constructor() {
    this.ui = new UIManager();
    this.audio = new AudioManager();
    this.leaderboard = new LeaderboardManager();
    this.stats = new PlayerStats();
    this.words = [];
    this.wordManager = new WordManager([]);
    this.mode = "Medium";
    this.state = GAME_STATE.START;
    this.currentWord = "ready";
    this.typedText = "";
    this.timeLimit = 4.5;
    this.wordStart = 0;
    this.level = 1;
    this.countdownAt = 0;
    this.pauseAt = 0;
    this.gameStartAt = 0;
    this.feedback = "Ready";
    this.feedbackUntil = 0;
    this.messageColor = COLORS.Medium;
    this.musicPlaying = true;
    this.particles = [];
    this.transitionAlpha = 0;
    this.countdownText = "3";
    this.countdownShownAt = 0;
    this.inputLocked = false;

    this._cacheElements();
    this._bindEvents();
    this._loadWords().then(() => this._renderLeaderboard());
    this._updateModeButtons();
    this._setScreen("start");
    this._tick = this._tick.bind(this);
    requestAnimationFrame(this._tick);
  }

  _cacheElements() {
    this.startScreen = $("startScreen");
    this.gameScreen = $("gameScreen");
    this.pauseOverlay = $("pauseOverlay");
    this.countdownOverlay = $("countdownOverlay");
    this.gameOverScreen = $("gameOverScreen");
    this.typingInput = $("typingInput");
    this.targetWord = $("targetWord");
    this.timerFill = $("timerFill");
    this.scoreValue = $("scoreValue");
    this.wpmValue = $("wpmValue");
    this.accuracyValue = $("accuracyValue");
    this.comboValue = $("comboValue");
    this.timeValue = $("timeValue");
    this.levelValue = $("levelValue");
    this.levelInline = $("levelInline");
    this.modeLabel = $("modeLabel");
    this.messageValue = $("messageValue");
    this.finalScore = $("finalScore");
    this.finalAccuracy = $("finalAccuracy");
    this.finalWpm = $("finalWpm");
    this.finalCombo = $("finalCombo");
    this.musicToggle = $("musicToggle");
    this.musicVolume = $("musicVolume");
  }

  _bindEvents() {
    document.querySelectorAll(".mode-button").forEach((button) => {
      button.addEventListener("click", () => {
        this.mode = button.dataset.mode;
        this._updateModeButtons();
      });
    });

    $("startButton").addEventListener("click", () => this.startGame());
    $("pauseButton").addEventListener("click", () => this.togglePause());
    $("restartButton").addEventListener("click", () => this.restartGame());
    $("menuButton").addEventListener("click", () => this.goToMenu());
    $("resumeButton").addEventListener("click", () => this.resumeGame());
    $("quitButton").addEventListener("click", () => this.goToMenu());
    $("restartFromOver").addEventListener("click", () => this.startCountdown());
    $("backToMenu").addEventListener("click", () => this.goToMenu());

    this.musicToggle.addEventListener("click", async () => {
      this.audio.ensureContext();
      this.audio.startMusic();
      const enabled = this.audio.toggleMusic();
      this.musicToggle.textContent = enabled ? "Music On" : "Music Off";
      await this.audio.ensureContext();
    });

    this.musicVolume.addEventListener("input", () => {
      this.audio.setVolume(Number(this.musicVolume.value) / 100);
    });

    this.typingInput.addEventListener("input", () => this._handleTyping());
    this.typingInput.addEventListener("keydown", (event) => {
      if (event.key === "Enter") {
        event.preventDefault();
        this.submitWord();
      } else if (event.key === "Escape") {
        event.preventDefault();
        this.togglePause();
      }
    });

    window.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        if (this.state === GAME_STATE.PLAYING || this.state === GAME_STATE.PAUSED) {
          event.preventDefault();
          this.togglePause();
        }
      }
    });
  }

  async _loadWords() {
    try {
      const response = await fetch(WORDS_URL);
      const text = await response.text();
      this.words = text.split(/\r?\n/).filter(Boolean);
    } catch {
      this.words = [
        "arcade", "signal", "future", "pixel", "glow", "energy", "matrix", "vector", "storm", "swift",
        "battle", "legend", "rocket", "neon", "phantom", "reactor", "system", "planet", "quantum", "engine",
        "rhythm", "vision", "sprint", "horizon", "crystal", "velocity", "binary", "random", "shadow", "gravity",
        "burst", "cyber", "dynamic", "fusion", "legendary", "chrome", "echo", "digital", "nebula", "momentum",
      ];
    }
    this.wordManager = new WordManager(this.words);
  }

  _updateModeButtons() {
    document.querySelectorAll(".mode-button").forEach((button) => {
      button.classList.toggle("active", button.dataset.mode === this.mode);
    });
  }

  _setScreen(target) {
    [this.startScreen, this.gameScreen].forEach((screen) => screen.classList.remove("screen-visible"));
    this.pauseOverlay.classList.add("hidden");
    this.countdownOverlay.classList.add("hidden");
    this.gameOverScreen.classList.add("hidden");

    if (target === "start") this.startScreen.classList.add("screen-visible");
    if (target === "game") this.gameScreen.classList.add("screen-visible");
    if (target === "pause") this.pauseOverlay.classList.remove("hidden");
    if (target === "countdown") this.countdownOverlay.classList.remove("hidden");
    if (target === "game_over") this.gameOverScreen.classList.remove("hidden");
  }

  startGame() {
    this.audio.ensureContext();
    this.audio.startMusic();
    this.stats.reset(MODE_SETTINGS[this.mode].lives);
    this.feedback = "Get ready";
    this.messageColor = COLORS[this.mode];
    this.particles = [];
    this.transitionAlpha = 0;
    this.startCountdown();
  }

  startCountdown() {
    this.state = GAME_STATE.COUNTDOWN;
    this.countdownAt = performance.now();
    this.countdownShownAt = this.countdownAt;
    this.countdownText = "3";
    this._setScreen("countdown");
    this.messageColor = COLORS[this.mode];
    this._updateCountdownText();
  }

  _beginRound() {
    this.stats.startRun();
    this._spawnNextWord();
    this.state = GAME_STATE.PLAYING;
    this.gameStartAt = performance.now();
    this._setScreen("game");
    this.typingInput.value = "";
    this.typingInput.disabled = false;
    this.typingInput.focus();
  }

  _spawnNextWord() {
    const result = this.wordManager.getWord(this.mode, this.stats.correctWords, this.stats.combo);
    this.currentWord = result.word;
    this.timeLimit = result.timeLimit;
    this.level = result.level;
    this.wordStart = performance.now();
    this.typedText = "";
    this.messageColor = COLORS[this.mode];
    this.feedback = "Keep going";
    this.feedbackUntil = 0;
  }

  _handleTyping() {
    if (this.state !== GAME_STATE.PLAYING || this.inputLocked) {
      return;
    }
    this.typedText = this.typingInput.value.toLowerCase();
    const prefixOk = this.currentWord.startsWith(this.typedText);
    this.messageColor = prefixOk ? COLORS.Medium : COLORS.Hard;
    this.feedback = prefixOk ? "Perfect!" : "Too Slow!";
    this.feedbackUntil = performance.now() + 800;
    if (this.typedText === this.currentWord) {
      this.submitWord();
    }
  }

  submitWord(timeout = false) {
    if (this.state !== GAME_STATE.PLAYING) return;

    const elapsed = (performance.now() - this.wordStart) / 1000;
    const timeLeft = Math.max(0, this.timeLimit - elapsed);
    const typed = this.typingInput.value.trim().toLowerCase();
    const success = !timeout && typed === this.currentWord;
    this.stats.registerAttempt(typed, this.currentWord, success, timeLeft);

    if (success) {
      this.audio.playCorrect();
      this.feedback = this.stats.lastMessage;
      this.messageColor = COLORS.Medium;
      this._spawnParticles();
      this._spawnNextWord();
      this.typingInput.value = "";
    } else {
      this.audio.playWrong();
      this.feedback = timeout ? "Too Slow!" : this.stats.lastMessage;
      this.messageColor = COLORS.Hard;
      this.stats.lives -= 1;
      this.typingInput.value = "";
      if (this.stats.lives <= 0) {
        this.endGame();
        return;
      }
      this._spawnNextWord();
    }
    this.feedbackUntil = performance.now() + 1100;
  }

  _spawnParticles() {
    const centerX = window.innerWidth / 2;
    const centerY = Math.max(250, window.innerHeight * 0.42);
    const palette = ["#50f0ff", "#17f5a6", "#ff57bf", "#ffd05d"];
    for (let i = 0; i < 24; i += 1) {
      const angle = Math.random() * Math.PI * 2;
      const speed = 120 + Math.random() * 200;
      this.particles.push({
        x: centerX,
        y: centerY,
        vx: Math.cos(angle) * speed,
        vy: Math.sin(angle) * speed,
        radius: 2 + Math.random() * 3,
        life: 0.8,
        maxLife: 0.8,
        color: palette[i % palette.length],
      });
    }
  }

  togglePause() {
    if (this.state === GAME_STATE.PLAYING) {
      this.state = GAME_STATE.PAUSED;
      this.pauseAt = performance.now();
      this.typingInput.disabled = true;
      this._setScreen("pause");
      return;
    }
    if (this.state === GAME_STATE.PAUSED) {
      this.resumeGame();
    }
  }

  resumeGame() {
    if (this.state !== GAME_STATE.PAUSED) return;
    const pausedDuration = performance.now() - this.pauseAt;
    this.wordStart += pausedDuration;
    this.countdownAt += pausedDuration;
    this.state = GAME_STATE.PLAYING;
    this.typingInput.disabled = false;
    this.typingInput.focus();
    this._setScreen("game");
  }

  goToMenu() {
    this.state = GAME_STATE.START;
    this.typingInput.value = "";
    this.typingInput.disabled = true;
    this.feedback = "Ready";
    this._setScreen("start");
    this._renderLeaderboard();
  }

  restartGame() {
    this.startGame();
  }

  endGame() {
    this.stats.finishRun();
    this.state = GAME_STATE.GAME_OVER;
    this.audio.playGameOver();
    const entry = {
      name: "Player",
      score: this.stats.score,
      wpm: this.stats.wpm,
      accuracy: this.stats.accuracy,
      mode: this.mode,
      date: new Date().toLocaleDateString(),
    };
    this.leaderboard.saveScore(entry);
    this._renderGameOver();
    this._setScreen("game_over");
  }

  _renderLeaderboard() {
    const scores = this.leaderboard.loadScores();
    const html = scores.length
      ? scores.map((entry, index) => formatLeaderboardEntry(entry, index + 1)).join("")
      : '<div class="leaderboard-item"><strong>No scores yet</strong><span>Start a run to create one.</span></div>';
    $("menuLeaderboard").innerHTML = html;
  }

  _renderGameOver() {
    this.finalScore.textContent = this.stats.score;
    this.finalAccuracy.textContent = `${this.stats.accuracy.toFixed(1)}%`;
    this.finalWpm.textContent = this.stats.wpm.toFixed(1);
    this.finalCombo.textContent = `x${this.stats.bestCombo}`;
    const scores = this.leaderboard.loadScores();
    $("gameOverLeaderboard").innerHTML = scores
      .map((entry, index) => formatLeaderboardEntry(entry, index + 1))
      .join("");
  }

  _updateCountdownText() {
    const elapsed = (performance.now() - this.countdownAt) / 1000;
    if (elapsed < 1) this.countdownText = "3";
    else if (elapsed < 2) this.countdownText = "2";
    else if (elapsed < 3) this.countdownText = "1";
    else this.countdownText = "GO!";
    $("countdownValue").textContent = this.countdownText;
  }

  _tick(now) {
    this.ui.clear();
    this._updateParticles(1 / 60);
    this.ui.drawParticles(this.particles);
    this._updateUI(now);
    requestAnimationFrame(this._tick);
  }

  _updateParticles(dt) {
    this.particles = this.particles.filter((particle) => particle.life > 0);
    for (const particle of this.particles) {
      particle.x += particle.vx * dt;
      particle.y += particle.vy * dt;
      particle.vy += 140 * dt;
      particle.life -= dt;
    }
  }

  _updateUI(now) {
    if (this.state === GAME_STATE.COUNTDOWN) {
      const elapsed = (now - this.countdownAt) / 1000;
      if (elapsed >= 3.8) {
        this._beginRound();
        return;
      }
      this._updateCountdownText();
      $("countdownValue").textContent = this.countdownText;
      return;
    }

    if (this.state === GAME_STATE.PLAYING) {
      const elapsed = (now - this.wordStart) / 1000;
      const remaining = Math.max(0, this.timeLimit - elapsed);
      this.targetWord.textContent = this.currentWord;
      this.timeValue.textContent = `${remaining.toFixed(1)}s`;
      this.scoreValue.textContent = this.stats.score;
      this.wpmValue.textContent = this.stats.wpm.toFixed(1);
      this.accuracyValue.textContent = `${this.stats.accuracy.toFixed(1)}%`;
      this.comboValue.textContent = `x${this.stats.combo}`;
      this.levelValue.textContent = this.level;
      this.levelInline.textContent = this.level;
      this.modeLabel.textContent = `Mode: ${this.mode}`;
      this.messageValue.textContent = this.feedback || this.stats.lastMessage || "Perfect!";
      this.messageValue.style.color = this.messageColor;
      this.timerFill.style.transform = `scaleX(${clamp(remaining / this.timeLimit, 0, 1)})`;
      this.typingInput.value = this.typedText;
      if (remaining <= 0) {
        this.submitWord(true);
      }
      if (this.feedbackUntil && now > this.feedbackUntil) {
        this.feedback = "";
      }
      return;
    }

    if (this.state === GAME_STATE.PAUSED) {
      this.messageValue.textContent = "Paused";
      this.messageValue.style.color = "#ffd05d";
      return;
    }

    if (this.state === GAME_STATE.GAME_OVER) {
      this.messageValue.textContent = "Battle lost";
      this.messageValue.style.color = "#ff667f";
    }
  }
}

window.typingSpeedBattle = null;
