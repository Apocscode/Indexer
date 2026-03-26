"""
Watchmaker's Lathe Controller — Reusable GUI Widgets
Custom tkinter widgets: RPM gauge, RPM graph, division ring, status bar.
"""

import tkinter as tk
from tkinter import font as tkfont
import math
import time
from collections import deque


# ============================================================================
# Color Themes
# ============================================================================
THEMES = {
    "dark": {
        "bg": "#1a1a2e",
        "bg2": "#16213e",
        "fg": "#e0e0e0",
        "fg2": "#a0a0a0",
        "accent": "#0f3460",
        "highlight": "#e94560",
        "green": "#00d474",
        "yellow": "#f0c030",
        "red": "#e94560",
        "blue": "#4da6ff",
        "gauge_bg": "#0a0a1a",
        "gauge_arc": "#333366",
        "gauge_needle": "#e94560",
        "graph_line": "#4da6ff",
        "graph_grid": "#222244",
        "button_bg": "#0f3460",
        "button_fg": "#ffffff",
        "button_active": "#1a5276",
        "entry_bg": "#16213e",
        "entry_fg": "#e0e0e0",
    },
    "light": {
        "bg": "#f0f0f0",
        "bg2": "#ffffff",
        "fg": "#222222",
        "fg2": "#666666",
        "accent": "#2980b9",
        "highlight": "#e74c3c",
        "green": "#27ae60",
        "yellow": "#f39c12",
        "red": "#e74c3c",
        "blue": "#3498db",
        "gauge_bg": "#e8e8e8",
        "gauge_arc": "#cccccc",
        "gauge_needle": "#e74c3c",
        "graph_line": "#2980b9",
        "graph_grid": "#dddddd",
        "button_bg": "#3498db",
        "button_fg": "#ffffff",
        "button_active": "#2980b9",
        "entry_bg": "#ffffff",
        "entry_fg": "#222222",
    },
}


def get_theme(name: str = "dark") -> dict:
    return THEMES.get(name, THEMES["dark"])


# ============================================================================
# RPM Gauge Widget — Analog-style tachometer
# ============================================================================
class RPMGauge(tk.Canvas):
    """Analog-style RPM gauge with needle, tick marks, and digital readout."""

    def __init__(self, parent, theme: dict, max_rpm: float = 8000,
                 size: int = 250, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=theme["bg"], highlightthickness=0, **kwargs)
        self.theme = theme
        self.max_rpm = max_rpm
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.radius = size // 2 - 20
        self._rpm = 0.0
        self._target_rpm = 0.0

        self._draw_static()
        self._needle_id = None
        self._text_id = None
        self._target_text_id = None
        self.set_rpm(0)

    def _draw_static(self):
        """Draw the static gauge elements (ring, ticks, labels)."""
        r = self.radius
        cx, cy = self.cx, self.cy

        # Outer ring
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        outline=self.theme["gauge_arc"], width=3)

        # Colored danger zone arc (last 20%)
        danger_start = 225 - (0.8 * 270)
        self.create_arc(cx - r + 5, cy - r + 5, cx + r - 5, cy + r - 5,
                       start=danger_start, extent=-(0.2 * 270),
                       style=tk.ARC, outline=self.theme["red"], width=4)

        # Tick marks and labels
        num_major = 8
        for i in range(num_major + 1):
            frac = i / num_major
            angle = math.radians(225 - frac * 270)
            # Major tick
            x1 = cx + (r - 15) * math.cos(angle)
            y1 = cy - (r - 15) * math.sin(angle)
            x2 = cx + r * math.cos(angle)
            y2 = cy - r * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill=self.theme["fg"], width=2)
            # Label
            rpm_val = int(self.max_rpm * frac)
            lx = cx + (r - 30) * math.cos(angle)
            ly = cy - (r - 30) * math.sin(angle)
            label = f"{rpm_val // 1000}k" if rpm_val >= 1000 else str(rpm_val)
            self.create_text(lx, ly, text=label, fill=self.theme["fg2"],
                           font=("Helvetica", 8))

        # Minor ticks
        num_minor = num_major * 5
        for i in range(num_minor + 1):
            if i % 5 == 0:
                continue
            frac = i / num_minor
            angle = math.radians(225 - frac * 270)
            x1 = cx + (r - 8) * math.cos(angle)
            y1 = cy - (r - 8) * math.sin(angle)
            x2 = cx + r * math.cos(angle)
            y2 = cy - r * math.sin(angle)
            self.create_line(x1, y1, x2, y2, fill=self.theme["gauge_arc"], width=1)

        # Center label
        self.create_text(cx, cy + r * 0.35, text="RPM",
                        fill=self.theme["fg2"], font=("Helvetica", 10))

    def set_rpm(self, rpm: float, target_rpm: float = None):
        """Update the displayed RPM."""
        self._rpm = max(0, min(rpm, self.max_rpm))
        if target_rpm is not None:
            self._target_rpm = target_rpm

        # Remove old needle
        if self._needle_id:
            self.delete(self._needle_id)
        if self._text_id:
            self.delete(self._text_id)
        if self._target_text_id:
            self.delete(self._target_text_id)

        # Draw needle
        frac = self._rpm / self.max_rpm
        angle = math.radians(225 - frac * 270)
        nx = self.cx + (self.radius - 40) * math.cos(angle)
        ny = self.cy - (self.radius - 40) * math.sin(angle)
        self._needle_id = self.create_line(
            self.cx, self.cy, nx, ny,
            fill=self.theme["gauge_needle"], width=3, arrow=tk.LAST
        )

        # Center dot
        self.create_oval(self.cx - 5, self.cy - 5, self.cx + 5, self.cy + 5,
                        fill=self.theme["gauge_needle"], outline="")

        # Digital readout
        self._text_id = self.create_text(
            self.cx, self.cy + self.radius * 0.55,
            text=f"{self._rpm:.0f}",
            fill=self.theme["fg"], font=("Helvetica", 18, "bold")
        )

        # Target RPM (smaller, below)
        if self._target_rpm > 0:
            self._target_text_id = self.create_text(
                self.cx, self.cy + self.radius * 0.72,
                text=f"→ {self._target_rpm:.0f}",
                fill=self.theme["fg2"], font=("Helvetica", 10)
            )


