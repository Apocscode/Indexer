"""
Watchmaker's Lathe Controller — Main Application
Top-level tkinter application with tabbed page navigation,
hardware integration loop, and controller bridge.
"""

import tkinter as tk
import sys
import os
import signal
import logging
from typing import Optional

from .widgets import StatusBar, get_theme
from .lathe_page import LathePage
from .index_page import IndexPage
from .preset_page import PresetPage
from .settings_page import SettingsPage

logger = logging.getLogger(__name__)


# ============================================================================
# Application Controller — bridges GUI ↔ hardware
# ============================================================================
class AppController:
    """
    Mediates between GUI pages and hardware subsystems.
    All hardware calls go through here so pages stay decoupled.
    """

    def __init__(self, config, motor, rpm_sensor, pid_controller,
                 indexer, hw_input):
        self.config = config
        self.motor = motor
        self.rpm = rpm_sensor
        self.pid = pid_controller
        self.indexer = indexer
        self.hw_input = hw_input

        self._rpm_mode = False
        self._app = None  # set by App after construction

    # ---- Lathe controls ------------------------------------------------
    def set_speed(self, rpm: float):
        if self._rpm_mode:
            self.pid.setpoint = rpm
        else:
            self.motor.set_rpm(rpm)

    def set_direction(self, direction: int):
        self.motor._set_direction(direction)

    def set_rpm_mode(self, enabled: bool):
        self._rpm_mode = enabled
        if enabled:
            self.pid.enable()
        else:
            self.pid.disable()

    def start_lathe(self, rpm: float, direction: int = 1):
        if self._rpm_mode:
            self.pid.setpoint = rpm
            self.pid.enable()
        self.motor.run_continuous(rpm, direction)

    def stop_lathe(self):
        self.motor.stop()
        self.pid.disable()

    def emergency_stop(self):
        self.motor.emergency_stop()
        self.pid.disable()
        logger.warning("E-STOP triggered")

    # ---- Index controls ------------------------------------------------
    def set_divisions(self, n: int):
        self.indexer.divisions = n

    def index_next(self):
        steps = self.indexer.next_steps()
        if steps:
            index_freq = self.config.rpm_to_step_freq(
                self.config.speed.default_rpm)
            self.motor.move_steps_async(steps, speed_hz=min(index_freq, 50000))
        return self.indexer

    def index_prev(self):
        steps = self.indexer.prev_steps()
        if steps:
            index_freq = self.config.rpm_to_step_freq(
                self.config.speed.default_rpm)
            self.motor.move_steps_async(steps, speed_hz=min(index_freq, 50000))
        return self.indexer

    def index_goto(self, division: int):
        steps = self.indexer.steps_to_division(division)
        if steps:
            index_freq = self.config.rpm_to_step_freq(
                self.config.speed.default_rpm)
            self.motor.move_steps_async(steps, speed_hz=min(index_freq, 50000))
        return self.indexer

    def jog_degrees(self, degrees: float):
        steps = self.indexer.degrees_to_steps(degrees)
        if steps:
            jog_freq = self.config.rpm_to_step_freq(
                self.config.speed.default_rpm)
            self.motor.move_steps_async(steps, speed_hz=min(jog_freq, 20000))

    def go_home(self):
        steps = self.indexer.steps_to_home()
        if steps:
            index_freq = self.config.rpm_to_step_freq(
                self.config.speed.default_rpm)
            self.motor.move_steps_async(steps, speed_hz=min(index_freq, 50000))
        self.indexer.reset_home()

    def get_position_degrees(self) -> float:
        return self.indexer.degrees

    def switch_to_index(self):
        if self._app:
            self._app.show_page("Index")

    # ---- Config controls -----------------------------------------------
    def save_config(self, updates: dict):
        self.config.update_and_save(updates)

    def reload_config(self):
        self.config.reload()

    def reset_defaults(self):
        self.config.reset_defaults()


