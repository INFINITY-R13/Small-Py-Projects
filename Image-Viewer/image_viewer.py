"""
Image Viewer
============
A feature-rich image viewer built with Python's tkinter and Pillow.

Features:
  - Open individual images or entire folders
  - Navigate forward / backward through a folder's images
  - Zoom in / out and reset zoom with keyboard shortcuts or buttons
  - Rotate 90 ° clockwise / counter-clockwise
  - Flip horizontal / vertical
  - Fit-to-window toggle
  - Drag to pan when image is larger than the window
  - Thumbnail strip at the bottom for quick jumping
  - Status bar with file name, dimensions, and zoom level
  - Supported formats: JPEG, PNG, BMP, GIF, TIFF, WEBP, ICO

Keyboard shortcuts:
  Arrow Right / D   → Next image
  Arrow Left  / A   → Previous image
  + / =             → Zoom in
  - / _             → Zoom out
  0                 → Reset zoom (100 %)
  F                 → Fit to window toggle
  R                 → Rotate clockwise
  Shift+R           → Rotate counter-clockwise
  H                 → Flip horizontal
  V                 → Flip vertical
  Ctrl+O            → Open file
  Ctrl+Shift+O      → Open folder
  Escape            → Quit
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path

from PIL import Image, ImageTk

# ---------------------------------------------------------------------------
# Harmonious Dark Theme Palette (high contrast, perfectly synced)
# ---------------------------------------------------------------------------
PALETTE = {
    "bg":           "#111827",   # Main window & canvas background (deep slate)
    "toolbar":      "#1f2937",   # Toolbar background
    "status_bg":    "#1f2937",   # Status bar background (synced with toolbar)
    "status_fg":    "#e5e7eb",   # Status bar text (light gray)
    "thumb_bg":     "#111827",   # Thumbnail strip outer background
    "thumb_inner":  "#1f2937",   # Thumbnail strip inner tray
    "thumb_sel":    "#3b82f6",   # Active thumbnail border highlight (vibrant blue)
    "btn_bg":       "#374151",   # Button background (medium slate)
    "btn_fg":       "#f9fafb",   # Button text (bright white - high contrast)
    "btn_hover":    "#4b5563",   # Button hover state (lighter slate)
    "btn_active":   "#1d4ed8",   # Button pressed state
    "btn_toggled":  "#2563eb",   # Button toggled ON state (e.g. Fit mode)
    "btn_disabled": "#1e2430",   # Disabled button background
    "btn_dis_fg":   "#4b5563",   # Disabled button text
    "separator":    "#4b5563",   # Toolbar dividers
    "placeholder":  "#6b7280",   # Canvas placeholder text
    "menu_bg":      "#1f2937",
    "menu_fg":      "#e5e7eb",
    "menu_active":  "#2563eb",
}

# ---------------------------------------------------------------------------
# Zoom constants
# ---------------------------------------------------------------------------
ZOOM_MIN  = 0.05   # 5 %
ZOOM_MAX  = 10.0   # 1000 %
ZOOM_STEP = 1.15   # 15 % per click
THUMB_SIZE = 80    # thumbnail cell size in px

# Supported image extensions
SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif",
                   ".tiff", ".tif", ".webp", ".ico"}


# ===========================================================================
# Custom Rounded Button (Canvas-based)
# ===========================================================================

class RoundedButton(tk.Canvas):
    """A polished tkinter Canvas widget that renders as a button with rounded corners."""

    RADIUS = 8    # corner radius in pixels
    PAD_X  = 12   # horizontal text padding
    PAD_Y  = 6    # vertical text padding

    def __init__(self, parent, text: str, command=None,
                 bg=PALETTE["btn_bg"],
                 fg=PALETTE["btn_fg"],
                 hover_bg=PALETTE["btn_hover"],
                 active_bg=PALETTE["btn_active"],
                 toggled_bg=PALETTE["btn_toggled"],
                 disabled_bg=PALETTE["btn_disabled"],
                 disabled_fg=PALETTE["btn_dis_fg"],
                 font=("Helvetica", 10),
                 **kwargs):
        # Measure text dimensions for auto-sizing
        tmp = tk.Label(parent, text=text, font=font)
        tw = tmp.winfo_reqwidth()
        th = tmp.winfo_reqheight()
        tmp.destroy()

        self._btn_w = max(32, tw + self.PAD_X * 2)
        self._btn_h = max(28, th + self.PAD_Y * 2)

        super().__init__(parent,
                         width=self._btn_w,
                         height=self._btn_h,
                         highlightthickness=0,
                         bg=PALETTE["toolbar"],
                         cursor="hand2",
                         **kwargs)

        self._text        = text
        self._command     = command
        self._bg          = bg
        self._fg          = fg
        self._hover_bg    = hover_bg
        self._active_bg   = active_bg
        self._toggled_bg  = toggled_bg
        self._disabled_bg = disabled_bg
        self._disabled_fg = disabled_fg
        self._font        = font
        self._enabled     = True
        self._toggled     = False

        self._draw(self._bg, self._fg)

        self.bind("<Enter>",           self._on_enter)
        self.bind("<Leave>",           self._on_leave)
        self.bind("<ButtonPress-1>",   self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)

    # ── Drawing ──────────────────────────────────────────────────────────────

    def _round_rect(self, x1, y1, x2, y2, r, **kw):
        """Draw a smooth rounded rectangle using duplicate bezier spline points."""
        r = min(r, (x2 - x1) // 2, (y2 - y1) // 2)
        points = (
            x1 + r, y1,
            x1 + r, y1,
            x2 - r, y1,
            x2 - r, y1,
            x2,     y1,
            x2,     y1 + r,
            x2,     y1 + r,
            x2,     y2 - r,
            x2,     y2 - r,
            x2,     y2,
            x2 - r, y2,
            x2 - r, y2,
            x1 + r, y2,
            x1 + r, y2,
            x1,     y2,
            x1,     y2 - r,
            x1,     y2 - r,
            x1,     y1 + r,
            x1,     y1 + r,
            x1,     y1
        )
        return self.create_polygon(points, smooth=True, **kw)

    def _draw(self, fill_color: str, text_color: str) -> None:
        self.delete("all")
        self._shape = self._round_rect(1, 1, self._btn_w - 1, self._btn_h - 1,
                                       self.RADIUS, fill=fill_color, outline="")
        self._label = self.create_text(self._btn_w // 2, self._btn_h // 2,
                                       text=self._text,
                                       fill=text_color,
                                       font=self._font,
                                       anchor=tk.CENTER)

    # ── Event handlers ────────────────────────────────────────────────────────

    def _on_enter(self, _):
        if self._enabled and not self._toggled:
            self._draw(self._hover_bg, self._fg)

    def _on_leave(self, _):
        if self._enabled:
            color = self._toggled_bg if self._toggled else self._bg
            self._draw(color, self._fg)

    def _on_press(self, _):
        if self._enabled:
            self._draw(self._active_bg, "#ffffff")

    def _on_release(self, event):
        if not self._enabled:
            return
        if 0 <= event.x <= self._btn_w and 0 <= event.y <= self._btn_h:
            color = self._toggled_bg if self._toggled else self._bg
            self._draw(color, self._fg)
            if self._command:
                self._command()

    # ── Public API ────────────────────────────────────────────────────────────

    def set_toggled(self, on: bool) -> None:
        """Visually mark button as toggled on or off."""
        self._toggled = on
        color = self._toggled_bg if on else self._bg
        self._draw(color, self._fg)

    def config(self, **kw):  # type: ignore[override]
        state = kw.pop("state", None)
        if state == tk.DISABLED:
            self._enabled = False
            super().configure(cursor="arrow")
            self._draw(self._disabled_bg, self._disabled_fg)
        elif state == tk.NORMAL:
            self._enabled = True
            super().configure(cursor="hand2")
            color = self._toggled_bg if self._toggled else self._bg
            self._draw(color, self._fg)
        if kw:
            super().config(**kw)

    configure = config


# ===========================================================================
# Main Application
# ===========================================================================

class ImageViewer(tk.Tk):
    """Main application window."""

    def __init__(self):
        super().__init__()
        self.title("Image Viewer")
        self.geometry("1050x740")
        self.minsize(550, 420)
        self.configure(bg=PALETTE["bg"])

        # ── State ────────────────────────────────────────────────────────────
        self._image_paths: list[Path] = []
        self._current_index: int = -1
        self._pil_image: Image.Image | None = None
        self._base_image: Image.Image | None = None
        self._zoom: float = 1.0
        self._fit_to_window: bool = True

        # Thumbnail references (prevent garbage collection)
        self._thumb_refs: list[ImageTk.PhotoImage] = []

        # ── Build UI ─────────────────────────────────────────────────────────
        self._build_menu()
        self._build_toolbar()
        self._build_canvas()
        self._build_thumbnail_strip()
        self._build_statusbar()
        self._bind_keys()
        self._update_ui_state()

    # =========================================================================
    # Menu
    # =========================================================================

    def _build_menu(self) -> None:
        P = PALETTE
        menubar = tk.Menu(self, bg=P["menu_bg"], fg=P["menu_fg"],
                          activebackground=P["menu_active"],
                          activeforeground="white",
                          relief=tk.FLAT, bd=0)

        def menu(label, items):
            m = tk.Menu(menubar, tearoff=0,
                        bg=P["menu_bg"], fg=P["menu_fg"],
                        activebackground=P["menu_active"],
                        activeforeground="white",
                        relief=tk.FLAT, bd=0)
            for item in items:
                if item is None:
                    m.add_separator()
                else:
                    m.add_command(label=item[0], command=item[1])
            menubar.add_cascade(label=label, menu=m)

        menu("File", [
            ("Open File…       Ctrl+O",        self._open_file),
            ("Open Folder…     Ctrl+Shift+O",  self._open_folder),
            None,
            ("Quit             Esc",           self.quit),
        ])
        menu("View", [
            ("Zoom In          +",             self._zoom_in),
            ("Zoom Out         -",             self._zoom_out),
            ("Reset Zoom       0",             self._zoom_reset),
            None,
            ("Fit to Window    F",             self._toggle_fit),
        ])
        menu("Transform", [
            ("Rotate CW        R",             self._rotate_cw),
            ("Rotate CCW       Shift+R",       self._rotate_ccw),
            None,
            ("Flip Horizontal  H",             self._flip_h),
            ("Flip Vertical    V",             self._flip_v),
        ])
        self.config(menu=menubar)

    # =========================================================================
    # Toolbar
    # =========================================================================

    def _build_toolbar(self) -> None:
        P = PALETTE
        tb = tk.Frame(self, bg=P["toolbar"], pady=6, padx=8)
        tb.pack(side=tk.TOP, fill=tk.X)

        def btn(parent, text, cmd, **kw) -> RoundedButton:
            b = RoundedButton(parent, text=text, command=cmd,
                              bg=P["btn_bg"], fg=P["btn_fg"],
                              hover_bg=P["btn_hover"],
                              active_bg=P["btn_active"],
                              toggled_bg=P["btn_toggled"],
                              disabled_bg=P["btn_disabled"],
                              disabled_fg=P["btn_dis_fg"],
                              **kw)
            b.pack(side=tk.LEFT, padx=3, pady=0)
            return b

        def sep():
            tk.Frame(tb, bg=P["separator"], width=1, height=22).pack(
                side=tk.LEFT, fill=tk.Y, padx=6, pady=2)

        btn(tb, "📂 Open File",   self._open_file)
        btn(tb, "📁 Open Folder", self._open_folder)
        sep()

        self._btn_prev = btn(tb, "◀ Prev", self._prev_image)
        self._btn_next = btn(tb, "Next ▶", self._next_image)
        sep()

        btn(tb, "🔍 +",   self._zoom_in)
        btn(tb, "🔍 -",   self._zoom_out)
        btn(tb, "1:1",    self._zoom_reset)
        self._btn_fit = btn(tb, "⊡ Fit", self._toggle_fit)
        sep()

        btn(tb, "↻ CW",     self._rotate_cw)
        btn(tb, "↺ CCW",    self._rotate_ccw)
        btn(tb, "↔ Flip H", self._flip_h)
        btn(tb, "↕ Flip V", self._flip_v)

    # =========================================================================
    # Main Canvas
    # =========================================================================

    def _build_canvas(self) -> None:
        P = PALETTE
        canvas_frame = tk.Frame(self, bg=P["bg"])
        canvas_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._canvas = tk.Canvas(canvas_frame, bg=P["bg"],
                                 highlightthickness=0, cursor="fleur")
        self._v_scroll = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL,
                                       command=self._canvas.yview)
        self._h_scroll = ttk.Scrollbar(self, orient=tk.HORIZONTAL,
                                       command=self._canvas.xview)
        self._canvas.configure(xscrollcommand=self._h_scroll.set,
                               yscrollcommand=self._v_scroll.set)

        self._v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self._canvas.create_text(
            500, 320,
            text="Open an image or folder to begin\n(Ctrl+O  /  Ctrl+Shift+O)",
            fill=P["placeholder"],
            font=("Helvetica", 15),
            justify=tk.CENTER,
            tags="placeholder")

        self._canvas.bind("<Configure>",       self._on_canvas_resize)
        self._canvas.bind("<ButtonPress-1>",   self._on_drag_start)
        self._canvas.bind("<B1-Motion>",       self._on_drag_motion)
        self._canvas.bind("<MouseWheel>",      self._on_mousewheel)
        self._canvas.bind("<Button-4>",        self._on_mousewheel)
        self._canvas.bind("<Button-5>",        self._on_mousewheel)

        self._photo: ImageTk.PhotoImage | None = None
        self._canvas_image_id: int | None = None

    # =========================================================================
    # Thumbnail Strip
    # =========================================================================

    def _build_thumbnail_strip(self) -> None:
        P = PALETTE
        strip_height = THUMB_SIZE + 20

        outer = tk.Frame(self, bg=P["thumb_bg"], height=strip_height)
        outer.pack(side=tk.BOTTOM, fill=tk.X)
        outer.pack_propagate(False)

        self._thumb_canvas = tk.Canvas(outer, bg=P["thumb_bg"],
                                       highlightthickness=0,
                                       height=strip_height)
        self._thumb_scroll = ttk.Scrollbar(outer, orient=tk.HORIZONTAL,
                                          command=self._thumb_canvas.xview)
        self._thumb_canvas.configure(xscrollcommand=self._thumb_scroll.set)
        self._thumb_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        self._thumb_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self._thumb_inner = tk.Frame(self._thumb_canvas, bg=P["thumb_bg"])
        self._thumb_canvas.create_window((0, 0), window=self._thumb_inner,
                                         anchor=tk.NW)
        self._thumb_inner.bind("<Configure>",
            lambda e: self._thumb_canvas.configure(
                scrollregion=self._thumb_canvas.bbox("all")))

    # =========================================================================
    # Status Bar
    # =========================================================================

    def _build_statusbar(self) -> None:
        P = PALETTE
        sb = tk.Frame(self, bg=P["status_bg"], pady=4, padx=8)
        sb.pack(side=tk.BOTTOM, fill=tk.X)

        self._status_left = tk.Label(
            sb, text="No image loaded",
            bg=P["status_bg"], fg=P["status_fg"],
            font=("Helvetica", 10), anchor=tk.W)
        self._status_left.pack(side=tk.LEFT)

        self._status_right = tk.Label(
            sb, text="",
            bg=P["status_bg"], fg=P["status_fg"],
            font=("Helvetica", 10), anchor=tk.E)
        self._status_right.pack(side=tk.RIGHT)

    # =========================================================================
    # Key Bindings
    # =========================================================================

    def _bind_keys(self) -> None:
        self.bind("<Right>",      lambda _: self._next_image())
        self.bind("<d>",          lambda _: self._next_image())
        self.bind("<Left>",       lambda _: self._prev_image())
        self.bind("<a>",          lambda _: self._prev_image())
        self.bind("<equal>",      lambda _: self._zoom_in())
        self.bind("<plus>",       lambda _: self._zoom_in())
        self.bind("<minus>",      lambda _: self._zoom_out())
        self.bind("<underscore>", lambda _: self._zoom_out())
        self.bind("<Key-0>",      lambda _: self._zoom_reset())
        self.bind("<f>",          lambda _: self._toggle_fit())
        self.bind("<r>",          lambda _: self._rotate_cw())
        self.bind("<R>",          lambda _: self._rotate_ccw())
        self.bind("<h>",          lambda _: self._flip_h())
        self.bind("<v>",          lambda _: self._flip_v())
        self.bind("<Control-o>",  lambda _: self._open_file())
        self.bind("<Control-O>",  lambda _: self._open_folder())
        self.bind("<Escape>",     lambda _: self.quit())

    # =========================================================================
    # File / Folder Loading
    # =========================================================================

    def _open_file(self) -> None:
        filetypes = [
            ("Image files", " ".join(f"*{e}" for e in SUPPORTED_EXTS)),
            ("All files", "*.*"),
        ]
        path = filedialog.askopenfilename(title="Open Image", filetypes=filetypes)
        if not path:
            return
        p = Path(path)
        self._load_folder(p.parent)
        try:
            self._current_index = self._image_paths.index(p)
        except ValueError:
            self._current_index = 0
        self._show_current()

    def _open_folder(self) -> None:
        folder = filedialog.askdirectory(title="Open Folder")
        if not folder:
            return
        self._load_folder(Path(folder))
        if self._image_paths:
            self._current_index = 0
            self._show_current()

    def _load_folder(self, folder: Path) -> None:
        self._image_paths = sorted(
            [p for p in folder.iterdir()
             if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS],
            key=lambda p: p.name.lower())
        self._build_thumbnails()

    # =========================================================================
    # Navigation
    # =========================================================================

    def _next_image(self) -> None:
        if not self._image_paths:
            return
        self._current_index = (self._current_index + 1) % len(self._image_paths)
        self._show_current()

    def _prev_image(self) -> None:
        if not self._image_paths:
            return
        self._current_index = (self._current_index - 1) % len(self._image_paths)
        self._show_current()

    # =========================================================================
    # Display & Render
    # =========================================================================

    def _show_current(self) -> None:
        if self._current_index < 0 or not self._image_paths:
            return
        path = self._image_paths[self._current_index]
        try:
            img = Image.open(path)
            if img.mode in ("P", "RGBA"):
                img = img.convert("RGBA")
            elif img.mode != "RGB":
                img = img.convert("RGB")
            self._base_image = img.copy()
            self._pil_image  = img.copy()
        except Exception as exc:
            messagebox.showerror("Error", f"Cannot open image:\n{exc}")
            return

        self._zoom          = 1.0
        self._fit_to_window = True
        self._btn_fit.set_toggled(True)

        self._render_image()
        self._update_ui_state()
        self._highlight_thumbnail()

    def _render_image(self) -> None:
        if self._pil_image is None:
            return

        cw = self._canvas.winfo_width()  or 900
        ch = self._canvas.winfo_height() or 640

        img = self._pil_image
        iw, ih = img.size

        if self._fit_to_window:
            scale = min(cw / iw, ch / ih, 1.0)
            self._zoom = scale
        else:
            scale = self._zoom

        new_w = max(1, int(iw * scale))
        new_h = max(1, int(ih * scale))

        resample = Image.LANCZOS if scale < 1 else Image.NEAREST
        display  = img.resize((new_w, new_h), resample)

        self._photo = ImageTk.PhotoImage(display)
        self._canvas.delete("all")
        self._canvas_image_id = self._canvas.create_image(
            max(cw // 2, new_w // 2),
            max(ch // 2, new_h // 2),
            anchor=tk.CENTER, image=self._photo)
        self._canvas.configure(
            scrollregion=(0, 0, max(cw, new_w), max(ch, new_h)))
        self._update_status()

    # =========================================================================
    # Zoom Controls
    # =========================================================================

    def _zoom_in(self) -> None:
        if self._pil_image is None:
            return
        self._disable_fit()
        self._zoom = min(self._zoom * ZOOM_STEP, ZOOM_MAX)
        self._render_image()

    def _zoom_out(self) -> None:
        if self._pil_image is None:
            return
        self._disable_fit()
        self._zoom = max(self._zoom / ZOOM_STEP, ZOOM_MIN)
        self._render_image()

    def _zoom_reset(self) -> None:
        if self._pil_image is None:
            return
        self._disable_fit()
        self._zoom = 1.0
        self._render_image()

    def _toggle_fit(self) -> None:
        if self._pil_image is None:
            return
        self._fit_to_window = not self._fit_to_window
        self._btn_fit.set_toggled(self._fit_to_window)
        self._render_image()

    def _disable_fit(self) -> None:
        self._fit_to_window = False
        self._btn_fit.set_toggled(False)

    # =========================================================================
    # Transformations
    # =========================================================================

    def _rotate_cw(self) -> None:
        if self._pil_image is None:
            return
        self._pil_image = self._pil_image.rotate(-90, expand=True)
        self._render_image()

    def _rotate_ccw(self) -> None:
        if self._pil_image is None:
            return
        self._pil_image = self._pil_image.rotate(90, expand=True)
        self._render_image()

    def _flip_h(self) -> None:
        if self._pil_image is None:
            return
        self._pil_image = self._pil_image.transpose(Image.FLIP_LEFT_RIGHT)
        self._render_image()

    def _flip_v(self) -> None:
        if self._pil_image is None:
            return
        self._pil_image = self._pil_image.transpose(Image.FLIP_TOP_BOTTOM)
        self._render_image()

    # =========================================================================
    # Pan & Mouse Interaction
    # =========================================================================

    def _on_drag_start(self, event: tk.Event) -> None:
        self._canvas.scan_mark(event.x, event.y)

    def _on_drag_motion(self, event: tk.Event) -> None:
        self._canvas.scan_dragto(event.x, event.y, gain=1)

    def _on_mousewheel(self, event: tk.Event) -> None:
        ctrl = bool(event.state & 0x4)
        scroll_down = event.num == 5 or (hasattr(event, "delta") and event.delta < 0)
        if ctrl:
            self._zoom_out() if scroll_down else self._zoom_in()
        else:
            self._next_image() if scroll_down else self._prev_image()

    # =========================================================================
    # Canvas Resize
    # =========================================================================

    def _on_canvas_resize(self, _: tk.Event) -> None:
        if self._fit_to_window and self._pil_image is not None:
            self._render_image()
        elif self._pil_image is None:
            cw = self._canvas.winfo_width() or 900
            ch = self._canvas.winfo_height() or 640
            self._canvas.coords("placeholder", cw // 2, ch // 2)

    # =========================================================================
    # Thumbnails
    # =========================================================================

    def _build_thumbnails(self) -> None:
        for w in self._thumb_inner.winfo_children():
            w.destroy()
        self._thumb_refs.clear()

        P = PALETTE
        for idx, path in enumerate(self._image_paths):
            try:
                img = Image.open(path)
                img.thumbnail((THUMB_SIZE, THUMB_SIZE))
                photo = ImageTk.PhotoImage(img)
                self._thumb_refs.append(photo)

                frame = tk.Frame(self._thumb_inner, bg=P["thumb_bg"],
                                 highlightthickness=2,
                                 highlightbackground=P["thumb_bg"])
                frame.pack(side=tk.LEFT, padx=3, pady=4)

                btn = tk.Button(frame, image=photo, relief=tk.FLAT,
                                bd=0, bg=P["thumb_bg"],
                                activebackground=P["btn_active"],
                                cursor="hand2",
                                command=lambda i=idx: self._jump_to(i))
                btn.pack()
                btn.image = photo
                frame._idx = idx   # type: ignore[attr-defined]
            except Exception:
                pass

    def _jump_to(self, index: int) -> None:
        self._current_index = index
        self._show_current()

    def _highlight_thumbnail(self) -> None:
        P = PALETTE
        for frame in self._thumb_inner.winfo_children():
            is_selected = getattr(frame, "_idx", None) == self._current_index
            frame.config(
                highlightbackground=P["thumb_sel"] if is_selected else P["thumb_bg"])

    # =========================================================================
    # Status Bar & UI State
    # =========================================================================

    def _update_status(self) -> None:
        if self._pil_image is None:
            self._status_left.config(text="No image loaded")
            self._status_right.config(text="")
            return
        path  = self._image_paths[self._current_index]
        iw, ih = self._pil_image.size
        n     = self._current_index + 1
        total = len(self._image_paths)
        self._status_left.config(
            text=f"  {path.name}   [{n} / {total}]   {iw} × {ih} px")
        self._status_right.config(
            text=f"Zoom: {self._zoom * 100:.0f} %  ")

    def _update_ui_state(self) -> None:
        has = bool(self._image_paths)
        self._btn_prev.config(state=tk.NORMAL if has else tk.DISABLED)
        self._btn_next.config(state=tk.NORMAL if has else tk.DISABLED)
        if not has:
            self._status_left.config(text="No image loaded")
            self._status_right.config(text="")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = ImageViewer()
    app.mainloop()
