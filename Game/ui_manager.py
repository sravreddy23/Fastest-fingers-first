from __future__ import annotations

from dataclasses import dataclass
import math
import random

import pygame

from config import COLORS, WINDOW_HEIGHT, WINDOW_WIDTH


@dataclass
class Particle:
    position: pygame.Vector2
    velocity: pygame.Vector2
    color: tuple[int, int, int]
    life: float
    max_life: float
    radius: float

    def update(self, dt: float) -> None:
        self.position += self.velocity * dt
        self.velocity.y += 55.0 * dt
        self.life -= dt

    def draw(self, surface: pygame.Surface) -> None:
        if self.life <= 0:
            return

        life_ratio = max(self.life / self.max_life, 0.0)
        alpha = int(255 * life_ratio)
        size = max(2, int(self.radius * (0.6 + life_ratio)))

        glow = pygame.Surface((size * 6, size * 6), pygame.SRCALPHA)
        center = glow.get_width() // 2, glow.get_height() // 2
        pygame.draw.circle(glow, (*self.color, alpha // 5), center, size * 2)
        pygame.draw.circle(glow, (*self.color, alpha // 2), center, size)
        surface.blit(glow, glow.get_rect(center=(int(self.position.x), int(self.position.y))))


class UIManager:
    def __init__(self) -> None:
        pygame.font.init()
        title_name = "bahnschrift"
        body_name = "segoe ui"
        fallback_name = "consolas"
        self.title_font = pygame.font.SysFont(title_name, 66, bold=True) or pygame.font.SysFont(fallback_name, 66, bold=True)
        self.header_font = pygame.font.SysFont(title_name, 36, bold=True) or pygame.font.SysFont(fallback_name, 36, bold=True)
        self.panel_font = pygame.font.SysFont(body_name, 24, bold=True) or pygame.font.SysFont(fallback_name, 24, bold=True)
        self.body_font = pygame.font.SysFont(body_name, 20) or pygame.font.SysFont(fallback_name, 20)
        self.small_font = pygame.font.SysFont(body_name, 16) or pygame.font.SysFont(fallback_name, 16)
        self.tiny_font = pygame.font.SysFont(body_name, 14) or pygame.font.SysFont(fallback_name, 14)

    def draw_background(self, surface: pygame.Surface, time_value: float) -> None:
        width, height = surface.get_size()
        surface.fill(COLORS["background"])

        overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        for step in range(7):
            band_y = int((time_value * (20 + step * 3) + step * 85) % (height + 120) - 60)
            color = (10 + step * 3, 14 + step * 4, 32 + step * 6, 15 + step * 5)
            pygame.draw.rect(overlay, color, pygame.Rect(0, band_y, width, 36), border_radius=18)

        pulse_x = int(width * 0.5 + math.sin(time_value * 0.7) * 180)
        pulse_y = int(height * 0.44 + math.cos(time_value * 0.9) * 46)
        self._draw_glow(overlay, (pulse_x, pulse_y), 165, COLORS["purple"], 40)
        self._draw_glow(overlay, (width - 120, 120), 120, COLORS["cyan"], 30)
        self._draw_glow(overlay, (120, height - 120), 150, COLORS["pink"], 24)
        surface.blit(overlay, (0, 0))

        grid_overlay = pygame.Surface((width, height), pygame.SRCALPHA)
        for x in range(0, width, 56):
            alpha = 12 if x % 112 else 26
            pygame.draw.line(grid_overlay, (80, 100, 170, alpha), (x, 0), (x, height), 1)
        for y in range(0, height, 48):
            alpha = 12 if y % 96 else 24
            pygame.draw.line(grid_overlay, (80, 100, 170, alpha), (0, y), (width, y), 1)
        surface.blit(grid_overlay, (0, 0))

        border = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(border, (255, 255, 255, 32), pygame.Rect(12, 12, width - 24, height - 24), width=1, border_radius=24)
        pygame.draw.rect(border, (79, 240, 255, 22), pygame.Rect(22, 22, width - 44, height - 44), width=1, border_radius=20)
        surface.blit(border, (0, 0))

    def draw_panel(self, surface: pygame.Surface, rect: pygame.Rect, accent: tuple[int, int, int], title: str | None = None) -> None:
        shadow_rect = rect.move(0, 8)
        pygame.draw.rect(surface, (0, 0, 0), shadow_rect, border_radius=20)
        shadow_surface = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (10, 14, 26, 235), shadow_surface.get_rect(), border_radius=20)
        pygame.draw.rect(shadow_surface, (*accent, 34), shadow_surface.get_rect(), width=1, border_radius=20)
        surface.blit(shadow_surface, rect.topleft)

        if title:
            header = self.small_font.render(title.upper(), True, accent)
            surface.blit(header, (rect.left + 18, rect.top + 12))

    def draw_button(self, surface: pygame.Surface, rect: pygame.Rect, label: str, accent: tuple[int, int, int], mouse_pos, active: bool = False, disabled: bool = False) -> bool:
        hovered = rect.collidepoint(mouse_pos) and not disabled
        glow_strength = 44 if hovered else 22
        if active:
            glow_strength = 58

        button_surface = pygame.Surface((rect.width + 40, rect.height + 40), pygame.SRCALPHA)
        center = button_surface.get_rect().center
        self._draw_glow(button_surface, center, max(rect.width, rect.height) // 2 + 6, accent, glow_strength)
        surface.blit(button_surface, button_surface.get_rect(center=rect.center))

        fill_color = (22, 30, 52) if not hovered else (32, 42, 72)
        if active:
            fill_color = (28, 44, 78)
        if disabled:
            fill_color = (20, 24, 36)

        pygame.draw.rect(surface, (0, 0, 0), rect.move(0, 5), border_radius=18)
        pygame.draw.rect(surface, fill_color, rect, border_radius=18)
        pygame.draw.rect(surface, (*accent, 220) if hovered or active else (100, 120, 190), rect, width=2, border_radius=18)

        label_color = COLORS["text"] if not disabled else COLORS["muted"]
        text = self.panel_font.render(label, True, label_color)
        text_rect = text.get_rect(center=rect.center)
        surface.blit(text, text_rect)
        return hovered

    def draw_metric_box(self, surface: pygame.Surface, rect: pygame.Rect, label: str, value: str, accent: tuple[int, int, int]) -> None:
        self.draw_panel(surface, rect, accent)
        label_surface = self.tiny_font.render(label.upper(), True, COLORS["muted"])
        value_surface = self.panel_font.render(value, True, COLORS["text"])
        surface.blit(label_surface, (rect.left + 14, rect.top + 12))
        surface.blit(value_surface, (rect.left + 14, rect.top + 34))

    def draw_input_box(self, surface: pygame.Surface, rect: pygame.Rect, typed_text: str, word: str, accent: tuple[int, int, int]) -> None:
        self.draw_panel(surface, rect, accent)
        is_prefix = word.startswith(typed_text)
        border_color = COLORS["success"] if typed_text and is_prefix else COLORS["danger"] if typed_text else accent
        pygame.draw.rect(surface, border_color, rect, width=2, border_radius=18)

        label = self.tiny_font.render("TYPE THE WORD", True, COLORS["muted"])
        surface.blit(label, (rect.left + 16, rect.top + 12))

        typed_color = COLORS["success"] if is_prefix else COLORS["danger"]
        if not typed_text:
            typed_color = COLORS["muted"]

        typed_surface = self.header_font.render(typed_text if typed_text else "...", True, typed_color)
        surface.blit(typed_surface, typed_surface.get_rect(midleft=(rect.left + 18, rect.centery)))

    def draw_center_word(self, surface: pygame.Surface, word: str, typed_text: str, accent: tuple[int, int, int], time_ratio: float, level: int) -> None:
        center_x = WINDOW_WIDTH // 2
        center_y = WINDOW_HEIGHT // 2 - 14
        is_prefix = word.startswith(typed_text)

        word_panel = pygame.Rect(center_x - 210, center_y - 78, 420, 152)
        self.draw_panel(surface, word_panel, accent)

        word_label = self.small_font.render(f"LEVEL {level}", True, COLORS["muted"])
        surface.blit(word_label, (word_panel.left + 18, word_panel.top + 12))

        if typed_text and is_prefix:
            prefix = typed_text
            remainder = word[len(typed_text):]
            prefix_surface = self.title_font.render(prefix, True, COLORS["success"])
            remainder_surface = self.title_font.render(remainder, True, COLORS["text"])
            combined_width = prefix_surface.get_width() + remainder_surface.get_width()
            start_x = center_x - combined_width // 2
            surface.blit(prefix_surface, (start_x, center_y - 20))
            surface.blit(remainder_surface, (start_x + prefix_surface.get_width(), center_y - 20))
        else:
            word_surface = self.title_font.render(word, True, COLORS["text"])
            surface.blit(word_surface, word_surface.get_rect(center=(center_x, center_y - 20)))

        if typed_text and not is_prefix:
            typed_surface = self.body_font.render("Input mismatch - keep typing or backspace", True, COLORS["danger"])
            surface.blit(typed_surface, typed_surface.get_rect(center=(center_x, center_y + 42)))
        else:
            typed_surface = self.body_font.render("Keep the streak alive", True, COLORS["muted"])
            surface.blit(typed_surface, typed_surface.get_rect(center=(center_x, center_y + 42)))

        timer_width = 280
        timer_rect = pygame.Rect(center_x - timer_width // 2, center_y + 58, timer_width, 14)
        pygame.draw.rect(surface, (26, 31, 52), timer_rect, border_radius=8)
        filled = max(0, min(timer_width, int(timer_width * time_ratio)))
        fill_color = COLORS["success"] if time_ratio > 0.55 else COLORS["warning"] if time_ratio > 0.25 else COLORS["danger"]
        pygame.draw.rect(surface, fill_color, pygame.Rect(timer_rect.left, timer_rect.top, filled, timer_rect.height), border_radius=8)
        pygame.draw.rect(surface, (*accent, 180), timer_rect, width=1, border_radius=8)

    def draw_hud(self, surface: pygame.Surface, stats, remaining_time: float, level: int, mode: str, accent: tuple[int, int, int]) -> None:
        hud_rect = pygame.Rect(20, 18, WINDOW_WIDTH - 40, 74)
        self.draw_panel(surface, hud_rect, accent, title=f"MODE {mode.upper()}")

        metrics = [
            ("Score", str(stats.score)),
            ("WPM", f"{stats.wpm:.1f}"),
            ("Accuracy", f"{stats.accuracy:.1f}%"),
            ("Combo", f"x{stats.combo}"),
            ("Time", f"{max(0.0, remaining_time):.1f}s"),
            ("Lives", str(stats.lives)),
        ]

        box_width = 150
        gap = 8
        start_x = 24
        y = 58
        for index, (label, value) in enumerate(metrics):
            rect = pygame.Rect(start_x + index * (box_width + gap), y, box_width, 52)
            self.draw_metric_box(surface, rect, label, value, accent)

        level_surface = self.small_font.render(f"LEVEL {level}", True, accent)
        surface.blit(level_surface, level_surface.get_rect(topright=(WINDOW_WIDTH - 28, 32)))

    def draw_message(self, surface: pygame.Surface, text: str, color: tuple[int, int, int], position, time_value: float, scale_boost: float = 0.0) -> None:
        if not text:
            return
        bounce = 1.0 + math.sin(time_value * 8.0) * 0.03 + scale_boost
        font_size = int(24 * bounce)
        font = pygame.font.SysFont("bahnschrift", font_size, bold=True)
        rendered = font.render(text, True, color)
        glow = pygame.Surface((rendered.get_width() + 40, rendered.get_height() + 40), pygame.SRCALPHA)
        self._draw_glow(glow, glow.get_rect().center, max(rendered.get_width(), rendered.get_height()) // 2 + 10, color, 34)
        surface.blit(glow, glow.get_rect(center=position))
        surface.blit(rendered, rendered.get_rect(center=position))

    def draw_start_screen(self, surface: pygame.Surface, mouse_pos, mode: str, music_volume: float, leaderboard_entries: list[dict], buttons: dict, time_value: float) -> None:
        self.draw_background(surface, time_value)
        title = self.title_font.render("TYPING SPEED BATTLE", True, COLORS["text"])
        subtitle = self.body_font.render("Cyberpunk arcade typing with neon combos and fast reactions", True, COLORS["muted"])
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 92)))
        surface.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 138)))

        accent = COLORS["cyan"]
        left_panel = pygame.Rect(36, 176, 260, 320)
        right_panel = pygame.Rect(704, 176, 260, 320)
        center_panel = pygame.Rect(318, 176, 364, 320)
        self.draw_panel(surface, left_panel, accent, title="HOW TO PLAY")
        self.draw_panel(surface, right_panel, accent, title="LEADERBOARD")
        self.draw_panel(surface, center_panel, accent, title="MODE SELECT")

        instructions = [
            "Type each word before the timer ends.",
            "Build combos to earn more score.",
            "ESC pauses the game instantly.",
            "Choose Easy, Medium, or Hard.",
            "The word gets faster as you level up.",
        ]
        for index, line in enumerate(instructions):
            rendered = self.body_font.render(line, True, COLORS["text"])
            surface.blit(rendered, (left_panel.left + 18, left_panel.top + 44 + index * 38))

        mode_label = self.small_font.render(f"Selected mode: {mode}", True, COLORS["muted"])
        surface.blit(mode_label, (center_panel.left + 18, center_panel.top + 42))

        mode_buttons = [
            ("Easy", buttons["easy"]),
            ("Medium", buttons["medium"]),
            ("Hard", buttons["hard"]),
        ]
        for label, rect in mode_buttons:
            self.draw_button(surface, rect, label, COLORS["cyan"] if label == "Easy" else COLORS["success"] if label == "Medium" else COLORS["danger"], mouse_pos, active=(label == mode))

        self.draw_button(surface, buttons["start"], "START GAME", COLORS["pink"], mouse_pos)

        volume_panel = pygame.Rect(center_panel.left + 18, center_panel.bottom - 100, center_panel.width - 36, 72)
        self.draw_panel(surface, volume_panel, COLORS["purple"], title="MUSIC VOLUME")
        self._draw_volume_slider(surface, buttons["volume_bar"], buttons["volume_knob"], music_volume, mouse_pos)
        volume_text = self.small_font.render(f"{int(music_volume * 100)}%", True, COLORS["text"])
        surface.blit(volume_text, volume_text.get_rect(midright=(volume_panel.right - 16, volume_panel.centery + 1)))

        for row_index, entry in enumerate(leaderboard_entries[:6]):
            text = f"{row_index + 1}. {entry.get('score', 0):>5}  |  {entry.get('wpm', 0):>5.1f} WPM  |  {entry.get('mode', '---')}"
            rendered = self.small_font.render(text, True, COLORS["text"] if row_index < 3 else COLORS["muted"])
            surface.blit(rendered, (right_panel.left + 18, right_panel.top + 46 + row_index * 38))

        footer = self.tiny_font.render("Run it like a modern arcade cabinet: clean, fast, and neon bright.", True, COLORS["muted"])
        surface.blit(footer, footer.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 34)))

    def draw_game_over(self, surface: pygame.Surface, mouse_pos, stats, mode: str, leaderboard_entries: list[dict], buttons: dict, time_value: float) -> None:
        self.draw_background(surface, time_value)
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 110))
        surface.blit(overlay, (0, 0))

        title = self.title_font.render("GAME OVER", True, COLORS["danger"])
        surface.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 84)))

        stats_panel = pygame.Rect(60, 150, 404, 360)
        board_panel = pygame.Rect(536, 150, 404, 360)
        self.draw_panel(surface, stats_panel, COLORS["danger"], title="FINAL STATS")
        self.draw_panel(surface, board_panel, COLORS["cyan"], title="TOP SCORES")

        stats_lines = [
            f"Final score: {stats.score}",
            f"Accuracy: {stats.accuracy:.1f}%",
            f"WPM: {stats.wpm:.1f}",
            f"Best combo: x{stats.best_combo}",
            f"Correct words: {stats.correct_words}",
            f"Mode: {mode}",
        ]
        for index, line in enumerate(stats_lines):
            rendered = self.body_font.render(line, True, COLORS["text"])
            surface.blit(rendered, (stats_panel.left + 20, stats_panel.top + 54 + index * 40))

        if leaderboard_entries:
            for index, entry in enumerate(leaderboard_entries[:7]):
                text = f"{index + 1}. {entry.get('score', 0):>5}  |  {entry.get('wpm', 0):>5.1f} WPM  |  {entry.get('accuracy', 0):>5.1f}%"
                rendered = self.small_font.render(text, True, COLORS["text"] if index < 3 else COLORS["muted"])
                surface.blit(rendered, (board_panel.left + 20, board_panel.top + 52 + index * 38))
        else:
            empty = self.body_font.render("No scores yet.", True, COLORS["muted"])
            surface.blit(empty, (board_panel.left + 20, board_panel.top + 56))

        self.draw_button(surface, buttons["restart"], "RESTART", COLORS["success"], mouse_pos)
        self.draw_button(surface, buttons["menu"], "BACK TO MENU", COLORS["purple"], mouse_pos)

    def draw_pause_overlay(self, surface: pygame.Surface, mouse_pos, buttons: dict, time_value: float) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        pause_title = self.title_font.render("PAUSED", True, COLORS["cyan"])
        surface.blit(pause_title, pause_title.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 110)))

        hint = self.body_font.render("Press ESC to continue the battle", True, COLORS["text"])
        surface.blit(hint, hint.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 58)))

        self.draw_button(surface, buttons["resume"], "RESUME", COLORS["success"], mouse_pos)
        self.draw_button(surface, buttons["quit"], "QUIT TO MENU", COLORS["pink"], mouse_pos)

    def draw_countdown(self, surface: pygame.Surface, value_text: str, time_value: float, accent: tuple[int, int, int]) -> None:
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 92))
        surface.blit(overlay, (0, 0))

        scale = 1.0 + math.sin(time_value * 9.0) * 0.08
        font = pygame.font.SysFont("bahnschrift", int(88 * scale), bold=True)
        rendered = font.render(value_text, True, accent)
        self._draw_glow(surface, (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2), 150, accent, 54)
        surface.blit(rendered, rendered.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 12)))

    def draw_particles(self, surface: pygame.Surface, particles: list[Particle]) -> None:
        for particle in particles:
            particle.draw(surface)

    def draw_transition(self, surface: pygame.Surface, alpha: int) -> None:
        if alpha <= 0:
            return
        fade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        fade.fill((4, 8, 20, alpha))
        surface.blit(fade, (0, 0))

    def _draw_volume_slider(self, surface: pygame.Surface, bar_rect: pygame.Rect, knob_rect: pygame.Rect, value: float, mouse_pos) -> None:
        pygame.draw.rect(surface, (32, 38, 64), bar_rect, border_radius=10)
        fill_width = int(bar_rect.width * value)
        pygame.draw.rect(surface, COLORS["purple"], pygame.Rect(bar_rect.left, bar_rect.top, fill_width, bar_rect.height), border_radius=10)
        knob_x = bar_rect.left + fill_width
        knob_rect.center = (knob_x, bar_rect.centery)
        knob_color = COLORS["text"] if knob_rect.collidepoint(mouse_pos) else COLORS["cyan"]
        pygame.draw.circle(surface, knob_color, knob_rect.center, knob_rect.width // 2)
        pygame.draw.circle(surface, COLORS["background"], knob_rect.center, knob_rect.width // 2 - 3)
        pygame.draw.circle(surface, COLORS["purple"], knob_rect.center, knob_rect.width // 2, width=2)

    def _draw_glow(self, surface: pygame.Surface, center, radius: int, color: tuple[int, int, int], alpha: int) -> None:
        glow = pygame.Surface((radius * 6, radius * 6), pygame.SRCALPHA)
        for step in range(3, 0, -1):
            current_radius = radius * step // 2
            current_alpha = max(2, alpha // (step * 2))
            pygame.draw.circle(glow, (*color, current_alpha), glow.get_rect().center, current_radius)
        surface.blit(glow, glow.get_rect(center=center))
