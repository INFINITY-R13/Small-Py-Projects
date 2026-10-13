<p align="center">
  <img src="https://img.icons8.com/sf-regular-filled/96/FF2D55/infinity.png" width="64" alt="logo"/>
</p>

<h1 align="center">Endless</h1>

<p align="center">
  <em>A minimalist music player, crafted with Python.</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10+-FF2D55?style=flat-square&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/platform-macOS%20·%20Linux%20·%20Windows-1D1D1F?style=flat-square" alt="Platform">
  <img src="https://img.shields.io/badge/license-MIT-FF6482?style=flat-square" alt="License">
</p>

---

## ✦ About

**Endless** is a lightweight desktop music player with a soft-pink, Apple-inspired UI.  
Built on `customtkinter` + `pygame-ce`, it plays your local library with zero fuss.

## ✦ Features

| | |
|---|---|
| 🎨 **Soft-pink UI** | Light theme with Apple-like typography and accents |
| 🎵 **Multi-format** | MP3 · FLAC · OGG · WAV |
| 🖼️ **Album art** | Extracts embedded cover art from metadata with rounded corners |
| 📂 **File browser** | Add individual audio tracks or entire folders |
| 🔀 **Playback modes** | Shuffle · Repeat all · Repeat one |
| 🎚️ **Volume slider** | Smooth, accent-colored control |
| 📜 **Playlist sidebar** | Scrollable track list with active song highlighting |

## ✦ Quick start

### 1. Prerequisites (Linux only)
If you are running on a Debian/Ubuntu-based distribution, ensure Tkinter is installed:
```bash
sudo apt install python3-tk
```

### 2. Setup & Installation
```bash
# Clone the repository & enter directory
git clone https://github.com/<your-username>/endless.git
cd endless

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# Install dependencies & launch player
pip install -r requirements.txt
python endless.py
```

## ✦ Generating test tracks

If you don't have local audio files ready, generate synthesized sample tracks with embedded album art:

```bash
python generate_test_music.py
```

This creates 5 short synthesized `.wav` tracks (with embedded ID3 tags and cover art) inside `test_music/`. Then, click **Add Folder** in Endless and select `test_music/` to test playback.

## ✦ Dependencies

| Package | Role |
|---|---|
| [`customtkinter`](https://github.com/TomSchimansky/CustomTkinter) | Modern themed GUI |
| [`pygame-ce`](https://pyga.me) | Audio playback engine |
| [`mutagen`](https://mutagen.readthedocs.io) | Audio metadata & tag extraction |
| [`Pillow`](https://python-pillow.org) | Image processing & rounded corners |

## ✦ Controls

| Action | Control | Behavior |
|---|---|---|
| Play / Pause | `▶` / `❙❙` center button | Toggles playback |
| Next track | `▷` | Plays next song in queue / shuffle |
| Previous track | `◁` | Restarts track if > 3s in, else goes to previous |
| Shuffle | `Shuffle` pill button | Toggles random playback order |
| Repeat | `Repeat` pill button | Cycles: Off → Repeat All → Repeat 1 |
| Seek position | Progress slider | Drag to jump to any part of the song |
| Volume | `Vol` slider | Adjusts mixer volume |

## ✦ Project structure

```
endless/
├── endless.py              # Main music player application
├── generate_test_music.py  # Script to generate sample synthesized audio
├── requirements.txt        # Python package dependencies
├── .gitignore              # Ignored files (virtualenvs, cache, test audio)
├── LICENSE                 # MIT License
└── README.md               # Documentation & setup guide
```

---

<p align="center"><sub>made with ♥ and python</sub></p>
