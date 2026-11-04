# YouTube Audio Downloader 🎵

A lightweight, robust Python application to extract and download high-quality audio from YouTube videos and playlists. Features both an **interactive terminal UI** and a **command-line interface (CLI)** with real-time download progress, batch processing, and flexible audio format support.

---

## 🌟 Key Features

- **Multiple Format Options**: Supports `mp3`, `m4a`, `wav`, `flac`, and `opus`.
- **Works Without FFmpeg**: Automatically falls back to high-quality native audio streams (`.m4a`/`.webm`) if FFmpeg is not installed, so downloads never crash.
- **FFmpeg Integration**: When FFmpeg is detected, seamlessly transcodes and extracts clean MP3s at your desired bitrate (128k, 192k, 256k, 320k).
- **Interactive Terminal UI**: Simple guided prompts with colorized status indicators and live download progress bars.
- **Batch Downloading**: Download multiple URLs from the command line or from a `.txt` file list.
- **Playlists & Shorts**: Supports YouTube videos, Shorts, YouTube Music, and entire playlists.
- **macOS SSL Ready**: Preconfigured with `certifi` to avoid macOS Python framework SSL handshake errors.

---

## 📋 Prerequisites

- **Python**: Version 3.8 or higher.
- *(Optional)* **FFmpeg**: Needed if you wish to convert audio directly into `.mp3`, `.wav`, or `.flac`.
  - **macOS (Homebrew)**:
    ```bash
    brew install ffmpeg
    ```
  - **Ubuntu / Debian**:
    ```bash
    sudo apt update && sudo apt install -y ffmpeg
    ```
  - **Windows**:
    ```powershell
    winget install Gyan.FFmpeg
    ```
  *(Note: If FFmpeg is not installed, the app works out-of-the-box by downloading Apple/universal native `.m4a` audio!)*

---

## 🚀 Quick Start Guide

### 1. Activate or Create Virtual Environment (`venv`)

The project is designed to run in a Python virtual environment.

**On macOS / Linux:**
```bash
# If venv doesn't exist yet, create it:
python3 -m venv venv

# Activate venv:
source venv/bin/activate
```

**On Windows:**
```powershell
# Create venv:
python -m venv venv

# Activate venv:
venv\Scripts\activate
```

### 2. Install Dependencies

Install the verified dependencies from `requirements.txt`:
```bash
pip install -r requirements.txt
```

---

## 💻 Usage

### 1. Interactive Mode (Default)

Simply run the app without arguments to start interactive mode:
```bash
python app.py
```
You will be prompted to:
1. Paste one or more YouTube URLs (or type `q` to quit).
2. Choose your preferred format (e.g. `mp3`, `m4a`, `best`).
3. Watch the real-time download progress bar.

---

### 2. Command-Line (CLI) Mode

Download a single video directly:
```bash
python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

Download as MP3 with a specific bitrate and custom destination directory:
```bash
python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -f mp3 -q 320 -o ~/Music
```

Download multiple URLs at once:
```bash
python app.py "https://youtu.be/video1" "https://youtu.be/video2"
```

---

### 3. Batch Download from a Text File

Create a text file containing YouTube links (one per line):
```text
https://www.youtube.com/watch?v=VIDEO_ID_1
https://www.youtube.com/watch?v=VIDEO_ID_2
```
Then run:
```bash
python app.py --batch sample_links.txt.example
```

---

### 4. Inspect Metadata Only

Check track title, channel, duration, and view count without downloading:
```bash
python app.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --info
```

---

## ⚙️ CLI Options Reference

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| `urls` | Positional | `None` | One or more YouTube video or playlist links |
| `--format` | `-f` | `mp3` (or `m4a`) | Audio format (`mp3`, `m4a`, `wav`, `flac`, `opus`, `best`) |
| `--quality` | `-q` | `192` | Bitrate quality in kbps (e.g. `128`, `192`, `256`, `320`) |
| `--output-dir`| `-o` | `downloads` | Directory to save audio files |
| `--batch` | `-b` | `None` | File path containing list of links |
| `--info` | `-i` | `False` | Display video metadata without downloading |
| `--no-playlist`| | `False` | Download only the single video even if part of a playlist |
| `--interactive`| | `False` | Force interactive mode |

---

## 🧪 Running Unit Tests

The test suite validates URL parsing, option building, and formatting:
```bash
python -m unittest tests/test_downloader.py
```

---

## 📁 Project Structure

```text
Audio-Download/
├── .gitignore               # Ignores virtual env, downloads, audio files, cache
├── README.md                # Documentation and setup instructions
├── requirements.txt         # Project dependencies (yt-dlp, certifi)
├── app.py                   # CLI and interactive entrypoint
├── downloader.py            # Core download engine and yt-dlp integration
├── utils.py                 # URL validation, formatting, and terminal UI utilities
├── sample_links.txt.example # Example file for batch downloads
├── tests/
│   └── test_downloader.py  # Unit test suite
└── downloads/               # Default output directory for audio files
```

---

## 🛡️ License

This project is licensed under the MIT License.
