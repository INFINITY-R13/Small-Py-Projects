# Python Image Viewer

A lightweight, feature-rich image viewer built with **Python**, **tkinter**, and **Pillow**, featuring a polished dark UI theme.

---

## ✨ Features

| Feature | Details |
|---|---|
| **Open images & folders** | Browse a single file or an entire directory |
| **Navigation** | Previous / Next with buttons, keyboard, or mouse scroll |
| **Zoom** | Zoom in / out / 1:1 / fit-to-window (5 % – 1000 %, 15 % per step) |
| **Transform** | Rotate CW / CCW, Flip Horizontal / Vertical |
| **Thumbnail strip** | Scrollable strip at the bottom for quick jumping |
| **Pan** | Click-drag to pan when zoomed in; scrollbars for precise control |
| **Menu bar** | Full File / View / Transform menu with keyboard shortcut hints |
| **Status bar** | Shows file name, index, dimensions, and zoom level |
| **Dark theme** | Harmonious dark palette with rounded custom buttons |
| **Supported formats** | JPEG, PNG, BMP, GIF, TIFF, WEBP, ICO |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 +
- `tkinter` (bundled with most Python installations)

### Installation

```bash
# 1. Clone / download the project
cd Image-Viewer

# 2. Create & activate a virtual environment
python3 -m venv venv
source venv/bin/activate       # macOS / Linux
# venv\Scripts\activate        # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
python image_viewer.py
```

---

## ⌨️ Keyboard Shortcuts

| Key | Action |
|---|---|
| `→` / `D` | Next image |
| `←` / `A` | Previous image |
| `+` / `=` | Zoom in |
| `-` / `_` | Zoom out |
| `0` | Reset zoom (100 %) |
| `F` | Toggle fit-to-window |
| `R` | Rotate clockwise |
| `Shift + R` | Rotate counter-clockwise |
| `H` | Flip horizontal |
| `V` | Flip vertical |
| `Ctrl + O` | Open file |
| `Ctrl + Shift + O` | Open folder |
| `Esc` | Quit |

### Mouse

| Action | Behavior |
|---|---|
| **Scroll wheel** | Navigate between images |
| **Ctrl + Scroll** | Zoom in / out |
| **Click & drag** | Pan when zoomed in |

---

## 📁 Project Structure

```
Image-Viewer/
├── image_viewer.py    # Main application (RoundedButton widget + ImageViewer app)
├── requirements.txt   # Python dependencies
├── README.md          # This file
└── venv/              # Virtual environment (not tracked by Git)
```

---

## 🛠️ Tech Stack

- **tkinter** – GUI framework (standard library); canvas, scrollbars, menus
- **Pillow (PIL)** – Image loading, resizing (LANCZOS / NEAREST), and transformations
- **`RoundedButton`** – Custom canvas-based widget with hover, active, and toggle states

---