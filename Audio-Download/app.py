#!/usr/bin/env python3
"""
YouTube Audio Downloader App
A command-line and interactive application to download YouTube audio.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import List

from downloader import AudioDownloader, AudioDownloadError
from utils import (
    Colors,
    clean_url,
    color_text,
    format_duration,
    is_ffmpeg_available,
    print_banner,
    print_error,
    print_step,
    print_success,
    print_warning,
    validate_youtube_url,
)


def run_interactive_mode() -> None:
    """Run interactive CLI session for downloading YouTube audio."""
    print_banner()

    ffmpeg_installed = is_ffmpeg_available()
    status_ffmpeg = (
        color_text("Detected ✔", Colors.GREEN)
        if ffmpeg_installed
        else color_text("Not detected ⚠ (Defaulting to native M4A/WebM)", Colors.YELLOW)
    )

    default_format = "mp3" if ffmpeg_installed else "m4a"
    default_dir = "downloads"

    print(f" {color_text('• Python:', Colors.CYAN)}   {sys.version.split()[0]}")
    print(f" {color_text('• FFmpeg:', Colors.CYAN)}   {status_ffmpeg}")
    print(f" {color_text('• Output:', Colors.CYAN)}   {Path(default_dir).resolve()}")
    if not ffmpeg_installed:
        print(
            f"\n {color_text('Tip:', Colors.YELLOW)} To enable MP3 conversion, install FFmpeg:\n"
            f"   • macOS: {color_text('brew install ffmpeg', Colors.BOLD)}\n"
            f"   • Linux: {color_text('sudo apt install ffmpeg', Colors.BOLD)}\n"
            f"   • Windows: {color_text('winget install Gyan.FFmpeg', Colors.BOLD)}"
        )
    print("\n" + "─" * 65)

    while True:
        try:
            print()
            user_input = input(
                color_text("Enter YouTube URL (or multiple separated by comma/space, 'q' to quit): ", Colors.BOLD)
            ).strip()

            if not user_input:
                continue

            if user_input.lower() in ("q", "quit", "exit"):
                print(f"\n{color_text('Goodbye! 🎵', Colors.GREEN)}")
                break

            # Split possible multiple URLs by comma or whitespace
            raw_links = [clean_url(u) for u in user_input.replace(",", " ").split() if u.strip()]
            valid_links = [u for u in raw_links if validate_youtube_url(u)]

            if not valid_links:
                print_error("No valid YouTube URLs recognized. Please check your link format.")
                print("  Example: https://www.youtube.com/watch?v=dQw4w9WgXcQ")
                continue

            if len(valid_links) < len(raw_links):
                invalid_count = len(raw_links) - len(valid_links)
                print_warning(f"Ignored {invalid_count} unrecognized link(s).")

            # Format selection
            fmt_prompt = (
                f"Choose audio format [mp3/m4a/wav/flac/best] "
                f"(Press Enter for '{default_format}'): "
            )
            chosen_format = input(color_text(fmt_prompt, Colors.CYAN)).strip().lower()
            if not chosen_format:
                chosen_format = default_format
            elif chosen_format not in AudioDownloader.SUPPORTED_FORMATS:
                print_warning(f"Unknown format '{chosen_format}', falling back to '{default_format}'.")
                chosen_format = default_format

            # Downloader instantiation
            downloader = AudioDownloader(
                output_dir=default_dir,
                audio_format=chosen_format,
                audio_quality="192",
            )

            # Download single or multiple
            if len(valid_links) == 1:
                target_url = valid_links[0]
                print_step(f"Fetching video info for: {target_url}")
                try:
                    result = downloader.download(target_url)
                    if result.get("type") == "playlist":
                        print_success(
                            f"Downloaded playlist: '{result.get('title')}' ({result.get('count')} tracks)!\n"
                            f"Saved in: {result.get('output_dir')}"
                        )
                    else:
                        print_success(
                            f"Successfully downloaded: {result.get('title')}\n"
                            f"• Format: {result.get('format')}\n"
                            f"• Duration: {result.get('duration_formatted')}\n"
                            f"• Size: {result.get('file_size_formatted')}\n"
                            f"• Location: {result.get('file_path')}"
                        )
                except AudioDownloadError as e:
                    print_error(f"Download failed: {e}")
            else:
                print_step(f"Starting batch download of {len(valid_links)} URLs...")
                results = downloader.download_batch(valid_links)
                succeeded = sum(1 for r in results if "error" not in r)
                print(
                    f"\n{color_text('Batch Summary:', Colors.BOLD)} "
                    f"{color_text(str(succeeded), Colors.GREEN)} succeeded, "
                    f"{color_text(str(len(results) - succeeded), Colors.RED)} failed."
                )

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n{color_text('Interrupted. Exiting...', Colors.YELLOW)}")
            break


def parse_batch_file(file_path: str) -> List[str]:
    """Read URLs from a text file, ignoring empty lines and comments."""
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"Batch file not found: {file_path}")

    with path.open("r", encoding="utf-8") as f:
        urls = [clean_url(line) for line in f if line.strip() and not line.strip().startswith("#")]
    return urls


def main() -> None:
    """Main CLI entrypoint."""
    ffmpeg_installed = is_ffmpeg_available()
    default_format = "mp3" if ffmpeg_installed else "m4a"

    parser = argparse.ArgumentParser(
        description="YouTube Audio Downloader - Download high quality audio from YouTube videos or playlists.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start interactive mode:
  python app.py

  # Download audio from a single video:
  python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

  # Download as MP3 (requires FFmpeg) into custom folder:
  python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f mp3 -o ~/Music

  # Download multiple URLs from a text file:
  python app.py --batch my_links.txt

  # Inspect video information without downloading:
  python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
        """,
    )

    parser.add_argument(
        "urls",
        nargs="*",
        help="One or more YouTube video or playlist URLs",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=AudioDownloader.SUPPORTED_FORMATS,
        default=default_format,
        help=f"Audio format (default: {default_format})",
    )
    parser.add_argument(
        "-q",
        "--quality",
        default="192",
        help="Audio quality / bitrate in kbps (default: 192)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        default="downloads",
        help="Directory to save downloaded files (default: downloads)",
    )
    parser.add_argument(
        "-b",
        "--batch",
        help="Path to a text file containing YouTube URLs (one per line)",
    )
    parser.add_argument(
        "-i",
        "--info",
        action="store_true",
        help="Display video details without downloading",
    )
    parser.add_argument(
        "--no-playlist",
        action="store_true",
        help="Download only the video, even if the URL belongs to a playlist",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Force interactive mode",
    )

    args = parser.parse_args()

    # Collect URLs from arguments or batch file
    urls_to_process: List[str] = [clean_url(u) for u in args.urls]

    if args.batch:
        try:
            batch_urls = parse_batch_file(args.batch)
            urls_to_process.extend(batch_urls)
        except Exception as e:
            print_error(str(e))
            sys.exit(1)

    # If no URLs provided, run interactive mode
    if not urls_to_process or args.interactive:
        run_interactive_mode()
        return

    # Validate URLs
    valid_urls = [u for u in urls_to_process if validate_youtube_url(u)]
    if not valid_urls:
        print_error("No valid YouTube URLs provided.")
        sys.exit(1)

    # Initialize downloader
    downloader = AudioDownloader(
        output_dir=args.output_dir,
        audio_format=args.format,
        audio_quality=args.quality,
        allow_playlist=not args.no_playlist,
    )

    # Info-only mode
    if args.info:
        for url in valid_urls:
            print_step(f"Fetching metadata: {url}")
            try:
                info = downloader.get_info(url)
                print(f" {color_text('Title:', Colors.BOLD)}    {info.get('title')}")
                print(f" {color_text('Channel:', Colors.BOLD)}  {info.get('uploader', 'N/A')}")
                print(f" {color_text('Duration:', Colors.BOLD)} {format_duration(info.get('duration'))}")
                print(f" {color_text('Views:', Colors.BOLD)}    {info.get('view_count', 'N/A'):,}" if info.get('view_count') else "")
            except AudioDownloadError as err:
                print_error(f"Failed to fetch metadata for {url}: {err}")
        return

    # Download URLs
    if len(valid_urls) == 1:
        url = valid_urls[0]
        print_step(f"Starting download: {url}")
        try:
            result = downloader.download(url)
            if result.get("type") == "playlist":
                print_success(
                    f"Playlist downloaded successfully: '{result.get('title')}' ({result.get('count')} tracks)\n"
                    f"Saved to: {result.get('output_dir')}"
                )
            else:
                print_success(
                    f"Download finished: {result.get('title')}\n"
                    f"• File: {result.get('file_path')}\n"
                    f"• Size: {result.get('file_size_formatted')}"
                )
        except AudioDownloadError as err:
            print_error(f"Download failed: {err}")
            sys.exit(1)
    else:
        print_step(f"Processing {len(valid_urls)} YouTube link(s)...")
        results = downloader.download_batch(valid_urls)
        succeeded = sum(1 for r in results if "error" not in r)
        print(
            f"\n{color_text('Finished:', Colors.BOLD)} "
            f"{color_text(str(succeeded), Colors.GREEN)} succeeded, "
            f"{color_text(str(len(results) - succeeded), Colors.RED)} failed."
        )


if __name__ == "__main__":
    main()
