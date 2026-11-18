"""Pipe OCR from the locally built approved-window helper into policy checks."""

import json
import subprocess
from pathlib import Path

from .core import MemoryError, NotePolicy


class ScreenReader:
    def __init__(self, title):
        if not title.strip():
            raise MemoryError("An exact approved window title is required")
        self.title = title
        self.helper = Path(__file__).resolve().parents[2] / ".neurobrain/window-probe"
        self.window_id = None

    def run(self, *args):
        try:
            result = subprocess.run(
                [str(self.helper), *args], capture_output=True, timeout=25, check=False
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise MemoryError(
                "Screen helper unavailable; build it using Observation Quickstart"
            ) from exc
        if result.returncode or len(result.stdout) > 100000:
            raise MemoryError(
                "Screen observation stopped: check recording permission and approved foreground window"
            )
        try:
            return json.loads(result.stdout)
        except (ValueError, TypeError) as exc:
            raise MemoryError("Invalid screen helper response") from exc

    def read(self):
        result = self.run("--read", self.title)
        if (
            not isinstance(result, dict)
            or type(result.get("window_id")) is not int
            or not isinstance(result.get("text"), str)
        ):
            raise MemoryError("Missing screen observation")
        current = result["window_id"]
        if self.window_id is not None and self.window_id != current:
            raise MemoryError("Approved window changed; start a new session")
        self.window_id = current
        return NotePolicy.decode(result["text"].encode())

    def check(self):
        if self.window_id is None:
            raise MemoryError("No approved observation")
        self.run("--check", self.title, str(self.window_id))
