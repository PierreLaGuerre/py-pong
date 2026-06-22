"""Pygame application loop shared by desktop and browser builds."""

from __future__ import annotations

import asyncio
import sys

import pygame

from . import config
from .audio import AudioManager
from .game import Game
from .renderer import Renderer


async def run() -> None:
    pygame.init()
    pygame.display.set_caption("Py-Pong // Matrix Protocol")
    window = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
    canvas = pygame.Surface((config.WIDTH, config.HEIGHT))
    clock = pygame.time.Clock()
    game = Game()
    renderer = Renderer()
    audio = AudioManager()
    running = True

    while running:
        dt = min(clock.tick(config.FPS) / 1000.0, 1 / 30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.start()
                elif event.key == pygame.K_p:
                    game.toggle_pause()
                elif event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_m:
                    audio.toggle_mute()

        keys = pygame.key.get_pressed()
        direction = float(keys[pygame.K_DOWN] or keys[pygame.K_s]) - float(
            keys[pygame.K_UP] or keys[pygame.K_w]
        )
        game.update(dt, direction)
        if game.last_event:
            audio.play(game.last_event)
        renderer.update(dt)
        renderer.draw(canvas, game, audio.muted)
        _fit_canvas(canvas, window)
        pygame.display.flip()

        # Required cooperative yield for Pygbag's browser event loop.
        await asyncio.sleep(0)

    if sys.platform != "emscripten":
        pygame.quit()


def _fit_canvas(canvas: pygame.Surface, window: pygame.Surface) -> None:
    width, height = window.get_size()
    scale = min(width / config.WIDTH, height / config.HEIGHT)
    draw_size = (max(1, int(config.WIDTH * scale)), max(1, int(config.HEIGHT * scale)))
    frame = pygame.transform.smoothscale(canvas, draw_size)
    window.fill(config.BLACK)
    window.blit(frame, ((width - draw_size[0]) // 2, (height - draw_size[1]) // 2))
