# Slate — Monochrome Notes App

A calm, minimalist desktop notes application built with Python and **PySide6**, crafted around a curated monochrome grey aesthetic with one-click switching between **Charcoal Slate** (dark grey) and **Ash Grey** (light grey).

## Features

- **Dual Monochrome Grey Themes** — Matte **Charcoal** (`#202226`) by default, with an instant toggle (`Cmd+Shift+T`) to soft **Ash Grey** (`#F4F5F7`).
- **Three-Pane Editorial Layout** — Navigation rail (`All Notes`, `Pinned`, `Trash`, dynamic `#tags`), custom-painted rounded note cards with live search, and a clean writing canvas.
- **Markdown Native (`Write` · `Split` · `Preview`)** — Subtle grey-hierarchy syntax highlighting while writing, paired with live rendered Markdown preview (headings, tables, fenced code blocks, quotes, and checklists) plus a quiet formatting bar.
- **Tags & Instant Search** — Add interactive `#tag` chips inline, filter by tag in the sidebar, and search across titles, note bodies, and `#tags`.
- **Zen Focus Mode** — Collapse sidebars (`Cmd+\`) to center your writing column for distraction-free focus.
- **Safe Trash & Local Persistence** — Debounced atomic JSON autosave (`data/notes.json`), soft-delete to `Trash` with `Restore` / `Empty Trash`, and one-click `.md` / `.txt` export.

## Monochrome Palette

| Surface | Charcoal (Dark Grey) | Ash (Light Grey) |
| --- | --- | --- |
| Sidebar Rail | `#161719` | `#E4E6EA` |
| Note Index | `#1B1D20` | `#ECEEF1` |
| Editorial Canvas | `#202226` | `#F4F5F7` |
| Active Card / Input | `#2D3138` / `#26292E` | `#DCDFE6` / `#E7E9ED` |
| Primary Text | `#E6E8EC` | `#212429` |

## Project Structure

```text
Notes-App/
├── main.py                  # Application entrypoint
├── requirements.txt         # Runtime dependencies (PySide6, markdown)
├── .gitignore               # Ignores .venv, caches, macOS files, and local data/
├── README.md
├── slate/
│   ├── __init__.py
│   ├── app.py               # MainWindow orchestration, autosave, shortcuts, export
│   ├── models.py            # Note dataclass, tags normalization, excerpts, search
│   ├── storage.py           # Atomic JSON persistence & initial welcome notes
│   ├── themes.py            # Charcoal & Ash grey tokens, QSS, and Markdown CSS
│   ├── icons.py             # High-DPI theme-tinted SVG icon renderer
│   ├── highlighter.py       # Monochrome Markdown syntax highlighter
│   └── widgets/
│       ├── sidebar.py       # Left navigation rail & tag list
│       ├── note_list.py     # Search bar & custom QPainter note card delegate
│       ├── editor_pane.py   # Toolbar, title, tags, editor, and Markdown preview
│       └── dialogs.py       # Shortcuts & confirmation modals
└── tests/
    └── test_notes.py        # Model, storage, and offscreen Qt UI smoke tests
```

## Setup & Usage

1. **Create and activate the virtual environment**:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Launch Slate**:

   ```bash
   python main.py
   ```

   *(Note: User notes and UI preferences are stored locally in `data/`, which is excluded by `.gitignore`.)*

## Running Tests

Run the unit and offscreen Qt UI smoke tests inside `.venv`:

```bash
.venv/bin/python -m unittest discover -s tests -v
```

## Keyboard Shortcuts

*(Use `Ctrl` instead of `Cmd` on Windows/Linux.)*

| Action | Shortcut |
| --- | --- |
| New Note | `Cmd + N` |
| Search Notes | `Cmd + F` |
| Pin / Unpin Note | `Cmd + Shift + P` |
| Toggle Charcoal / Ash Theme | `Cmd + Shift + T` |
| Write / Split / Preview Mode | `Cmd + 1` / `Cmd + 2` / `Cmd + 3` |
| Toggle Zen Focus Mode | `Cmd + \` |
| Export Note (`.md` / `.txt`) | `Cmd + E` |
| Move Note to Trash | `Cmd + Backspace` |
