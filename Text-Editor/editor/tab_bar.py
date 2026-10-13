"""
Aesthetic Tab Bar with file icons, modified indicator dots, close buttons,
and active tab styling.
"""

import os
import tkinter as tk
from typing import Callable, List, Optional


def get_file_icon(filepath: Optional[str]) -> str:
    if not filepath:
        return "📄"
    ext = os.path.splitext(filepath)[1].lower()
    icons = {
        ".py": "🐍",
        ".pyw": "🐍",
        ".md": "📝",
        ".markdown": "📝",
        ".json": "⚙️",
        ".js": "⚡",
        ".jsx": "⚡",
        ".ts": "⚡",
        ".tsx": "⚡",
        ".html": "🌐",
        ".htm": "🌐",
        ".css": "🎨",
        ".sh": "🐚",
        ".bash": "🐚",
        ".zsh": "🐚",
        ".sql": "🗄️",
        ".txt": "📄",
        ".yml": "⚙️",
        ".yaml": "⚙️",
        ".toml": "⚙️",
    }
    return icons.get(ext, "📄")


class TabItem(tk.Frame):
    """Individual aesthetic tab button."""

    def __init__(
        self,
        master,
        tab_id: int,
        title: str,
        filepath: Optional[str],
        theme: dict,
        on_select: Callable[[int], None],
        on_close: Callable[[int], None],
    ):
        super().__init__(master, bg=theme["tab_inactive_bg"], cursor="hand2")
        self.tab_id = tab_id
        self.title_text = title
        self.filepath = filepath
        self.theme = theme
        self.on_select_cb = on_select
        self.on_close_cb = on_close
        self.is_active = False
        self.is_modified = False

        self._init_ui()

    def _init_ui(self):
        self.config(padx=10, pady=6)

        # Bottom accent indicator line
        self.accent_indicator = tk.Frame(
            self,
            bg=self.theme["tab_inactive_bg"],
            height=2,
        )
        self.accent_indicator.pack(side="bottom", fill="x")

        # Content container
        self.content_frame = tk.Frame(self, bg=self.theme["tab_inactive_bg"])
        self.content_frame.pack(side="top", fill="both", expand=True)

        icon_char = get_file_icon(self.filepath)
        self.icon_label = tk.Label(
            self.content_frame,
            text=icon_char,
            bg=self.theme["tab_inactive_bg"],
            fg=self.theme["tab_fg"],
            font=("Helvetica Neue", 12),
        )
        self.icon_label.pack(side="left", padx=(0, 6))

        self.title_label = tk.Label(
            self.content_frame,
            text=self.title_text,
            bg=self.theme["tab_inactive_bg"],
            fg=self.theme["tab_fg"],
            font=("Helvetica Neue", 12),
        )
        self.title_label.pack(side="left", padx=(0, 6))

        self.dot_label = tk.Label(
            self.content_frame,
            text="●",
            bg=self.theme["tab_inactive_bg"],
            fg=self.theme["tab_inactive_bg"],  # hidden by default
            font=("Helvetica Neue", 9),
        )
        self.dot_label.pack(side="left", padx=(0, 4))

        self.close_btn = tk.Label(
            self.content_frame,
            text="✕",
            bg=self.theme["tab_inactive_bg"],
            fg=self.theme["tab_fg"],
            font=("Helvetica Neue", 10),
            cursor="hand2",
            padx=3,
            pady=1,
        )
        self.close_btn.pack(side="left")

        # Events
        for widget in (self, self.content_frame, self.icon_label, self.title_label, self.dot_label):
            widget.bind("<Button-1>", lambda e: self.on_select_cb(self.tab_id))
            widget.bind("<Enter>", self._on_hover)
            widget.bind("<Leave>", self._on_leave)

        self.close_btn.bind("<Button-1>", lambda e: self.on_close_cb(self.tab_id))
        self.close_btn.bind("<Enter>", self._on_close_hover)
        self.close_btn.bind("<Leave>", self._on_close_leave)

    def set_active(self, active: bool):
        self.is_active = active
        bg = self.theme["tab_active_bg"] if active else self.theme["tab_inactive_bg"]
        fg = self.theme["tab_active_fg"] if active else self.theme["tab_fg"]
        accent_color = self.theme["tab_active_border"] if active else bg

        self.config(bg=bg)
        self.content_frame.config(bg=bg)
        self.icon_label.config(bg=bg)
        self.title_label.config(bg=bg, fg=fg)
        self.close_btn.config(bg=bg, fg=fg)
        self.dot_label.config(bg=bg)
        self.accent_indicator.config(bg=accent_color)
        self._update_dot()

    def set_modified(self, modified: bool):
        self.is_modified = modified
        self._update_dot()

    def _update_dot(self):
        bg = self.theme["tab_active_bg"] if self.is_active else self.theme["tab_inactive_bg"]
        if self.is_modified:
            self.dot_label.config(fg=self.theme["accent"], bg=bg)
        else:
            self.dot_label.config(fg=bg, bg=bg)

    def set_filepath(self, filepath: Optional[str]):
        self.filepath = filepath
        name = os.path.basename(filepath) if filepath else "Untitled"
        self.title_text = name
        self.title_label.config(text=name)
        self.icon_label.config(text=get_file_icon(filepath))

    def _on_hover(self, event):
        if not self.is_active:
            h_bg = self.theme["tab_hover_bg"]
            self.config(bg=h_bg)
            self.content_frame.config(bg=h_bg)
            self.icon_label.config(bg=h_bg)
            self.title_label.config(bg=h_bg)
            self.close_btn.config(bg=h_bg)
            self.dot_label.config(bg=h_bg)
            self.accent_indicator.config(bg=h_bg)

    def _on_leave(self, event):
        if not self.is_active:
            bg = self.theme["tab_inactive_bg"]
            self.config(bg=bg)
            self.content_frame.config(bg=bg)
            self.icon_label.config(bg=bg)
            self.title_label.config(bg=bg)
            self.close_btn.config(bg=bg)
            self.dot_label.config(bg=bg)
            self.accent_indicator.config(bg=bg)

    def _on_close_hover(self, event):
        self.close_btn.config(
            bg=self.theme.get("tab_close_hover", "#f7768e"),
            fg="#ffffff",
        )

    def _on_close_leave(self, event):
        bg = self.theme["tab_active_bg"] if self.is_active else self.theme["tab_inactive_bg"]
        fg = self.theme["tab_active_fg"] if self.is_active else self.theme["tab_fg"]
        self.close_btn.config(bg=bg, fg=fg)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.set_active(self.is_active)


