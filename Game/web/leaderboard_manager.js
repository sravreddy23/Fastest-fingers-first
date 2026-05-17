const STORAGE_KEY = "typing_speed_battle_leaderboard";

export class LeaderboardManager {
  loadScores() {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      const data = raw ? JSON.parse(raw) : [];
      return Array.isArray(data) ? data.filter(Boolean) : [];
    } catch {
      return [];
    }
  }

  saveScore(entry) {
    const scores = this.loadScores();
    scores.push(entry);
    scores.sort((a, b) => (b.score - a.score) || (b.wpm - a.wpm) || (b.accuracy - a.accuracy));
    const top = scores.slice(0, 10);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(top));
    return top;
  }
}
