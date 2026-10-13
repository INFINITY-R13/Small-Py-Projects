"""
Endless — A Minimalist Music Player
"""

import os
import io
import time
import random
import threading
import tkinter as tk
from tkinter import filedialog
from pathlib import Path

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageFont
from mutagen.mp3 import MP3
from mutagen.flac import FLAC
from mutagen.oggvorbis import OggVorbis
from mutagen.wave import WAVE
from mutagen import File as MutagenFile

import pygame


# ─────────────────────────────────────────────
# Theme — Soft Pink, Apple-inspired
# ─────────────────────────────────────────────

class Theme:
    """Light pink minimalist palette."""

    # Backgrounds
    BG             = "#FFF5F6"
    BG_SIDEBAR     = "#FFF0F2"
    BG_CARD        = "#FFFFFF"
    BG_HOVER       = "#FFE4EA"
    BG_INPUT       = "#FFF8F9"
    BG_ACTIVE      = "#FFD6DF"

    # Accent
    ACCENT         = "#FF2D55"       # Apple pink-red
    ACCENT_SOFT    = "#FF6482"
    ACCENT_PALE    = "#FFECF0"
    ACCENT_MUTED   = "#F9A8BA"

    # Text
    TEXT_PRIMARY    = "#1D1D1F"
    TEXT_SECONDARY  = "#6E6E73"
    TEXT_TERTIARY   = "#AEAEB2"

    # Surfaces
    DIVIDER        = "#F2E2E6"
    SLIDER_TRACK   = "#F0DFE3"
    SLIDER_PROG    = "#FF2D55"
    SLIDER_KNOB    = "#FF2D55"

    # Typography (Apple-like hierarchy)
    FONT           = "Helvetica Neue"
    TITLE          = (FONT, 20, "bold")
    HEADLINE       = (FONT, 16, "bold")
    SUBHEAD        = (FONT, 12)
    BODY           = (FONT, 13)
    BODY_BOLD      = (FONT, 13, "bold")
    CAPTION        = (FONT, 11)
    CAPTION2       = (FONT, 10)
    MICRO          = (FONT, 10)

    # Control glyphs (SF Symbols–style text, not emoji)
    ICON_FONT      = (FONT, 15)
    ICON_LARGE     = (FONT, 22)


# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

SUPPORTED_FORMATS = (".mp3", ".flac", ".ogg", ".wav")


def format_time(seconds: float) -> str:
    if seconds < 0:
        seconds = 0
    m, s = divmod(int(seconds), 60)
    return f"{m}:{s:02d}"


def extract_metadata(filepath: str):
    title = Path(filepath).stem
    artist = "Unknown Artist"
    album = "Unknown Album"
    duration = 0.0
    cover_bytes = None

    try:
        audio = MutagenFile(filepath)
        if audio is None:
            return title, artist, album, duration, cover_bytes

        if hasattr(audio.info, "length"):
            duration = audio.info.length

        if isinstance(audio, (MP3, WAVE)):
            tags = audio.tags
            if tags:
                title = str(tags.get("TIT2", title))
                artist = str(tags.get("TPE1", artist))
                album = str(tags.get("TALB", album))
                for key in tags:
                    if key.startswith("APIC"):
                        cover_bytes = tags[key].data
                        break
        elif isinstance(audio, FLAC):
            title = audio.get("title", [title])[0]
            artist = audio.get("artist", [artist])[0]
            album = audio.get("album", [album])[0]
            if audio.pictures:
                cover_bytes = audio.pictures[0].data
        elif isinstance(audio, OggVorbis):
            title = audio.get("title", [title])[0]
            artist = audio.get("artist", [artist])[0]
            album = audio.get("album", [album])[0]
    except Exception:
        pass

    return title, artist, album, duration, cover_bytes


