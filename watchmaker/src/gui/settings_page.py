"""
Watchmaker's Lathe Controller — Settings Page
Configuration editor for motor, gear ratio, PID tuning,
GPIO pins, display, and system options.
"""

import tkinter as tk
from tkinter import messagebox
from .widgets import StyledButton, get_theme


class SettingsPage(tk.Frame):
    """Settings / configuration editor with tabbed sections."""

    def __init__(self, parent, theme: dict, controller=None, **kwargs):
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.theme = theme
        self.ctrl = controller
        self._fields = {}  # section.key -> Entry widget

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        t = self.theme

        # Title
        tk.Label(self, text="Settings", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 16, "bold")).pack(anchor=tk.W, padx=15, pady=(10, 5))

        # Tab buttons
        tab_bar = tk.Frame(self, bg=t["bg"])
        tab_bar.pack(fill=tk.X, padx=10, pady=5)

        self._sections = [
            ("Motor", self._motor_fields),
            ("Gear Ratio", self._gear_fields),
            ("Speed", self._speed_fields),
            ("PID", self._pid_fields),
            ("RPM Sensor", self._rpm_fields),
            ("GPIO", self._gpio_fields),
            ("Display", self._display_fields),
            ("Advanced", self._advanced_fields),
        ]

        self._tab_buttons = {}
        for name, _ in self._sections:
            btn = StyledButton(tab_bar, t, text=name, width=max(6, len(name)),
                              height=1, font_size=9,
                              command=lambda n=name: self._show_section(n))
            btn.pack(side=tk.LEFT, padx=2)
            self._tab_buttons[name] = btn

        # Scrollable content area
        container = tk.Frame(self, bg=t["bg"])
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self._canvas = tk.Canvas(container, bg=t["bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient=tk.VERTICAL,
                                  command=self._canvas.yview)
        self._scroll_frame = tk.Frame(self._canvas, bg=t["bg"])

        self._scroll_frame.bind("<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")))

        self._canvas.create_window((0, 0), window=self._scroll_frame, anchor=tk.NW)
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Touch scrolling
        def _on_scroll(event):
            self._canvas.yview_scroll(-1 * (event.delta // 120), "units")
        self._canvas.bind("<MouseWheel>", _on_scroll)

        # Bottom buttons
        bottom = tk.Frame(self, bg=t["bg"])
        bottom.pack(fill=tk.X, padx=10, pady=(5, 10))

        StyledButton(bottom, t, text="💾  Save", width=12, height=2,
                    font_size=12, color=t["green"],
                    command=self._save).pack(side=tk.LEFT, padx=5)

        StyledButton(bottom, t, text="↺  Reload", width=12, height=2,
                    font_size=12, command=self._reload).pack(side=tk.LEFT, padx=5)

        StyledButton(bottom, t, text="⚙  Defaults", width=12, height=2,
                    font_size=12, color=t["yellow"],
                    command=self._reset_defaults).pack(side=tk.RIGHT, padx=5)

        # Show first section
        self._current_section = None
        self._show_section("Motor")

    # ------------------------------------------------------------------ Sections
    def _show_section(self, name: str):
        if self._current_section == name:
            return
        self._current_section = name

        # Highlight tab
        for n, btn in self._tab_buttons.items():
            btn.config(bg=self.theme["highlight"] if n == name
                      else self.theme["button_bg"])

        # Clear content
        for w in self._scroll_frame.winfo_children():
            w.destroy()

        # Build fields
        for section_name, builder in self._sections:
            if section_name == name:
                builder()
                break

    def _add_field(self, parent, section: str, key: str, label: str,
                   value: str, description: str = ""):
        """Add a labeled entry field."""
        t = self.theme
        row = tk.Frame(parent, bg=t["bg"])
        row.pack(fill=tk.X, pady=3, padx=5)

        tk.Label(row, text=label, bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 11), width=20, anchor=tk.W).pack(side=tk.LEFT)

        entry = tk.Entry(row, width=12, font=("Helvetica", 12),
                        bg=t["entry_bg"], fg=t["entry_fg"],
                        insertbackground=t["fg"], justify=tk.RIGHT)
        entry.insert(0, str(value))
        entry.pack(side=tk.LEFT, padx=10)

        if description:
            tk.Label(row, text=description, bg=t["bg"], fg=t["fg2"],
                    font=("Helvetica", 9)).pack(side=tk.LEFT, padx=5)

        field_key = f"{section}.{key}"
        self._fields[field_key] = entry

    def _get_config_value(self, section: str, key: str, default=""):
        """Read a value from the controller's config."""
        if self.ctrl and hasattr(self.ctrl, 'config'):
            cfg = self.ctrl.config
            sec = getattr(cfg, section, None)
            if sec:
                return getattr(sec, key, default)
        return default

    def _motor_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="Motor Configuration", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("motor", "steps_per_rev", "Steps / Rev", "200", "Full steps per revolution"),
            ("motor", "microsteps", "Microsteps", "16", "1, 2, 4, 8, 16, 32, 64, 128, 256"),
            ("motor", "current_ma", "Current (mA)", "800", "RMS current limit"),
            ("motor", "hold_current_pct", "Hold Current %", "50", "0-100, % of run current"),
            ("motor", "stealthchop", "StealthChop", "true", "true / false, silent mode"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

    def _gear_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="Gear / Pulley Ratio", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("gear", "motor_teeth", "Motor Pulley", "20", "Teeth on motor pulley"),
            ("gear", "spindle_teeth", "Spindle Pulley", "60", "Teeth on spindle pulley"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

        # Show computed ratio
        tk.Label(f, text="", bg=t["bg"]).pack(pady=2)
        self._ratio_label = tk.Label(
            f, text="Ratio: 3.000 : 1  |  Total steps/rev: 9600",
            bg=t["bg"], fg=t["blue"], font=("Helvetica", 11)
        )
        self._ratio_label.pack(anchor=tk.W, padx=10)

    def _speed_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="Speed Limits", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("speed", "max_rpm", "Max RPM", "8000", "Speed limiter"),
            ("speed", "accel_rpm_s", "Accel (RPM/s)", "2000", "Acceleration rate"),
            ("speed", "index_speed_rpm", "Index Speed", "60", "Indexing move speed"),
            ("speed", "jog_speed_rpm", "Jog Speed", "30", "Jog move speed"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

    def _pid_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="PID Controller", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("pid", "kp", "Kp (Proportional)", "1.0", ""),
            ("pid", "ki", "Ki (Integral)", "0.5", ""),
            ("pid", "kd", "Kd (Derivative)", "0.05", ""),
            ("pid", "output_min", "Output Min", "0", "Hz"),
            ("pid", "output_max", "Output Max", "50000", "Hz"),
            ("pid", "sample_interval", "Sample (s)", "0.05", "PID update interval"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

        tk.Label(f, text="💡 Tune: increase Kp until oscillation, "
                "then add Ki for steady-state, Kd for damping.",
                bg=t["bg"], fg=t["fg2"], font=("Helvetica", 9),
                wraplength=400, justify=tk.LEFT).pack(anchor=tk.W, padx=10, pady=5)

    def _rpm_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="RPM Sensor (Hall Effect)", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("rpm_sensor", "magnets", "Magnets", "1", "Magnet count on spindle"),
            ("rpm_sensor", "filter_size", "Filter Size", "5", "Moving average window"),
            ("rpm_sensor", "timeout_s", "Timeout (s)", "2.0", "Zero RPM threshold"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

    def _gpio_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="GPIO Pin Assignments (BCM)", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("gpio", "step_pin", "Step", "17", ""),
            ("gpio", "dir_pin", "Direction", "27", ""),
            ("gpio", "enable_pin", "Enable", "22", "Active LOW"),
            ("gpio", "uart_tx", "UART TX", "14", "TMC2209"),
            ("gpio", "uart_rx", "UART RX", "15", "TMC2209"),
            ("gpio", "rpm_pin", "RPM Sensor", "23", "Hall effect"),
            ("gpio", "enc_clk", "Encoder CLK", "5", ""),
            ("gpio", "enc_dt", "Encoder DT", "6", ""),
            ("gpio", "enc_sw", "Encoder SW", "13", "Press button"),
            ("gpio", "btn_mode", "Mode Button", "16", ""),
            ("gpio", "btn_go", "Go / Stop", "20", ""),
            ("gpio", "btn_estop", "E-Stop", "21", "NC wiring"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

        tk.Label(f, text="⚠ Changes require restart. Double-check wiring!",
                bg=t["bg"], fg=t["yellow"], font=("Helvetica", 10)).pack(
                    anchor=tk.W, padx=10, pady=5)

    def _display_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="Display Settings", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("display", "width", "Width (px)", "800", "Window width"),
            ("display", "height", "Height (px)", "480", "Window height"),
            ("display", "fullscreen", "Fullscreen", "true", "true / false"),
            ("display", "theme", "Theme", "dark", "dark / light"),
            ("display", "graph_seconds", "Graph History", "30", "Seconds of RPM history"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

    def _advanced_fields(self):
        f = self._scroll_frame
        t = self.theme
        tk.Label(f, text="Advanced / Timing", bg=t["bg"], fg=t["fg"],
                font=("Helvetica", 13, "bold")).pack(anchor=tk.W, padx=5, pady=5)

        fields = [
            ("advanced", "step_pulse_us", "Step Pulse (µs)", "5", "Minimum pulse width"),
            ("advanced", "dir_setup_us", "Dir Setup (µs)", "10", "Direction setup time"),
            ("advanced", "gui_refresh_ms", "GUI Refresh (ms)", "50", "Telemetry update rate"),
            ("advanced", "save_position", "Save Position", "true", "Persist position on exit"),
        ]
        for sec, key, label, default, desc in fields:
            val = self._get_config_value(sec, key, default)
            self._add_field(f, sec, key, label, val, desc)

    # ------------------------------------------------------------------ Actions
    def _save(self):
        """Save all fields back to config file."""
        if not self.ctrl:
            messagebox.showinfo("Save", "No controller connected (demo mode)")
            return

        try:
            updates = {}
            for field_key, entry in self._fields.items():
                section, key = field_key.split(".", 1)
                if section not in updates:
                    updates[section] = {}
                updates[section][key] = entry.get().strip()

            if hasattr(self.ctrl, 'save_config'):
                self.ctrl.save_config(updates)
                messagebox.showinfo("Settings", "Configuration saved.\n"
                                    "Some changes require a restart.")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    def _reload(self):
        """Reload config from file."""
        if self.ctrl and hasattr(self.ctrl, 'reload_config'):
            self.ctrl.reload_config()
        # Refresh current section
        current = self._current_section
        self._current_section = None
        self._show_section(current)

    def _reset_defaults(self):
        """Reset to factory defaults."""
        if messagebox.askyesno("Reset", "Reset all settings to defaults?\n"
                              "Current config will be overwritten."):
            if self.ctrl and hasattr(self.ctrl, 'reset_defaults'):
                self.ctrl.reset_defaults()
            self._reload()
