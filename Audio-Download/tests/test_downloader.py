"""Unit tests for YouTube Audio Downloader."""

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from downloader import AudioDownloader, AudioDownloadError
from utils import (
    clean_url,
    format_bytes,
    format_duration,
    is_ffmpeg_available,
    sanitize_filename,
    validate_youtube_url,
)


class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_validate_youtube_url_valid(self):
        valid_urls = [
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "http://www.youtube.com/watch?v=dQw4w9WgXcQ",
            "www.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://youtu.be/dQw4w9WgXcQ",
            "https://m.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://music.youtube.com/watch?v=dQw4w9WgXcQ",
            "https://www.youtube.com/shorts/dQw4w9WgXcQ",
            "https://www.youtube.com/playlist?list=PLrEnWoR732-DNm084vW01b33A2kIqj5Wb",
        ]
        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(validate_youtube_url(url), f"Should be valid: {url}")

    def test_validate_youtube_url_invalid(self):
        invalid_urls = [
            "https://google.com",
            "https://vimeo.com/12345678",
            "not a url",
            "",
            None,
        ]
        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(validate_youtube_url(url), f"Should be invalid: {url}")

    def test_clean_url(self):
        self.assertEqual(clean_url("  https://youtu.be/test  "), "https://youtu.be/test")
        self.assertEqual(clean_url("<https://youtu.be/test>"), "https://youtu.be/test")
        self.assertEqual(clean_url('"https://youtu.be/test"'), "https://youtu.be/test")

    def test_format_bytes(self):
        self.assertEqual(format_bytes(500), "500.0 B")
        self.assertEqual(format_bytes(1024), "1.0 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 2.5), "2.5 MB")
        self.assertEqual(format_bytes(None), "N/A")

    def test_format_duration(self):
        self.assertEqual(format_duration(45), "0:45")
        self.assertEqual(format_duration(125), "2:05")
        self.assertEqual(format_duration(3665), "1:01:05")
        self.assertEqual(format_duration(None), "N/A")

    def test_sanitize_filename(self):
        dirty = 'My: Favorite / Song * Track? "Name" <Test> | 2026.mp3'
        clean = sanitize_filename(dirty)
        for char in r'\/*?:"<>|':
            self.assertNotIn(char, clean)


class TestDownloader(unittest.TestCase):
    """Test AudioDownloader class initialization and options."""

    def test_initialization_defaults(self):
        with TemporaryDirectory() as tmpdir:
            downloader = AudioDownloader(output_dir=tmpdir)
            self.assertEqual(downloader.audio_format, "mp3")
            self.assertEqual(downloader.audio_quality, "192")
            self.assertTrue(downloader.output_dir.is_dir())

    def test_unsupported_format_raises_error(self):
        with self.assertRaises(ValueError):
            AudioDownloader(audio_format="avi")

    def test_build_ydl_opts_without_ffmpeg(self):
        with TemporaryDirectory() as tmpdir:
            downloader = AudioDownloader(output_dir=tmpdir, audio_format="mp3")
            downloader.has_ffmpeg = False
            opts = downloader._build_ydl_opts("mp3")
            # Should fall back to bestaudio[ext=m4a]/bestaudio/best
            self.assertIn("m4a", opts["format"])
            self.assertNotIn("postprocessors", opts)

    def test_build_ydl_opts_with_ffmpeg(self):
        with TemporaryDirectory() as tmpdir:
            downloader = AudioDownloader(output_dir=tmpdir, audio_format="mp3")
            downloader.has_ffmpeg = True
            opts = downloader._build_ydl_opts("mp3")
            self.assertIn("postprocessors", opts)
            self.assertEqual(opts["postprocessors"][0]["preferredcodec"], "mp3")

    def test_invalid_url_download_raises_exception(self):
        with TemporaryDirectory() as tmpdir:
            downloader = AudioDownloader(output_dir=tmpdir)
            with self.assertRaises(AudioDownloadError):
                downloader.download("https://invalid-site.com/video")


if __name__ == "__main__":
    unittest.main()