def create_default_cover(size=300):
    """Minimal default album art — soft gradient with the app name."""
    img = Image.new("RGBA", (size, size))
    draw = ImageDraw.Draw(img)

    # Gentle rose gradient
    for y in range(size):
        r = min(int(255 - y * 0.06), 255)
        g = min(int(228 - y * 0.15), 255)
        b = min(int(235 - y * 0.12), 255)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))

    # Centered music note symbol
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size // 4)
    except Exception:
        font = ImageFont.load_default()

    symbol = "♪"
    bbox = draw.textbbox((0, 0), symbol, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    cx, cy = size // 2, size // 2 - 12
    draw.text((cx - tw // 2, cy - th // 2), symbol, fill=(255, 45, 85, 100), font=font)

    # Subtle app name
    try:
        small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", size // 16)
    except Exception:
        small = ImageFont.load_default()
    label = "endless"
    bbox2 = draw.textbbox((0, 0), label, font=small)
    sw = bbox2[2] - bbox2[0]
    draw.text((cx - sw // 2, cy + th // 2 + 10), label, fill=(180, 120, 140, 160), font=small)

    return img


def make_rounded(img: Image.Image, radius=20) -> Image.Image:
    img = img.convert("RGBA")
    w, h = img.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    img.putalpha(mask)
    return img


# ─────────────────────────────────────────────
# Track
# ─────────────────────────────────────────────

class Track:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.title, self.artist, self.album, self.duration, self._cover_bytes = (
            extract_metadata(filepath)
        )

    @property
    def display_title(self):
        return self.title if self.title else Path(self.filepath).stem

    @property
    def display_artist(self):
        return self.artist if self.artist else "Unknown Artist"

    def get_cover_image(self, size=(300, 300)) -> Image.Image:
        if self._cover_bytes:
            try:
                img = Image.open(io.BytesIO(self._cover_bytes))
                img = img.convert("RGBA")
                img = img.resize(size, Image.LANCZOS)
                return img
            except Exception:
                pass
        return create_default_cover(size[0])


# ─────────────────────────────────────────────
# Playlist Item — clean, minimal row
# ─────────────────────────────────────────────

class PlaylistItem(ctk.CTkFrame):
    def __init__(self, master, track: Track, index: int, on_click=None, **kwargs):
        super().__init__(master, fg_color="transparent", corner_radius=10, height=52, **kwargs)
        self.track = track
        self.index = index
        self._on_click = on_click
        self._is_active = False

        self.grid_columnconfigure(1, weight=1)

        # Track number
        self.num = ctk.CTkLabel(
            self, text=str(index + 1), font=Theme.CAPTION,
            text_color=Theme.TEXT_TERTIARY, width=28,
        )
        self.num.grid(row=0, column=0, padx=(12, 2), pady=8)

        # Info
        info = ctk.CTkFrame(self, fg_color="transparent")
        info.grid(row=0, column=1, sticky="w", padx=4, pady=6)

        self.title_lbl = ctk.CTkLabel(
            info, text=track.display_title,
            font=Theme.BODY_BOLD, text_color=Theme.TEXT_PRIMARY, anchor="w",
            pady=1,
        )
        self.title_lbl.pack(anchor="w")

        self.artist_lbl = ctk.CTkLabel(
            info, text=track.display_artist,
            font=Theme.MICRO, text_color=Theme.TEXT_TERTIARY, anchor="w",
            pady=2,
        )
        self.artist_lbl.pack(anchor="w")

        # Duration
        self.dur = ctk.CTkLabel(
            self, text=format_time(track.duration),
            font=Theme.MICRO, text_color=Theme.TEXT_TERTIARY, width=36,
        )
        self.dur.grid(row=0, column=2, padx=(2, 14), pady=8)

        for w in (self, self.num, info, self.title_lbl, self.artist_lbl, self.dur):
            w.bind("<Button-1>", self._clicked)
            w.bind("<Enter>", self._enter)
            w.bind("<Leave>", self._leave)

    def _clicked(self, e=None):
        if self._on_click:
            self._on_click(self.index)

    def _enter(self, e=None):
        if not self._is_active:
            self.configure(fg_color=Theme.BG_HOVER)

    def _leave(self, e=None):
        if not self._is_active:
            self.configure(fg_color="transparent")

    def set_active(self, active: bool):
        self._is_active = active
        if active:
            self.configure(fg_color=Theme.BG_ACTIVE)
            self.title_lbl.configure(text_color=Theme.ACCENT)
            self.num.configure(text_color=Theme.ACCENT)
        else:
            self.configure(fg_color="transparent")
            self.title_lbl.configure(text_color=Theme.TEXT_PRIMARY)
            self.num.configure(text_color=Theme.TEXT_TERTIARY)


# ─────────────────────────────────────────────
# Pill Button — minimal, Apple-style
# ─────────────────────────────────────────────

class PillButton(ctk.CTkButton):
    """A small rounded pill button."""
    def __init__(self, master, text, on_click=None,
                 fg=Theme.BG_CARD, hover=Theme.BG_HOVER,
                 text_color=Theme.TEXT_SECONDARY,
                 font=Theme.CAPTION, width=40, height=36, **kw):
        super().__init__(
            master, text=text, command=on_click,
            fg_color=fg, hover_color=hover,
            text_color=text_color, font=font,
            width=width, height=height,
            corner_radius=height // 2,
            border_width=0,
            **kw,
        )


# ─────────────────────────────────────────────
# Main Application
# ─────────────────────────────────────────────

class EndlessApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=2048)

        # Window
        self.title("Endless")
        self.geometry("960x600")
        self.minsize(840, 520)
        self.configure(fg_color=Theme.BG)

        ctk.set_appearance_mode("light")

        # State
        self.playlist: list[Track] = []
        self.playlist_widgets: list[PlaylistItem] = []
        self.current_index: int = -1
        self.is_playing: bool = False
        self.is_paused: bool = False
        self.is_shuffle: bool = False
        self.repeat_mode: int = 0
        self.track_length: float = 0.0
        self.current_position: float = 0.0
        self._seek_offset: float = 0.0
        self._seek_active: bool = False
        self._volume: float = 0.7
        self._update_job = None
        self._default_cover_pil = create_default_cover(300)

        self._build_ui()
        self._schedule_update()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._running = True
        self._was_busy = False
        self._end_thread = threading.Thread(target=self._track_end_poller, daemon=True)
        self._end_thread.start()

    # ───────────── UI ─────────────

    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self._build_sidebar()
        self._build_player()

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=280, fg_color=Theme.BG_SIDEBAR, corner_radius=0)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_rowconfigure(3, weight=1)
        sb.grid_columnconfigure(0, weight=1)

        # ── App title ──
        ctk.CTkLabel(
            sb, text="Endless", font=Theme.TITLE,
            text_color=Theme.TEXT_PRIMARY, anchor="w",
        ).grid(row=0, column=0, sticky="w", padx=24, pady=(24, 0))

        ctk.CTkLabel(
            sb, text="Your music, simply.",
            font=Theme.CAPTION, text_color=Theme.TEXT_TERTIARY, anchor="w",
        ).grid(row=1, column=0, sticky="w", padx=24, pady=(2, 16))

        # ── Action buttons ──
        btn_row = ctk.CTkFrame(sb, fg_color="transparent")
        btn_row.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 8))
        btn_row.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            btn_row, text="Add Files",
            font=Theme.BODY_BOLD,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_SOFT,
            text_color="#FFFFFF", corner_radius=12, height=36,
            command=self._add_files,
        ).grid(row=0, column=0, sticky="ew", padx=(0, 4))

        ctk.CTkButton(
            btn_row, text="Add Folder",
            font=Theme.BODY,
            fg_color=Theme.BG_CARD, hover_color=Theme.BG_HOVER,
            text_color=Theme.TEXT_SECONDARY, corner_radius=12, height=36,
            border_width=1, border_color=Theme.DIVIDER,
            command=self._add_folder,
        ).grid(row=0, column=1, sticky="ew", padx=(4, 0))

        # ── Playlist header ──
        ph = ctk.CTkFrame(sb, fg_color="transparent")
        ph.grid(row=2, column=0, sticky="ew", padx=24, pady=(52, 0))
        ph.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            ph, text="Library", font=Theme.CAPTION,
            text_color=Theme.TEXT_TERTIARY, anchor="w",
        ).grid(row=0, column=0, sticky="w")

        self.track_count_label = ctk.CTkLabel(
            ph, text="", font=Theme.MICRO,
            text_color=Theme.TEXT_TERTIARY, anchor="e",
        )
        self.track_count_label.grid(row=0, column=1, sticky="e")

        # ── Scrollable list ──
        self.playlist_scroll = ctk.CTkScrollableFrame(
            sb, fg_color="transparent",
            scrollbar_button_color=Theme.ACCENT_MUTED,
            scrollbar_button_hover_color=Theme.ACCENT,
        )
        self.playlist_scroll.grid(row=3, column=0, sticky="nsew", padx=8, pady=(4, 16))
        self.playlist_scroll.grid_columnconfigure(0, weight=1)

    def _build_player(self):
        player = ctk.CTkFrame(self, fg_color=Theme.BG, corner_radius=0)
        player.grid(row=0, column=1, sticky="nsew")
        player.grid_columnconfigure(0, weight=1)
        player.grid_rowconfigure(0, weight=1)

        center = ctk.CTkFrame(player, fg_color="transparent")
        center.grid(row=0, column=0, sticky="nsew")
        center.grid_columnconfigure(0, weight=1)
        center.grid_rowconfigure(0, weight=1)

        # ── Album Art ──
        art_container = ctk.CTkFrame(center, fg_color="transparent")
        art_container.grid(row=0, column=0, pady=(36, 8))

        cover = make_rounded(self._default_cover_pil, radius=20)
        self._cover_ctk = ctk.CTkImage(light_image=cover, dark_image=cover, size=(260, 260))
        self.cover_label = ctk.CTkLabel(art_container, image=self._cover_ctk, text="")
        self.cover_label.pack()

        # ── Song info ──
        info = ctk.CTkFrame(center, fg_color="transparent")
        info.grid(row=1, column=0, pady=(8, 4))

        self.song_title_label = ctk.CTkLabel(
            info, text="No Track Selected",
            font=Theme.HEADLINE, text_color=Theme.TEXT_PRIMARY,
            pady=2,
        )
        self.song_title_label.pack()

        self.song_artist_label = ctk.CTkLabel(
            info, text="Add music to begin",
            font=Theme.SUBHEAD, text_color=Theme.TEXT_SECONDARY,
            pady=4,
        )
        self.song_artist_label.pack(pady=(2, 0))

        # ── Progress ──
        prog_frame = ctk.CTkFrame(center, fg_color="transparent")
        prog_frame.grid(row=2, column=0, sticky="ew", padx=80, pady=(12, 0))
        prog_frame.grid_columnconfigure(1, weight=1)

        self.time_elapsed = ctk.CTkLabel(
            prog_frame, text="0:00", font=Theme.MICRO,
            text_color=Theme.TEXT_TERTIARY, width=32,
        )
        self.time_elapsed.grid(row=0, column=0, padx=(0, 8))

        self.progress_slider = ctk.CTkSlider(
            prog_frame, from_=0, to=100, number_of_steps=1000,
            fg_color=Theme.SLIDER_TRACK,
            progress_color=Theme.SLIDER_PROG,
            button_color=Theme.SLIDER_KNOB,
            button_hover_color=Theme.ACCENT_SOFT,
            height=4, button_length=12,
            command=self._on_progress_drag,
        )
        self.progress_slider.set(0)
        self.progress_slider.grid(row=0, column=1, sticky="ew")
        self.progress_slider.bind("<ButtonPress-1>", lambda e: self._seek_start())
        self.progress_slider.bind("<ButtonRelease-1>", lambda e: self._seek_end())

        self.time_total = ctk.CTkLabel(
            prog_frame, text="0:00", font=Theme.MICRO,
            text_color=Theme.TEXT_TERTIARY, width=32,
        )
        self.time_total.grid(row=0, column=2, padx=(8, 0))

        # ── Transport Controls ──
        controls = ctk.CTkFrame(center, fg_color="transparent")
        controls.grid(row=3, column=0, pady=(16, 8))

        # Shuffle
        self.shuffle_btn = PillButton(
            controls, text="Shuffle", on_click=self._toggle_shuffle,
            text_color=Theme.TEXT_TERTIARY,
        )
        self.shuffle_btn.pack(side="left", padx=4)

        # Previous
        PillButton(
            controls, text="◁", on_click=self._prev_track,
            font=Theme.ICON_FONT, width=44,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(side="left", padx=4)

        # Play / Pause — prominent
        self.play_btn = ctk.CTkButton(
            controls, text="▶", font=Theme.ICON_LARGE,
            fg_color=Theme.ACCENT, hover_color=Theme.ACCENT_SOFT,
            text_color="#FFFFFF", width=56, height=56,
            corner_radius=28, command=self._toggle_play,
        )
        self.play_btn.pack(side="left", padx=10)

        # Next
        PillButton(
            controls, text="▷", on_click=self._next_track,
            font=Theme.ICON_FONT, width=44,
            text_color=Theme.TEXT_PRIMARY,
        ).pack(side="left", padx=4)

        # Repeat
        self.repeat_btn = PillButton(
            controls, text="Repeat", on_click=self._toggle_repeat,
            text_color=Theme.TEXT_TERTIARY,
        )
        self.repeat_btn.pack(side="left", padx=4)

        # ── Volume ──
        vol_frame = ctk.CTkFrame(center, fg_color="transparent")
        vol_frame.grid(row=4, column=0, pady=(4, 24))

        ctk.CTkLabel(
            vol_frame, text="Vol", font=Theme.MICRO,
            text_color=Theme.TEXT_TERTIARY,
        ).pack(side="left", padx=(0, 6))

        self.volume_slider = ctk.CTkSlider(
            vol_frame, from_=0, to=1, number_of_steps=100,
            width=120, height=4,
            fg_color=Theme.SLIDER_TRACK,
            progress_color=Theme.ACCENT_MUTED,
            button_color="#FFFFFF",
            button_hover_color=Theme.ACCENT,
            button_length=8,
            command=self._set_volume,
        )
        self.volume_slider.set(self._volume)
        self.volume_slider.pack(side="left")
        pygame.mixer.music.set_volume(self._volume)

    # ───────────── FILE I/O ─────────────

    def _add_files(self):
        files = filedialog.askopenfilenames(
            title="Select Music Files",
            filetypes=[
                ("Audio Files", "*.mp3 *.MP3 *.flac *.FLAC *.ogg *.OGG *.wav *.WAV"),
                ("All Files", "*.*"),
            ],
        )
        if files:
            self._load_files(list(files))

    def _add_folder(self):
        folder = filedialog.askdirectory(title="Select Music Folder")
        if folder:
            files = []
            for root, _, filenames in os.walk(folder):
                for f in sorted(filenames):
                    if Path(f).suffix.lower() in SUPPORTED_FORMATS:
                        files.append(os.path.join(root, f))
            if files:
                self._load_files(files)

    def _load_files(self, filepaths: list[str]):
        start = len(self.playlist)
        for fp in filepaths:
            if Path(fp).suffix.lower() in SUPPORTED_FORMATS:
                self.playlist.append(Track(fp))
        self._rebuild_playlist_ui()
        if not self.is_playing and self.current_index == -1 and len(self.playlist) > start:
            self._play_track(start)

    def _rebuild_playlist_ui(self):
        for w in self.playlist_widgets:
            w.destroy()
        self.playlist_widgets.clear()

        for i, track in enumerate(self.playlist):
            item = PlaylistItem(self.playlist_scroll, track, i, on_click=self._play_track)
            item.pack(fill="x", padx=4, pady=1)
            if i == self.current_index:
                item.set_active(True)
            self.playlist_widgets.append(item)

        n = len(self.playlist)
        self.track_count_label.configure(text=f"{n} song{'s' if n != 1 else ''}" if n else "")

    # ───────────── PLAYBACK ─────────────

    def _play_track(self, index: int):
        if index < 0 or index >= len(self.playlist):
            return
        track = self.playlist[index]

        try:
            pygame.mixer.music.load(track.filepath)
            pygame.mixer.music.play()
        except Exception as e:
            print(f"Error: {e}")
            return

        old = self.current_index
        self.current_index = index
        self.is_playing = True
        self.is_paused = False
        self.track_length = track.duration
        self.current_position = 0.0
        self._seek_offset = 0.0
        self._was_busy = True

        self._update_now_playing(track)
        self._highlight(old, index)
        self.play_btn.configure(text="❙❙")

    def _update_now_playing(self, track: Track):
        self.song_title_label.configure(text=track.display_title)
        artist_text = track.display_artist
        if track.album and track.album != "Unknown Album":
            artist_text += f"  ·  {track.album}"
        self.song_artist_label.configure(text=artist_text)

        cover = make_rounded(track.get_cover_image((300, 300)), radius=20)
        self._cover_ctk = ctk.CTkImage(light_image=cover, dark_image=cover, size=(260, 260))
        self.cover_label.configure(image=self._cover_ctk)

        self.time_total.configure(text=format_time(track.duration))
        self.time_elapsed.configure(text="0:00")
        self.progress_slider.set(0)

    def _highlight(self, old_idx: int, new_idx: int):
        if 0 <= old_idx < len(self.playlist_widgets):
            self.playlist_widgets[old_idx].set_active(False)
        if 0 <= new_idx < len(self.playlist_widgets):
            self.playlist_widgets[new_idx].set_active(True)

    def _toggle_play(self):
        if not self.playlist:
            return
        if self.current_index == -1:
            self._play_track(0)
            return
        if self.is_paused:
            pygame.mixer.music.unpause()
            self.is_paused = False
            self.is_playing = True
            self.play_btn.configure(text="❙❙")
        elif self.is_playing:
            pygame.mixer.music.pause()
            self.is_paused = True
            self.is_playing = False
            self.play_btn.configure(text="▶")
        else:
            self._play_track(self.current_index)

    def _next_track(self):
        if not self.playlist:
            return
        if self.is_shuffle:
            pool = [i for i in range(len(self.playlist)) if i != self.current_index]
            nxt = random.choice(pool) if pool else self.current_index
        else:
            nxt = (self.current_index + 1) % len(self.playlist)
        self._play_track(nxt)

    def _prev_track(self):
        if not self.playlist:
            return
        if self.current_position > 3:
            self._play_track(self.current_index)
            return
        self._play_track((self.current_index - 1) % len(self.playlist))

    def _on_track_end(self):
        if self.repeat_mode == 2:
            self._play_track(self.current_index)
        elif self.repeat_mode == 1:
            self._next_track()
        else:
            if self.current_index < len(self.playlist) - 1:
                self._next_track()
            else:
                self.is_playing = False
                self.current_position = 0.0
                self._seek_offset = 0.0
                self.progress_slider.set(0)
                self.time_elapsed.configure(text="0:00")
                self.play_btn.configure(text="▶")

    # ───────────── CONTROLS ─────────────

    def _toggle_shuffle(self):
        self.is_shuffle = not self.is_shuffle
        self.shuffle_btn.configure(
            text_color=Theme.ACCENT if self.is_shuffle else Theme.TEXT_TERTIARY,
            fg_color=Theme.ACCENT_PALE if self.is_shuffle else Theme.BG_CARD,
        )

    def _toggle_repeat(self):
        self.repeat_mode = (self.repeat_mode + 1) % 3
        labels = {0: "Repeat", 1: "Repeat All", 2: "Repeat 1"}
        self.repeat_btn.configure(
            text=labels[self.repeat_mode],
            text_color=Theme.ACCENT if self.repeat_mode else Theme.TEXT_TERTIARY,
            fg_color=Theme.ACCENT_PALE if self.repeat_mode else Theme.BG_CARD,
        )

    def _set_volume(self, val):
        self._volume = val
        pygame.mixer.music.set_volume(val)

    # ───────────── PROGRESS ─────────────

    def _seek_start(self):
        self._seek_active = True

    def _seek_end(self):
        self._seek_active = False
        if self.is_playing or self.is_paused:
            pos = self.progress_slider.get() / 100.0 * self.track_length
            try:
                pygame.mixer.music.play(start=pos)
                self._seek_offset = pos
                self.current_position = pos
                if self.is_paused:
                    pygame.mixer.music.pause()
            except Exception as e:
                print(f"Seek error: {e}")

    def _on_progress_drag(self, val):
        if self._seek_active and self.track_length > 0:
            self.time_elapsed.configure(text=format_time(val / 100.0 * self.track_length))

    def _schedule_update(self):
        self._update_progress()
        self._update_job = self.after(250, self._schedule_update)

    def _update_progress(self):
        if self.is_playing and not self._seek_active:
            pos_ms = pygame.mixer.music.get_pos()
            if pos_ms >= 0:
                self.current_position = min(
                    self._seek_offset + (pos_ms / 1000.0),
                    self.track_length if self.track_length > 0 else float("inf"),
                )
                if self.track_length > 0:
                    pct = min((self.current_position / self.track_length) * 100, 100)
                    self.progress_slider.set(pct)
                self.time_elapsed.configure(text=format_time(self.current_position))

    # ───────────── TRACK END POLLER ─────────────

    def _track_end_poller(self):
        while self._running:
            busy = pygame.mixer.music.get_busy()
            if self._was_busy and not busy and not self.is_paused:
                self.after(0, self._on_track_end)
            self._was_busy = busy
            time.sleep(0.15)

    # ───────────── CLEANUP ─────────────

    def _on_close(self):
        self._running = False
        if self._update_job:
            self.after_cancel(self._update_job)
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        self.destroy()


def main():
    app = EndlessApp()
    app.mainloop()


if __name__ == "__main__":
    main()
