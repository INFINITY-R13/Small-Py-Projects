<div align="center">

# Today

**A thoughtfully minimal desktop to-do list.**

*Simplicity, focus, and craft — inspired by Things 3 and Apple design principles.*

---

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Tkinter](https://img.shields.io/badge/GUI-Tkinter%20(Standard%20Library)-0071E3?style=flat-square)](https://docs.python.org/3/library/tkinter.html)
[![Dependencies](https://img.shields.io/badge/Dependencies-Zero-1D1D1F?style=flat-square)](file:///Users/infinity/Documents/Python-learn/Small-Py-Projects/To-Do-List/todo_app.py)
[![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows%20%7C%20Linux-86868B?style=flat-square)](file:///Users/infinity/Documents/Python-learn/Small-Py-Projects/To-Do-List/README.md)

</div>

<br>

## Overview

**Today** is an elegant, distraction-free desktop to-do list crafted with Python's standard-library Tkinter. It pairs the calm, airy aesthetic of **Things 3** with modern desktop ergonomics: responsive trackpad scrolling, dual themes, segmented filter capsules, and inline editing.

No external packages. No account required. No telemetry. Your to-dos remain private on your device.

---

## Highlights

<table>
<tr>
<td width="50%">

### ✦ Minimalist Craft
Clean Apple system typography, subtle hairline borders, and calm neutral tones designed to keep your attention on your work, not the interface.

</td>
<td width="50%">

### ◐ Light & Dark Themes
Toggle smoothly between **Minimalist Clean Light** and **Sleek Modern Dark** mode. Your theme preference is preserved across app launches.

</td>
</tr>
<tr>
<td width="50%">

### ✎ Inline Editing
Double-click any to-do title or click the `✎` icon to edit text in place. Press <kbd>Return</kbd> to save or <kbd>Esc</kbd> to cancel.

</td>
<td width="50%">

### ◫ Segmented Filters
Seamlessly cycle between **All**, **Active**, and **Completed** views with Apple-style segmented capsule controls.

</td>
</tr>
<tr>
<td width="50%">

### ⚡︎ Native & Fluid
Custom cross-platform flat components ensure smooth mousewheel and trackpad scrolling across macOS, Windows, and Linux.

</td>
<td width="50%">

### 🛡 Safe Persistence
Atomic file operations protect against data loss on unexpected shutdowns, with automatic recovery backups on corrupted loads.

</td>
</tr>
</table>

---

## Quick Start

Ensure Python 3 is installed, then launch the app:

```bash
python3 todo_app.py
```

> [!NOTE]
> No `pip install` required. The application uses only Python standard library modules (`tkinter`, `json`, `pathlib`, `uuid`).

---

## Gestures & Shortcuts

| Action | Shortcut / Gesture | Description |
| :--- | :--- | :--- |
| **New To-Do** | <kbd>Return</kbd> or click `+ Add` | Creates a new task and keeps focus ready for the next one |
| **Complete To-Do** | Click checkbox | Toggles strikethrough in-place without jarring scroll jumps |
| **Edit To-Do** | **Double-click** or click `✎` | Opens an inline text field with existing title selected |
| **Save Edit** | <kbd>Return</kbd> or click away | Commits title changes and updates list layout |
| **Cancel Edit** | <kbd>Esc</kbd> | Reverts changes without modifying the task |
| **Delete To-Do** | Click `×` | Instantly removes the task |
| **Clear Completed** | Click `Clear completed` | Prompts confirmation and removes all finished tasks |
| **Toggle Theme** | Click `🌙 Dark` / `☀️ Light` | Switches palette instantly across the entire interface |

---

## Data & Storage

Your tasks are stored locally in a clean, human-readable JSON format beside the script:

```
To-Do-List/
├── todo_app.py     # Main application
├── tasks.json      # Local task storage & preferences
├── .gitignore      # Git exclusion rules
└── README.md       # Documentation
```

- **Storage File**: `tasks.json`
- **Format**: Standard UTF-8 JSON (emojis and international characters supported)
- **Atomic Writes**: Writes to a temporary buffer before atomic replacement, eliminating half-written file corruption.

---

## Design Details

- **Typography**: Apple SF / Helvetica typography hierarchy with deliberate optical sizing.
- **Color Systems**:
  - *Light Theme*: Airy off-white canvas (`#FBFBFD`), pure white card surfaces (`#FFFFFF`), subtle dividers (`#E5E5EA`), Apple blue accents (`#0071E3`).
  - *Dark Theme*: Elevated slate canvas (`#161618`), dark surfaces (`#212124`), borders (`#323236`), dark-mode blue accents (`#2997FF`).
- **Zero Aqua Quirks**: Custom `FlatButton` component ensures consistent flat geometry and hover feedback on macOS Aqua.

---

<div align="center">

*Designed with care for focused days.*

</div>
