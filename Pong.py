"""Backward-compatible launcher for the original project filename."""

import asyncio

from py_pong.app import run

if __name__ == "__main__":
    asyncio.run(run())
