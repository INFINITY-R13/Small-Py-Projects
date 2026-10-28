# 📒 Contact Book

<div align="center">

![Python Version](https://img.shields.io/badge/Python-3.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue?style=for-the-badge&logo=python&logoColor=white)
![GUI](https://img.shields.io/badge/GUI-Tkinter%209.0-slate?style=for-the-badge)
![Database](https://img.shields.io/badge/Database-SQLite3-003B57?style=for-the-badge&logo=sqlite&logoColor=white)
![Theme](https://img.shields.io/badge/Theme-Aesthetic%20Light%20Grey-lightgrey?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-emerald?style=for-the-badge)

<p align="center">
  A modern, aesthetic desktop contact manager designed with a clean light grey aesthetic, instant real-time search, birthday countdowns, Instagram integration, and SQLite persistence.
</p>

</div>

---

## 🌟 Highlights

- 🎨 **Aesthetic Light Grey Palette**: Thoughtfully designed with a soft light-grey background (`#F1F3F5`), crisp white content cards (`#FFFFFF`), subtle slate typography (`#0F172A`), and pastel initial avatars.
- 📋 **Comprehensive Contact Info**:
  - **Full Name**
  - **Phone Number** (with quick copy button)
  - **Email Address** (with one-click mail composer)
  - **Birth Date** (with automatic age calculation and countdown)
  - **Instagram Handle** (with direct one-click browser profile launcher)
  - **Category / Group** (*Friends, Family, Work, VIP, General*)
  - **Notes & Bio**
- ⚡ **Instant Real-Time Search**: Search on-the-fly across names, numbers, email addresses, Instagram handles, and notes.
- 🎂 **Smart Birthday Tracker**:
  - Highlights contacts whose birthdays are coming up within 30 days or today.
  - Displays age turning, days remaining, and celebratory badges.
- ⭐ **Favorites System**: Quick one-click star toggle directly from the list or detail view.
- 🗂️ **Categories & Sorting**: Filter by group and sort by Name (A-Z / Z-A), Recently Added, or Upcoming Birthday.
- 📤 **Data Export & Import**: Full backup and restore in both **CSV** and **JSON** formats.
- 🔒 **Zero External Dependencies**: Built entirely with Python's standard library (`tkinter`, `sqlite3`, `json`, `csv`, `webbrowser`). No fragile pip packages required!
- 💾 **Reliable SQLite Storage**: Automatic database creation, indexed search, and lively sample contacts on first launch.

---

## 🖥️ UI Overview

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ 📒 Contact Book      🔍 [ Search name, phone, email, @insta... ]   ⇅ Data ➕ │
├──────────────────────────────┬───────────────────────────────────────────────┤
│ [All (5)] [⭐ Favs] [🎂 Bdays]│  (Avatar)  Elena Vance ★                      │
│ Group: [ All ▾ ] Sort: [A-Z▾]│            [ Friends ]        [✏️ Edit] [🗑️]   │
├──────────────────────────────┼───────────────────────────────────────────────┤
│ [EV] Elena Vance         ★   │  [📞 Copy] [✉️ Email] [📸 @elena_vance]       │
│      +1 (555) 234-5678       │  ──────────────────────────────────────────── │
│ ───────────────────────────  │  🎂 In 5 days (turning 28)                    │
│ [LG] Liam Gallagher          │     Born March 15, 1997 • Current age: 27     │
│      +44 7911 123456         │  ──────────────────────────────────────────── │
│ ───────────────────────────  │  📞 Phone:  +1 (555) 234-5678          [Copy] │
│ [SR] Sophia Rossi        ★   │  ✉️ Email:  elena.vance@designcraft.io [Copy] │
│      sophia.rossi@milan-art  │  📸 Insta:  @elena_vance       [Open Profile ↗]│
│ ───────────────────────────  │  🎂 Birth:  1997-03-15                        │
│ [DC] David Chen              │  ──────────────────────────────────────────── │
│      dchen@berkeley.edu      │  📝 Notes & Bio:                              │
│ ───────────────────────────  │     Lead UI/UX designer. Loves coffee & art.  │
│ 5 contacts shown • 5 total   │                                               │
└──────────────────────────────┴───────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### 1. Direct Run (No setup needed)

The application has zero third-party dependencies:

```bash
# Clone or navigate to the directory
cd Contact-Book

# Run the app
python3 app.py
```

*(You can also run `python3 main.py` as an alias).*

---

### 2. Run with Virtual Environment (Optional)

If you prefer isolating your environment:

```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
# On macOS / Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Run the app
python app.py
```

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
| :--- | :--- |
| <kbd>Cmd</kbd> + <kbd>F</kbd> / <kbd>Ctrl</kbd> + <kbd>F</kbd> | Focus the Search input |
| <kbd>Cmd</kbd> + <kbd>N</kbd> / <kbd>Ctrl</kbd> + <kbd>N</kbd> | Open New Contact dialog |
| <kbd>Return</kbd> / <kbd>Enter</kbd> | Save contact in dialog |
| <kbd>Esc</kbd> | Close active dialog |
| <kbd>Cmd</kbd> + <kbd>Backspace</kbd> | Delete selected contact |

---

## 📂 Project Structure

```
Contact-Book/
├── app.py                  # Main application entry point & high-DPI configuration
├── main.py                 # Convenience alias for app.py
├── database.py             # SQLite database layer with auto-seeding & indexes
├── models.py               # Contact dataclass, avatar theme, & birthday calculations
├── test_app.py             # Comprehensive automated test suite
├── requirements.txt        # Package documentation & optional tools
├── .gitignore              # Complete Python and OS gitignore rules
├── README.md               # Aesthetic project documentation
│
├── ui/                     # UI Layer
│   ├── __init__.py
│   ├── theme.py            # Light grey color palette, fonts, & styles
│   ├── components.py       # AvatarCanvas, ModernButton, Toast notifications
│   ├── contact_dialog.py   # Add / Edit modal window with real-time validation
│   └── main_window.py      # Two-pane master-detail desktop window
│
└── utils/                  # Utility Layer
    ├── __init__.py
    ├── validators.py       # Name, phone, email, date, & Instagram validators
    └── exporters.py        # CSV & JSON import and export handlers
```

---

## 🧪 Running Tests

The project includes unit tests covering data models, validation rules, birthday calculations, SQLite CRUD, and CSV/JSON export/import:

```bash
python3 -m unittest test_app.py
```

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for details.
