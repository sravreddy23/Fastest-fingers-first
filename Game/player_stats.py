from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
import random


@dataclass
class PlayerStats:
    score: int = 0
    correct_words: int = 0
    total_attempts: int = 0
    total_typed_chars: int = 0
    total_correct_chars: int = 0
    combo: int = 0
    best_combo: int = 0
    lives: int = 3
    started_at: float = 0.0
    finished_at: float = 0.0
    last_message: str = ""
    last_message_kind: str = "neutral"
    history: list[dict] = field(default_factory=list)

    def reset(self, lives: int) -> None:
        self.score = 0
        self.correct_words = 0
        self.total_attempts = 0
        self.total_typed_chars = 0
        self.total_correct_chars = 0
        self.combo = 0
        self.best_combo = 0
        self.lives = lives
        self.started_at = 0.0
        self.finished_at = 0.0
        self.last_message = ""
        self.last_message_kind = "neutral"
        self.history.clear()

    def start_run(self) -> None:
        self.started_at = perf_counter()
        self.finished_at = 0.0

    def finish_run(self) -> None:
        self.finished_at = perf_counter()

    def register_attempt(self, typed: str, target: str, success: bool, time_left: float) -> int:
        self.total_attempts += 1
        self.total_typed_chars += len(typed)
        self.total_correct_chars += sum(1 for typed_char, target_char in zip(typed, target) if typed_char == target_char)

        if success:
            self.correct_words += 1
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            score_delta = 100 + int(time_left * 45) + (self.combo * 15)
            self.score += score_delta
            self.last_message = self._success_message()
            self.last_message_kind = "success"
        else:
            self.combo = 0
            score_delta = 0
            self.last_message = random.choice(["Too Slow!", "Wrong!", "Focus up!"])
            self.last_message_kind = "failure"

        self.history.append(
            {
                "typed": typed,
                "target": target,
                "success": success,
                "time_left": round(time_left, 2),
            }
        )
        return score_delta

    def _success_message(self) -> str:
        if self.combo >= 10:
            return f"Combo x{self.combo}!"
        if self.combo >= 5:
            return f"Combo x{self.combo}!"
        if self.combo >= 3:
            return "Perfect!"
        return random.choice(["Great!", "Nice!", "Clean!", "Sharp!"])

    @property
    def accuracy(self) -> float:
        if self.total_typed_chars == 0:
            return 100.0
        value = (self.total_correct_chars / self.total_typed_chars) * 100.0
        return round(value, 1)

    @property
    def wpm(self) -> float:
        if self.started_at <= 0.0:
            return 0.0
        end_time = self.finished_at if self.finished_at > 0.0 else perf_counter()
        elapsed_minutes = max((end_time - self.started_at) / 60.0, 1 / 60.0)
        words_per_minute = self.correct_words / elapsed_minutes
        return round(words_per_minute, 1)
