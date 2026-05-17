from __future__ import annotations

import math
import random
from time import perf_counter

import pygame

from asset_utils import ensure_placeholder_assets
from config import COLORS, FPS, GAME_TITLE, LEADERBOARD_FILE, MODES, SOUNDS_DIR, WINDOW_HEIGHT, WINDOW_WIDTH, WORDS_FILE
from leaderboard_manager import LeaderboardManager
from player_stats import PlayerStats
from ui_manager import Particle, UIManager
from word_manager import WordManager


class Game:
    def __init__(self) -> None:
        ensure_placeholder_assets()

        pygame.init()
        self.audio_enabled = self._init_audio()

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        pygame.key.set_repeat(0)

        self.clock = pygame.time.Clock()
        self.ui = UIManager()
        self.word_manager = WordManager(WORDS_FILE)
        self.leaderboard = LeaderboardManager(LEADERBOARD_FILE)
        self.stats = PlayerStats()

        self.state = "start"
        self.running = True
        self.mode = "Medium"
        self.score_saved = False

        self.music_volume = 0.45
        self.volume_dragging = False
        self.time_value = 0.0
        self.transition_alpha = 0
        self.feedback_text = ""
        self.feedback_color = COLORS["text"]
        self.feedback_until = 0.0
        self.pause_snapshot_time = 0.0

        self.current_word = ""
        self.typed_text = ""
        self.time_limit = 0.0
        self.word_started_at = 0.0
        self.level = 1

        self.countdown_started_at = 0.0
        self.particles: list[Particle] = []

        self.buttons = {
            "easy": pygame.Rect(354, 242, 90, 50),
            "medium": pygame.Rect(456, 242, 120, 50),
            "hard": pygame.Rect(588, 242, 90, 50),
            "start": pygame.Rect(404, 406, 192, 58),
            "restart": pygame.Rect(352, 432, 140, 52),
            "menu": pygame.Rect(512, 432, 168, 52),
            "resume": pygame.Rect(350, 350, 140, 52),
            "quit": pygame.Rect(510, 350, 170, 52),
            "volume_bar": pygame.Rect(342, 432, 260, 10),
            "volume_knob": pygame.Rect(0, 0, 26, 26),
        }

        self.set_music_volume(self.music_volume)
        self._play_music()
        self._set_text_input(False)

    def _init_audio(self) -> bool:
        try:
            pygame.mixer.init()
            pygame.mixer.set_num_channels(12)
        except pygame.error:
            return False

        self.sounds: dict[str, pygame.mixer.Sound] = {}
        sound_map = {
            "correct": SOUNDS_DIR / "correct.wav",
            "wrong": SOUNDS_DIR / "wrong.wav",
            "game_over": SOUNDS_DIR / "game_over.wav",
        }
        for name, path in sound_map.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(str(path))
            except pygame.error:
                pass
        return True

    def _play_music(self) -> None:
        if not self.audio_enabled:
            return
        try:
            pygame.mixer.music.load(str(SOUNDS_DIR / "background_music.wav"))
            pygame.mixer.music.play(-1)
        except pygame.error:
            self.audio_enabled = False

    def set_music_volume(self, value: float) -> None:
        self.music_volume = max(0.0, min(1.0, value))
        if self.audio_enabled:
            try:
                pygame.mixer.music.set_volume(self.music_volume)
            except pygame.error:
                pass

    def _set_text_input(self, enabled: bool) -> None:
        if enabled:
            pygame.key.start_text_input()
        else:
            pygame.key.stop_text_input()

    def _play_sound(self, name: str) -> None:
        if not self.audio_enabled:
            return
        sound = self.sounds.get(name)
        if sound:
            sound.play()

    def run(self) -> None:
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            self._handle_events()
            self._update(dt)
            self._draw()
            pygame.display.flip()

        pygame.quit()

    def _handle_events(self) -> None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                continue

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self._handle_mouse_down(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.volume_dragging = False
            elif event.type == pygame.MOUSEMOTION and self.volume_dragging:
                self._set_volume_from_mouse(event.pos)
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            elif event.type == pygame.TEXTINPUT and self.state == "playing":
                self._handle_text_input(event.text)

    def _handle_keydown(self, event: pygame.event.Event) -> None:
        if event.key == pygame.K_ESCAPE:
            if self.state == "playing":
                self._pause_game()
            elif self.state == "paused":
                self._resume_game()
            return

        if self.state != "playing":
            return

        if event.key == pygame.K_BACKSPACE:
            self.typed_text = self.typed_text[:-1]
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            self._submit_attempt()

    def _handle_text_input(self, text: str) -> None:
        if self.state != "playing":
            return

        cleaned = text.lower()
        if not cleaned.strip():
            return

        self.typed_text += cleaned
        if self.typed_text == self.current_word:
            self._submit_attempt()

    def _handle_mouse_down(self, position) -> None:
        if self.state == "start":
            if self.buttons["easy"].collidepoint(position):
                self.mode = "Easy"
            elif self.buttons["medium"].collidepoint(position):
                self.mode = "Medium"
            elif self.buttons["hard"].collidepoint(position):
                self.mode = "Hard"
            elif self.buttons["start"].collidepoint(position):
                self._begin_countdown()
            elif self.buttons["volume_bar"].inflate(20, 18).collidepoint(position):
                self.volume_dragging = True
                self._set_volume_from_mouse(position)
        elif self.state == "paused":
            if self.buttons["resume"].collidepoint(position):
                self._resume_game()
            elif self.buttons["quit"].collidepoint(position):
                self._go_to_menu()
        elif self.state == "game_over":
            if self.buttons["restart"].collidepoint(position):
                self._begin_countdown()
            elif self.buttons["menu"].collidepoint(position):
                self._go_to_menu()

    def _set_volume_from_mouse(self, position) -> None:
        bar = self.buttons["volume_bar"]
        ratio = (position[0] - bar.left) / max(1, bar.width)
        self.set_music_volume(ratio)

    def _begin_countdown(self) -> None:
        self.stats.reset(MODES[self.mode]["lives"])
        self.particles.clear()
        self.typed_text = ""
        self.current_word = ""
        self.time_limit = 0.0
        self.word_started_at = 0.0
        self.level = 1
        self.feedback_text = ""
        self.feedback_until = 0.0
        self.score_saved = False
        self.countdown_started_at = perf_counter()
        self.state = "countdown"
        self.transition_alpha = 210
        self._set_text_input(False)

    def _start_round(self) -> None:
        self.stats.start_run()
        self._spawn_next_word()
        self.state = "playing"
        self.transition_alpha = 120
        self._set_text_input(True)

    def _spawn_next_word(self) -> None:
        self.current_word, self.time_limit, self.level = self.word_manager.get_word(self.mode, self.stats.correct_words, self.stats.combo)
        self.word_started_at = perf_counter()
        self.typed_text = ""

    def _submit_attempt(self, timeout: bool = False) -> None:
        if self.state != "playing" or not self.current_word:
            return

        now = perf_counter()
        remaining = max(0.0, self.time_limit - (now - self.word_started_at))
        typed = self.typed_text.strip().lower()
        success = (typed == self.current_word) and not timeout

        self.stats.register_attempt(typed, self.current_word, success, remaining if not timeout else 0.0)
        if success:
            self._play_sound("correct")
            self.feedback_text = self.stats.last_message
            self.feedback_color = COLORS["success"]
            self.feedback_until = now + 1.0
            self._spawn_particles()
            self._spawn_next_word()
            self.transition_alpha = min(90, self.transition_alpha + 20)
        else:
            self._play_sound("wrong")
            self.feedback_text = "Too Slow!" if timeout else self.stats.last_message
            self.feedback_color = COLORS["danger"]
            self.feedback_until = now + 1.0
            self.stats.lives -= 1
            if self.stats.lives <= 0:
                self._trigger_game_over()
                return
            self._spawn_next_word()
            self.transition_alpha = min(100, self.transition_alpha + 25)

    def _spawn_particles(self) -> None:
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2 - 14
        accent = MODES[self.mode]["accent"]
        for _ in range(24):
            angle = random.uniform(0.0, 6.28318)
            speed = random.uniform(120.0, 320.0)
            velocity = pygame.Vector2(math.cos(angle) * speed, math.sin(angle) * speed)
            color = random.choice([accent, COLORS["cyan"], COLORS["success"], COLORS["pink"]])
            self.particles.append(
                Particle(
                    position=pygame.Vector2(center_x, center_y),
                    velocity=velocity,
                    color=color,
                    life=random.uniform(0.35, 0.85),
                    max_life=0.85,
                    radius=random.uniform(2.0, 4.2),
                )
            )

    def _pause_game(self) -> None:
        if self.state != "playing":
            return
        self.state = "paused"
        self.pause_snapshot_time = perf_counter()
        self.transition_alpha = 160
        self._set_text_input(False)

    def _resume_game(self) -> None:
        if self.state != "paused":
            return
        paused_for = perf_counter() - self.pause_snapshot_time
        self.word_started_at += paused_for
        if self.feedback_until > 0.0:
            self.feedback_until += paused_for
        self.state = "playing"
        self.transition_alpha = 90
        self._set_text_input(True)

    def _go_to_menu(self) -> None:
        self.state = "start"
        self.typed_text = ""
        self.feedback_text = ""
        self.feedback_until = 0.0
        self.current_word = ""
        self._set_text_input(False)
        self.transition_alpha = 150

    def _trigger_game_over(self) -> None:
        self.stats.finish_run()
        self.state = "game_over"
        self.feedback_text = ""
        self._set_text_input(False)
        self.transition_alpha = 220
        self._play_sound("game_over")
        if not self.score_saved:
            self.leaderboard.save_score(self.stats.score, self.stats.wpm, self.stats.accuracy, self.mode)
            self.score_saved = True

    def _update(self, dt: float) -> None:
        self.time_value += dt
        if self.transition_alpha > 0:
            self.transition_alpha = max(0, self.transition_alpha - int(280 * dt))

        if self.state == "countdown":
            elapsed = perf_counter() - self.countdown_started_at
            if elapsed >= 3.8:
                self._start_round()
        elif self.state == "playing":
            elapsed = perf_counter() - self.word_started_at
            remaining = self.time_limit - elapsed
            if remaining <= 0:
                self._submit_attempt(timeout=True)

            if self.feedback_until and perf_counter() > self.feedback_until:
                self.feedback_text = ""

            self._update_particles(dt)
        elif self.state == "paused":
            if self.feedback_until and perf_counter() > self.feedback_until:
                self.feedback_text = ""
        elif self.state == "game_over":
            if self.feedback_until and perf_counter() > self.feedback_until:
                self.feedback_text = ""

    def _update_particles(self, dt: float) -> None:
        alive_particles: list[Particle] = []
        for particle in self.particles:
            particle.update(dt)
            if particle.life > 0:
                alive_particles.append(particle)
        self.particles = alive_particles

    def _draw(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        accent = MODES[self.mode]["accent"]

        if self.state == "start":
            leaderboard_entries = self.leaderboard.load_scores()
            self.ui.draw_start_screen(self.screen, mouse_pos, self.mode, self.music_volume, leaderboard_entries, self.buttons, self.time_value)
        elif self.state == "countdown":
            self.ui.draw_background(self.screen, self.time_value)
            title = self.ui.title_font.render(GAME_TITLE, True, COLORS["text"])
            self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 112)))
            subtitle = self.ui.body_font.render("Get ready for a neon word duel", True, COLORS["muted"])
            self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 156)))
            self._draw_countdown_value()
        elif self.state in ("playing", "paused"):
            self._draw_play_scene(mouse_pos, accent)
            if self.state == "paused":
                self.ui.draw_pause_overlay(self.screen, mouse_pos, self.buttons, self.time_value)
        elif self.state == "game_over":
            leaderboard_entries = self.leaderboard.load_scores()
            self.ui.draw_game_over(self.screen, mouse_pos, self.stats, self.mode, leaderboard_entries, self.buttons, self.time_value)

        self.ui.draw_transition(self.screen, self.transition_alpha)

    def _draw_play_scene(self, mouse_pos, accent) -> None:
        self.ui.draw_background(self.screen, self.time_value)
        remaining = max(0.0, self.time_limit - (perf_counter() - self.word_started_at))
        self.ui.draw_hud(self.screen, self.stats, remaining, self.level, self.mode, accent)
        self.ui.draw_center_word(self.screen, self.current_word, self.typed_text, accent, remaining / max(0.001, self.time_limit), self.level)

        input_rect = pygame.Rect(250, 420, 500, 84)
        self.ui.draw_input_box(self.screen, input_rect, self.typed_text, self.current_word, accent)

        feedback_color = self.feedback_color if self.feedback_text else COLORS["muted"]
        feedback_position = (WINDOW_WIDTH // 2, 532)
        if self.feedback_text:
            self.ui.draw_message(self.screen, self.feedback_text, feedback_color, feedback_position, self.time_value, scale_boost=0.02)

        self.ui.draw_particles(self.screen, self.particles)

        hint = self.ui.small_font.render("Enter submits the word. Backspace edits. ESC pauses.", True, COLORS["muted"])
        self.screen.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 24)))

    def _draw_countdown_value(self) -> None:
        elapsed = perf_counter() - self.countdown_started_at
        if elapsed < 1.0:
            value = "3"
            accent = COLORS["cyan"]
        elif elapsed < 2.0:
            value = "2"
            accent = COLORS["success"]
        elif elapsed < 3.0:
            value = "1"
            accent = COLORS["pink"]
        else:
            value = "GO!"
            accent = COLORS["warning"]
        self.ui.draw_countdown(self.screen, value, self.time_value, accent)


if __name__ == "__main__":
    Game().run()
