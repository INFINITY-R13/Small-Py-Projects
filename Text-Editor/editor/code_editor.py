"""
Core Code Editor widget with line numbers gutter, current line highlighting,
bracket matching, auto-indentation, auto-closing brackets, and syntax highlighting.
"""

import tkinter as tk
from tkinter import font as tkfont
from typing import Callable, Optional

from editor.syntax import SyntaxHighlighter, detect_language


class LineGutter(tk.Canvas):
    """Line number gutter that syncs with editor text scrolling."""

    def __init__(self, master, text_widget, theme: dict, font: tkfont.Font, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.theme = theme
        self.font = font
        self.bold_font = tkfont.Font(
            family=font.cget("family"),
            size=font.cget("size"),
            weight="bold"
        )
        self.config(
            bg=self.theme["gutter_bg"],
            highlightthickness=0,
            bd=0,
            width=50,
        )

    def set_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=self.theme["gutter_bg"])
        self.redraw()

    def set_font(self, font: tkfont.Font):
        self.font = font
        self.bold_font.config(
            family=font.cget("family"),
            size=font.cget("size"),
            weight="bold"
        )
        self.redraw()

    def redraw(self):
        """Redraws the visible line numbers on the canvas."""
        self.delete("all")
        try:
            # Current cursor line
            insert_line = int(self.text_widget.index("insert").split(".")[0])
        except (ValueError, tk.TclError):
            insert_line = 1

        try:
            i = self.text_widget.index("@0,0")
        except tk.TclError:
            return

        # Dynamically size gutter based on total lines
        try:
            last_line = int(self.text_widget.index("end-1c").split(".")[0])
        except (ValueError, tk.TclError):
            last_line = 1
        num_digits = max(3, len(str(last_line)))
        char_width = self.font.measure("0")
        desired_width = max(44, num_digits * char_width + 24)
        if self.winfo_width() != desired_width:
            self.config(width=desired_width)

        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = int(i.split(".")[0])
            is_active = (linenum == insert_line)

            fg = self.theme["gutter_active_fg"] if is_active else self.theme["gutter_fg"]
            fnt = self.bold_font if is_active else self.font

            # Draw line number right-aligned with 12px margin
            self.create_text(
                desired_width - 12,
                y + dline[3] // 2,
                text=str(linenum),
                anchor="e",
                fill=fg,
                font=fnt,
            )

            next_i = self.text_widget.index(f"{i}+1line")
            if next_i == i or self.text_widget.compare(next_i, ">", "end-1c"):
                break
            i = next_i


