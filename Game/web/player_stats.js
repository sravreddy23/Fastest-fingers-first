export class PlayerStats {
  constructor() {
    this.reset();
  }

  reset(lives = 3) {
    this.score = 0;
    this.correctWords = 0;
    this.totalAttempts = 0;
    this.totalTypedChars = 0;
    this.totalCorrectChars = 0;
    this.combo = 0;
    this.bestCombo = 0;
    this.lives = lives;
    this.startedAt = 0;
    this.finishedAt = 0;
    this.lastMessage = "";
  }

  startRun() {
    this.startedAt = performance.now();
    this.finishedAt = 0;
  }

  finishRun() {
    this.finishedAt = performance.now();
  }

  registerAttempt(typed, target, success, timeLeft) {
    this.totalAttempts += 1;
    this.totalTypedChars += typed.length;
    this.totalCorrectChars += [...typed].reduce((count, char, index) => count + (char === target[index] ? 1 : 0), 0);

    if (success) {
      this.correctWords += 1;
      this.combo += 1;
      this.bestCombo = Math.max(this.bestCombo, this.combo);
      const scoreDelta = 100 + Math.floor(timeLeft * 45) + this.combo * 15;
      this.score += scoreDelta;
      this.lastMessage = this._successMessage();
      return scoreDelta;
    }

    this.combo = 0;
    this.lastMessage = ["Too Slow!", "Wrong!", "Focus up!"][(Math.random() * 3) | 0];
    return 0;
  }

  _successMessage() {
    if (this.combo >= 10) return `Combo x${this.combo}!`;
    if (this.combo >= 5) return `Combo x${this.combo}!`;
    if (this.combo >= 3) return "Perfect!";
    return ["Great!", "Nice!", "Clean!", "Sharp!"][(Math.random() * 4) | 0];
  }

  get accuracy() {
    if (this.totalTypedChars === 0) return 100;
    return Math.round((this.totalCorrectChars / this.totalTypedChars) * 1000) / 10;
  }

  get wpm() {
    if (!this.startedAt) return 0;
    const end = this.finishedAt || performance.now();
    const minutes = Math.max((end - this.startedAt) / 60000, 1 / 60);
    return Math.round((this.correctWords / minutes) * 10) / 10;
  }
}
