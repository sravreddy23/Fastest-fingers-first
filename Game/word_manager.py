from __future__ import annotations

import random
from pathlib import Path

from config import MODES


class WordManager:
    def __init__(self, words_file: Path) -> None:
        self.words_file = Path(words_file)
        self.all_words = self._load_words()

    def _load_words(self) -> list[str]:
        try:
            raw_words = self.words_file.read_text(encoding="utf-8").splitlines()
        except FileNotFoundError:
            raw_words = []

        words = []
        for word in raw_words:
            cleaned = word.strip().lower()
            if cleaned and cleaned.isalpha():
                words.append(cleaned)

        if len(words) < 50:
            words.extend(self._fallback_words())

        return sorted(set(words))

    def _fallback_words(self) -> list[str]:
        return [
            "arcade", "signal", "future", "pixel", "glow", "energy", "matrix", "vector",
            "storm", "swift", "battle", "legend", "rocket", "neon", "phantom", "reactor",
            "system", "planet", "quantum", "engine", "gamer", "rhythm", "vision", "sprint",
            "horizon", "crystal", "velocity", "launch", "binary", "random", "secure",
            "shadow", "gravity", "burst", "cyber", "dynamic", "fusion", "legendary",
            "chrome", "signal", "echo", "digital", "nebula", "momentum", "impact", "drift",
            "tunnel", "freedom", "command", "focus", "precision", "power", "vertex", "charge",
            "hyper", "cluster", "connect", "stream", "zenith", "surge", "plasma", "orbit",
        ]

    def get_word(self, mode: str, correct_words: int, combo: int) -> tuple[str, float, int]:
        mode_config = MODES[mode]
        level = max(1, 1 + correct_words // 4)
        word = self._pick_word(mode, level)
        time_limit = self._time_limit(mode_config, level, len(word), combo)
        return word, time_limit, level

    def _pick_word(self, mode: str, level: int) -> str:
        mode_config = MODES[mode]
        min_length = 3 + mode_config["min_length_bonus"] + (level // 2)
        max_length = 7 + mode_config["max_length_bonus"] + (level // 2)
        pool = [word for word in self.all_words if min_length <= len(word) <= max_length]

        if not pool:
            pool = self.all_words[:]

        weighted_pool = pool[:]
        for word in pool:
            if len(word) >= max(6, min_length + 1):
                weighted_pool.append(word)
            if len(word) >= max(8, min_length + 3):
                weighted_pool.append(word)

        return random.choice(weighted_pool)

    def _time_limit(self, mode_config: dict, level: int, word_length: int, combo: int) -> float:
        base_time = mode_config["base_time"]
        time_drop = mode_config["time_drop_per_level"] * (level - 1)
        length_penalty = max(0, word_length - 5) * 0.12
        combo_bonus = min(combo, 10) * 0.03
        time_limit = base_time - time_drop - length_penalty - combo_bonus
        return max(mode_config["time_floor"], round(time_limit, 2))
