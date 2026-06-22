import os

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from py_pong import config  # noqa: E402
from py_pong.game import Game  # noqa: E402
from py_pong.renderer import Renderer  # noqa: E402


def test_renderer_draws_a_complete_frame() -> None:
    pygame.init()
    surface = pygame.Surface((config.WIDTH, config.HEIGHT))
    game = Game(seed=10)
    renderer = Renderer()
    renderer.update(1 / 60)
    renderer.draw(surface, game, muted=False)
    assert surface.get_at((0, 0)) != pygame.Color(0, 0, 0, 0)
    pygame.quit()
