"""
Pomodoro Timer — A beautiful, minimal Pomodoro timer for desktop
Built with pure Python + tkinter (stdlib only)
"""

import math
import platform
import subprocess
import sys
import time
import tkinter as tk
from tkinter import font as tkfont


# ─── Color Palette ────────────────────────────────────────────────────────────
BG          = "#FFF0F3"   # soft blush background
CARD        = "#FFE4E9"   # light pink card/panel
TRACK       = "#FFD6DF"   # progress ring track
ACCENT      = "#FF6B8A"   # rose pink (primary accent)
ACCENT2     = "#FF8FA3"   # muted rose (secondary)
TEXT        = "#3D1A24"   # deep plum (primary text)
TEXT2       = "#8C6570"   # muted plum (secondary text)
WHITE       = "#FFFFFF"
SHADOW      = "#F0C8D2"   # subtle shadow tint
DANGER      = "#E04F6E"   # validation error text

# ─── Default Durations (seconds) ──────────────────────────────────────────────
DEFAULT_DURATIONS = {
    "pomodoro":    25 * 60,
    "short_break":  5 * 60,
    "long_break":  15 * 60,
}

RING_SIZE    = 280          # canvas width/height
RING_RADIUS  = 120          # arc radius from centre
RING_WIDTH   = 12           # stroke width
RING_CX      = RING_SIZE // 2
RING_CY      = RING_SIZE // 2


