const MODE_SETTINGS = {
  Easy: { baseTime: 5.8, timeFloor: 2.2, timeDropPerLevel: 0.16, minLengthBonus: 0, maxLengthBonus: 2 },
  Medium: { baseTime: 4.5, timeFloor: 1.8, timeDropPerLevel: 0.18, minLengthBonus: 1, maxLengthBonus: 3 },
  Hard: { baseTime: 3.4, timeFloor: 1.4, timeDropPerLevel: 0.2, minLengthBonus: 2, maxLengthBonus: 4 },
};

export class WordManager {
  constructor(words) {
    this.words = [...new Set(words.map((word) => word.trim().toLowerCase()).filter((word) => /^[a-z]+$/.test(word)))];
  }

  getWord(mode, correctWords, combo) {
    const level = Math.max(1, 1 + Math.floor(correctWords / 4));
    const word = this._pickWord(mode, level);
    const timeLimit = this._timeLimit(mode, level, word.length, combo);
    return { word, timeLimit, level };
  }

  _pickWord(mode, level) {
    const settings = MODE_SETTINGS[mode];
    const minLength = 3 + settings.minLengthBonus + Math.floor(level / 2);
    const maxLength = 7 + settings.maxLengthBonus + Math.floor(level / 2);
    let pool = this.words.filter((word) => word.length >= minLength && word.length <= maxLength);
    if (!pool.length) pool = this.words.slice();
    const weighted = [...pool];
    for (const word of pool) {
      if (word.length >= Math.max(6, minLength + 1)) weighted.push(word);
      if (word.length >= Math.max(8, minLength + 3)) weighted.push(word);
    }
    return weighted[(Math.random() * weighted.length) | 0];
  }

  _timeLimit(mode, level, wordLength, combo) {
    const settings = MODE_SETTINGS[mode];
    const timeDrop = settings.timeDropPerLevel * (level - 1);
    const lengthPenalty = Math.max(0, wordLength - 5) * 0.12;
    const comboBonus = Math.min(combo, 10) * 0.03;
    return Math.max(settings.timeFloor, Math.round((settings.baseTime - timeDrop - lengthPenalty - comboBonus) * 100) / 100);
  }
}

export { MODE_SETTINGS };