# ============================================================================
# RPM Graph Widget — Rolling line chart
# ============================================================================
class RPMGraph(tk.Canvas):
    """Rolling RPM history graph."""

    def __init__(self, parent, theme: dict, max_rpm: float = 8000,
                 history_sec: int = 30, width: int = 400, height: int = 150,
                 **kwargs):
        super().__init__(parent, width=width, height=height,
                        bg=theme["gauge_bg"], highlightthickness=0, **kwargs)
        self.theme = theme
        self.max_rpm = max_rpm
        self.history_sec = history_sec
        self.w = width
        self.h = height
        self._data = deque(maxlen=width)  # one point per pixel

        self._draw_grid()

    def _draw_grid(self):
        """Draw background grid."""
        # Horizontal grid lines (every 25% of max RPM)
        for i in range(1, 4):
            y = self.h - (i / 4) * self.h
            self.create_line(0, y, self.w, y,
                           fill=self.theme["graph_grid"], dash=(2, 4))
            rpm_label = int(self.max_rpm * i / 4)
            label = f"{rpm_label // 1000}k" if rpm_label >= 1000 else str(rpm_label)
            self.create_text(25, y - 8, text=label,
                           fill=self.theme["fg2"], font=("Helvetica", 7))

    def add_point(self, rpm: float):
        """Add an RPM data point and redraw."""
        self._data.append(rpm)
        self._redraw()

    def _redraw(self):
        """Redraw the line from current data."""
        self.delete("line")

        if len(self._data) < 2:
            return

        points = []
        for i, rpm in enumerate(self._data):
            x = self.w - (len(self._data) - 1 - i)
            y = self.h - (rpm / self.max_rpm) * self.h
            y = max(2, min(y, self.h - 2))
            points.append((x, y))

        # Draw as polyline
        coords = []
        for x, y in points:
            coords.extend([x, y])

        if len(coords) >= 4:
            self.create_line(*coords, fill=self.theme["graph_line"],
                           width=2, tags="line", smooth=True)


