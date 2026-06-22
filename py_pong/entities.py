"""Pure game entities with no dependency on Pygame."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass

from . import config


@dataclass
class Paddle:
    x: float
    y: float
    width: float = config.PADDLE_WIDTH
    height: float = config.PADDLE_HEIGHT
    speed: float = config.PLAYER_SPEED

    @property
    def center_y(self) -> float:
        return self.y + self.height / 2

    def move(self, direction: float, dt: float, field_height: float) -> None:
        self.y += max(-1.0, min(1.0, direction)) * self.speed * dt
        self.y = max(0.0, min(field_height - self.height, self.y))


@dataclass
class Ball:
    x: float
    y: float
    radius: float = config.BALL_RADIUS
    vx: float = 0.0
    vy: float = 0.0

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def reset(self, rng: random.Random, direction: int | None = None) -> None:
        self.x = config.WIDTH / 2
        self.y = config.HEIGHT / 2
        horizontal = direction if direction in (-1, 1) else rng.choice((-1, 1))
        angle = rng.uniform(-0.42, 0.42)
        self.vx = horizontal * config.BALL_START_SPEED * math.cos(angle)
        self.vy = config.BALL_START_SPEED * math.sin(angle)

    def update(self, dt: float) -> None:
        self.x += self.vx * dt
        self.y += self.vy * dt

    def bounce_from(self, paddle: Paddle, horizontal_direction: int) -> None:
        offset = (self.y - paddle.center_y) / (paddle.height / 2)
        offset = max(-1.0, min(1.0, offset))
        angle = offset * config.MAX_BOUNCE_ANGLE
        speed = min(max(self.speed, config.BALL_START_SPEED) * config.BALL_ACCELERATION,
                    config.BALL_MAX_SPEED)
        self.vx = horizontal_direction * speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        self.x = (paddle.x + paddle.width + self.radius
                  if horizontal_direction > 0 else paddle.x - self.radius)


class ComputerPlayer:
    """A deliberately imperfect opponent with reaction delay and dead zone."""

    def __init__(self, paddle: Paddle) -> None:
        self.paddle = paddle
        self.reaction_timer = 0.0
        self.target_y = config.HEIGHT / 2

    def reset(self) -> None:
        self.reaction_timer = 0.0
        self.target_y = config.HEIGHT / 2

    def update(self, ball: Ball, dt: float, field_height: float) -> None:
        self.reaction_timer -= dt
        if self.reaction_timer <= 0:
            # The CPU tracks less accurately while the ball moves away.
            self.target_y = ball.y if ball.vx > 0 else field_height / 2
            self.reaction_timer = config.CPU_REACTION_TIME

        delta = self.target_y - self.paddle.center_y
        direction = 0.0 if abs(delta) <= config.CPU_DEAD_ZONE else (1.0 if delta > 0 else -1.0)
        self.paddle.move(direction, dt, field_height)
