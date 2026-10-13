"""
Aesthetic Status Bar for Aura Text Editor.
Displays line/col stats, word/char counts, encoding, language mode, and theme picker.
"""

import tkinter as tk
from typing import Callable, Optional

from editor.syntax import LANGUAGE_NAMES
from editor.themes import THEMES


class StatusBar(tk.Frame):
    """Bottom status bar with editor statistics and interactive pills."""

    def __init__(
        self,
        master,
        theme: dict,
        on_change_language: Optional[Callable[[str], None]] = None,
        on_change_theme: Optional[Callable[[str], None]] = None,
        **kwargs,
    ):
        super().__init__(master, bg=theme["status_bg"], **kwargs)
        self.theme = theme
        self.on_change_language = on_change_language
        self.on_change_theme = on_change_theme

        self._init_ui()

    def _init_ui(self):
        self.config(height=28)

        # Top border line
        self.top_border = tk.Frame(self, bg=self.theme["border"], height=1)
        self.top_border.pack(side="top", fill="x")

        # Content bar
        self.content_bar = tk.Frame(self, bg=self.theme["status_bg"], padx=14, pady=4)
        self.content_bar.pack(side="top", fill="both", expand=True)

        # Left items
        self.left_frame = tk.Frame(self.content_bar, bg=self.theme["status_bg"])
        self.left_frame.pack(side="left")

        self.pos_label = tk.Label(
            self.left_frame,
            text="Ln 1, Col 1",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
        )
        self.pos_label.pack(side="left", padx=(0, 16))

        self.sel_label = tk.Label(
            self.left_frame,
            text="",
            bg=self.theme["status_bg"],
            fg=self.theme["accent"],
            font=("Helvetica Neue", 11),
        )
        self.sel_label.pack(side="left", padx=(0, 16))

        self.stats_label = tk.Label(
            self.left_frame,
            text="0 lines • 0 words • 0 chars",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
        )
        self.stats_label.pack(side="left")

        # Right items
        self.right_frame = tk.Frame(self.content_bar, bg=self.theme["status_bg"])
        self.right_frame.pack(side="right")

        self.encoding_label = tk.Label(
            self.right_frame,
            text="UTF-8",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
        )
        self.encoding_label.pack(side="left", padx=(0, 16))

        self.indent_label = tk.Label(
            self.right_frame,
            text="Spaces: 4",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
        )
        self.indent_label.pack(side="left", padx=(0, 16))

        # Language clickable pill
        self.lang_btn = tk.Label(
            self.right_frame,
            text="Plain Text ▾",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
            cursor="hand2",
            padx=4,
        )
        self.lang_btn.pack(side="left", padx=(0, 16))
        self.lang_btn.bind("<Button-1>", self._show_language_menu)
        self.lang_btn.bind("<Enter>", lambda e: self.lang_btn.config(fg=self.theme["accent"]))
        self.lang_btn.bind("<Leave>", lambda e: self.lang_btn.config(fg=self.theme["status_fg"]))

        # Theme clickable pill
        self.theme_btn = tk.Label(
            self.right_frame,
            text=f"🎨 {self.theme['name']} ▾",
            bg=self.theme["status_bg"],
            fg=self.theme["status_fg"],
            font=("Helvetica Neue", 11),
            cursor="hand2",
            padx=4,
        )
        self.theme_btn.pack(side="left")
        self.theme_btn.bind("<Button-1>", self._show_theme_menu)
        self.theme_btn.bind("<Enter>", lambda e: self.theme_btn.config(fg=self.theme["accent"]))
        self.theme_btn.bind("<Leave>", lambda e: self.theme_btn.config(fg=self.theme["status_fg"]))

    def update_stats(
        self,
        line: int,
        col: int,
        total_lines: int,
        total_words: int,
        total_chars: int,
        sel_count: int = 0,
    ):
        self.pos_label.config(text=f"Ln {line}, Col {col}")
        if sel_count > 0:
            self.sel_label.config(text=f"({sel_count:,} selected)")
        else:
            self.sel_label.config(text="")

        self.stats_label.config(
            text=f"{total_lines:,} lines • {total_words:,} words • {total_chars:,} chars"
        )

    def set_language(self, lang_key: str):
        display_name = LANGUAGE_NAMES.get(lang_key, lang_key.title())
        self.lang_btn.config(text=f"{display_name} ▾")

    def _show_language_menu(self, event):
        menu = tk.Menu(self, tearoff=False)
        for key, name in sorted(LANGUAGE_NAMES.items(), key=lambda x: x[1]):
            menu.add_command(
                label=name,
                command=lambda k=key: self._on_language_selected(k),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_language_selected(self, lang_key: str):
        self.set_language(lang_key)
        if self.on_change_language:
            self.on_change_language(lang_key)

    def _show_theme_menu(self, event):
        menu = tk.Menu(self, tearoff=False)
        for theme_name in THEMES.keys():
            menu.add_command(
                label=theme_name,
                command=lambda t=theme_name: self._on_theme_selected(t),
            )
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()

    def _on_theme_selected(self, theme_name: str):
        if self.on_change_theme:
            self.on_change_theme(theme_name)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=theme["status_bg"])
        self.top_border.config(bg=theme["border"])
        self.content_bar.config(bg=theme["status_bg"])
        self.left_frame.config(bg=theme["status_bg"])
        self.right_frame.config(bg=theme["status_bg"])

        self.pos_label.config(bg=theme["status_bg"], fg=theme["status_fg"])
        self.sel_label.config(bg=theme["status_bg"], fg=theme["accent"])
        self.stats_label.config(bg=theme["status_bg"], fg=theme["status_fg"])
        self.encoding_label.config(bg=theme["status_bg"], fg=theme["status_fg"])
        self.indent_label.config(bg=theme["status_bg"], fg=theme["status_fg"])
        self.lang_btn.config(bg=theme["status_bg"], fg=theme["status_fg"])
        self.theme_btn.config(
            text=f"🎨 {theme['name']} ▾",
            bg=theme["status_bg"],
            fg=theme["status_fg"],
        )
