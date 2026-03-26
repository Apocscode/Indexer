"""
Watchmaker's Lathe Controller — Index Page
Division / indexing control with visual division ring,
step controls, jog, division editor, and degree display.
"""

import tkinter as tk
from .widgets import DivisionRing, StyledButton, get_theme


class IndexPage(tk.Frame):
    """Indexing / division control page."""

    def __init__(self, parent, theme: dict, controller=None, **kwargs):
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.theme = theme
        self.ctrl = controller
        self._divisions = 6
        self._current = 0
        self._degrees = 0.0
        self._editing = False

        self._build_ui()
        self._refresh_display()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        t = self.theme

        # --- Top: Division ring + info ----------------------------------
        top = tk.Frame(self, bg=t["bg"])
        top.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Division ring (left)
        self.ring = DivisionRing(top, t, size=230)
        self.ring.pack(side=tk.LEFT, padx=(10, 20), pady=10)

        # Info panel (right of ring)
        info = tk.Frame(top, bg=t["bg"])
        info.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, pady=10)

        tk.Label(info, text="DIVISIONS", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 10)).pack(anchor=tk.W)

        div_row = tk.Frame(info, bg=t["bg"])
        div_row.pack(fill=tk.X, pady=5)

        self._div_label = tk.Label(div_row, text="6", bg=t["bg"],
                                    fg=t["fg"], font=("Helvetica", 36, "bold"))
        self._div_label.pack(side=tk.LEFT)

        edit_btn = StyledButton(div_row, t, text="✎", width=3, height=1,
                               font_size=14, command=self._toggle_edit)
        edit_btn.pack(side=tk.LEFT, padx=10)

        # Edit controls (hidden by default)
        self._edit_frame = tk.Frame(info, bg=t["bg"])

        edit_row = tk.Frame(self._edit_frame, bg=t["bg"])
        edit_row.pack(fill=tk.X, pady=5)

        self._div_entry = tk.Entry(edit_row, width=6, font=("Helvetica", 18),
                                    bg=t["entry_bg"], fg=t["entry_fg"],
                                    insertbackground=t["fg"],
                                    justify=tk.CENTER)
        self._div_entry.pack(side=tk.LEFT, padx=5)
        self._div_entry.insert(0, "6")

        StyledButton(edit_row, t, text="SET", width=5, height=1,
                    font_size=10, command=self._apply_divisions).pack(
                        side=tk.LEFT, padx=5)

        # Quick division buttons
        quick_frame = tk.Frame(self._edit_frame, bg=t["bg"])
        quick_frame.pack(fill=tk.X, pady=3)
        for n in [2, 3, 4, 5, 6, 8, 10, 12, 15, 24, 36, 60]:
            btn = StyledButton(quick_frame, t, text=str(n), width=3, height=1,
                              font_size=9, command=lambda d=n: self._set_divisions(d))
            btn.pack(side=tk.LEFT, padx=1, pady=1)

        # Position readout
        tk.Label(info, text="", bg=t["bg"]).pack(pady=3)  # spacer
        tk.Label(info, text="POSITION", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 10)).pack(anchor=tk.W)

        self._pos_label = tk.Label(info, text="0.000°", bg=t["bg"],
                                    fg=t["fg"], font=("Helvetica", 24, "bold"))
        self._pos_label.pack(anchor=tk.W)

        # Division fraction
        self._frac_label = tk.Label(info, text="1 / 6", bg=t["bg"],
                                     fg=t["blue"], font=("Helvetica", 18))
        self._frac_label.pack(anchor=tk.W, pady=3)

        # Step size info
        self._step_info = tk.Label(info, text="", bg=t["bg"],
                                    fg=t["fg2"], font=("Helvetica", 9))
        self._step_info.pack(anchor=tk.W)

        # --- Bottom: Navigation controls --------------------------------
        bottom = tk.Frame(self, bg=t["bg"])
        bottom.pack(fill=tk.X, padx=10, pady=(0, 10))

        nav_frame = tk.Frame(bottom, bg=t["bg"])
        nav_frame.pack()

        StyledButton(nav_frame, t, text="⏮", width=4, height=2,
                    font_size=16, command=self._go_first).pack(
                        side=tk.LEFT, padx=5)

        StyledButton(nav_frame, t, text="◀  PREV", width=10, height=2,
                    font_size=14, command=self._go_prev).pack(
                        side=tk.LEFT, padx=5)

        self._go_btn = StyledButton(nav_frame, t, text="▶  NEXT", width=10,
                                     height=2, font_size=14,
                                     color=t["green"],
                                     command=self._go_next)
        self._go_btn.pack(side=tk.LEFT, padx=5)

        StyledButton(nav_frame, t, text="⏭", width=4, height=2,
                    font_size=16, command=self._go_last).pack(
                        side=tk.LEFT, padx=5)

        # Jog controls
        jog_frame = tk.Frame(bottom, bg=t["bg"])
        jog_frame.pack(pady=5)

        tk.Label(jog_frame, text="Jog:", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 9)).pack(side=tk.LEFT, padx=5)

        for deg in [0.1, 1.0, 5.0, 10.0, 45.0, 90.0]:
            label = f"{deg:.1f}°" if deg < 1 else f"{deg:.0f}°"
            StyledButton(jog_frame, t, text=label, width=4, height=1,
                        font_size=9, command=lambda d=deg: self._jog(d)).pack(
                            side=tk.LEFT, padx=2)

        StyledButton(jog_frame, t, text="HOME", width=6, height=1,
                    font_size=9, color=t["yellow"],
                    command=self._go_home).pack(side=tk.LEFT, padx=5)

    # ------------------------------------------------------------------ Actions
    def _toggle_edit(self):
        self._editing = not self._editing
        if self._editing:
            self._edit_frame.pack(fill=tk.X, pady=5)
            self._div_entry.delete(0, tk.END)
            self._div_entry.insert(0, str(self._divisions))
            self._div_entry.focus_set()
            self._div_entry.select_range(0, tk.END)
        else:
            self._edit_frame.pack_forget()

    def _apply_divisions(self):
        try:
            n = int(self._div_entry.get())
            if 1 <= n <= 1000:
                self._set_divisions(n)
        except ValueError:
            pass

    def _set_divisions(self, n: int):
        self._divisions = n
        self._current = 0
        self._degrees = 0.0
        self._div_entry.delete(0, tk.END)
        self._div_entry.insert(0, str(n))
        if self.ctrl:
            self.ctrl.set_divisions(n)
        self._refresh_display()

    def _go_next(self):
        if self.ctrl:
            result = self.ctrl.index_next()
            if result:
                self._current = result.current_division
                self._degrees = result.degrees
        else:
            self._current = (self._current + 1) % self._divisions
            self._degrees = (self._current / self._divisions) * 360.0
        self._refresh_display()

    def _go_prev(self):
        if self.ctrl:
            result = self.ctrl.index_prev()
            if result:
                self._current = result.current_division
                self._degrees = result.degrees
        else:
            self._current = (self._current - 1) % self._divisions
            self._degrees = (self._current / self._divisions) * 360.0
        self._refresh_display()

    def _go_first(self):
        if self.ctrl:
            result = self.ctrl.index_goto(0)
            if result:
                self._current = result.current_division
                self._degrees = result.degrees
        else:
            self._current = 0
            self._degrees = 0.0
        self._refresh_display()

    def _go_last(self):
        last = self._divisions - 1
        if self.ctrl:
            result = self.ctrl.index_goto(last)
            if result:
                self._current = result.current_division
                self._degrees = result.degrees
        else:
            self._current = last
            self._degrees = (last / self._divisions) * 360.0
        self._refresh_display()

    def _jog(self, degrees: float):
        if self.ctrl:
            self.ctrl.jog_degrees(degrees)
            self._degrees = self.ctrl.get_position_degrees()
        else:
            self._degrees = (self._degrees + degrees) % 360.0
        self._refresh_display()

    def _go_home(self):
        if self.ctrl:
            self.ctrl.go_home()
            self._degrees = 0.0
            self._current = 0
        else:
            self._degrees = 0.0
            self._current = 0
        self._refresh_display()

    # ------------------------------------------------------------------ Display
    def _refresh_display(self):
        self.ring.draw(self._divisions, self._current, self._degrees)
        self._div_label.config(text=str(self._divisions))
        self._pos_label.config(text=f"{self._degrees:.3f}°")
        self._frac_label.config(text=f"{self._current + 1} / {self._divisions}")

        angle_per = 360.0 / self._divisions
        self._step_info.config(
            text=f"Step angle: {angle_per:.4f}°  |  "
                 f"Remaining: {self._divisions - self._current - 1}"
        )

    def on_encoder_delta(self, delta: int):
        """Encoder turn in index mode — navigate divisions."""
        if delta > 0:
            self._go_next()
        elif delta < 0:
            self._go_prev()
