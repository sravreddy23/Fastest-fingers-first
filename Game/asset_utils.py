from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from config import ASSETS_DIR, LEADERBOARD_DIR, LEADERBOARD_FILE, SOUNDS_DIR

SAMPLE_RATE = 44100


def ensure_placeholder_assets() -> None:
    """Create the local folders and generated WAV files if they do not exist."""
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    SOUNDS_DIR.mkdir(parents=True, exist_ok=True)
    LEADERBOARD_DIR.mkdir(parents=True, exist_ok=True)

    if not LEADERBOARD_FILE.exists():
        LEADERBOARD_FILE.write_text("[]", encoding="utf-8")

    sound_files = {
        "correct.wav": _correct_sample,
        "wrong.wav": _wrong_sample,
        "game_over.wav": _game_over_sample,
        "background_music.wav": _background_music_sample,
    }

    for file_name, sample_function in sound_files.items():
        target_path = SOUNDS_DIR / file_name
        if not target_path.exists():
            _write_wav(target_path, sample_function)


def _write_wav(path: Path, sample_function) -> None:
    duration = 1.2 if path.stem != "background_music" else 18.0
    if path.stem == "background_music":
        duration = 24.0

    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(2)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)

        total_frames = int(duration * SAMPLE_RATE)
        frames = bytearray()
        for frame_index in range(total_frames):
            time_value = frame_index / SAMPLE_RATE
            left, right = sample_function(time_value, frame_index, total_frames)
            frames.extend(_pack_frame(left, right))

        wav_file.writeframes(frames)


def _pack_frame(left: float, right: float) -> bytes:
    left = max(-1.0, min(1.0, left))
    right = max(-1.0, min(1.0, right))
    return struct.pack("<hh", int(left * 32767), int(right * 32767))


def _envelope(time_value: float, duration: float, attack: float = 0.04, release: float = 0.12) -> float:
    if time_value < attack:
        return time_value / attack
    if time_value > duration - release:
        return max(0.0, (duration - time_value) / release)
    return 1.0


def _sine(frequency: float, time_value: float) -> float:
    return math.sin(2.0 * math.pi * frequency * time_value)


def _correct_sample(time_value: float, frame_index: int, total_frames: int):
    duration = total_frames / SAMPLE_RATE
    envelope = _envelope(time_value, duration)
    sweep = 760.0 + 220.0 * (time_value / max(duration, 0.001))
    tone = 0.45 * _sine(sweep, time_value) + 0.18 * _sine(sweep * 1.5, time_value)
    shimmer = 0.08 * _sine(3040.0, time_value)
    value = envelope * (tone + shimmer)
    return value * 0.8, value * 0.92


def _wrong_sample(time_value: float, frame_index: int, total_frames: int):
    duration = total_frames / SAMPLE_RATE
    envelope = _envelope(time_value, duration)
    base = 180.0 - 70.0 * (time_value / max(duration, 0.001))
    tone = 0.55 * _sine(base, time_value) + 0.15 * _sine(base * 0.5, time_value)
    buzz = 0.12 * _sine(70.0, time_value)
    value = envelope * (tone + buzz)
    return value * 0.95, value * 0.7


def _game_over_sample(time_value: float, frame_index: int, total_frames: int):
    duration = total_frames / SAMPLE_RATE
    envelope = _envelope(time_value, duration, attack=0.02, release=0.2)
    note_a = 180.0 - 55.0 * (time_value / max(duration, 0.001))
    note_b = note_a * 0.75
    chord = 0.35 * _sine(note_a, time_value) + 0.2 * _sine(note_b, time_value)
    pulse = 0.08 * _sine(55.0, time_value)
    value = envelope * (chord + pulse)
    return value * 0.9, value * 0.9


def _background_music_sample(time_value: float, frame_index: int, total_frames: int):
    duration = total_frames / SAMPLE_RATE
    loop_time = time_value % 8.0
    beat = int(loop_time // 0.5) % 8
    notes = [261.63, 329.63, 392.0, 523.25, 440.0, 349.23, 392.0, 293.66]
    base = notes[beat]
    harmony = notes[(beat + 2) % len(notes)]
    bass = notes[(beat + 4) % len(notes)] / 2.0
    pulse = 0.55 + 0.45 * math.sin(2.0 * math.pi * 0.5 * loop_time)
    lead = 0.12 * _sine(base, loop_time) + 0.06 * _sine(base * 2.0, loop_time)
    pad = 0.08 * _sine(harmony, loop_time + 0.05)
    low = 0.11 * _sine(bass, loop_time)
    airy = 0.025 * _sine(980.0, loop_time)
    value = pulse * (lead + pad + low + airy)
    return value * 0.55, value * 0.62
