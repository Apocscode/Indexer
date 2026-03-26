"""
Watchmaker's Lathe Controller — Indexing / Division Math Engine
Handles all division calculations with Bresenham error distribution
for zero cumulative error over 360°.
"""

import logging
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DivisionResult:
    """Result of a division calculation."""
    divisions: int
    steps_per_division: int     # Base (floor) steps per division
    remainder_steps: int        # Extra steps to distribute via Bresenham
    degrees_per_division: float
    total_steps_per_rev: int
    is_exact: bool              # True if divisions divide evenly


class Indexer:
    """
    Precision indexing / dividing engine.
    
    Calculates exact step counts for any number of divisions,
    using Bresenham-style error accumulation to guarantee that
    after N divisions, the total is exactly `total_steps_per_rev`.
    
    No cumulative rounding error — ever.
    """

    def __init__(self, config):
        self.cfg = config
        self._total_steps = config.total_steps_per_rev
        self._divisions = config.indexing.default_divisions
        self._base_steps = 0
        self._remainder = 0
        self._current_division = 0
        self._position = 0           # Absolute step position
        self._bresenham_error = 0

        self._recalculate()
        logger.info(f"[INDEXER] Init: {self._total_steps} steps/rev, "
                     f"{self._divisions} divisions")

    # ================================================================
    # Division Setup
    # ================================================================
    @property
    def divisions(self) -> int:
        return self._divisions

    @divisions.setter
    def divisions(self, n: int):
        n = max(1, min(n, 1000))
        self._divisions = n
        self._current_division = 0
        self._position = 0
        self._bresenham_error = 0
        self._recalculate()
        logger.info(f"[INDEXER] Divisions set to {n}")

    def calculate(self, n: int) -> DivisionResult:
        """Calculate division parameters without changing state."""
        if n <= 0:
            return DivisionResult(0, 0, 0, 0.0, self._total_steps, False)

        base = self._total_steps // n
        rem = self._total_steps % n
        return DivisionResult(
            divisions=n,
            steps_per_division=base,
            remainder_steps=rem,
            degrees_per_division=360.0 / n,
            total_steps_per_rev=self._total_steps,
            is_exact=(rem == 0)
        )

    # ================================================================
    # Navigation
    # ================================================================
    def next_steps(self) -> int:
        """
        Get steps to the next division (forward).
        Uses Bresenham error accumulation.
        """
        steps = self._base_steps

        self._bresenham_error += self._remainder
        if self._bresenham_error >= self._divisions:
            self._bresenham_error -= self._divisions
            steps += 1

        self._current_division = (self._current_division + 1) % self._divisions
        self._position += steps

        # Wrap at full revolution
        if self._position >= self._total_steps:
            self._position -= self._total_steps
            self._bresenham_error = 0

        return steps

    def prev_steps(self) -> int:
        """Get steps to the previous division (reverse)."""
        # Move backward by recalculating target position
        self._current_division -= 1
        if self._current_division < 0:
            self._current_division = self._divisions - 1

        target_pos, err = self._position_of_division(self._current_division)
        steps = self._position - target_pos
        self._position = target_pos
        self._bresenham_error = err

        if self._position < 0:
            self._position += self._total_steps

        return -steps  # Negative = backward

    def steps_to_division(self, index: int) -> int:
        """Calculate steps to reach a specific division index (0-based)."""
        if index < 0 or index >= self._divisions:
            return 0

        target_pos, err = self._position_of_division(index)
        steps = target_pos - self._position

        # Shortest path
        if steps > self._total_steps // 2:
            steps -= self._total_steps
        elif steps < -(self._total_steps // 2):
            steps += self._total_steps

        self._current_division = index
        self._position = target_pos
        self._bresenham_error = err
        return steps

    def steps_to_home(self) -> int:
        """Steps to return to division 0 (home)."""
        steps = -self._position
        if steps < -(self._total_steps // 2):
            steps += self._total_steps
        return steps

    def reset_home(self):
        """Define current position as home (division 0)."""
        self._current_division = 0
        self._position = 0
        self._bresenham_error = 0
        logger.info("[INDEXER] Home reset")

    # ================================================================
    # Position Queries
    # ================================================================
    @property
    def current_division(self) -> int:
        return self._current_division

    @property
    def position_steps(self) -> int:
        return self._position

    @property
    def degrees(self) -> float:
        return self.steps_to_degrees(self._position)

    # ================================================================
    # Unit Conversions
    # ================================================================
    def degrees_to_steps(self, deg: float) -> int:
        """Convert degrees to the nearest step count."""
        return round((deg / 360.0) * self._total_steps)

    def steps_to_degrees(self, steps: int) -> float:
        """Convert steps to degrees."""
        return (steps / self._total_steps) * 360.0

    def jog_steps(self, degrees: float) -> int:
        """Get step count for a jog increment."""
        return self.degrees_to_steps(degrees)

    # ================================================================
    # Internal
    # ================================================================
    def _recalculate(self):
        self._base_steps = self._total_steps // self._divisions
        self._remainder = self._total_steps % self._divisions

        result = self.calculate(self._divisions)
        logger.debug(f"[INDEXER] {result}")

    def _position_of_division(self, index: int) -> tuple:
        """Calculate the absolute step position and Bresenham error for a division."""
        pos = 0
        err = 0
        for i in range(index):
            pos += self._base_steps
            err += self._remainder
            if err >= self._divisions:
                err -= self._divisions
                pos += 1
        return pos, err
