"""Utility functions for the YouTube Audio Downloader."""

from __future__ import annotations

import re
import shutil
import sys
from typing import Optional


# ANSI color codes for terminal formatting
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"


def supports_color() -> bool:
    """Check if the current terminal supports ANSI color escape sequences."""
    return sys.stdout.isatty()


def color_text(text: str, color_code: str) -> str:
    """Wrap text in ANSI color escape codes if supported."""
    if supports_color():
        return f"{color_code}{text}{Colors.RESET}"
    return text


def is_ffmpeg_available() -> bool:
    """Check if ffmpeg is installed and available in the system PATH."""
    return shutil.which("ffmpeg") is not None


# Regex matching youtube video/playlist URLs
YOUTUBE_URL_PATTERN = re.compile(
    r"^(https?://)?(www\.|m\.|music\.)?"
    r"(youtube\.com/(watch\?v=|embed/|v/|shorts/|playlist\?list=)|youtu\.be/)"
    r"([a-zA-Z0-9_-]{11}|[a-zA-Z0-9_-]{12,})"
)


def validate_youtube_url(url: str) -> bool:
    """
    Validate whether a given string is a valid YouTube video or playlist URL.

    Accepts:
      - https://www.youtube.com/watch?v=VIDEO_ID
      - https://youtu.be/VIDEO_ID
      - https://www.youtube.com/shorts/VIDEO_ID
      - https://music.youtube.com/watch?v=VIDEO_ID
      - https://www.youtube.com/playlist?list=PLAYLIST_ID
    """
    if not url or not isinstance(url, str):
        return False
    url = url.strip()
    return bool(YOUTUBE_URL_PATTERN.match(url))


def clean_url(url: str) -> str:
    """Clean and sanitize user-provided URL string."""
    url = url.strip()
    # Strip any accidental wrapping quotes or brackets
    url = url.strip("\"'<>`")
    return url


def format_bytes(num_bytes: Optional[float | int]) -> str:
    """Format byte size into human readable string (KB, MB, GB)."""
    if num_bytes is None:
        return "N/A"
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num_bytes) < 1024.0:
            return f"{num_bytes:3.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def format_duration(seconds: Optional[float | int]) -> str:
    """Format duration in seconds to HH:MM:SS or MM:SS."""
    if seconds is None:
        return "N/A"
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def sanitize_filename(filename: str) -> str:
    """Remove illegal characters for cross-platform filenames."""
    # Replace illegal characters with an underscore
    sanitized = re.sub(r'[\\/*?:"<>|]', "_", filename)
    # Strip whitespace and trailing periods
    return sanitized.strip(" .")


def print_banner() -> None:
    """Print a terminal header banner."""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}╔═══════════════════════════════════════════════════════════════╗
║                   YouTube Audio Downloader 🎵                 ║
╚═══════════════════════════════════════════════════════════════╝{Colors.RESET}
"""
    print(banner)


def print_step(message: str) -> None:
    """Print an informational step message."""
    print(f"{color_text('==>', Colors.CYAN)} {message}")


def print_success(message: str) -> None:
    """Print a success message."""
    print(f"{color_text('✔', Colors.GREEN)} {color_text(message, Colors.GREEN)}")


def print_warning(message: str) -> None:
    """Print a warning message."""
    print(f"{color_text('⚠', Colors.YELLOW)} {color_text(message, Colors.YELLOW)}")


def print_error(message: str) -> None:
    """Print an error message."""
    print(f"{color_text('✖', Colors.RED)} {color_text(message, Colors.RED)}")
