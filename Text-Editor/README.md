# ◈ Aura Text Editor

An **aesthetic, lightweight, distraction-free** code and text editor built with Python and modern Tkinter (Tk 9). Designed with a minimalist dark interface, vibrant syntax themes, synchronized line numbers, and keyboard-centric workflows.

---

## ✨ Features

- **🎨 Curated Modern Themes**:
  - **Tokyo Night** (default) — Dark cyberpunk deep indigo
  - **Catppuccin Mocha** — Warm pastel dark palette
  - **Dracula** — High contrast gothic theme
  - **Nord** — Arctic, north-bluish clean theme
  - **One Dark** — Iconic Atom/VS Code dark theme
  - **Catppuccin Latte** — Soft, clean light mode
  - *Live switching without restarting the app!*

- **⚡ Multi-Language Syntax Highlighting**:
  - High-performance regex token engine with binary search line-index caching.
  - Supports **Python**, **Markdown**, **JSON**, **JavaScript/TypeScript**, **HTML**, **CSS**, **Shell/Bash**, **SQL**, and **Plain Text**.

- **📑 Multi-Tab Interface**:
  - Flat aesthetic tabs with file-type icons (🐍, 📝, ⚙️, 🌐, etc.).
  - Unsaved change indicator dot (`●`).
  - Close button with hover animation and middle-click support.
  - Welcome landing screen when all tabs are closed.

- **📁 Collapsible File Explorer (Sidebar)**:
  - Directory tree navigation with file and folder icons.
  - Single/double-click to open or switch between files.
  - Folder chooser dialog to open any workspace directory.
  - Toggle sidebar visibility (`⌘B` or header button).

- **🔍 Modern Find & Replace**:
  - Docked search bar with real-time match counter (`3 of 12 matches`).
  - Highlighting for all matching occurrences and active jump target.
  - Previous (`Shift+Enter`) and Next (`Enter`) navigation.
  - Case-sensitivity toggle (`Aa`).
  - Single replace and Replace All.

- **🧠 Smart Editing**:
  - Synchronized line numbers gutter that dynamically resizes and highlights the current active line in bold.
  - Subtle current-line background tint.
  - Matching bracket pair highlighting `()`, `[]`, `{}`.
  - Auto-closing bracket pairs and quotes with paired backspace deletion.
  - Smart indentation on `Enter` (preserves indentation and adds 4 spaces after `:`, `{`, `[`, `(`).
  - Multi-line `Tab` indent and `Shift+Tab` unindent.
  - Comment toggling (`⌘/` or `Ctrl+/`).
  - Line duplication (`⌘D` or `Ctrl+D`).
  - Move lines up/down (`Alt+Up`, `Alt+Down`).
  - Dynamic font zoom (`⌘=` / `⌘-` / `⌘0`).

- **📊 Sleek Status Bar**:
  - Cursor coordinates (`Ln 14, Col 22`) and selection character count.
  - Real-time word, line, and character metrics.
  - File encoding (`UTF-8`) and indentation (`Spaces: 4`).
  - Interactive clickable pills for switching syntax language or theme on the fly.

- **🧘 Zen Mode (Distraction-Free)**:
  - Press `F11` to toggle Zen Mode: hides all headers, sidebars, and status bars for focused typing. Press `Esc` or `F11` to exit.

---

## 🚀 Quick Start

Run the editor directly using Python 3:

```bash
python3 main.py
```

Or open a file directly:

```bash
python3 main.py demo.py
```

Zero external dependencies required — runs out-of-the-box on standard Python 3 with Tkinter!

---

## ⌨️ Keyboard Shortcuts

| Shortcut (macOS / Linux / Windows) | Action |
| :--- | :--- |
| `⌘N` / `Ctrl+N` | New Tab / File |
| `⌘O` / `Ctrl+O` | Open File |
| `⌘Shift+O` / `Ctrl+Shift+O` | Open Folder |
| `⌘S` / `Ctrl+S` | Save File |
| `⌘Shift+S` / `Ctrl+Shift+S` | Save File As... |
| `⌘W` / `Ctrl+W` | Close Tab |
| `⌘F` / `Ctrl+F` | Find & Replace |
| `⌘B` / `Ctrl+B` | Toggle File Explorer Sidebar |
| `⌘/` / `Ctrl+/` | Toggle Line Comment (`#`) |
| `⌘D` / `Ctrl+D` | Duplicate Current Line |
| `Alt+Up` / `Alt+Down` | Move Current Line Up / Down |
| `Tab` / `Shift+Tab` | Indent / Unindent Selection |
| `⌘=` / `⌘-` / `⌘0` | Zoom In / Zoom Out / Reset Font Zoom |
| `F11` | Toggle Zen Mode (Distraction-free) |
| `Esc` | Close Find Bar / Exit Zen Mode |

---

## 📂 Project Architecture

```
Text-Editor/
├── main.py              # Application entrypoint & CLI argument handler
├── demo.py              # Sample code file demonstrating syntax highlighting
├── README.md            # Documentation & shortcuts guide
└── editor/
    ├── __init__.py      # Package export
    ├── app.py           # Main application window, layouts, menus, shortcuts
    ├── code_editor.py   # Code editor widget, line gutter, auto-indent, brackets
    ├── find_replace.py  # Floating/docked find & replace toolbar
    ├── sidebar.py       # Collapsible file explorer with folder tree
    ├── status_bar.py    # Metric counters, language selector, theme picker
    ├── syntax.py        # Fast regex syntax tokenizer with offset caching
    ├── tab_bar.py       # Tab bar with file icons, close buttons, dirty dots
    └── themes.py        # Color palettes (Tokyo Night, Catppuccin, Dracula, Nord, One Dark, Latte)
```
