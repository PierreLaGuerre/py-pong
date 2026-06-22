"""Py-Pong entry point for desktop and Pygbag/WebAssembly."""

# /// script
# dependencies = ["pygame-ce"]
# ///

import asyncio

import pygame  # noqa: F401 - makes the dependency visible to Pygbag's scanner

from py_pong.app import run

asyncio.run(run())
