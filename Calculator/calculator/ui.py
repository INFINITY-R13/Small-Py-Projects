"""
Modern GUI for Calculator application using Tkinter.
Supports Standard and Scientific modes, responsive dark theme,
keyboard shortcuts, and a collapsible calculation history drawer.
"""

import os
import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

from .engine import SafeMathEvaluator, CalculationError, format_result
from .history import HistoryManager, HistoryEntry


# Modern Dark Theme Palette
THEME = {
    "bg_main": "#18181b",        # Window background (zinc-900)
    "bg_card": "#27272a",        # Display & cards (zinc-800)
    "bg_card_border": "#3f3f46", # Subtle border (zinc-700)
    "bg_header": "#18181b",
    
    # Text colors
    "text_primary": "#fafafa",   # Bright white
    "text_secondary": "#a1a1aa", # Muted grey
    "text_accent": "#38bdf8",    # Sky blue
    "text_error": "#f87171",     # Soft red
    
    # Button Colors: [Normal, Hover, Pressed, Text]
    "btn_num": {
        "normal": "#27272a",
        "hover": "#3f3f46",
        "pressed": "#52525b",
        "text": "#ffffff",
    },
    "btn_op": {
        "normal": "#3b82f6",     # Blue
        "hover": "#2563eb",
        "pressed": "#1d4ed8",
        "text": "#ffffff",
    },
    "btn_equal": {
        "normal": "#10b981",     # Emerald green
        "hover": "#059669",
        "pressed": "#047857",
        "text": "#ffffff",
    },
    "btn_clear": {
        "normal": "#ef4444",     # Red
        "hover": "#dc2626",
        "pressed": "#b91c1c",
        "text": "#ffffff",
    },
    "btn_action": {
        "normal": "#334155",     # Slate
        "hover": "#475569",
        "pressed": "#64748b",
        "text": "#f1f5f9",
    },
    "btn_sci": {
        "normal": "#20232a",     # Darker tile for scientific
        "hover": "#2e3440",
        "pressed": "#3b4252",
        "text": "#cbd5e1",
    },
    "badge_active": "#3b82f6",
    "badge_inactive": "#27272a",
}


class ModernButton(tk.Label):
    """
    Custom cross-platform flat button built on tk.Label.
    Provides reliable background colors and hover/press feedback across all OSes.
    """

    def __init__(
        self,
        master,
        text: str,
        style: dict,
        font_config,
        command: Optional[Callable] = None,
        padx: int = 12,
        pady: int = 10,
        **kwargs,
    ):
        super().__init__(
            master,
            text=text,
            bg=style["normal"],
            fg=style["text"],
            font=font_config,
            cursor="hand2",
            relief="flat",
            bd=0,
            padx=padx,
            pady=pady,
            **kwargs,
        )
        self.style = style
        self.command = command
        self.default_bg = style["normal"]
        self.hover_bg = style["hover"]
        self.pressed_bg = style["pressed"]

        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    def _on_enter(self, event):
        self.configure(bg=self.hover_bg)

    def _on_leave(self, event):
        self.configure(bg=self.default_bg)

    def _on_press(self, event):
        self.configure(bg=self.pressed_bg)

    def _on_release(self, event):
        self.configure(bg=self.hover_bg)
        if self.command:
            self.command()

    def update_style(self, style: dict):
        self.style = style
        self.default_bg = style["normal"]
        self.hover_bg = style["hover"]
        self.pressed_bg = style["pressed"]
        self.configure(bg=self.default_bg, fg=style["text"])


