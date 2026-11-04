"""Core downloader module using yt-dlp for downloading YouTube audio."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

# Ensure SSL certificates are resolved correctly on macOS / Python environments
try:
    import certifi
    os.environ.setdefault("SSL_CERT_FILE", certifi.where())
except ImportError:
    pass

import yt_dlp
from utils import (
    Colors,
    color_text,
    format_bytes,
    format_duration,
    is_ffmpeg_available,
    print_error,
    print_step,
    print_success,
    print_warning,
    sanitize_filename,
    validate_youtube_url,
)


class AudioDownloadError(Exception):
    """Custom exception raised when an audio download fails."""
    pass


class AudioDownloader:
    """Handles audio extraction and download from YouTube URLs."""

    SUPPORTED_FORMATS = ("mp3", "m4a", "wav", "flac", "opus", "best")
    DEFAULT_FORMAT = "mp3"
    DEFAULT_QUALITY = "192"

    def __init__(
        self,
        output_dir: str | Path = "downloads",
        audio_format: str = DEFAULT_FORMAT,
        audio_quality: str = DEFAULT_QUALITY,
        allow_playlist: bool = True,
        quiet: bool = False,
        progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.audio_format = audio_format.lower()
        self.audio_quality = str(audio_quality)
        self.allow_playlist = allow_playlist
        self.quiet = quiet
        self.progress_callback = progress_callback
        self.has_ffmpeg = is_ffmpeg_available()

        if self.audio_format not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"Unsupported format '{self.audio_format}'. "
                f"Supported formats: {', '.join(self.SUPPORTED_FORMATS)}"
            )

    def _default_progress_hook(self, d: Dict[str, Any]) -> None:
        """Default real-time terminal progress hook."""
        if self.quiet:
            return

        status = d.get("status")
        if status == "downloading":
            downloaded = d.get("downloaded_bytes", 0)
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            speed = d.get("speed")
            eta = d.get("eta")

            percent_str = f"{(downloaded / total * 100):.1f}%" if total > 0 else "---%"
            speed_str = f"{format_bytes(speed)}/s" if speed else "--- B/s"
            eta_str = f"{eta}s" if eta is not None else "--:--"
            size_str = f"{format_bytes(downloaded)} / {format_bytes(total)}" if total else format_bytes(downloaded)

            bar_length = 25
            filled_length = int(bar_length * downloaded // total) if total > 0 else 0
            bar = "█" * filled_length + "░" * (bar_length - filled_length)

            sys.stdout.write(
                f"\r{color_text('Downloading:', Colors.CYAN)} [{bar}] "
                f"{color_text(percent_str, Colors.BOLD)} ({size_str}) "
                f"at {speed_str} ETA {eta_str}   "
            )
            sys.stdout.flush()

        elif status == "finished":
            sys.stdout.write("\n")
            print_step("Download complete. Extracting audio...")
            sys.stdout.flush()

    def _build_ydl_opts(self, target_format: str) -> Dict[str, Any]:
        """Construct configuration options for yt-dlp."""
        outtmpl = str(self.output_dir / "%(title)s.%(ext)s")

        hooks = []
        if self.progress_callback:
            hooks.append(self.progress_callback)
        else:
            hooks.append(self._default_progress_hook)

        ydl_opts: Dict[str, Any] = {
            "outtmpl": outtmpl,
            "noplaylist": not self.allow_playlist,
            "quiet": True,
            "no_warnings": True,
            "progress_hooks": hooks,
            "ignoreerrors": False,
        }

        # Handle audio formats with or without FFmpeg
        if target_format == "best":
            ydl_opts["format"] = "bestaudio/best"
        elif target_format == "m4a" and not self.has_ffmpeg:
            # Native M4A audio stream direct from YouTube without conversion
            ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"
        elif self.has_ffmpeg:
            # Use FFmpeg post-processing to extract and convert to preferred format
            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": target_format,
                    "preferredquality": self.audio_quality,
                }
            ]
        else:
            # FFmpeg is needed for formats like MP3/WAV/FLAC, but not present
            print_warning(
                f"FFmpeg is not installed. Falling back to native audio stream (m4a/webm).\n"
                f"To convert to '{target_format}', install ffmpeg (e.g. 'brew install ffmpeg')."
            )
            ydl_opts["format"] = "bestaudio[ext=m4a]/bestaudio/best"

        return ydl_opts

    def get_info(self, url: str) -> Dict[str, Any]:
        """
        Extract video information without downloading media files.

        Returns a dictionary with title, duration, uploader, views, etc.
        """
        if not validate_youtube_url(url):
            raise AudioDownloadError(f"Invalid YouTube URL: {url}")

        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
        }

        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info is None:
                    raise AudioDownloadError("Could not retrieve video information.")
                return info
        except Exception as e:
            raise AudioDownloadError(f"Failed to fetch video info: {e}") from e

    def download(self, url: str) -> Dict[str, Any]:
        """
        Download audio from a YouTube URL.

        Returns a dictionary containing download metadata:
          - title: Track title
          - duration: Duration in seconds
          - file_path: Local path to the downloaded file
          - format: File extension
        """
        if not validate_youtube_url(url):
            raise AudioDownloadError(f"Invalid YouTube URL: {url}")

        ydl_opts = self._build_ydl_opts(self.audio_format)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # Extract info and perform download
                info = ydl.extract_info(url, download=True)
                if info is None:
                    raise AudioDownloadError("Failed to extract video information.")

                # If this was a playlist, extract information from entries
                if "_type" in info and info["_type"] == "playlist":
                    entries = list(info.get("entries", []))
                    count = len(entries)
                    return {
                        "type": "playlist",
                        "title": info.get("title", "Playlist"),
                        "count": count,
                        "output_dir": str(self.output_dir.resolve()),
                    }

                title = info.get("title", "Unknown Title")
                duration = info.get("duration")
                ext = info.get("ext", self.audio_format)

                # Determine expected output filename
                filename = ydl.prepare_filename(info)
                # If postprocessed to another extension, adjust it
                if self.has_ffmpeg and self.audio_format != "best":
                    base_path = os.path.splitext(filename)[0]
                    expected_file = f"{base_path}.{self.audio_format}"
                else:
                    expected_file = filename

                # Check if file exists, or locate closest match in output directory
                actual_path = expected_file
                if not os.path.exists(actual_path):
                    # Check for base name with any audio extension
                    base = os.path.splitext(filename)[0]
                    for candidate_ext in ("mp3", "m4a", "webm", "opus", "wav", "flac"):
                        candidate = f"{base}.{candidate_ext}"
                        if os.path.exists(candidate):
                            actual_path = candidate
                            ext = candidate_ext
                            break

                file_size = os.path.getsize(actual_path) if os.path.exists(actual_path) else None

                return {
                    "type": "video",
                    "title": title,
                    "duration": duration,
                    "duration_formatted": format_duration(duration),
                    "file_path": str(Path(actual_path).resolve()) if os.path.exists(actual_path) else actual_path,
                    "file_size": file_size,
                    "file_size_formatted": format_bytes(file_size),
                    "format": ext,
                    "uploader": info.get("uploader", "Unknown"),
                }

        except yt_dlp.utils.DownloadError as e:
            raise AudioDownloadError(f"Download failed: {e}") from e
        except Exception as e:
            raise AudioDownloadError(f"An unexpected error occurred: {e}") from e

    def download_batch(self, urls: List[str]) -> List[Dict[str, Any]]:
        """Download multiple YouTube URLs sequentially."""
        results = []
        for i, url in enumerate(urls, 1):
            url = url.strip()
            if not url or url.startswith("#"):
                continue

            print_step(f"Processing ({i}/{len(urls)}): {url}")
            try:
                result = self.download(url)
                results.append(result)
                if result.get("type") == "playlist":
                    print_success(
                        f"Finished playlist: '{result.get('title')}' ({result.get('count')} tracks)"
                    )
                else:
                    print_success(
                        f"Saved: {result.get('title')} [{result.get('file_size_formatted')}] -> {result.get('file_path')}"
                    )
            except AudioDownloadError as err:
                print_error(f"Failed to download {url}: {err}")
                results.append({"url": url, "error": str(err)})

        return results