# ============================================================================
# Main Application Window
# ============================================================================
class App:
    """Main tkinter application with tabbed navigation."""

    PAGES = ["Lathe", "Index", "Presets", "Settings"]

    def __init__(self, controller: Optional[AppController] = None,
                 fullscreen: bool = True, width: int = 800, height: int = 480,
                 theme_name: str = "dark"):
        self.controller = controller
        self.theme = get_theme(theme_name)
        self._current_page = None

        # ---- Root window -----------------------------------------------
        self.root = tk.Tk()
        self.root.title("Watchmaker's Lathe Controller")
        self.root.configure(bg=self.theme["bg"])

        if fullscreen:
            self.root.attributes("-fullscreen", True)
        else:
            self.root.geometry(f"{width}x{height}")
            self.root.minsize(640, 400)

        # Escape exits fullscreen (Pi convenience)
        self.root.bind("<Escape>", lambda e: self.root.attributes("-fullscreen", False))
        self.root.bind("<F11>", lambda e: self.root.attributes(
            "-fullscreen", not self.root.attributes("-fullscreen")))

        # Link controller back to app
        if controller:
            controller._app = self

        self._build_ui()
        self.show_page("Lathe")

        # Start periodic update
        self._update_interval = 50  # ms
        self._schedule_update()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        t = self.theme

        # ---- Navigation bar (top) --------------------------------------
        nav = tk.Frame(self.root, bg=t["accent"], height=50)
        nav.pack(fill=tk.X)
        nav.pack_propagate(False)

        # App title
        tk.Label(nav, text="⚙ Watchmaker", bg=t["accent"], fg=t["fg"],
                font=("Helvetica", 14, "bold")).pack(side=tk.LEFT, padx=15)

        # Page tabs
        self._nav_buttons = {}
        for page_name in self.PAGES:
            btn = tk.Button(
                nav, text=page_name, bg=t["accent"], fg=t["fg"],
                activebackground=t["highlight"], activeforeground=t["fg"],
                relief=tk.FLAT, font=("Helvetica", 12, "bold"),
                padx=20, pady=10, cursor="hand2",
                command=lambda n=page_name: self.show_page(n)
            )
            btn.pack(side=tk.LEFT, padx=2)
            self._nav_buttons[page_name] = btn

        # ---- Page container --------------------------------------------
        self._container = tk.Frame(self.root, bg=t["bg"])
        self._container.pack(fill=tk.BOTH, expand=True)

        self._pages = {}
        for page_name in self.PAGES:
            cls = {
                "Lathe": LathePage,
                "Index": IndexPage,
                "Presets": PresetPage,
                "Settings": SettingsPage,
            }[page_name]
            page = cls(self._container, t, controller=self.controller)
            self._pages[page_name] = page

        # ---- Status bar (bottom) ---------------------------------------
        self.status_bar = StatusBar(self.root, t)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def show_page(self, name: str):
        """Switch to the named page."""
        if name == self._current_page:
            return

        # Hide current
        if self._current_page and self._current_page in self._pages:
            self._pages[self._current_page].pack_forget()

        # Show new
        self._pages[name].pack(fill=tk.BOTH, expand=True)
        self._current_page = name

        # Highlight nav button
        for n, btn in self._nav_buttons.items():
            btn.config(bg=self.theme["highlight"] if n == name
                      else self.theme["accent"])

        # Update status bar
        self.status_bar.update_status(mode=name.upper())

    # ------------------------------------------------------------------ Update loop
    def _schedule_update(self):
        """Periodic telemetry + input polling."""
        try:
            self._tick()
        except Exception as e:
            logger.error(f"Update tick error: {e}")
        self.root.after(self._update_interval, self._schedule_update)

    def _tick(self):
        """One update cycle."""
        ctrl = self.controller
        if not ctrl:
            return

        # Poll hardware inputs
        if ctrl.hw_input:
            from ..input_hw import InputEvent
            for event in ctrl.hw_input.poll_all():
                self._handle_input(event)

        # Update RPM telemetry
        if ctrl.rpm:
            actual_rpm = ctrl.rpm.rpm
            target = ctrl.pid.setpoint if ctrl.pid else 0

            # PID loop (if in RPM mode)
            if ctrl._rpm_mode and ctrl.motor.is_moving:
                output = ctrl.pid.update(actual_rpm)
                if output is not None:
                    # PID output is 0.0–1.0, scale to max frequency
                    max_freq = ctrl.config.rpm_to_step_freq(ctrl.config.speed.max_rpm)
                    ctrl.motor.set_rpm(ctrl.config.step_freq_to_rpm(output * max_freq))

            # Update lathe page gauges
            lathe = self._pages.get("Lathe")
            if lathe:
                lathe.update_telemetry(actual_rpm, target)

        # Update status bar
        motor_state = "IDLE"
        state_color = self.theme["fg2"]
        if ctrl.motor:
            from ..motor import MotorState
            if ctrl.motor.state == MotorState.RUNNING:
                motor_state = "RUNNING"
                state_color = self.theme["green"]
            elif ctrl.motor.is_moving:
                motor_state = "MOVING"
                state_color = self.theme["yellow"]
            elif ctrl.motor.state == MotorState.ESTOP:
                motor_state = "E-STOP"
                state_color = self.theme["red"]

        pos_deg = ctrl.get_position_degrees()
        self.status_bar.update_status(
            status=motor_state,
            status_color=state_color,
            position=f"{pos_deg:.3f}°"
        )

    def _handle_input(self, event):
        """Route hardware input events to the active page."""
        from ..input_hw import InputEvent

        page = self._pages.get(self._current_page)

        if event == InputEvent.BTN_ESTOP:
            self.controller.emergency_stop()
            return

        if event == InputEvent.BTN_MODE:
            # Cycle pages
            idx = self.PAGES.index(self._current_page)
            next_page = self.PAGES[(idx + 1) % len(self.PAGES)]
            self.show_page(next_page)
            return

        if event == InputEvent.BTN_MODE_LONG:
            # Toggle fullscreen
            fs = self.root.attributes("-fullscreen")
            self.root.attributes("-fullscreen", not fs)
            return

        # Encoder delta
        if event in (InputEvent.ENC_CW, InputEvent.ENC_CCW):
            delta = 1 if event == InputEvent.ENC_CW else -1
            if page and hasattr(page, 'on_encoder_delta'):
                page.on_encoder_delta(delta)
            return

        # Encoder press → GO
        if event == InputEvent.ENC_PRESS:
            if self._current_page == "Index":
                self._pages["Index"]._go_next()
            elif self._current_page == "Lathe":
                self._pages["Lathe"]._toggle_run()
            return

        if event == InputEvent.BTN_GO_STOP:
            if self._current_page == "Lathe":
                self._pages["Lathe"]._toggle_run()
            elif self._current_page == "Index":
                self._pages["Index"]._go_next()

    # ------------------------------------------------------------------ Lifecycle
    def run(self):
        """Start the main loop."""
        logger.info("Starting GUI main loop")
        try:
            self.root.mainloop()
        except KeyboardInterrupt:
            self.shutdown()

    def shutdown(self):
        """Clean shutdown."""
        logger.info("Shutting down GUI")
        if self.controller:
            try:
                self.controller.stop_lathe()
            except Exception:
                pass
        try:
            self.root.destroy()
        except Exception:
            pass
