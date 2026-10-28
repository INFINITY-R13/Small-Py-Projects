"""
Custom aesthetic UI components for Contact Book:
- AvatarCanvas: Circular avatar with initials and pastel backgrounds
- ModernButton: Clean flat button with hover feedback
- Toast: Floating toast notification pill
- PlaceholderEntry: Text entry with placeholder behavior
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional, Tuple
from ui.theme import (
    TEXT_PRIMARY,
    TEXT_SECONDARY,
    TEXT_MUTED,
    BG_SURFACE,
    BG_SURFACE_HOVER,
    BG_SELECTED,
    BORDER_COLOR,
    BORDER_MUTED,
    ACCENT_PRIMARY,
    ACCENT_PRIMARY_HOVER,
    ACCENT_PRIMARY_TEXT,
    FONT_BODY,
    FONT_BODY_BOLD,
    FONT_SMALL,
    FONT_AVATAR,
    SUCCESS_COLOR,
    DANGER_COLOR,
    ACCENT_STAR,
)


class AvatarCanvas(tk.Canvas):
    """Circular avatar widget with centered initials."""

    def __init__(
        self,
        parent,
        initials: str,
        bg_color: str,
        text_color: str,
        size: int = 42,
        font_size: int = 13,
        **kwargs
    ):
        super().__init__(
            parent,
            width=size,
            height=size,
            bg=parent.cget("bg") if hasattr(parent, "cget") else BG_SURFACE,
            highlightthickness=0,
            **kwargs
        )
        self.size = size
        self.font_size = font_size
        self.initials = initials
        self.bg_color = bg_color
        self.text_color = text_color
        self.draw()

    def update_avatar(self, initials: str, bg_color: str, text_color: str):
        self.initials = initials
        self.bg_color = bg_color
        self.text_color = text_color
        self.draw()

    def draw(self):
        self.delete("all")
        pad = 2
        # Draw smooth circle
        self.create_oval(
            pad,
            pad,
            self.size - pad,
            self.size - pad,
            fill=self.bg_color,
            outline="",
        )
        # Draw initials
        self.create_text(
            self.size // 2,
            self.size // 2,
            text=self.initials,
            fill=self.text_color,
            font=("Helvetica Neue", self.font_size, "bold"),
        )


class ModernButton(tk.Frame):
    """
    A stylized, clickable flat button with hover effects and optional icon.
    """

    def __init__(
        self,
        parent,
        text: str = "",
        command: Optional[Callable] = None,
        bg: str = ACCENT_PRIMARY,
        fg: str = ACCENT_PRIMARY_TEXT,
        hover_bg: Optional[str] = None,
        font=FONT_BODY_BOLD,
        padx: int = 14,
        pady: int = 7,
        border_color: Optional[str] = None,
        cursor: str = "pointinghand",
        width: Optional[int] = None,
        **kwargs
    ):
        super().__init__(
            parent,
            bg=border_color if border_color else bg,
            padx=1 if border_color else 0,
            pady=1 if border_color else 0,
            cursor=cursor,
            **kwargs
        )

        self.normal_bg = bg
        self.hover_bg = hover_bg if hover_bg else bg
        self.normal_fg = fg
        self.command = command

        self.inner_frame = tk.Frame(self, bg=bg, cursor=cursor)
        self.inner_frame.pack(fill=tk.BOTH, expand=True)

        self.label = tk.Label(
            self.inner_frame,
            text=text,
            bg=bg,
            fg=fg,
            font=font,
            padx=padx,
            pady=pady,
            cursor=cursor,
        )
        if width:
            self.label.config(width=width)
        self.label.pack(fill=tk.BOTH, expand=True)

        for widget in (self, self.inner_frame, self.label):
            widget.bind("<Enter>", self._on_enter)
            widget.bind("<Leave>", self._on_leave)
            widget.bind("<Button-1>", self._on_click)

    def _on_enter(self, _):
        self.inner_frame.config(bg=self.hover_bg)
        self.label.config(bg=self.hover_bg)

    def _on_leave(self, _):
        self.inner_frame.config(bg=self.normal_bg)
        self.label.config(bg=self.normal_bg)

    def _on_click(self, _):
        if self.command:
            self.command()

    def set_text(self, text: str):
        self.label.config(text=text)


class PlaceholderEntry(tk.Frame):
    """Modern input entry with animated placeholder and subtle focus ring."""

    def __init__(
        self,
        parent,
        placeholder: str = "",
        show: str = "",
        font=FONT_BODY,
        width: int = 25,
        **kwargs
    ):
        super().__init__(parent, bg=BORDER_COLOR, padx=1, pady=1, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = TEXT_MUTED
        self.default_fg = TEXT_PRIMARY
        self.show = show

        self.entry = tk.Entry(
            self,
            font=font,
            bg=BG_SURFACE,
            fg=self.placeholder_color,
            bd=0,
            relief=tk.FLAT,
            insertbackground=TEXT_PRIMARY,
            width=width,
        )
        self.entry.pack(fill=tk.BOTH, expand=True, padx=8, pady=7)

        self.entry.insert(0, self.placeholder)

        self.entry.bind("<FocusIn>", self._on_focus_in)
        self.entry.bind("<FocusOut>", self._on_focus_out)

    def _on_focus_in(self, _):
        self.config(bg=BORDER_MUTED)
        if self.entry.get() == self.placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.default_fg)
            if self.show:
                self.entry.config(show=self.show)

    def _on_focus_out(self, _):
        self.config(bg=BORDER_COLOR)
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
            if self.show:
                self.entry.config(show="")

    def get(self) -> str:
        val = self.entry.get()
        if val == self.placeholder:
            return ""
        return val

    def set(self, text: str):
        self.entry.delete(0, tk.END)
        if text:
            self.entry.insert(0, text)
            self.entry.config(fg=self.default_fg)
            if self.show:
                self.entry.config(show=self.show)
        else:
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
            if self.show:
                self.entry.config(show="")


class Toast:
    """Non-blocking floating notification banner."""

    @staticmethod
    def show(root, message: str, is_success: bool = True, duration_ms: int = 2600):
        try:
            toast = tk.Toplevel(root)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)

            bg_color = "#0F172A"
            fg_color = "#F8FAFC"
            accent_icon = "✓ " if is_success else "ℹ "

            frame = tk.Frame(toast, bg=bg_color, padx=16, pady=9)
            frame.pack()

            label = tk.Label(
                frame,
                text=accent_icon + message,
                bg=bg_color,
                fg=fg_color,
                font=FONT_BODY_BOLD,
            )
            label.pack()

            # Position in bottom center of root window
            root.update_idletasks()
            rx = root.winfo_rootx()
            ry = root.winfo_rooty()
            rw = root.winfo_width()
            rh = root.winfo_height()

            toast.update_idletasks()
            tw = toast.winfo_width()
            th = toast.winfo_height()

            pos_x = rx + (rw - tw) // 2
            pos_y = ry + rh - th - 35
            toast.geometry(f"+{pos_x}+{pos_y}")

            # Destroy after duration
            toast.after(duration_ms, toast.destroy)
        except Exception:
            pass
