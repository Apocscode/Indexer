"""
Watchmaker's Lathe Controller — Lathe Page
Variable-speed lathe mode with RPM gauge, graph, speed knob display,
PID status, and directional control.
"""

import tkinter as tk
from .widgets import RPMGauge, RPMGraph, StyledButton, get_theme


class LathePage(tk.Frame):
    """Main lathe / continuous-rotation control page."""

    def __init__(self, parent, theme: dict, controller=None, **kwargs):
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.theme = theme
        self.ctrl = controller  # AppController reference
        self._running = False
        self._direction = 1     # 1 = CW, -1 = CCW
        self._target_rpm = 0.0
        self._rpm_mode = False  # False = open-loop, True = PID RPM

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        t = self.theme

        # --- Left column: gauge -----------------------------------------
        left = tk.Frame(self, bg=t["bg"])
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.gauge = RPMGauge(left, t, max_rpm=self._max_rpm, size=260)
        self.gauge.pack(pady=(10, 5))

        self.graph = RPMGraph(left, t, max_rpm=self._max_rpm,
                              width=280, height=120)
        self.graph.pack(pady=(5, 10))

        # --- Right column: controls -------------------------------------
        right = tk.Frame(self, bg=t["bg"], width=260)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)
        right.pack_propagate(False)

        # Target RPM display
        rpm_frame = tk.Frame(right, bg=t["bg"])
        rpm_frame.pack(fill=tk.X, pady=(10, 5))

        tk.Label(rpm_frame, text="Target", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 10)).pack()
        self._target_label = tk.Label(rpm_frame, text="0",
                                       bg=t["bg"], fg=t["fg"],
                                       font=("Helvetica", 32, "bold"))
        self._target_label.pack()
        tk.Label(rpm_frame, text="RPM", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 10)).pack()

        # Speed slider (touchscreen-friendly large slider)
        slider_frame = tk.Frame(right, bg=t["bg"])
        slider_frame.pack(fill=tk.X, pady=10, padx=10)

        self._speed_var = tk.DoubleVar(value=0)
        self._slider = tk.Scale(
            slider_frame, from_=0, to=self._max_rpm,
            orient=tk.HORIZONTAL, variable=self._speed_var,
            bg=t["bg"], fg=t["fg"], troughcolor=t["accent"],
            highlightthickness=0, sliderrelief=tk.FLAT,
            sliderlength=40, width=30, showvalue=False,
            command=self._on_slider_change
        )
        self._slider.pack(fill=tk.X)

        # Quick RPM presets
        presets_frame = tk.Frame(right, bg=t["bg"])
        presets_frame.pack(fill=tk.X, pady=5, padx=10)
        for rpm in [100, 500, 1000, 2000, 4000]:
            label = f"{rpm // 1000}k" if rpm >= 1000 else str(rpm)
            btn = StyledButton(presets_frame, t, text=label, width=4, height=1,
                              font_size=9, command=lambda r=rpm: self._set_target(r))
            btn.pack(side=tk.LEFT, expand=True, padx=2)

        # Direction toggle
        dir_frame = tk.Frame(right, bg=t["bg"])
        dir_frame.pack(fill=tk.X, pady=10, padx=10)

        self._dir_btn = StyledButton(
            dir_frame, t, text="CW ↻", width=8, height=2,
            font_size=11, command=self._toggle_direction
        )
        self._dir_btn.pack(side=tk.LEFT, expand=True, padx=5)

        # RPM mode toggle
        self._mode_btn = StyledButton(
            dir_frame, t, text="OPEN", width=8, height=2,
            font_size=11, command=self._toggle_rpm_mode
        )
        self._mode_btn.pack(side=tk.RIGHT, expand=True, padx=5)

        # Start / Stop button
        self._start_btn = StyledButton(
            right, t, text="▶  START", width=20, height=3,
            font_size=16, color=t["green"], command=self._toggle_run
        )
        self._start_btn.pack(pady=15, padx=10)

        # E-STOP
        self._estop_btn = StyledButton(
            right, t, text="⬛  E-STOP", width=20, height=2,
            font_size=14, color=t["red"], command=self._emergency_stop
        )
        self._estop_btn.pack(pady=5, padx=10)

    # ------------------------------------------------------------------ Properties
    @property
    def _max_rpm(self) -> float:
        if self.ctrl and hasattr(self.ctrl, 'config'):
            return self.ctrl.config.speed.max_rpm
        return 8000.0

    # ------------------------------------------------------------------ Callbacks
    def _on_slider_change(self, value):
        rpm = float(value)
        self._target_rpm = rpm
        self._target_label.config(text=f"{rpm:.0f}")
        if self._running and self.ctrl:
            self.ctrl.set_speed(rpm)

    def _set_target(self, rpm: float):
        self._target_rpm = rpm
        self._speed_var.set(rpm)
        self._target_label.config(text=f"{rpm:.0f}")
        if self._running and self.ctrl:
            self.ctrl.set_speed(rpm)

    def _toggle_direction(self):
        self._direction *= -1
        text = "CW ↻" if self._direction == 1 else "CCW ↺"
        self._dir_btn.config(text=text)
        if self.ctrl:
            self.ctrl.set_direction(self._direction)

    def _toggle_rpm_mode(self):
        self._rpm_mode = not self._rpm_mode
        if self._rpm_mode:
            self._mode_btn.config(text="PID")
        else:
            self._mode_btn.config(text="OPEN")
        if self.ctrl:
            self.ctrl.set_rpm_mode(self._rpm_mode)

    def _toggle_run(self):
        if self._running:
            self._stop()
        else:
            self._start()

    def _start(self):
        self._running = True
        self._start_btn.config(text="⏹  STOP", bg=self.theme["yellow"])
        if self.ctrl:
            self.ctrl.start_lathe(self._target_rpm, self._direction)

    def _stop(self):
        self._running = False
        self._start_btn.config(text="▶  START", bg=self.theme["green"])
        if self.ctrl:
            self.ctrl.stop_lathe()

    def _emergency_stop(self):
        self._running = False
        self._start_btn.config(text="▶  START", bg=self.theme["green"])
        if self.ctrl:
            self.ctrl.emergency_stop()

    # ------------------------------------------------------------------ Periodic update
    def update_telemetry(self, actual_rpm: float, target_rpm: float = None):
        """Called periodically by main loop with current RPM."""
        if target_rpm is not None:
            self._target_rpm = target_rpm
        self.gauge.set_rpm(actual_rpm, self._target_rpm)
        self.graph.add_point(actual_rpm)

    def on_encoder_delta(self, delta: int):
        """Speed knob turned — adjust target RPM."""
        step = max(1, self._target_rpm * 0.02)  # 2% per click
        step = max(step, 10)  # minimum 10 RPM per click
        new_rpm = max(0, min(self._target_rpm + delta * step, self._max_rpm))
        self._set_target(new_rpm)