class CalculatorUI:
    """Main Calculator application GUI."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Python Scientific Calculator")
        self.root.configure(bg=THEME["bg_main"])
        self.root.minsize(360, 560)

        # Storage directory for calculation history
        history_file = os.path.join(os.path.dirname(__file__), "..", ".calculator_history.json")
        self.history_mgr = HistoryManager(storage_path=history_file)
        self.engine = SafeMathEvaluator(angle_unit="DEG")

        # UI state variables
        self.is_scientific_mode = True
        self.is_history_open = False
        self.just_evaluated = False
        self.status_message_timer = None

        self._init_fonts()
        self._build_layout()
        self._bind_keyboard()

        # Update initial mode visibility
        self._update_mode_view()
        self._refresh_history_list()

    def _init_fonts(self):
        # Configure fonts with graceful fallbacks
        system_fonts = tkfont.families()
        primary_font = "SF Pro Display" if "SF Pro Display" in system_fonts else ("Helvetica Neue" if "Helvetica Neue" in system_fonts else "Arial")

        self.font_brand = tkfont.Font(family=primary_font, size=11, weight="bold")
        self.font_pill = tkfont.Font(family=primary_font, size=10, weight="bold")
        self.font_formula = tkfont.Font(family=primary_font, size=13)
        self.font_display = tkfont.Font(family=primary_font, size=26, weight="bold")
        self.font_btn_num = tkfont.Font(family=primary_font, size=16, weight="bold")
        self.font_btn_op = tkfont.Font(family=primary_font, size=16, weight="bold")
        self.font_btn_sci = tkfont.Font(family=primary_font, size=12)
        self.font_history = tkfont.Font(family=primary_font, size=11)

    def _build_layout(self):
        # Master Horizontal Container: [ Calculator Pane | History Pane ]
        self.main_container = tk.Frame(self.root, bg=THEME["bg_main"])
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Calculator Pane
        self.calc_pane = tk.Frame(self.main_container, bg=THEME["bg_main"], padx=16, pady=16)
        self.calc_pane.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 1. Header Toolbar
        self._build_header(self.calc_pane)

        # 2. Display Area
        self._build_display(self.calc_pane)

        # 3. Keypad Container
        self.keypad_container = tk.Frame(self.calc_pane, bg=THEME["bg_main"])
        self.keypad_container.pack(fill=tk.BOTH, expand=True, pady=(12, 0))

        # Scientific keypad (Left)
        self.sci_frame = tk.Frame(self.keypad_container, bg=THEME["bg_main"])
        self.sci_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        # Standard keypad (Right)
        self.std_frame = tk.Frame(self.keypad_container, bg=THEME["bg_main"])
        self.std_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._build_scientific_keypad(self.sci_frame)
        self._build_standard_keypad(self.std_frame)

        # 4. History Drawer (Collapsible Right Pane)
        self.history_pane = tk.Frame(
            self.main_container,
            bg=THEME["bg_card"],
            width=260,
            padx=12,
            pady=16,
            highlightbackground=THEME["bg_card_border"],
            highlightthickness=1,
        )
        self._build_history_drawer(self.history_pane)

    def _build_header(self, parent):
        header = tk.Frame(parent, bg=THEME["bg_main"])
        header.pack(fill=tk.X, pady=(0, 10))

        # Brand / App Title
        title_label = tk.Label(
            header,
            text="CALCULATOR",
            font=self.font_brand,
            bg=THEME["bg_main"],
            fg=THEME["text_secondary"],
        )
        title_label.pack(side=tk.LEFT)

        # Right-aligned toolbar buttons
        right_tools = tk.Frame(header, bg=THEME["bg_main"])
        right_tools.pack(side=tk.RIGHT)

        # Angle Unit Toggle (DEG / RAD)
        self.angle_btn = ModernButton(
            right_tools,
            text="DEG",
            style={
                "normal": THEME["badge_active"],
                "hover": "#2563eb",
                "pressed": "#1d4ed8",
                "text": "#ffffff",
            },
            font_config=self.font_pill,
            command=self._toggle_angle_unit,
            padx=8,
            pady=4,
        )
        self.angle_btn.pack(side=tk.LEFT, padx=3)

        # Mode Toggle (Standard / Scientific)
        self.mode_btn = ModernButton(
            right_tools,
            text="Scientific",
            style=THEME["btn_action"],
            font_config=self.font_pill,
            command=self._toggle_mode,
            padx=8,
            pady=4,
        )
        self.mode_btn.pack(side=tk.LEFT, padx=3)

        # History Toggle
        self.history_toggle_btn = ModernButton(
            right_tools,
            text="📜 History",
            style=THEME["btn_action"],
            font_config=self.font_pill,
            command=self._toggle_history_drawer,
            padx=8,
            pady=4,
        )
        self.history_toggle_btn.pack(side=tk.LEFT, padx=3)

    def _build_display(self, parent):
        # Rounded Display Card Container
        display_card = tk.Frame(
            parent,
            bg=THEME["bg_card"],
            highlightbackground=THEME["bg_card_border"],
            highlightthickness=1,
            padx=14,
            pady=12,
        )
        display_card.pack(fill=tk.X)

        # Formula / Previous expression & Notification bar
        formula_row = tk.Frame(display_card, bg=THEME["bg_card"])
        formula_row.pack(fill=tk.X)

        self.status_label = tk.Label(
            formula_row,
            text="",
            font=self.font_formula,
            bg=THEME["bg_card"],
            fg=THEME["text_accent"],
            anchor="w",
        )
        self.status_label.pack(side=tk.LEFT, fill=tk.X)

        self.formula_label = tk.Label(
            formula_row,
            text="",
            font=self.font_formula,
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
            anchor="e",
        )
        self.formula_label.pack(side=tk.RIGHT, fill=tk.X)

        # Primary Display (Interactive Entry widget)
        entry_row = tk.Frame(display_card, bg=THEME["bg_card"])
        entry_row.pack(fill=tk.X, pady=(6, 0))

        self.display_var = tk.StringVar(value="0")
        self.display_entry = tk.Entry(
            entry_row,
            textvariable=self.display_var,
            font=self.font_display,
            bg=THEME["bg_card"],
            fg=THEME["text_primary"],
            bd=0,
            relief="flat",
            justify="right",
            insertbackground=THEME["text_primary"],
            highlightthickness=0,
        )
        self.display_entry.pack(fill=tk.X, expand=True)

        # Quick action: copy button right beside entry
        copy_btn = ModernButton(
            entry_row,
            text="📋",
            style={
                "normal": THEME["bg_card"],
                "hover": THEME["bg_card_border"],
                "pressed": "#52525b",
                "text": THEME["text_secondary"],
            },
            font_config=self.font_formula,
            command=self.copy_to_clipboard,
            padx=6,
            pady=4,
        )
        copy_btn.pack(side=tk.RIGHT, padx=(6, 0))

        # Focus entry by default
        self.display_entry.focus_set()

    def _build_standard_keypad(self, parent):
        # Grid: 5 rows x 4 columns
        layout = [
            [("AC", THEME["btn_clear"], self.clear_all),
             ("⌫", THEME["btn_action"], self.backspace),
             ("%", THEME["btn_action"], lambda: self.insert_token("%")),
             ("÷", THEME["btn_op"], lambda: self.insert_token(" ÷ "))],
            
            [("7", THEME["btn_num"], lambda: self.insert_token("7")),
             ("8", THEME["btn_num"], lambda: self.insert_token("8")),
             ("9", THEME["btn_num"], lambda: self.insert_token("9")),
             ("×", THEME["btn_op"], lambda: self.insert_token(" × "))],
            
            [("4", THEME["btn_num"], lambda: self.insert_token("4")),
             ("5", THEME["btn_num"], lambda: self.insert_token("5")),
             ("6", THEME["btn_num"], lambda: self.insert_token("6")),
             ("−", THEME["btn_op"], lambda: self.insert_token(" − "))],
            
            [("1", THEME["btn_num"], lambda: self.insert_token("1")),
             ("2", THEME["btn_num"], lambda: self.insert_token("2")),
             ("3", THEME["btn_num"], lambda: self.insert_token("3")),
             ("+", THEME["btn_op"], lambda: self.insert_token(" + "))],
            
            [("±", THEME["btn_num"], self.toggle_negation),
             ("0", THEME["btn_num"], lambda: self.insert_token("0")),
             (".", THEME["btn_num"], lambda: self.insert_token(".")),
             ("=", THEME["btn_equal"], self.calculate_result)],
        ]

        for r in range(5):
            parent.rowconfigure(r, weight=1, uniform="std_row")
        for c in range(4):
            parent.columnconfigure(c, weight=1, uniform="std_col")

        for r_idx, row in enumerate(layout):
            for c_idx, (text, style, action) in enumerate(row):
                btn = ModernButton(
                    parent,
                    text=text,
                    style=style,
                    font_config=self.font_btn_op if text in ("+", "−", "×", "÷", "=") else self.font_btn_num,
                    command=action,
                )
                btn.grid(row=r_idx, column=c_idx, padx=3, pady=3, sticky="nsew")

    def _build_scientific_keypad(self, parent):
        # Grid: 5 rows x 4 columns
        sci_layout = [
            [("(", THEME["btn_sci"], lambda: self.insert_token("(")),
             (")", THEME["btn_sci"], lambda: self.insert_token(")")),
             ("π", THEME["btn_sci"], lambda: self.insert_token("π")),
             ("e", THEME["btn_sci"], lambda: self.insert_token("e"))],
            
            [("sin", THEME["btn_sci"], lambda: self.insert_token("sin(")),
             ("cos", THEME["btn_sci"], lambda: self.insert_token("cos(")),
             ("tan", THEME["btn_sci"], lambda: self.insert_token("tan(")),
             ("x²", THEME["btn_sci"], lambda: self.insert_token("^2"))],
            
            [("asin", THEME["btn_sci"], lambda: self.insert_token("asin(")),
             ("acos", THEME["btn_sci"], lambda: self.insert_token("acos(")),
             ("atan", THEME["btn_sci"], lambda: self.insert_token("atan(")),
             ("xʸ", THEME["btn_sci"], lambda: self.insert_token("^"))],
            
            [("log", THEME["btn_sci"], lambda: self.insert_token("log(")),
             ("ln", THEME["btn_sci"], lambda: self.insert_token("ln(")),
             ("√x", THEME["btn_sci"], lambda: self.insert_token("√(")),
             ("∛x", THEME["btn_sci"], lambda: self.insert_token("cbrt("))],
            
            [("1/x", THEME["btn_sci"], self.reciprocal),
             ("n!", THEME["btn_sci"], lambda: self.insert_token("!")),
             ("|x|", THEME["btn_sci"], lambda: self.insert_token("abs(")),
             ("Ans", THEME["btn_sci"], lambda: self.insert_token("ans"))],
        ]

        for r in range(5):
            parent.rowconfigure(r, weight=1, uniform="sci_row")
        for c in range(4):
            parent.columnconfigure(c, weight=1, uniform="sci_col")

        for r_idx, row in enumerate(sci_layout):
            for c_idx, (text, style, action) in enumerate(row):
                btn = ModernButton(
                    parent,
                    text=text,
                    style=style,
                    font_config=self.font_btn_sci,
                    command=action,
                )
                btn.grid(row=r_idx, column=c_idx, padx=3, pady=3, sticky="nsew")

    def _build_history_drawer(self, parent):
        parent.pack_propagate(False)

        # Header with title and Clear History button
        h_header = tk.Frame(parent, bg=THEME["bg_card"])
        h_header.pack(fill=tk.X, pady=(0, 10))

        h_title = tk.Label(
            h_header,
            text="HISTORY",
            font=self.font_brand,
            bg=THEME["bg_card"],
            fg=THEME["text_secondary"],
        )
        h_title.pack(side=tk.LEFT)

        clear_btn = ModernButton(
            h_header,
            text="Clear",
            style={
                "normal": THEME["bg_card"],
                "hover": "#3f3f46",
                "pressed": "#52525b",
                "text": THEME["text_error"],
            },
            font_config=self.font_pill,
            command=self.clear_history,
            padx=6,
            pady=2,
        )
        clear_btn.pack(side=tk.RIGHT)

        # Scrollable area
        container = tk.Frame(parent, bg=THEME["bg_card"])
        container.pack(fill=tk.BOTH, expand=True)

        self.history_canvas = tk.Canvas(
            container,
            bg=THEME["bg_card"],
            highlightthickness=0,
            bd=0,
        )
        self.history_scrollbar = tk.Scrollbar(
            container,
            orient="vertical",
            command=self.history_canvas.yview,
        )
        self.history_scroll_frame = tk.Frame(self.history_canvas, bg=THEME["bg_card"])

        self.history_scroll_frame.bind(
            "<Configure>",
            lambda e: self.history_canvas.configure(scrollregion=self.history_canvas.bbox("all")),
        )
        self.history_canvas_window = self.history_canvas.create_window(
            (0, 0), window=self.history_scroll_frame, anchor="nw"
        )
        self.history_canvas.configure(yscrollcommand=self.history_scrollbar.set)

        self.history_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.history_canvas.bind(
            "<Configure>",
            lambda e: self.history_canvas.itemconfig(self.history_canvas_window, width=e.width),
        )

    def _refresh_history_list(self):
        # Clear existing history widgets
        for widget in self.history_scroll_frame.winfo_children():
            widget.destroy()

        entries = self.history_mgr.get_all()
        if not entries:
            empty_lbl = tk.Label(
                self.history_scroll_frame,
                text="No recent calculations",
                font=self.font_history,
                bg=THEME["bg_card"],
                fg=THEME["text_secondary"],
                pady=20,
            )
            empty_lbl.pack(fill=tk.X)
            return

        for entry in entries:
            card = tk.Frame(
                self.history_scroll_frame,
                bg=THEME["bg_main"],
                highlightbackground=THEME["bg_card_border"],
                highlightthickness=1,
                padx=8,
                pady=8,
                cursor="hand2",
            )
            card.pack(fill=tk.X, pady=4)

            # Card Header: Timestamp
            time_lbl = tk.Label(
                card,
                text=entry.timestamp,
                font=tkfont.Font(size=9),
                bg=THEME["bg_main"],
                fg=THEME["text_secondary"],
                anchor="w",
            )
            time_lbl.pack(fill=tk.X)

            # Expression Line
            expr_lbl = tk.Label(
                card,
                text=entry.expression,
                font=self.font_history,
                bg=THEME["bg_main"],
                fg=THEME["text_secondary"],
                anchor="e",
            )
            expr_lbl.pack(fill=tk.X, pady=(2, 0))

            # Result Line
            res_lbl = tk.Label(
                card,
                text=f"= {entry.result}",
                font=tkfont.Font(size=13, weight="bold"),
                bg=THEME["bg_main"],
                fg=THEME["text_primary"],
                anchor="e",
            )
            res_lbl.pack(fill=tk.X)

            # Clicking card restores expression or result
            for w in (card, time_lbl, expr_lbl, res_lbl):
                w.bind("<Button-1>", lambda e, val=entry.result: self._load_from_history(val))

    def _load_from_history(self, value: str):
        # Clean formatted commas for evaluation
        clean_val = value.replace(",", "")
        self.display_var.set(clean_val)
        self.formula_label.configure(text=f"Recalled: {value}")
        self.just_evaluated = True
        self.show_status("Loaded from history")

    def _bind_keyboard(self):
        # Global hotkeys on root window
        self.root.bind("<Return>", lambda e: self.calculate_result())
        self.root.bind("<KP_Enter>", lambda e: self.calculate_result())
        self.root.bind("<Escape>", lambda e: self.clear_all())
        self.root.bind("<BackSpace>", lambda e: self.backspace())

        # Bind operator characters
        self.root.bind("+", lambda e: self.insert_token(" + "))
        self.root.bind("-", lambda e: self.insert_token(" − "))
        self.root.bind("*", lambda e: self.insert_token(" × "))
        self.root.bind("/", lambda e: self.insert_token(" ÷ "))
        self.root.bind("%", lambda e: self.insert_token("%"))
        self.root.bind("^", lambda e: self.insert_token("^"))
        self.root.bind("(", lambda e: self.insert_token("("))
        self.root.bind(")", lambda e: self.insert_token(")"))

        # Keyboard shortcuts for quick access
        self.root.bind("<Control-h>", lambda e: self._toggle_history_drawer())
        self.root.bind("<Command-h>", lambda e: self._toggle_history_drawer())
        self.root.bind("<Control-c>", lambda e: self.copy_to_clipboard())
        self.root.bind("<Command-c>", lambda e: self.copy_to_clipboard())

        # Digits 0-9 and period
        for digit in "0123456789.":
            self.root.bind(digit, lambda e, d=digit: self._on_key_digit(d))

    def _on_key_digit(self, digit: str):
        # If entry is not directly focused, insert digit cleanly
        if self.root.focus_get() != self.display_entry:
            self.insert_token(digit)

    def insert_token(self, token: str):
        current = self.display_var.get()

        # If user just calculated and inputs a new number/function, start fresh
        is_operator = token.strip() in ("+", "−", "×", "÷", "^", "%")
        if self.just_evaluated:
            if not is_operator:
                current = ""
            self.just_evaluated = False

        if current == "0" and token not in (".", " + ", " − ", " × ", " ÷ ", "%", "^"):
            new_text = token.lstrip()
        else:
            new_text = current + token

        self.display_var.set(new_text)
        self.display_entry.icursor(tk.END)

    def calculate_result(self):
        expr = self.display_var.get().strip()
        if not expr:
            return

        try:
            val = self.engine.evaluate(expr)
            formatted = format_result(val)
            self.formula_label.configure(text=f"{expr} =")
            self.display_var.set(formatted)
            self.engine.set_last_answer(val)
            self.just_evaluated = True

            # Save to history
            self.history_mgr.add(expr, formatted)
            if self.is_history_open:
                self._refresh_history_list()

            self.clear_status()
        except CalculationError as err:
            self.show_status(str(err), is_error=True)
        except Exception:
            self.show_status("Invalid syntax", is_error=True)

    def clear_all(self):
        self.display_var.set("0")
        self.formula_label.configure(text="")
        self.clear_status()
        self.just_evaluated = False

    def backspace(self):
        current = self.display_var.get()
        if self.just_evaluated:
            self.clear_all()
            return

        if len(current) > 1:
            # Handle spaced operators like " + "
            if current.endswith(" "):
                new_text = current.rstrip()[:-1].rstrip()
            else:
                new_text = current[:-1]
            self.display_var.set(new_text if new_text else "0")
        else:
            self.display_var.set("0")

    def toggle_negation(self):
        current = self.display_var.get().strip()
        if not current or current == "0":
            self.display_var.set("-")
            return

        if current.startswith("-"):
            self.display_var.set(current[1:])
        elif current.startswith("−"):
            self.display_var.set(current[1:])
        else:
            self.display_var.set("-" + current)

    def reciprocal(self):
        current = self.display_var.get().strip()
        if current and current != "0":
            self.display_var.set(f"1 / ({current})")
            self.calculate_result()
        else:
            self.insert_token("1 / (")

    def copy_to_clipboard(self):
        val = self.display_var.get()
        self.root.clipboard_clear()
        self.root.clipboard_append(val)
        self.show_status("Copied to clipboard!")

    def show_status(self, message: str, is_error: bool = False):
        color = THEME["text_error"] if is_error else THEME["text_accent"]
        self.status_label.configure(text=message, fg=color)

        if self.status_message_timer:
            self.root.after_cancel(self.status_message_timer)
        self.status_message_timer = self.root.after(4000, self.clear_status)

    def clear_status(self):
        self.status_label.configure(text="")
        self.status_message_timer = None

    def clear_history(self):
        self.history_mgr.clear()
        self._refresh_history_list()
        self.show_status("History cleared")

    def _toggle_angle_unit(self):
        current = self.engine.angle_unit
        new_unit = "RAD" if current == "DEG" else "DEG"
        self.engine.set_angle_unit(new_unit)
        self.angle_btn.configure(text=new_unit)
        self.show_status(f"Mode: {new_unit}")

    def _toggle_mode(self):
        self.is_scientific_mode = not self.is_scientific_mode
        self._update_mode_view()

    def _update_mode_view(self):
        if self.is_scientific_mode:
            self.sci_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))
            self.mode_btn.configure(text="Standard View")
            self.root.geometry("640x560")
        else:
            self.sci_frame.pack_forget()
            self.mode_btn.configure(text="Scientific View")
            self.root.geometry("380x560")

    def _toggle_history_drawer(self):
        self.is_history_open = not self.is_history_open
        if self.is_history_open:
            self.history_pane.pack(side=tk.RIGHT, fill=tk.Y)
            self._refresh_history_list()
            # Expand window width slightly to fit drawer smoothly
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            self.root.geometry(f"{cur_w + 260}x{cur_h}")
        else:
            self.history_pane.pack_forget()
            cur_w = self.root.winfo_width()
            cur_h = self.root.winfo_height()
            self.root.geometry(f"{max(380, cur_w - 260)}x{cur_h}")
