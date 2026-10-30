<!-- Banner -->
<div align="center">

# 🍅 Pomodoro Timer

**A beautiful, minimal Pomodoro timer for the desktop — built with pure Python + tkinter.**

![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=flat-square&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/UI-tkinter%20stdlib-FF6B8A?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-lightgrey?style=flat-square)

</div>

---

```
┌───────────────────────────────────┐
│          🍅 Pomodoro              │
│  [ Pomodoro ] Short Break  Long   │
│         ╭─────────╮               │
│        ╱  25:00    ╲              │
│       │  Focus Time  │            │
│        ╲           ╱              │
│         ╰─────────╯               │
│       [  Start  ]  [ Reset ]      │
│          ● ○ ○ ○   Today 1/4     │
│  Auto-start ○        ⚙           │
└───────────────────────────────────┘
```

---

## ✨ Features

- 🍅 **Three timer modes** — Pomodoro (25 min), Short Break (5 min), Long Break (15 min)
- ⏯ **Start / Pause / Resume / Reset** controls with drift-free monotonic clock accuracy
- 🔁 **Auto-start** next session toggle (Pomodoro 1–3 → Short Break; Pomodoro 4 → Long Break)
- 🎯 **Session counter** with auto-scaling dot indicators and configurable daily goal (up to 20)
- 🔔 **System sound notification** when a session ends (`afplay` on macOS, `winsound` on Windows, audio player fallback on Linux)
- 🏷 **Window title** updates live with timer status and remaining countdown
- 🎛 **Settings panel** (modal) — configure durations for each mode and your daily Pomodoro goal
- ⌨️ **Keyboard shortcuts** for quick hands-on productivity
- 🎨 **Light pink aesthetic** — rose-pink circular progress ring, pill-style mode tabs, rounded cards, Apple-inspired whitespace and typography

---

## 🚀 Installation & Running

### Prerequisites

- Python **3.9+** (tkinter is included in standard macOS and Windows distributions)
- On Linux, install Tkinter if not already present: `sudo apt install python3-tk`

### Steps

```bash
# 1. Clone the repository
git clone https://github.com/your-username/pomodoro-timer.git
cd pomodoro-timer

# 2. (Optional) Create and activate a virtual environment
./setup.sh
# — or manually:
python3 -m venv venv
source venv/bin/activate   # macOS / Linux
# venv\Scripts\activate    # Windows

# 3. Run the app
python3 pomodoro.py
```

> **No pip installs needed.** The app runs on Python's standard library only.

### Running Tests

```bash
python3 -m unittest test_pomodoro.py
```

Or verify syntax with:

```bash
python3 pomodoro.py --check
```

---

## ⌨️ Keyboard Shortcuts

| Action                  | Shortcut        |
|-------------------------|-----------------|
| Start / Pause / Resume  | `Space`         |
| Reset Timer             | `R`             |
| Switch to Pomodoro      | `1`             |
| Switch to Short Break   | `2`             |
| Switch to Long Break    | `3`             |
| Open Settings           | `S`             |
| Toggle Auto-start       | `A`             |
| Settings: Save          | `Enter`         |
| Settings: Cancel/Close  | `Escape`        |

---

## ⚙️ Settings

Open the settings panel (⚙ icon or press `S`) to customise:

| Setting        | Default | Range          | Description |
|----------------|---------|----------------|-------------|
| Pomodoro       | 25 min  | 1–60 min       | Focus session length |
| Short Break    | 5 min   | 1–60 min       | Rest period between regular sessions |
| Long Break     | 15 min  | 1–60 min       | Extended rest after every 4th Pomodoro |
| Daily Goal     | 4       | 1–20 sessions  | Daily target Pomodoro count |

---

## 🛠 Tech Stack

| Layer       | Technology                          |
|-------------|-------------------------------------|
| Language    | Python 3.9+                         |
| UI Toolkit  | `tkinter` (stdlib)                  |
| Timing      | `time.monotonic()` (drift-free)     |
| Drawing     | `tkinter.Canvas` (progress ring)    |
| Sound       | `subprocess` → `afplay` (macOS) / `winsound` (Windows) / `paplay` (Linux) |
| Fonts       | SF Pro / Helvetica Neue / system    |
| Packaging   | Zero external dependencies          |

---

## 📁 Project Structure

```
Pomodoro/
├── pomodoro.py      # Main application (single-file GUI)
├── test_pomodoro.py # Automated test suite (stdlib unittest)
├── setup.sh         # Virtual environment bootstrap script
├── requirements.txt # Dependency documentation (stdlib only)
├── .gitignore       # Standard Python .gitignore
└── README.md        # Project overview & documentation
```

---