class CodeEditor(tk.Frame):
    """Aesthetic Code & Text Editor container with Gutter, Scrollbars, and Features."""

    def __init__(
        self,
        master,
        theme: dict,
        filepath: Optional[str] = None,
        on_modified: Optional[Callable[[bool], None]] = None,
        on_cursor_move: Optional[Callable] = None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.theme = theme
        self.filepath = filepath
        self.on_modified_cb = on_modified
        self.on_cursor_move_cb = on_cursor_move
        self.is_modified = False

        self._font_size = 14
        # Menlo is native and crisp on macOS; fallback to Monaco, Courier New
        families = list(tkfont.families(self))
        if "Menlo" in families:
            self._font_family = "Menlo"
        elif "Monaco" in families:
            self._font_family = "Monaco"
        else:
            self._font_family = "Courier"

        self.editor_font = tkfont.Font(
            family=self._font_family,
            size=self._font_size,
        )

        self._highlight_timer = None
        self._stats_timer = None

        self._init_ui()
        self._bind_events()

        # Language and syntax highlighter
        lang = detect_language(self.filepath)
        self.highlighter = SyntaxHighlighter(self.text, language=lang)
        self.apply_theme(self.theme)

    def _init_ui(self):
        self.config(bg=self.theme["editor_bg"])

        # Editor frame
        self.editor_frame = tk.Frame(self, bg=self.theme["editor_bg"])
        self.editor_frame.pack(fill="both", expand=True)

        # Text widget
        self.text = tk.Text(
            self.editor_frame,
            wrap="none",
            undo=True,
            maxundo=1000,
            autoseparators=True,
            font=self.editor_font,
            bg=self.theme["editor_bg"],
            fg=self.theme["fg"],
            insertbackground=self.theme["cursor"],
            insertwidth=2,
            insertofftime=300,
            insertontime=600,
            selectbackground=self.theme["selection_bg"],
            selectforeground=self.theme.get("selection_fg", self.theme["fg"]),
            padx=18,
            pady=14,
            spacing1=3,
            spacing3=3,
            relief="flat",
            bd=0,
            highlightthickness=0,
        )

        # Custom Scrollbar (Vertical)
        self.v_scroll = tk.Scrollbar(
            self.editor_frame,
            orient="vertical",
            command=self._on_v_scroll,
            relief="flat",
            bd=0,
            width=12,
        )

        # Line Gutter
        self.gutter = LineGutter(
            self.editor_frame,
            self.text,
            self.theme,
            self.editor_font,
        )

        # Layout
        self.gutter.pack(side="left", fill="y")
        self.v_scroll.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        # Link scrolling
        self.text.config(yscrollcommand=self._on_text_scroll)

    def _on_text_scroll(self, first, last):
        self.v_scroll.set(first, last)
        self.gutter.redraw()

    def _on_v_scroll(self, *args):
        self.text.yview(*args)
        self.gutter.redraw()

    def _bind_events(self):
        # Keyboard & mouse events
        self.text.bind("<KeyRelease>", self._on_key_release)
        self.text.bind("<KeyPress>", self._on_key_press)
        self.text.bind("<Button-1>", self._on_mouse_click)
        self.text.bind("<ButtonRelease-1>", self._on_mouse_release)
        self.text.bind("<MouseWheel>", lambda e: self.after_idle(self.gutter.redraw))
        self.text.bind("<Configure>", lambda e: self.after_idle(self.gutter.redraw))
        self.text.bind("<FocusIn>", lambda e: self.after_idle(self._update_decorations))

        # macOS specific keybindings & cross-platform
        self.text.bind("<Command-slash>", self.toggle_comment)
        self.text.bind("<Control-slash>", self.toggle_comment)
        self.text.bind("<Command-d>", self.duplicate_line)
        self.text.bind("<Control-d>", self.duplicate_line)

        # Zoom
        self.text.bind("<Command-equal>", lambda e: self.zoom(1))
        self.text.bind("<Command-plus>", lambda e: self.zoom(1))
        self.text.bind("<Control-equal>", lambda e: self.zoom(1))
        self.text.bind("<Command-minus>", lambda e: self.zoom(-1))
        self.text.bind("<Control-minus>", lambda e: self.zoom(-1))
        self.text.bind("<Command-0>", lambda e: self.reset_zoom())
        self.text.bind("<Control-0>", lambda e: self.reset_zoom())

        # Line movement
        self.text.bind("<Alt-Up>", self._move_line_up)
        self.text.bind("<Alt-Down>", self._move_line_down)

        # Smart tab / shift tab
        self.text.bind("<Tab>", self._handle_tab)
        self.text.bind("<Shift-Tab>", self._handle_shift_tab)
        self.text.bind("<ISO_Left_Tab>", self._handle_shift_tab)

        # Auto indent on Return
        self.text.bind("<Return>", self._handle_return)

        # Auto pair closing
        self.text.bind("<parenleft>", lambda e: self._handle_auto_pair("(", ")"))
        self.text.bind("<bracketleft>", lambda e: self._handle_auto_pair("[", "]"))
        self.text.bind("<braceleft>", lambda e: self._handle_auto_pair("{", "}"))
        self.text.bind("<quotedbl>", lambda e: self._handle_quote('"'))
        self.text.bind("<quoteright>", lambda e: self._handle_quote("'"))
        self.text.bind("<BackSpace>", self._handle_backspace)

    def _on_key_press(self, event):
        # Ignore modifier keys for modification flag
        if event.keysym in (
            "Control_L", "Control_R", "Shift_L", "Shift_R",
            "Alt_L", "Alt_R", "Meta_L", "Meta_R", "Super_L", "Super_R",
            "Left", "Right", "Up", "Down", "Prior", "Next", "Home", "End",
            "Caps_Lock", "Escape"
        ):
            return

        if not self.is_modified and event.char:
            self.set_modified(True)

    def _on_key_release(self, event):
        self._update_decorations()
        self._schedule_highlight()
        self._schedule_stats_update()

    def _on_mouse_click(self, event):
        self.after_idle(self._update_decorations)

    def _on_mouse_release(self, event):
        self._update_decorations()
        self._schedule_stats_update()

    def _update_decorations(self):
        """Updates current line highlight and bracket matching."""
        self.gutter.redraw()
        self._update_line_highlight()
        self._update_bracket_match()

    def _update_line_highlight(self):
        self.text.tag_remove("current_line", "1.0", "end")
        try:
            line = self.text.index("insert").split(".")[0]
            self.text.tag_add("current_line", f"{line}.0", f"{line}.0 + 1 line")
        except tk.TclError:
            pass

    def _update_bracket_match(self):
        self.text.tag_remove("bracket_match", "1.0", "end")
        pos = self.text.index("insert")
        pairs = {"(": ")", "[": "]", "{": "}"}
        rev_pairs = {")": "(", "]": "[", "}": "{"}

        # Check char before cursor and char at cursor
        for delta in ["-1c", "+0c"]:
            check_idx = self.text.index(f"{pos} {delta}")
            char = self.text.get(check_idx)
            if char in pairs:
                target = pairs[char]
                # Find matching forward
                match_idx = self._find_matching_bracket(check_idx, char, target, forward=True)
                if match_idx:
                    self.text.tag_add("bracket_match", check_idx, f"{check_idx}+1c")
                    self.text.tag_add("bracket_match", match_idx, f"{match_idx}+1c")
                break
            elif char in rev_pairs:
                target = rev_pairs[char]
                # Find matching backward
                match_idx = self._find_matching_bracket(check_idx, char, target, forward=False)
                if match_idx:
                    self.text.tag_add("bracket_match", check_idx, f"{check_idx}+1c")
                    self.text.tag_add("bracket_match", match_idx, f"{match_idx}+1c")
                break

    def _find_matching_bracket(self, start_idx: str, open_ch: str, close_ch: str, forward: bool) -> Optional[str]:
        depth = 0
        cur = start_idx
        limit = 500  # Avoid deep traversal hangs
        count = 0
        while count < limit:
            count += 1
            if forward:
                cur = self.text.index(f"{cur}+1c")
                if self.text.compare(cur, ">=", "end-1c"):
                    break
            else:
                if self.text.compare(cur, "<=", "1.0"):
                    break
                cur = self.text.index(f"{cur}-1c")

            c = self.text.get(cur)
            if c == open_ch:
                depth += 1
            elif c == close_ch:
                if depth == 0:
                    return cur
                depth -= 1
        return None

    def _handle_auto_pair(self, open_ch: str, close_ch: str):
        self.text.insert("insert", open_ch + close_ch)
        self.text.mark_set("insert", "insert - 1 char")
        self.set_modified(True)
        return "break"

    def _handle_quote(self, q_ch: str):
        cur_char = self.text.get("insert")
        if cur_char == q_ch:
            self.text.mark_set("insert", "insert + 1 char")
            return "break"
        self.text.insert("insert", q_ch + q_ch)
        self.text.mark_set("insert", "insert - 1 char")
        self.set_modified(True)
        return "break"

    def _handle_backspace(self, event):
        try:
            prev_char = self.text.get("insert - 1 char")
            next_char = self.text.get("insert")
            pairs = {("(", ")"), ("[", "]"), ("{", "}"), ('"', '"'), ("'", "'")}
            if (prev_char, next_char) in pairs:
                self.text.delete("insert - 1 char", "insert + 1 char")
                self.set_modified(True)
                return "break"
        except tk.TclError:
            pass
        return None

    def _handle_tab(self, event):
        try:
            sel_ranges = self.text.tag_ranges("sel")
            if sel_ranges:
                start_line = int(self.text.index(sel_ranges[0]).split(".")[0])
                end_line = int(self.text.index(sel_ranges[1]).split(".")[0])
                for line in range(start_line, end_line + 1):
                    self.text.insert(f"{line}.0", "    ")
                self.set_modified(True)
                return "break"
        except tk.TclError:
            pass
        self.text.insert("insert", "    ")
        self.set_modified(True)
        return "break"

    def _handle_shift_tab(self, event):
        try:
            sel_ranges = self.text.tag_ranges("sel")
            if sel_ranges:
                start_line = int(self.text.index(sel_ranges[0]).split(".")[0])
                end_line = int(self.text.index(sel_ranges[1]).split(".")[0])
            else:
                start_line = int(self.text.index("insert").split(".")[0])
                end_line = start_line

            for line in range(start_line, end_line + 1):
                line_str = self.text.get(f"{line}.0", f"{line}.4")
                if line_str == "    ":
                    self.text.delete(f"{line}.0", f"{line}.4")
                elif line_str.startswith(" "):
                    # Remove leading spaces up to 4
                    count = len(line_str) - len(line_str.lstrip(" "))
                    if count > 0:
                        self.text.delete(f"{line}.0", f"{line}.{min(count, 4)}")
            self.set_modified(True)
        except tk.TclError:
            pass
        return "break"

    def _handle_return(self, event):
        """Smart indentation on Return."""
        try:
            line_idx = self.text.index("insert").split(".")[0]
            line_content = self.text.get(f"{line_idx}.0", "insert")
            indent = ""
            for ch in line_content:
                if ch in (" ", "\t"):
                    indent += ch
                else:
                    break

            stripped = line_content.rstrip()
            if stripped.endswith(":") or stripped.endswith("{") or stripped.endswith("[") or stripped.endswith("("):
                indent += "    "

            self.text.insert("insert", "\n" + indent)
            self.text.see("insert")
            self.set_modified(True)
            self._update_decorations()
            return "break"
        except tk.TclError:
            return None

    def toggle_comment(self, event=None):
        """Toggles line comment (#) for selection or current line."""
        try:
            sel_ranges = self.text.tag_ranges("sel")
            if sel_ranges:
                start_line = int(self.text.index(sel_ranges[0]).split(".")[0])
                end_line = int(self.text.index(sel_ranges[1]).split(".")[0])
            else:
                start_line = int(self.text.index("insert").split(".")[0])
                end_line = start_line

            # Check if all lines are commented
            all_commented = True
            for line in range(start_line, end_line + 1):
                text = self.text.get(f"{line}.0", f"{line}.end").strip()
                if text and not text.startswith("#"):
                    all_commented = False
                    break

            for line in range(start_line, end_line + 1):
                line_text = self.text.get(f"{line}.0", f"{line}.end")
                if all_commented:
                    # Uncomment
                    if "# " in line_text:
                        pos = line_text.find("# ")
                        self.text.delete(f"{line}.{pos}", f"{line}.{pos + 2}")
                    elif "#" in line_text:
                        pos = line_text.find("#")
                        self.text.delete(f"{line}.{pos}", f"{line}.{pos + 1}")
                else:
                    # Comment
                    self.text.insert(f"{line}.0", "# ")

            self.set_modified(True)
            self._schedule_highlight()
        except tk.TclError:
            pass
        return "break"

    def duplicate_line(self, event=None):
        """Duplicates current line or selection."""
        try:
            line = self.text.index("insert").split(".")[0]
            line_content = self.text.get(f"{line}.0", f"{line}.end")
            self.text.insert(f"{line}.end", "\n" + line_content)
            self.set_modified(True)
            self._update_decorations()
        except tk.TclError:
            pass
        return "break"

    def _move_line_up(self, event=None):
        try:
            line = int(self.text.index("insert").split(".")[0])
            if line <= 1:
                return "break"
            cur_line = self.text.get(f"{line}.0", f"{line}.end")
            prev_line = self.text.get(f"{line - 1}.0", f"{line - 1}.end")

            self.text.delete(f"{line - 1}.0", f"{line}.end")
            self.text.insert(f"{line - 1}.0", cur_line + "\n" + prev_line)
            self.text.mark_set("insert", f"{line - 1}.0")
            self.set_modified(True)
            self._update_decorations()
        except tk.TclError:
            pass
        return "break"

    def _move_line_down(self, event=None):
        try:
            line = int(self.text.index("insert").split(".")[0])
            total_lines = int(self.text.index("end-1c").split(".")[0])
            if line >= total_lines:
                return "break"
            cur_line = self.text.get(f"{line}.0", f"{line}.end")
            next_line = self.text.get(f"{line + 1}.0", f"{line + 1}.end")

            self.text.delete(f"{line}.0", f"{line + 1}.end")
            self.text.insert(f"{line}.0", next_line + "\n" + cur_line)
            self.text.mark_set("insert", f"{line + 1}.0")
            self.set_modified(True)
            self._update_decorations()
        except tk.TclError:
            pass
        return "break"

    def zoom(self, delta: int):
        new_size = max(9, min(36, self._font_size + delta))
        if new_size != self._font_size:
            self._font_size = new_size
            self.editor_font.config(size=self._font_size)
            self.gutter.set_font(self.editor_font)
            self.gutter.redraw()

    def reset_zoom(self):
        self._font_size = 14
        self.editor_font.config(size=self._font_size)
        self.gutter.set_font(self.editor_font)
        self.gutter.redraw()

    def _schedule_highlight(self):
        if self._highlight_timer:
            self.after_cancel(self._highlight_timer)
        self._highlight_timer = self.after(70, self._do_highlight)

    def _do_highlight(self):
        self._highlight_timer = None
        self.highlighter.highlight_all()

    def _schedule_stats_update(self):
        if self._stats_timer:
            self.after_cancel(self._stats_timer)
        self._stats_timer = self.after(50, self._do_stats_update)

    def _do_stats_update(self):
        self._stats_timer = None
        if not self.on_cursor_move_cb:
            return

        try:
            idx = self.text.index("insert")
            line, col = idx.split(".")
            total_lines = int(self.text.index("end-1c").split(".")[0])
            content = self.text.get("1.0", "end-1c")
            total_chars = len(content)
            total_words = len(content.split())

            sel_chars = 0
            sel_ranges = self.text.tag_ranges("sel")
            if sel_ranges:
                sel_text = self.text.get(sel_ranges[0], sel_ranges[1])
                sel_chars = len(sel_text)

            self.on_cursor_move_cb(
                line=int(line),
                col=int(col) + 1,
                total_lines=total_lines,
                total_words=total_words,
                total_chars=total_chars,
                sel_count=sel_chars,
            )
        except tk.TclError:
            pass

    def set_modified(self, modified: bool):
        if self.is_modified != modified:
            self.is_modified = modified
            if self.on_modified_cb:
                self.on_modified_cb(modified)

    def apply_theme(self, theme: dict):
        self.theme = theme
        self.config(bg=theme["editor_bg"])
        self.editor_frame.config(bg=theme["editor_bg"])

        self.text.config(
            bg=theme["editor_bg"],
            fg=theme["fg"],
            insertbackground=theme["cursor"],
            selectbackground=theme["selection_bg"],
            selectforeground=theme.get("selection_fg", theme["fg"]),
        )

        # Tags configuration
        self.text.tag_configure("current_line", background=theme["line_highlight"])
        self.text.tag_configure(
            "bracket_match",
            background=theme["bracket_match_bg"],
            foreground=theme["bracket_match_fg"],
        )
        self.text.tag_configure(
            "search_match",
            background=theme["search_match_bg"],
            foreground=theme["search_match_fg"],
        )
        self.text.tag_configure(
            "search_current",
            background=theme["search_current_bg"],
            foreground=theme["search_match_fg"],
        )

        # Syntax tags configuration
        syntax = theme.get("syntax", {})
        for tag, color in syntax.items():
            font_opts = {}
            if tag in ("comment",):
                font_opts = {"slant": "italic"}
            elif tag in ("keyword", "class", "md_bold", "md_header"):
                font_opts = {"weight": "bold"}
            tag_font = tkfont.Font(
                family=self._font_family,
                size=self._font_size,
                **font_opts
            )
            self.text.tag_configure(tag, foreground=color, font=tag_font)

        self.gutter.set_theme(theme)
        self._schedule_highlight()
        self._update_decorations()

    def set_filepath(self, filepath: Optional[str]):
        self.filepath = filepath
        lang = detect_language(filepath)
        self.highlighter.set_language(lang)
        self._schedule_highlight()
