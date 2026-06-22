"""Matrix-inspired presentation layer."""

from __future__ import annotations

import random

import pygame

from . import config
from .game import Game, GameState


class MatrixRain:
    def __init__(self, seed: int = 1337) -> None:
        rng = random.Random(seed)
        self.columns = [
            [x, rng.uniform(-config.HEIGHT, config.HEIGHT), rng.uniform(28, 75), rng.randint(4, 11)]
            for x in range(12, config.WIDTH, 24)
        ]
        self.rng = rng

    def update(self, dt: float) -> None:
        for column in self.columns:
            column[1] += column[2] * dt
            if column[1] > config.HEIGHT + 100:
                column[1] = self.rng.uniform(-220, -30)
                column[2] = self.rng.uniform(28, 75)

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        chars = "01<>/{}[]"
        for x, y, _, length in self.columns:
            for index in range(int(length)):
                alpha = max(15, 75 - index * 7)
                glyph = chars[(int(x) + index * 3) % len(chars)]
                image = font.render(glyph, True, config.MATRIX_GREEN)
                image.set_alpha(alpha)
                surface.blit(image, (x, y - index * 17))


class Renderer:
    def __init__(self) -> None:
        self.font_small = pygame.font.SysFont("consolas,couriernew,monospace", 18)
        self.font_medium = pygame.font.SysFont("consolas,couriernew,monospace", 30, bold=True)
        self.font_large = pygame.font.SysFont("consolas,couriernew,monospace", 72, bold=True)
        self.font_score = pygame.font.SysFont("consolas,couriernew,monospace", 62, bold=True)
        self.rain = MatrixRain()
        self.overlay = pygame.Surface((config.WIDTH, config.HEIGHT), pygame.SRCALPHA)

    def update(self, dt: float) -> None:
        self.rain.update(dt)

    def draw(self, surface: pygame.Surface, game: Game, muted: bool) -> None:
        self._draw_background(surface)
        self.rain.draw(surface, self.font_small)
        self._draw_arena(surface)
        self._draw_paddle(surface, game.player)
        self._draw_paddle(surface, game.cpu_paddle)
        self._draw_ball(surface, game.ball)
        self._draw_hud(surface, game, muted)
        self._draw_state(surface, game)

    @staticmethod
    def _draw_background(surface: pygame.Surface) -> None:
        surface.fill(config.BLACK)
        for y in range(config.HEIGHT):
            strength = int(13 * (1 - abs(y - config.HEIGHT / 2) / (config.HEIGHT / 2)))
            pygame.draw.line(surface, (2, 7 + strength, 5 + strength // 2),
                             (0, y), (config.WIDTH, y))

    @staticmethod
    def _draw_arena(surface: pygame.Surface) -> None:
        arena = (18, 18, config.WIDTH - 36, config.HEIGHT - 36)
        pygame.draw.rect(surface, config.DIM_GREEN, arena, 1)
        for y in range(38, config.HEIGHT - 38, 28):
            pygame.draw.line(surface, config.DIM_GREEN,
                             (config.WIDTH // 2, y), (config.WIDTH // 2, y + 13), 2)

    def _draw_paddle(self, surface: pygame.Surface, paddle: object) -> None:
        rect = pygame.Rect(
            round(paddle.x), round(paddle.y), round(paddle.width), round(paddle.height)
        )
        self._glow_rect(surface, rect, config.MATRIX_GREEN)
        pygame.draw.rect(surface, config.PALE_GREEN, rect, border_radius=3)
        pygame.draw.line(surface, config.WHITE_GREEN, rect.topleft, rect.topright, 2)

    def _draw_ball(self, surface: pygame.Surface, ball: object) -> None:
        center = (round(ball.x), round(ball.y))
        self.overlay.fill((0, 0, 0, 0))
        for radius, alpha in ((28, 14), (20, 28), (14, 65)):
            pygame.draw.circle(self.overlay, (*config.MATRIX_GREEN, alpha), center, radius)
        surface.blit(self.overlay, (0, 0))
        pygame.draw.circle(surface, config.WHITE_GREEN, center, round(ball.radius))

    def _glow_rect(
        self, surface: pygame.Surface, rect: pygame.Rect, color: tuple[int, int, int]
    ) -> None:
        self.overlay.fill((0, 0, 0, 0))
        for amount, alpha in ((14, 18), (8, 35), (4, 70)):
            glow = rect.inflate(amount, amount)
            pygame.draw.rect(self.overlay, (*color, alpha), glow, border_radius=6)
        surface.blit(self.overlay, (0, 0))

    def _draw_hud(self, surface: pygame.Surface, game: Game, muted: bool) -> None:
        player_score = self.font_score.render(f"{game.player_score:02}", True, config.PALE_GREEN)
        cpu_score = self.font_score.render(f"{game.cpu_score:02}", True, config.PALE_GREEN)
        surface.blit(player_score, player_score.get_rect(midtop=(config.WIDTH // 2 - 75, 35)))
        surface.blit(cpu_score, cpu_score.get_rect(midtop=(config.WIDTH // 2 + 75, 35)))

        player = self.font_small.render("USER", True, config.MATRIX_GREEN)
        machine = self.font_small.render("MACHINE", True, config.MATRIX_GREEN)
        surface.blit(player, (38, 32))
        surface.blit(machine, (config.WIDTH - machine.get_width() - 38, 32))
        sound = "AUDIO: OFF" if muted else "AUDIO: ON"
        label = self.font_small.render(f"[M] {sound}", True, config.DIM_GREEN)
        surface.blit(label, (config.WIDTH - label.get_width() - 32, config.HEIGHT - 45))

    def _draw_state(self, surface: pygame.Surface, game: Game) -> None:
        if game.state is GameState.PLAYING:
            return
        self.overlay.fill((0, 6, 3, 185))
        surface.blit(self.overlay, (0, 0))

        if game.state is GameState.READY:
            title, prompt = "SYSTEM READY", "[SPACE] INITIALIZE"
            detail = "W/S OR ARROWS TO MOVE  //  FIRST TO 7"
        elif game.state is GameState.PAUSED:
            title, prompt = "PAUSED", "[P] RESUME"
            detail = "CONNECTION SUSPENDED"
        else:
            title = "YOU WIN" if game.winner == "player" else "MACHINE WINS"
            prompt = "[R] REBOOT"
            detail = f"FINAL SCORE  {game.player_score:02} : {game.cpu_score:02}"

        title_image = self.font_large.render(title, True, config.MATRIX_GREEN)
        prompt_image = self.font_medium.render(prompt, True, config.PALE_GREEN)
        detail_image = self.font_small.render(detail, True, config.DIM_GREEN)
        surface.blit(title_image, title_image.get_rect(center=(config.WIDTH // 2, 245)))
        surface.blit(prompt_image, prompt_image.get_rect(center=(config.WIDTH // 2, 335)))
        surface.blit(detail_image, detail_image.get_rect(center=(config.WIDTH // 2, 382)))
