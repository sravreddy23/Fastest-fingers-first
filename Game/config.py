from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
SOUNDS_DIR = ASSETS_DIR / "sounds"
FONTS_DIR = ASSETS_DIR / "fonts"
LEADERBOARD_DIR = BASE_DIR / "leaderboard"
LEADERBOARD_FILE = LEADERBOARD_DIR / "scores.json"
WORDS_FILE = ASSETS_DIR / "words.txt"

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600
FPS = 60
GAME_TITLE = "Typing Speed Battle"

MODES = {
    "Easy": {
        "base_time": 5.8,
        "time_floor": 2.2,
        "time_drop_per_level": 0.16,
        "lives": 4,
        "min_length_bonus": 0,
        "max_length_bonus": 2,
        "accent": (79, 240, 255),
    },
    "Medium": {
        "base_time": 4.5,
        "time_floor": 1.8,
        "time_drop_per_level": 0.18,
        "lives": 3,
        "min_length_bonus": 1,
        "max_length_bonus": 3,
        "accent": (0, 255, 170),
    },
    "Hard": {
        "base_time": 3.4,
        "time_floor": 1.4,
        "time_drop_per_level": 0.2,
        "lives": 3,
        "min_length_bonus": 2,
        "max_length_bonus": 4,
        "accent": (255, 77, 109),
    },
}

COLORS = {
    "background": (8, 10, 20),
    "background_deep": (4, 6, 14),
    "panel": (16, 20, 36),
    "panel_soft": (25, 30, 52),
    "panel_line": (60, 75, 130),
    "text": (234, 240, 255),
    "muted": (153, 166, 198),
    "success": (0, 255, 170),
    "danger": (255, 95, 122),
    "warning": (255, 206, 92),
    "cyan": (79, 240, 255),
    "pink": (255, 84, 191),
    "purple": (168, 120, 255),
    "shadow": (0, 0, 0),
}
