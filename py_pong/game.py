"""Game rules and state transitions, kept independent from rendering."""

from __future__ import annotations

import random
from enum import Enum, auto

from . import config
from .entities import Ball, ComputerPlayer, Paddle


class GameState(Enum):
    READY = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()


class Game:
    def __init__(self, seed: int | None = None) -> None:
        self.rng = random.Random(seed)
        paddle_y = (config.HEIGHT - config.PADDLE_HEIGHT) / 2
        self.player = Paddle(config.PADDLE_MARGIN, paddle_y)
        self.cpu_paddle = Paddle(
            config.WIDTH - config.PADDLE_MARGIN - config.PADDLE_WIDTH,
            paddle_y,
            speed=config.CPU_SPEED,
        )
        self.cpu = ComputerPlayer(self.cpu_paddle)
        self.ball = Ball(config.WIDTH / 2, config.HEIGHT / 2)
        self.state = GameState.READY
        self.player_score = 0
        self.cpu_score = 0
        self.serve_timer = 0.0
        self.last_event: str | None = None
        self.ball.reset(self.rng)

    @property
    def winner(self) -> str | None:
        if self.player_score >= config.WINNING_SCORE:
            return "player"
        if self.cpu_score >= config.WINNING_SCORE:
            return "cpu"
        return None

    def start(self) -> None:
        if self.state is GameState.READY:
            self.state = GameState.PLAYING

    def toggle_pause(self) -> None:
        if self.state is GameState.PLAYING:
            self.state = GameState.PAUSED
        elif self.state is GameState.PAUSED:
            self.state = GameState.PLAYING

    def restart(self) -> None:
        self.player_score = 0
        self.cpu_score = 0
        self.state = GameState.READY
        self._center_paddles()
        self.cpu.reset()
        self.ball.reset(self.rng)
        self.serve_timer = 0.0
        self.last_event = None

    def update(self, dt: float, player_direction: float = 0.0) -> None:
        self.last_event = None
        if self.state is not GameState.PLAYING:
            return

        self.player.move(player_direction, dt, config.HEIGHT)
        self.cpu.update(self.ball, dt, config.HEIGHT)
        if self.serve_timer > 0:
            self.serve_timer = max(0.0, self.serve_timer - dt)
            return

        previous_x = self.ball.x
        self.ball.update(dt)
        self._collide_with_walls()
        self._collide_with_paddles(previous_x)
        self._check_score()

    def _collide_with_walls(self) -> None:
        if self.ball.y - self.ball.radius <= 0 and self.ball.vy < 0:
            self.ball.y = self.ball.radius
            self.ball.vy *= -1
            self.last_event = "bounce"
        elif self.ball.y + self.ball.radius >= config.HEIGHT and self.ball.vy > 0:
            self.ball.y = config.HEIGHT - self.ball.radius
            self.ball.vy *= -1
            self.last_event = "bounce"

    def _collide_with_paddles(self, previous_x: float) -> None:
        ball = self.ball
        player_front = self.player.x + self.player.width
        touches_player = (
            self.player.y - ball.radius
            <= ball.y
            <= self.player.y + self.player.height + ball.radius
        )
        if (
            ball.vx < 0
            and previous_x - ball.radius >= player_front
            and ball.x - ball.radius <= player_front
            and touches_player
        ):
            ball.bounce_from(self.player, 1)
            self.last_event = "paddle"

        cpu_front = self.cpu_paddle.x
        touches_cpu = (
            self.cpu_paddle.y - ball.radius
            <= ball.y
            <= self.cpu_paddle.y + self.cpu_paddle.height + ball.radius
        )
        if (
            ball.vx > 0
            and previous_x + ball.radius <= cpu_front
            and ball.x + ball.radius >= cpu_front
            and touches_cpu
        ):
            ball.bounce_from(self.cpu_paddle, -1)
            self.last_event = "paddle"

    def _check_score(self) -> None:
        if self.ball.x + self.ball.radius < 0:
            self._award_point("cpu")
        elif self.ball.x - self.ball.radius > config.WIDTH:
            self._award_point("player")

    def _award_point(self, scorer: str) -> None:
        if scorer == "player":
            self.player_score += 1
            serve_direction = -1
        else:
            self.cpu_score += 1
            serve_direction = 1
        self.last_event = "point"

        if self.winner:
            self.state = GameState.GAME_OVER
            self.last_event = "game_over"
            return

        self.ball.reset(self.rng, serve_direction)
        self.serve_timer = config.SERVE_DELAY

    def _center_paddles(self) -> None:
        center_y = (config.HEIGHT - config.PADDLE_HEIGHT) / 2
        self.player.y = center_y
        self.cpu_paddle.y = center_y
