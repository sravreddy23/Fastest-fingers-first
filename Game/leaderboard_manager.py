from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


class LeaderboardManager:
    def __init__(self, file_path: Path) -> None:
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load_scores(self) -> list[dict]:
        try:
            raw_data = self.file_path.read_text(encoding="utf-8")
            data = json.loads(raw_data)
        except (FileNotFoundError, json.JSONDecodeError):
            data = []

        if not isinstance(data, list):
            return []
        return [entry for entry in data if isinstance(entry, dict)]

    def save_score(self, score: int, wpm: float, accuracy: float, mode: str, name: str = "Player") -> list[dict]:
        entries = self.load_scores()
        entries.append(
            {
                "name": name,
                "score": int(score),
                "wpm": round(float(wpm), 1),
                "accuracy": round(float(accuracy), 1),
                "mode": mode,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            }
        )
        entries.sort(key=lambda item: (item.get("score", 0), item.get("wpm", 0), item.get("accuracy", 0)), reverse=True)
        entries = entries[:10]
        self.file_path.write_text(json.dumps(entries, indent=2), encoding="utf-8")
        return entries