# ─── Main Application ──────────────────────────────────────────────────────────
class PomodoroApp(tk.Tk):
    def __init__(self):
        super().__init__()

        # ── Window setup ──────────────────────────────────────────────────────
        self.title("🍅 Pomodoro")
        self.resizable(False, False)
        self.configure(bg=BG)
        self.geometry("400x620")
        # Centre on screen
        self.update_idletasks()
        x = max(0, (self.winfo_screenwidth()  - 400) // 2)
        y = max(0, (self.winfo_screenheight() - 620) // 2)
        self.geometry(f"400x620+{x}+{y}")

        # ── State variables ────────────────────────────────────────────────────
        self.mode          = tk.StringVar(value="pomodoro")
        self.running       = False
        self.after_id      = None
        self.end_time      = None                      # monotonic timestamp when timer runs
        self.durations     = dict(DEFAULT_DURATIONS)   # mutable copy (seconds)
        self.remaining     = float(self.durations["pomodoro"])
        self.total         = float(self.durations["pomodoro"])
        self.sessions_done = 0
        self.daily_goal    = tk.IntVar(value=4)
        self.auto_start    = tk.BooleanVar(value=False)
        self.settings_win  = None                      # singleton settings modal reference
        self._sound_proc   = None                      # track active notification sound process

        # ── Font helpers (SF Pro → Helvetica Neue → system) ───────────────────
        self._init_fonts()

        # ── Build UI ──────────────────────────────────────────────────────────
        self.create_widgets()
        self.update_window_title()

        # ── Keyboard shortcuts ────────────────────────────────────────────────
        self._bind_shortcuts()

        # Graceful quit
        self.protocol("WM_DELETE_WINDOW", self.on_close)

    # ── Fonts ─────────────────────────────────────────────────────────────────
    def _init_fonts(self):
        families = tkfont.families()
        preferred = ["SF Pro Display", "SF Pro Text", ".AppleSystemUIFont",
                     "Helvetica Neue", "Helvetica", "Arial"]
        body_family = next((f for f in preferred if f in families), "TkDefaultFont")

        self.font_huge   = tkfont.Font(family=body_family, size=48, weight="bold")
        self.font_large  = tkfont.Font(family=body_family, size=18, weight="bold")
        self.font_medium = tkfont.Font(family=body_family, size=13)
        self.font_small  = tkfont.Font(family=body_family, size=11)
        self.font_tiny   = tkfont.Font(family=body_family, size=10)
        self.font_tab    = tkfont.Font(family=body_family, size=12, weight="bold")
        self.font_btn    = tkfont.Font(family=body_family, size=14, weight="bold")
        self.font_btn_sm = tkfont.Font(family=body_family, size=12)

    # ── Shortcuts ─────────────────────────────────────────────────────────────
    def _bind_shortcuts(self):
        self.bind("<space>", lambda e: self.start_pause())
        self.bind("<r>", lambda e: self.reset_timer())
        self.bind("<R>", lambda e: self.reset_timer())
        self.bind("<Key-1>", lambda e: self.switch_mode("pomodoro"))
        self.bind("<Key-2>", lambda e: self.switch_mode("short_break"))
        self.bind("<Key-3>", lambda e: self.switch_mode("long_break"))
        self.bind("<s>", lambda e: self.open_settings())
        self.bind("<S>", lambda e: self.open_settings())
        self.bind("<a>", lambda e: self._toggle_auto())
        self.bind("<A>", lambda e: self._toggle_auto())

    # ── Widget Construction ────────────────────────────────────────────────────
    def create_widgets(self):
        # Outer padding frame
        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True, padx=20, pady=20)

        # App title
        title_lbl = tk.Label(outer, text="Pomodoro", font=self.font_large,
                             bg=BG, fg=TEXT)
        title_lbl.pack(pady=(0, 16))

        # Mode tabs
        self.create_mode_tabs(outer)

        # Spacer
        tk.Frame(outer, bg=BG, height=12).pack()

        # Timer canvas (circular progress ring)
        self.create_timer_canvas(outer)

        # Spacer
        tk.Frame(outer, bg=BG, height=16).pack()

        # Start/Pause/Resume + Reset controls
        self.create_controls(outer)

        # Spacer
        tk.Frame(outer, bg=BG, height=20).pack()

        # Session dots
        self.create_session_counter(outer)

        # Bottom bar (auto-start + settings)
        self.create_bottom_bar(outer)

    # ── Mode Tabs ─────────────────────────────────────────────────────────────
    def create_mode_tabs(self, parent):
        """Pill-style tab bar for the three modes."""
        tab_bar = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=0,
                           padx=4, pady=4)
        tab_bar.pack()

        self.tab_buttons = {}
        modes = [
            ("Pomodoro",    "pomodoro"),
            ("Short Break", "short_break"),
            ("Long Break",  "long_break"),
        ]

        for label, key in modes:
            btn = tk.Label(tab_bar, text=label, font=self.font_tab,
                           padx=14, pady=6, cursor="hand2")
            btn.pack(side="left", padx=3)
            btn.bind("<Button-1>", lambda e, k=key: self.switch_mode(k))
            btn.bind("<Enter>", lambda e, k=key: self._hover_tab(k, True))
            btn.bind("<Leave>", lambda e, k=key: self._hover_tab(k, False))
            self.tab_buttons[key] = btn

        self._refresh_tabs()

    def _hover_tab(self, key: str, entering: bool):
        if key == self.mode.get():
            return
        btn = self.tab_buttons.get(key)
        if btn:
            btn.configure(bg=TRACK if entering else CARD,
                          fg=TEXT if entering else TEXT2)

    def _refresh_tabs(self):
        """Update tab visual state to match current mode."""
        cur = self.mode.get()
        for key, btn in self.tab_buttons.items():
            if key == cur:
                btn.configure(bg=ACCENT, fg=WHITE)
            else:
                btn.configure(bg=CARD, fg=TEXT2)

    # ── Timer Canvas ──────────────────────────────────────────────────────────
    def create_timer_canvas(self, parent):
        """Circular progress ring with centred MM:SS label."""
        card_frame = tk.Frame(parent, bg=CARD, bd=0, highlightthickness=0)
        card_frame.pack()

        self.canvas = tk.Canvas(card_frame, width=RING_SIZE, height=RING_SIZE,
                                bg=CARD, highlightthickness=0)
        self.canvas.pack(padx=20, pady=12)

        # Draw static track circle
        r = RING_RADIUS
        self.canvas.create_oval(RING_CX - r, RING_CY - r,
                                RING_CX + r, RING_CY + r,
                                outline=TRACK, width=RING_WIDTH, fill=CARD,
                                tags="track")

        # Progress arc (will be redrawn each tick)
        self.arc_id = self.canvas.create_arc(
            RING_CX - r, RING_CY - r, RING_CX + r, RING_CY + r,
            start=90, extent=-359.99,   # start at top, sweep clockwise
            outline=ACCENT, width=RING_WIDTH, style="arc",
            tags="arc"
        )

        # Centre time label
        self.canvas.create_text(RING_CX, RING_CY - 14,
                                text=self._format_time(self.remaining),
                                font=self.font_huge, fill=TEXT,
                                tags="time_text")

        # Centre mode sub-label
        self.canvas.create_text(RING_CX, RING_CY + 42,
                                text=self._mode_label(self.mode.get()),
                                font=self.font_medium, fill=TEXT2,
                                tags="mode_text")

    # ── Controls ──────────────────────────────────────────────────────────────
    def _get_start_label(self) -> str:
        if self.running:
            return "Pause"
        if 0 < self.remaining < self.total:
            return "Resume"
        return "Start"

    def create_controls(self, parent):
        """Start/Pause/Resume button and Reset button."""
        ctrl_frame = tk.Frame(parent, bg=BG)
        ctrl_frame.pack()

        # Start / Pause / Resume
        self.start_btn_canvas = tk.Canvas(ctrl_frame, width=168, height=52,
                                          bg=BG, highlightthickness=0,
                                          cursor="hand2")
        self.start_btn_canvas.pack(side="left", padx=(0, 12))
        self._draw_start_btn()
        self.start_btn_canvas.bind("<Button-1>", lambda e: self.start_pause())
        self.start_btn_canvas.bind("<Enter>",
                                   lambda e: self._hover_start(True))
        self.start_btn_canvas.bind("<Leave>",
                                   lambda e: self._hover_start(False))

        # Reset
        self.reset_btn_canvas = tk.Canvas(ctrl_frame, width=100, height=52,
                                          bg=BG, highlightthickness=0,
                                          cursor="hand2")
        self.reset_btn_canvas.pack(side="left")
        self._draw_reset_btn()
        self.reset_btn_canvas.bind("<Button-1>", lambda e: self.reset_timer())
        self.reset_btn_canvas.bind("<Enter>",
                                   lambda e: self._hover_reset(True))
        self.reset_btn_canvas.bind("<Leave>",
                                   lambda e: self._hover_reset(False))

    def _draw_start_btn(self, label=None, hover=False):
        if label is None:
            label = self._get_start_label()
        c = self.start_btn_canvas
        c.delete("all")
        bg = ACCENT2 if hover else ACCENT
        self._round_rect(c, 0, 0, 168, 52, radius=14, fill=bg, outline=bg)
        c.create_text(84, 26, text=label, font=self.font_btn, fill=WHITE)

    def _draw_reset_btn(self, hover=False):
        c = self.reset_btn_canvas
        c.delete("all")
        bg = ACCENT if hover else CARD
        fg = WHITE  if hover else ACCENT
        self._round_rect(c, 0, 0, 100, 52, radius=14, fill=bg, outline=ACCENT)
        c.create_text(50, 26, text="Reset", font=self.font_btn_sm, fill=fg)

    def _hover_start(self, on):
        self._draw_start_btn(self._get_start_label(), hover=on)

    def _hover_reset(self, on):
        self._draw_reset_btn(hover=on)

    # ── Session Dots ──────────────────────────────────────────────────────────
    def create_session_counter(self, parent):
        """Row of dot indicators showing Pomodoros completed vs goal."""
        self.dots_frame = tk.Frame(parent, bg=BG)
        self.dots_frame.pack()
        self._rebuild_dots()

    def _rebuild_dots(self):
        for w in self.dots_frame.winfo_children():
            w.destroy()

        goal = max(1, self.daily_goal.get())
        done = self.sessions_done

        lbl = tk.Label(self.dots_frame, text="Today's Progress",
                       font=self.font_tiny, bg=BG, fg=TEXT2)
        lbl.pack()

        dot_row = tk.Frame(self.dots_frame, bg=BG)
        dot_row.pack(pady=(4, 0))

        # Dynamically scale dot size and padding so up to 20 dots fit the window
        dot_size = max(8, min(14, 260 // goal))
        gap = max(3, min(8, 100 // goal))

        for i in range(goal):
            filled = i < done
            cv = tk.Canvas(dot_row, width=dot_size, height=dot_size,
                           bg=BG, highlightthickness=0)
            cv.pack(side="left", padx=gap // 2)
            color = ACCENT if filled else TRACK
            cv.create_oval(0, 0, dot_size, dot_size, fill=color, outline=color)

        count_lbl = tk.Label(self.dots_frame,
                             text=f"{done}/{goal} Pomodoros",
                             font=self.font_tiny, bg=BG, fg=TEXT2)
        count_lbl.pack(pady=(4, 0))

    # ── Bottom Bar ────────────────────────────────────────────────────────────
    def create_bottom_bar(self, parent):
        """Auto-start toggle + Settings gear."""
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", pady=(16, 0))

        # Auto-start toggle (left side)
        auto_frame = tk.Frame(bar, bg=BG)
        auto_frame.pack(side="left")

        auto_lbl = tk.Label(auto_frame, text="Auto-start",
                            font=self.font_small, bg=BG, fg=TEXT2,
                            cursor="hand2")
        auto_lbl.pack(side="left", padx=(0, 6))
        auto_lbl.bind("<Button-1>", lambda e: self._toggle_auto())

        self.toggle_cv = tk.Canvas(auto_frame, width=44, height=24,
                                   bg=BG, highlightthickness=0,
                                   cursor="hand2")
        self.toggle_cv.pack(side="left")
        self.toggle_cv.bind("<Button-1>", lambda e: self._toggle_auto())
        self._draw_toggle()

        # Settings gear (right side)
        gear_btn = tk.Label(bar, text="⚙", font=self.font_large,
                            bg=BG, fg=TEXT2, cursor="hand2")
        gear_btn.pack(side="right")
        gear_btn.bind("<Button-1>", lambda e: self.open_settings())
        gear_btn.bind("<Enter>", lambda e: gear_btn.configure(fg=ACCENT))
        gear_btn.bind("<Leave>", lambda e: gear_btn.configure(fg=TEXT2))

    def _draw_toggle(self):
        c = self.toggle_cv
        c.delete("all")
        on = self.auto_start.get()
        bg = ACCENT if on else TRACK
        # Track
        self._round_rect(c, 0, 0, 44, 24, radius=12, fill=bg, outline=bg)
        # Knob
        kx = 22 if on else 2
        c.create_oval(kx, 2, kx + 20, 22, fill=WHITE, outline=WHITE)

    def _toggle_auto(self):
        self.auto_start.set(not self.auto_start.get())
        self._draw_toggle()

    # ── Timer Logic ───────────────────────────────────────────────────────────
    def start_pause(self):
        if self.running:
            # Pause
            self.running = False
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None
            if self.end_time is not None:
                self.remaining = max(0.0, self.end_time - time.monotonic())
            self._draw_start_btn()
            self.update_window_title()
        else:
            # Start / Resume
            if self.remaining <= 0:
                self.remaining = float(self.total)
            self.running = True
            self.end_time = time.monotonic() + self.remaining
            self._draw_start_btn()
            self.update_window_title()
            self.tick()

    def reset_timer(self):
        """Stop and reset to the current mode's full duration."""
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.end_time = None
        self.remaining = float(self.total)
        self.draw_progress_arc(1.0)
        self._update_canvas_time()
        self._draw_start_btn("Start")
        self.update_window_title()

    def tick(self):
        """Called periodically while the timer is running."""
        if not self.running:
            return

        now = time.monotonic()
        remaining_sec = self.end_time - now

        if remaining_sec <= 0:
            self.session_complete()
            return

        self.remaining = remaining_sec
        fraction = self.remaining / self.total if self.total > 0 else 0.0
        self.draw_progress_arc(fraction)
        self._update_canvas_time()
        self.update_window_title()

        # Check every 250 ms for smooth progress and prompt tick
        self.after_id = self.after(250, self.tick)

    def switch_mode(self, mode: str, force: bool = False):
        """Switch to pomodoro / short_break / long_break."""
        if not force and mode == self.mode.get():
            return

        # Stop any running timer
        if self.running:
            self.running = False
            if self.after_id:
                self.after_cancel(self.after_id)
                self.after_id = None

        self.mode.set(mode)
        self.total     = float(self.durations[mode])
        self.remaining = self.total
        self.end_time  = None

        self.draw_progress_arc(1.0)
        self._update_canvas_time()
        self._refresh_tabs()
        self._draw_start_btn("Start")
        self.update_window_title()

        # Update mode sub-label on canvas
        self.canvas.itemconfigure("mode_text",
                                  text=self._mode_label(mode))

    def session_complete(self):
        """Handle timer reaching zero."""
        self.running = False
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.remaining = 0.0
        self.end_time = None
        self.draw_progress_arc(0.0)
        self._update_canvas_time()
        self.update_window_title()

        # Count Pomodoro completions (not breaks)
        is_pomodoro = (self.mode.get() == "pomodoro")
        if is_pomodoro:
            self.sessions_done += 1
            self._rebuild_dots()

        self.play_notification_sound()

        # Transition to next mode
        if is_pomodoro:
            # Every 4th Pomodoro → long break; otherwise short break
            next_mode = "long_break" if (self.sessions_done % 4 == 0) else "short_break"
        else:
            next_mode = "pomodoro"

        self.switch_mode(next_mode, force=True)

        # Auto-start next session if enabled
        if self.auto_start.get():
            self.start_pause()

    # ── Canvas Helpers ────────────────────────────────────────────────────────
    def draw_progress_arc(self, fraction: float):
        """Redraw the progress arc. fraction=1.0 means full, 0.0 means empty."""
        fraction = max(0.0, min(1.0, fraction))
        if fraction <= 0:
            extent = 0
        else:
            extent = -359.99 * fraction   # clockwise sweep (negative in tkinter)

        self.canvas.itemconfigure(
            "arc",
            start=90,
            extent=extent,
            outline=ACCENT,
        )

    def _update_canvas_time(self):
        self.canvas.itemconfigure("time_text",
                                  text=self._format_time(self.remaining))

    def update_window_title(self):
        label = self._mode_label(self.mode.get())
        time_str = self._format_time(self.remaining)
        status = "▶" if self.running else "⏸" if self.remaining < self.total else "🍅"
        self.title(f"{status} {time_str} — {label}")

    # ── Progress Ring Drawing Utility ─────────────────────────────────────────
    @staticmethod
    def _round_rect(canvas, x1, y1, x2, y2, radius=16, **kw):
        """Draw a rounded rectangle on a Canvas."""
        pts = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(pts, smooth=True, **kw)

    # ── Notification Sound ────────────────────────────────────────────────────
    def play_notification_sound(self):
        """Play a system sound when a session ends."""
        if self._sound_proc and self._sound_proc.poll() is None:
            try:
                self._sound_proc.terminate()
            except Exception:
                pass

        system = platform.system()
        try:
            if system == "Darwin":   # macOS
                self._sound_proc = subprocess.Popen(
                    ["afplay", "/System/Library/Sounds/Glass.aiff"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            elif system == "Windows":
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            elif system == "Linux":
                for player, sound in [
                    ("paplay", "/usr/share/sounds/freedesktop/stereo/complete.oga"),
                    ("aplay", "/usr/share/sounds/alsa/Front_Center.wav"),
                    ("canberra-gtk-play", "-i", "complete"),
                ]:
                    try:
                        cmd = [player, sound] if isinstance(sound, str) else [player, *sound]
                        self._sound_proc = subprocess.Popen(
                            cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                        )
                        return
                    except FileNotFoundError:
                        continue
                self.bell()
            else:
                self.bell()
        except Exception:
            # Last resort: tkinter bell
            try:
                self.bell()
            except Exception:
                pass

    # ── Settings Modal ────────────────────────────────────────────────────────
    def open_settings(self):
        """Open a Toplevel modal for editing durations and daily goal."""
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.lift()
            self.settings_win.focus_set()
            return

        win = tk.Toplevel(self)
        self.settings_win = win
        win.title("Settings")
        win.configure(bg=BG)
        win.resizable(False, False)
        win.transient(self)
        win.grab_set()

        # Centre relative to main window
        ww, wh = 360, 360
        self.update_idletasks()
        cx = self.winfo_x() + max(0, (self.winfo_width() - ww) // 2)
        cy = self.winfo_y() + max(0, (self.winfo_height() - wh) // 2)
        win.geometry(f"{ww}x{wh}+{cx}+{cy}")

        # Title
        tk.Label(win, text="Settings", font=self.font_large,
                 bg=BG, fg=TEXT).pack(pady=(18, 12))

        # Fields frame
        fields_frame = tk.Frame(win, bg=CARD, padx=20, pady=14)
        fields_frame.pack(padx=20, fill="x")

        def add_field(parent, label, default_val, unit="min"):
            row = tk.Frame(parent, bg=CARD)
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=self.font_small,
                     bg=CARD, fg=TEXT, width=15, anchor="w").pack(side="left")
            var = tk.StringVar(value=str(default_val))
            entry = tk.Entry(row, textvariable=var, width=5,
                             font=self.font_medium, fg=TEXT,
                             bg=WHITE, bd=1, relief="flat",
                             highlightthickness=1,
                             highlightbackground=ACCENT2,
                             highlightcolor=ACCENT,
                             justify="center")
            entry.pack(side="left")
            tk.Label(row, text=f" {unit}", font=self.font_small,
                     bg=CARD, fg=TEXT2).pack(side="left")
            return var

        pom_var   = add_field(fields_frame, "Pomodoro",
                              int(self.durations["pomodoro"] // 60), "min")
        short_var = add_field(fields_frame, "Short Break",
                              int(self.durations["short_break"] // 60), "min")
        long_var  = add_field(fields_frame, "Long Break",
                              int(self.durations["long_break"] // 60), "min")
        goal_var  = add_field(fields_frame, "Daily Goal",
                              int(self.daily_goal.get()), "sessions")

        err_lbl = tk.Label(win, text="", font=self.font_tiny,
                           bg=BG, fg=DANGER)
        err_lbl.pack(pady=(6, 0))

        # Buttons
        btn_frame = tk.Frame(win, bg=BG)
        btn_frame.pack(pady=14)

        def save(event=None):
            try:
                pom_m   = int(pom_var.get().strip())
                short_m = int(short_var.get().strip())
                long_m  = int(long_var.get().strip())
                goal    = int(goal_var.get().strip())
                if pom_m <= 0 or short_m <= 0 or long_m <= 0 or goal <= 0:
                    raise ValueError("Must be positive")
            except ValueError:
                err_lbl.configure(text="Please enter positive numbers (1–60 min, 1–20 goal).")
                return

            pom_s    = max(60, min(pom_m * 60, 3600))
            short_s  = max(60, min(short_m * 60, 3600))
            long_s   = max(60, min(long_m * 60, 3600))
            new_goal = max(1, min(goal, 20))

            cur_mode = self.mode.get()
            old_duration = self.durations[cur_mode]

            self.durations["pomodoro"]    = pom_s
            self.durations["short_break"] = short_s
            self.durations["long_break"]  = long_s
            self.daily_goal.set(new_goal)
            self._rebuild_dots()

            # Only adjust running/current timer if the active mode's duration changed
            if self.durations[cur_mode] != old_duration:
                if not self.running:
                    self.total = float(self.durations[cur_mode])
                    self.remaining = self.total
                    self.draw_progress_arc(1.0)
                    self._update_canvas_time()
                    self._draw_start_btn()
                    self.update_window_title()
                else:
                    self.total = float(self.durations[cur_mode])
                    if self.remaining > self.total:
                        self.remaining = self.total
                        self.end_time = time.monotonic() + self.remaining
                    self._update_canvas_time()
                    self.update_window_title()

            win.destroy()

        save_c = tk.Canvas(btn_frame, width=120, height=44,
                           bg=BG, highlightthickness=0, cursor="hand2")
        save_c.pack(side="left", padx=6)
        self._round_rect(save_c, 0, 0, 120, 44, radius=12,
                         fill=ACCENT, outline=ACCENT)
        save_c.create_text(60, 22, text="Save", font=self.font_btn,
                           fill=WHITE)
        save_c.bind("<Button-1>", lambda e: save())

        cancel_c = tk.Canvas(btn_frame, width=120, height=44,
                             bg=BG, highlightthickness=0, cursor="hand2")
        cancel_c.pack(side="left", padx=6)
        self._round_rect(cancel_c, 0, 0, 120, 44, radius=12,
                         fill=CARD, outline=ACCENT)
        cancel_c.create_text(60, 22, text="Cancel", font=self.font_btn_sm,
                             fill=ACCENT)
        cancel_c.bind("<Button-1>", lambda e: win.destroy())

        win.bind("<Return>", save)
        win.bind("<Escape>", lambda e: win.destroy())

        def _cleanup(event):
            if event.widget == win:
                self.settings_win = None
        win.bind("<Destroy>", _cleanup)

    # ── Utilities ─────────────────────────────────────────────────────────────
    @staticmethod
    def _format_time(seconds) -> str:
        s_int = int(math.ceil(seconds)) if isinstance(seconds, float) else int(seconds)
        m, s = divmod(max(0, s_int), 60)
        return f"{m:02d}:{s:02d}"

    @staticmethod
    def _mode_label(mode: str) -> str:
        return {
            "pomodoro":    "Focus Time",
            "short_break": "Short Break",
            "long_break":  "Long Break",
        }.get(mode, mode)

    def on_close(self):
        """Graceful shutdown."""
        if self.after_id:
            self.after_cancel(self.after_id)
        if self.settings_win and self.settings_win.winfo_exists():
            self.settings_win.destroy()
        if self._sound_proc and self._sound_proc.poll() is None:
            try:
                self._sound_proc.terminate()
            except Exception:
                pass
        self.destroy()


# ─── Entry Point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if "--check" in sys.argv:
        print("✅ Syntax OK")
        sys.exit(0)

    app = PomodoroApp()
    app.mainloop()
