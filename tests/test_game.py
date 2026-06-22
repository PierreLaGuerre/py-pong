import math

from py_pong import config
from py_pong.entities import Ball, ComputerPlayer, Paddle
from py_pong.game import Game, GameState


def playing_game() -> Game:
    game = Game(seed=7)
    game.start()
    return game


def test_game_starts_ready_and_can_begin() -> None:
    game = Game(seed=1)
    assert game.state is GameState.READY
    game.start()
    assert game.state is GameState.PLAYING


def test_player_paddle_stays_inside_field() -> None:
    paddle = Paddle(0, 0)
    paddle.move(-1, 10, config.HEIGHT)
    assert paddle.y == 0
    paddle.move(1, 10, config.HEIGHT)
    assert paddle.y == config.HEIGHT - paddle.height


def test_wall_collision_reverses_vertical_velocity() -> None:
    game = playing_game()
    game.ball.y = game.ball.radius - 1
    game.ball.vy = -200
    game._collide_with_walls()
    assert game.ball.vy == 200
    assert game.ball.y == game.ball.radius


def test_paddle_impact_changes_bounce_angle() -> None:
    paddle = Paddle(20, 200)
    ball = Ball(35, paddle.y + 12, vx=-350, vy=0)
    ball.bounce_from(paddle, 1)
    assert ball.vx > 0
    assert ball.vy < 0
    assert ball.speed > config.BALL_START_SPEED


def test_scoring_resets_ball_and_sets_delay() -> None:
    game = playing_game()
    game.ball.x = config.WIDTH + game.ball.radius + 1
    game._check_score()
    assert game.player_score == 1
    assert game.ball.x == config.WIDTH / 2
    assert game.ball.vx < 0
    assert game.serve_timer == config.SERVE_DELAY


def test_first_to_seven_ends_game() -> None:
    game = playing_game()
    game.player_score = config.WINNING_SCORE - 1
    game._award_point("player")
    assert game.winner == "player"
    assert game.state is GameState.GAME_OVER


def test_restart_resets_scores_state_and_positions() -> None:
    game = playing_game()
    game.player_score = 4
    game.cpu_score = 2
    game.player.y = 1
    game.restart()
    assert (game.player_score, game.cpu_score) == (0, 0)
    assert game.state is GameState.READY
    assert game.player.center_y == config.HEIGHT / 2


def test_pause_freezes_ball() -> None:
    game = playing_game()
    game.toggle_pause()
    before = (game.ball.x, game.ball.y)
    game.update(0.5, 1)
    assert (game.ball.x, game.ball.y) == before


def test_cpu_is_speed_limited_and_moves_towards_ball() -> None:
    paddle = Paddle(800, 200, speed=300)
    cpu = ComputerPlayer(paddle)
    ball = Ball(600, 500, vx=300)
    before = paddle.y
    cpu.update(ball, 0.1, config.HEIGHT)
    assert paddle.y > before
    assert paddle.y - before <= 30.001


def test_ball_speed_never_exceeds_cap_after_rebounds() -> None:
    paddle = Paddle(20, 200)
    ball = Ball(40, paddle.center_y, vx=config.BALL_MAX_SPEED, vy=200)
    ball.bounce_from(paddle, 1)
    assert math.isclose(ball.speed, config.BALL_MAX_SPEED, rel_tol=1e-9)
