"""Small generated retro sound effects; no external audio assets required."""

from __future__ import annotations

import math
from array import array

import pygame


class AudioManager:
    def __init__(self) -> None:
        self.muted = False
        self.available = False
        self.sounds: dict[str, pygame.mixer.Sound] = {}
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22_050, size=-16, channels=1)
            self.sounds = {
                "bounce": self._tone(330, 0.035, 0.20),
                "paddle": self._tone(720, 0.045, 0.24),
                "point": self._tone(180, 0.13, 0.22),
                "game_over": self._tone(95, 0.32, 0.25),
            }
            self.available = True
        except pygame.error:
            # Browsers and headless environments may block audio until interaction.
            self.available = False

    def toggle_mute(self) -> None:
        self.muted = not self.muted

    def play(self, name: str) -> None:
        if self.available and not self.muted and name in self.sounds:
            self.sounds[name].play()

    @staticmethod
    def _tone(frequency: float, duration: float, volume: float) -> pygame.mixer.Sound:
        sample_rate = 22_050
        count = int(sample_rate * duration)
        samples = array("h")
        for index in range(count):
            envelope = 1.0 - index / count
            value = math.sin(2 * math.pi * frequency * index / sample_rate)
            samples.append(int(32_767 * volume * envelope * value))
        return pygame.mixer.Sound(buffer=samples.tobytes())
