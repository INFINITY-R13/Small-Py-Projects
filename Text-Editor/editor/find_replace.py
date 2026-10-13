"""
Modern Find & Replace Bar for Aura Text Editor.
Features real-time match count, highlighted matches, case toggle, and shortcuts.
"""

import tkinter as tk
from typing import Callable, List, Optional


class FindReplaceBar(tk.Frame):
    """Aesthetic Find & Replace floating/docked toolbar."""

    def __init__(
        self,
        master,
        theme: dict,
        get_active_editor: Callable,
        on_close: Optional[Callable[[], None]] = None,
        **kwargs,
    ):
        super().__init__(master, bg=theme["header_bg"], bd=0, padx=12, pady=8, **kwargs)
        self.theme = theme
        self.get_active_editor = get_active_editor
        self.on_close_cb = on_close
        self.matches: List[str] = []
        self.current_match_idx: int = -1
        self.match_case = False

        self._init_ui()

    def _init_ui(self):
        # Row 1: Find
        self.row1 = tk.Frame(self, bg=self.theme["header_bg"])
        self.row1.pack(fill="x", pady=(0, 6))

        self.find_icon = tk.Label(
            self.row1,
            text="🔍",
            bg=self.theme["header_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 12),
        )
        self.find_icon.pack(side="left", padx=(0, 6))

        # Find Entry Container with subtle border
        self.find_entry_border = tk.Frame(self.row1, bg=self.theme["border"], padx=1, pady=1)
        self.find_entry_border.pack(side="left", padx=(0, 8))

        self.find_entry = tk.Entry(
            self.find_entry_border,
            bg=self.theme["editor_bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["cursor"],
            relief="flat",
            font=("Menlo", 12),
            width=26,
            highlightthickness=0,
            bd=4,
        )
        self.find_entry.pack(fill="both")

        # Match counter pill
        self.counter_label = tk.Label(
            self.row1,
            text="0 matches",
            bg=self.theme["btn_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 10),
            padx=8,
            pady=2,
        )
        self.counter_label.pack(side="left", padx=(0, 8))

        # Prev / Next buttons
        self.btn_prev = self._create_btn(self.row1, "▲ Prev", self.prev_match)
        self.btn_prev.pack(side="left", padx=(0, 4))

        self.btn_next = self._create_btn(self.row1, "▼ Next", self.next_match)
        self.btn_next.pack(side="left", padx=(0, 8))

        # Case sensitivity toggle
        self.btn_case = self._create_btn(self.row1, "Aa", self.toggle_case)
        self.btn_case.pack(side="left", padx=(0, 8))

        # Close button
        self.btn_close = tk.Label(
            self.row1,
            text="✕",
            bg=self.theme["header_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 12),
            cursor="hand2",
            padx=6,
        )
        self.btn_close.pack(side="right")
        self.btn_close.bind("<Button-1>", lambda e: self.close())
        self.btn_close.bind("<Enter>", lambda e: self.btn_close.config(fg=self.theme["tab_close_hover"]))
        self.btn_close.bind("<Leave>", lambda e: self.btn_close.config(fg=self.theme["fg_dim"]))

        # Row 2: Replace
        self.row2 = tk.Frame(self, bg=self.theme["header_bg"])
        self.row2.pack(fill="x")

        self.replace_icon = tk.Label(
            self.row2,
            text="⇄",
            bg=self.theme["header_bg"],
            fg=self.theme["fg_dim"],
            font=("Helvetica Neue", 12),
        )
        self.replace_icon.pack(side="left", padx=(0, 6))

        self.replace_entry_border = tk.Frame(self.row2, bg=self.theme["border"], padx=1, pady=1)
        self.replace_entry_border.pack(side="left", padx=(0, 8))

        self.replace_entry = tk.Entry(
            self.replace_entry_border,
            bg=self.theme["editor_bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["cursor"],
            relief="flat",
            font=("Menlo", 12),
            width=26,
            highlightthickness=0,
            bd=4,
        )
        self.replace_entry.pack(fill="both")

        self.btn_replace = self._create_btn(self.row2, "Replace", self.replace_one)
        self.btn_replace.pack(side="left", padx=(0, 6))

        self.btn_replace_all = self._create_btn(self.row2, "Replace All", self.replace_all)
        self.btn_replace_all.pack(side="left")

        # Key bindings
        self.find_entry.bind("<KeyRelease>", self._on_find_change)
        self.find_entry.bind("<Return>", lambda e: self.next_match())
        self.find_entry.bind("<Shift-Return>", lambda e: self.prev_match())
        self.find_entry.bind("<Escape>", lambda e: self.close())
        self.replace_entry.bind("<Escape>", lambda e: self.close())
        self.replace_entry.bind("<Return>", lambda e: self.replace_one())

    def _create_btn(self, parent, text: str, command: Callable) -> tk.Label:
        btn = tk.Label(
            parent,
            text=text,
            bg=self.theme["btn_bg"],
            fg=self.theme["fg"],
            font=("Helvetica Neue", 10),
            cursor="hand2",
            padx=8,
            pady=3,
        )
        btn.bind("<Button-1>", lambda e: command())
        btn.bind("<Enter>", lambda e, b=btn: b.config(bg=self.theme["btn_hover"]))
        btn.bind("<Leave>", lambda e, b=btn: self._restore_btn_bg(b))
        return btn

    def _restore_btn_bg(self, btn: tk.Label):
        if btn == self.btn_case and self.match_case:
            btn.config(bg=self.theme["accent"], fg=self.theme["accent_fg"])
        else:
            btn.config(bg=self.theme["btn_bg"], fg=self.theme["fg"])

    def toggle_case(self):
        self.match_case = not self.match_case
        if self.match_case:
            self.btn_case.config(bg=self.theme["accent"], fg=self.theme["accent_fg"])
        else:
            self.btn_case.config(bg=self.theme["btn_bg"], fg=self.theme["fg"])
        self._on_find_change()

    def _on_find_change(self, event=None):
        query = self.find_entry.get()
        editor = self.get_active_editor()
        if not editor:
            return

        text = editor.text
        text.tag_remove("search_match", "1.0", "end")
        text.tag_remove("search_current", "1.0", "end")
        self.matches.clear()
        self.current_match_idx = -1

        if not query:
            self.counter_label.config(text="0 matches")
            return

        pos = "1.0"
        nocase = not self.match_case
        while True:
            idx = text.search(query, pos, stopindex="end", nocase=nocase)
            if not idx:
                break
            end_idx = f"{idx}+{len(query)}c"
            self.matches.append((idx, end_idx))
            text.tag_add("search_match", idx, end_idx)
            pos = end_idx

        total = len(self.matches)
        if total > 0:
            self.current_match_idx = 0
            self._highlight_current()
            self.counter_label.config(text=f"1 of {total}")
        else:
            self.counter_label.config(text="No matches")

    def _highlight_current(self):
        editor = self.get_active_editor()
        if not editor or not self.matches or self.current_match_idx < 0:
            return
        text = editor.text
        text.tag_remove("search_current", "1.0", "end")

        idx, end_idx = self.matches[self.current_match_idx]
        text.tag_add("search_current", idx, end_idx)
        text.see(idx)
        text.mark_set("insert", end_idx)
        self.counter_label.config(text=f"{self.current_match_idx + 1} of {len(self.matches)}")

    def next_match(self):
        if not self.matches:
            self._on_find_change()
            return
        self.current_match_idx = (self.current_match_idx + 1) % len(self.matches)
        self._highlight_current()

    def prev_match(self):
        if not self.matches:
            self._on_find_change()
            return
        self.current_match_idx = (self.current_match_idx - 1) % len(self.matches)
        self._highlight_current()

    def replace_one(self):
        editor = self.get_active_editor()
        if not editor or not self.matches or self.current_match_idx < 0:
            return
        replacement = self.replace_entry.get()
        idx, end_idx = self.matches[self.current_match_idx]

        editor.text.delete(idx, end_idx)
        editor.text.insert(idx, replacement)
        editor.set_modified(True)
        # Refresh matches
        self._on_find_change()

    def replace_all(self):
        editor = self.get_active_editor()
        if not editor or not self.matches:
            return
        replacement = self.replace_entry.get()
        # Replace in reverse to keep index positions valid
        for idx, end_idx in reversed(self.matches):
            editor.text.delete(idx, end_idx)
            editor.text.insert(idx, replacement)

        editor.set_modified(True)
        self._on_find_change()

    def open_find(self, initial_query: str = ""):
        self.pack(side="top", fill="x")
        if initial_query:
            self.find_entry.delete(0, "end")
            self.find_entry.insert(0, initial_query)
        self.find_entry.focus_set()
        self.find_entry.select_range(0, "end")
        self._on_find_change()

    def close(self):
        editor = self.get_active_editor()
        if editor:
            editor.text.tag_remove("search_match", "1.0", "end")
            editor.text.tag_remove("search_current", "1.0", "end")
            editor.text.focus_set()
        self.pack_forget()
        if self.on_close_cb:
            self.on_close_cb()

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=theme["header_bg"])
        self.row1.config(bg=theme["header_bg"])
        self.row2.config(bg=theme["header_bg"])
        self.find_icon.config(bg=theme["header_bg"], fg=theme["fg_dim"])
        self.replace_icon.config(bg=theme["header_bg"], fg=theme["fg_dim"])
        self.find_entry_border.config(bg=theme["border"])
        self.replace_entry_border.config(bg=theme["border"])
        self.find_entry.config(
            bg=theme["editor_bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
        )
        self.replace_entry.config(
            bg=theme["editor_bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
        )
        self.counter_label.config(bg=theme["btn_bg"], fg=theme["fg_dim"])
        self.btn_close.config(bg=theme["header_bg"], fg=theme["fg_dim"])

        for b in (self.btn_prev, self.btn_next, self.btn_replace, self.btn_replace_all):
            b.config(bg=theme["btn_bg"], fg=theme["fg"])

        self._restore_btn_bg(self.btn_case)
