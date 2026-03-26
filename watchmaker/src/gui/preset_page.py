"""
Watchmaker's Lathe Controller — Preset Page
Scrollable, searchable preset browser with category filtering.
Loads presets for watchmaking, geometry, and general machining.
"""

import tkinter as tk
from tkinter import ttk
from .widgets import StyledButton, get_theme

# Late import to avoid circular
from ..presets import get_all, get_categories, get_by_category, search, Preset


class PresetPage(tk.Frame):
    """Preset browser with categories and search."""

    def __init__(self, parent, theme: dict, controller=None, **kwargs):
        super().__init__(parent, bg=theme["bg"], **kwargs)
        self.theme = theme
        self.ctrl = controller
        self._all_presets = get_all()
        self._categories = get_categories()
        self._current_category = "All"
        self._filtered = list(self._all_presets)
        self._selected_preset = None

        self._build_ui()
        self._populate_list()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        t = self.theme

        # ---- Top bar: search + category filter -------------------------
        top = tk.Frame(self, bg=t["bg"])
        top.pack(fill=tk.X, padx=10, pady=(10, 5))

        # Search
        tk.Label(top, text="🔍", bg=t["bg"], fg=t["fg2"],
                font=("Helvetica", 14)).pack(side=tk.LEFT, padx=(0, 5))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search)
        self._search_entry = tk.Entry(
            top, textvariable=self._search_var, width=20,
            font=("Helvetica", 12), bg=t["entry_bg"], fg=t["entry_fg"],
            insertbackground=t["fg"]
        )
        self._search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        StyledButton(top, t, text="Clear", width=5, height=1, font_size=9,
                    command=self._clear_search).pack(side=tk.LEFT, padx=5)

        # ---- Category tabs ---------------------------------------------
        cat_frame = tk.Frame(self, bg=t["bg"])
        cat_frame.pack(fill=tk.X, padx=10, pady=5)

        # Scrollable category bar
        cat_canvas = tk.Canvas(cat_frame, bg=t["bg"], height=35,
                               highlightthickness=0)
        cat_canvas.pack(fill=tk.X)

        cat_inner = tk.Frame(cat_canvas, bg=t["bg"])
        cat_canvas.create_window((0, 0), window=cat_inner, anchor=tk.NW)

        self._cat_buttons = {}
        btn = StyledButton(cat_inner, t, text="All", width=6, height=1,
                          font_size=9, command=lambda: self._select_category("All"))
        btn.pack(side=tk.LEFT, padx=2)
        self._cat_buttons["All"] = btn

        for cat in self._categories:
            short = cat[:12]
            btn = StyledButton(cat_inner, t, text=short, width=max(6, len(short)),
                              height=1, font_size=9,
                              command=lambda c=cat: self._select_category(c))
            btn.pack(side=tk.LEFT, padx=2)
            self._cat_buttons[cat] = btn

        cat_inner.update_idletasks()
        cat_canvas.config(scrollregion=cat_canvas.bbox("all"))

        # Enable horizontal scroll via touch drag
        def _cat_scroll(event):
            cat_canvas.xview_scroll(-1 * (event.delta // 120), "units")
        cat_canvas.bind("<MouseWheel>", _cat_scroll)

        # ---- Preset list -----------------------------------------------
        list_frame = tk.Frame(self, bg=t["bg"])
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Custom treeview style
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Preset.Treeview",
                        background=t["bg2"],
                        foreground=t["fg"],
                        fieldbackground=t["bg2"],
                        font=("Helvetica", 11),
                        rowheight=32)
        style.configure("Preset.Treeview.Heading",
                        background=t["accent"],
                        foreground=t["fg"],
                        font=("Helvetica", 10, "bold"))
        style.map("Preset.Treeview",
                  background=[("selected", t["accent"])],
                  foreground=[("selected", t["fg"])])

        self._tree = ttk.Treeview(
            list_frame, columns=("div", "cat", "desc"),
            show="headings", style="Preset.Treeview",
            selectmode="browse"
        )
        self._tree.heading("div", text="Div")
        self._tree.heading("cat", text="Category")
        self._tree.heading("desc", text="Description")
        self._tree.column("div", width=60, anchor=tk.CENTER)
        self._tree.column("cat", width=140)
        self._tree.column("desc", width=300)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                   command=self._tree.yview)
        self._tree.configure(yscrollcommand=scrollbar.set)

        self._tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", self._on_apply)

        # ---- Bottom: selected preset info + apply ----------------------
        bottom = tk.Frame(self, bg=t["accent"])
        bottom.pack(fill=tk.X, padx=10, pady=(5, 10))

        self._info_label = tk.Label(
            bottom, text="Select a preset", bg=t["accent"],
            fg=t["fg"], font=("Helvetica", 11), anchor=tk.W
        )
        self._info_label.pack(side=tk.LEFT, padx=10, pady=8, fill=tk.X, expand=True)

        self._apply_btn = StyledButton(
            bottom, t, text="APPLY", width=10, height=1,
            font_size=12, color=t["green"], command=self._apply_selected
        )
        self._apply_btn.pack(side=tk.RIGHT, padx=10, pady=5)

    # ------------------------------------------------------------------ Data
    def _populate_list(self):
        """Fill treeview with filtered presets."""
        self._tree.delete(*self._tree.get_children())
        for i, p in enumerate(self._filtered):
            self._tree.insert("", tk.END, iid=str(i),
                            values=(p.divisions, p.category, p.name))

    def _select_category(self, cat: str):
        self._current_category = cat
        self._apply_filter()

        # Highlight active category button
        for name, btn in self._cat_buttons.items():
            if name == cat:
                btn.config(bg=self.theme["highlight"])
            else:
                btn.config(bg=self.theme["button_bg"])

    def _on_search(self, *_args):
        self._apply_filter()

    def _clear_search(self):
        self._search_var.set("")
        self._search_entry.focus_set()

    def _apply_filter(self):
        query = self._search_var.get().strip()
        if self._current_category == "All":
            pool = list(self._all_presets)
        else:
            pool = get_by_category(self._current_category)

        if query:
            # Simple contains search across name + category
            q = query.lower()
            pool = [p for p in pool
                    if q in p.name.lower() or q in p.category.lower()]

        self._filtered = pool
        self._populate_list()

    def _on_select(self, _event):
        sel = self._tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._filtered):
            p = self._filtered[idx]
            self._selected_preset = p
            self._info_label.config(
                text=f"{p.name}  —  {p.divisions} divisions  ({p.category})"
            )

    def _on_apply(self, _event):
        self._apply_selected()

    def _apply_selected(self):
        if self._selected_preset is None:
            return
        p = self._selected_preset
        if self.ctrl:
            self.ctrl.set_divisions(p.divisions)
            self.ctrl.switch_to_index()
        self._info_label.config(
            text=f"✓ Applied: {p.name} ({p.divisions} divisions)"
        )

    # ------------------------------------------------------------------ External
    def on_encoder_delta(self, delta: int):
        """Scroll the list with the encoder knob."""
        sel = self._tree.selection()
        children = self._tree.get_children()
        if not children:
            return
        if sel:
            idx = children.index(sel[0])
            new_idx = max(0, min(idx + delta, len(children) - 1))
        else:
            new_idx = 0
        self._tree.selection_set(children[new_idx])
        self._tree.see(children[new_idx])
        self._on_select(None)