# ============================================================================
# Division Ring Widget — Visual division indicator
# ============================================================================
class DivisionRing(tk.Canvas):
    """Circular visualization of divisions with current position marker."""

    def __init__(self, parent, theme: dict, size: int = 200, **kwargs):
        super().__init__(parent, width=size, height=size,
                        bg=theme["bg"], highlightthickness=0, **kwargs)
        self.theme = theme
        self.size = size
        self.cx = size // 2
        self.cy = size // 2
        self.radius = size // 2 - 15

    def draw(self, divisions: int, current: int, degrees: float = 0.0):
        """Draw the division ring."""
        self.delete("all")
        r = self.radius
        cx, cy = self.cx, self.cy

        # Outer circle
        self.create_oval(cx - r, cy - r, cx + r, cy + r,
                        outline=self.theme["gauge_arc"], width=2)

        # Division marks
        for i in range(divisions):
            angle = math.radians(90 - (i / divisions) * 360)
            # Tick mark
            x1 = cx + (r - 10) * math.cos(angle)
            y1 = cy - (r - 10) * math.sin(angle)
            x2 = cx + r * math.cos(angle)
            y2 = cy - r * math.sin(angle)

            color = self.theme["green"] if i == current else self.theme["fg2"]
            width = 3 if i == current else 1
            self.create_line(x1, y1, x2, y2, fill=color, width=width)

            # Division number (only if not too crowded)
            if divisions <= 36:
                lx = cx + (r - 22) * math.cos(angle)
                ly = cy - (r - 22) * math.sin(angle)
                self.create_text(lx, ly, text=str(i + 1),
                               fill=color, font=("Helvetica", 8 if divisions <= 18 else 6))

        # Current position marker (filled dot)
        pos_angle = math.radians(90 - (degrees / 360) * 360)
        mx = cx + (r - 5) * math.cos(pos_angle)
        my = cy - (r - 5) * math.sin(pos_angle)
        self.create_oval(mx - 4, my - 4, mx + 4, my + 4,
                        fill=self.theme["highlight"], outline="")

        # Center text
        self.create_text(cx, cy - 10, text=f"{current + 1}/{divisions}",
                        fill=self.theme["fg"], font=("Helvetica", 16, "bold"))
        self.create_text(cx, cy + 12, text=f"{degrees:.3f}°",
                        fill=self.theme["fg2"], font=("Helvetica", 11))


# ============================================================================
# Styled Button
# ============================================================================
class StyledButton(tk.Button):
    """Themed button with consistent styling."""

    def __init__(self, parent, theme: dict, text: str = "", command=None,
                 width: int = 10, height: int = 2, font_size: int = 12,
                 color: str = None, **kwargs):
        bg = color or theme["button_bg"]
        super().__init__(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=theme["button_fg"],
            activebackground=theme["button_active"],
            activeforeground=theme["button_fg"],
            relief=tk.FLAT,
            width=width,
            height=height,
            font=("Helvetica", font_size, "bold"),
            cursor="hand2",
            **kwargs
        )


# ============================================================================
# Status Bar
# ============================================================================
class StatusBar(tk.Frame):
    """Bottom status bar showing mode, motor state, and position."""

    def __init__(self, parent, theme: dict, **kwargs):
        super().__init__(parent, bg=theme["accent"], height=30, **kwargs)
        self.theme = theme
        self.pack_propagate(False)

        self._mode_label = tk.Label(self, text="LATHE", bg=theme["accent"],
                                     fg=theme["fg"], font=("Helvetica", 10, "bold"))
        self._mode_label.pack(side=tk.LEFT, padx=10)

        self._status_label = tk.Label(self, text="IDLE", bg=theme["accent"],
                                       fg=theme["green"], font=("Helvetica", 10))
        self._status_label.pack(side=tk.LEFT, padx=10)

        self._pos_label = tk.Label(self, text="0.000°", bg=theme["accent"],
                                    fg=theme["fg2"], font=("Helvetica", 10))
        self._pos_label.pack(side=tk.RIGHT, padx=10)

        self._info_label = tk.Label(self, text="", bg=theme["accent"],
                                     fg=theme["fg2"], font=("Helvetica", 9))
        self._info_label.pack(side=tk.RIGHT, padx=10)

    def update_status(self, mode: str = None, status: str = None,
                      position: str = None, info: str = None,
                      status_color: str = None):
        if mode:
            self._mode_label.config(text=mode)
        if status:
            color = status_color or self.theme["green"]
            self._status_label.config(text=status, fg=color)
        if position:
            self._pos_label.config(text=position)
        if info is not None:
            self._info_label.config(text=info)