class AestheticTabBar(tk.Frame):
    """Container holding tabs with a new tab button."""

    def __init__(
        self,
        master,
        theme: dict,
        on_tab_select: Callable[[int], None],
        on_tab_close: Callable[[int], None],
        on_new_tab: Callable[[], None],
        **kwargs,
    ):
        super().__init__(master, bg=theme["tab_bar_bg"], **kwargs)
        self.theme = theme
        self.on_tab_select_cb = on_tab_select
        self.on_tab_close_cb = on_tab_close
        self.on_new_tab_cb = on_new_tab
        self.tabs: List[TabItem] = []

        self._init_ui()

    def _init_ui(self):
        # Tabs scrollable/packable frame
        self.tabs_container = tk.Frame(self, bg=self.theme["tab_bar_bg"])
        self.tabs_container.pack(side="left", fill="y")

        # New tab '+' button
        self.new_btn = tk.Label(
            self,
            text="+",
            bg=self.theme["tab_bar_bg"],
            fg=self.theme["tab_fg"],
            font=("Helvetica Neue", 15, "bold"),
            cursor="hand2",
            padx=10,
            pady=4,
        )
        self.new_btn.pack(side="left", fill="y")
        self.new_btn.bind("<Button-1>", lambda e: self.on_new_tab_cb())
        self.new_btn.bind("<Enter>", lambda e: self.new_btn.config(bg=self.theme["tab_hover_bg"], fg=self.theme["accent"]))
        self.new_btn.bind("<Leave>", lambda e: self.new_btn.config(bg=self.theme["tab_bar_bg"], fg=self.theme["tab_fg"]))

        # Bottom thin border line
        self.border_line = tk.Frame(self, bg=self.theme["border"], height=1)
        self.border_line.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw")

    def add_tab(self, tab_id: int, title: str, filepath: Optional[str] = None) -> TabItem:
        tab = TabItem(
            self.tabs_container,
            tab_id=tab_id,
            title=title,
            filepath=filepath,
            theme=self.theme,
            on_select=self.on_tab_select_cb,
            on_close=self.on_tab_close_cb,
        )
        tab.pack(side="left", fill="y")
        self.tabs.append(tab)
        return tab

    def remove_tab(self, tab_id: int):
        tab = self.get_tab(tab_id)
        if tab:
            tab.destroy()
            self.tabs.remove(tab)

    def get_tab(self, tab_id: int) -> Optional[TabItem]:
        for tab in self.tabs:
            if tab.tab_id == tab_id:
                return tab
        return None

    def select_tab(self, tab_id: int):
        for tab in self.tabs:
            tab.set_active(tab.tab_id == tab_id)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=theme["tab_bar_bg"])
        self.tabs_container.config(bg=theme["tab_bar_bg"])
        self.new_btn.config(bg=theme["tab_bar_bg"], fg=theme["tab_fg"])
        self.border_line.config(bg=theme["border"])
        for tab in self.tabs:
            tab.apply_theme(theme)
