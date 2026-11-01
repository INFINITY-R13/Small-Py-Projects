# 🌸 Bloom — Minimalist Habit Tracker

<p align="center">
  <img src="https://img.shields.io/badge/Design-Apple%20Minimalist-FF5288?style=for-the-badge&logoColor=white" />
  <img src="https://img.shields.io/badge/Theme-Blush%20Pink-FCE5ED?style=for-the-badge&labelColor=FF5288&color=FCE5ED" />
  <img src="https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge" />
</p>

An aesthetic, minimalist habit tracking desktop application built in Python. Designed with Apple Human Interface Guidelines in mind, **Bloom** features clean typography, generous white space, soft hairline borders, and an elegant pink pastel palette (Blush Light & Midnight Rose Dark).

---

## ✨ Features

- **Apple-Inspired Design Language**:
  - Smooth rounded corners (`corner_radius=18`), subtle hairline borders, and generous padding.
  - Native macOS typography using system fonts (`Helvetica Neue` / `SF Pro`).
  - Curated aesthetic color palette: soft porcelain blush backgrounds, crisp card surfaces, and vibrant Apple-style rose pink accents (`#FF5288`).

- **⭕️ Dynamic Progress Ring**:
  - Anti-aliased circular progress ring (inspired by Apple Fitness / Activity rings) rendered via supersampled Pillow graphics.
  - Live percentage and completed count indicators with motivational status messages.

- **📅 Interactive 7-Day Week Calendar Strip**:
  - Weekly view bar showing each day of the week with status indicator dots.
  - Click any day to inspect past completions or log retrospective habits.
  - Quick "Jump to Today" shortcut when reviewing historical records.

- **🔥 Visual Streaks & Mini 7-Day History Dots**:
  - Each habit card displays current streak count with a flame badge (`🔥 7d streak`).
  - Row of 7 mini status dots indicating daily consistency at a glance.
  - Smooth circular checkmark toggle with instant visual feedback.

- **🗂️ Routine Filter Tabs**:
  - Quickly filter habits by time of day: `All`, `Morning ☀️`, `Afternoon 🌤️`, `Evening 🌙`, or `Completed ✓`.

- **📊 Insights & Analytics Sheet**:
  - Apple Health-style modal with key metrics (Active Streak, Best Record, Total Completions).
  - 7-day completion vertical bar chart.
  - Habit adherence scores for the past 30 days.
  - Inspiring minimalist quotes on daily discipline and mindfulness.

- **🌓 Dual Theme Support**:
  - **Blush Light**: Soft porcelain blush with vibrant rose accents.
  - **Midnight Rose**: Deep obsidian berry with luminous neon rose highlights.

- **💾 JSON Persistence & Starter Habits**:
  - Auto-saves all habits and logs locally to `data/habits.json`.
  - Comes pre-populated with aesthetic starter habits (Hydration, Meditation, Movement, Reading, Matcha, Journaling).

- **⚡️ Built-in CLI Mode**:
  - Run `--cli` for interactive terminal tracking or `--list` / `--stats` for quick shell checks.

---

## 📁 Project Structure

```
Habit-Tracker/
├── .venv/                      # Python virtual environment
├── .gitignore                  # Git ignore rules for Python & macOS
├── README.md                   # Documentation
├── requirements.txt            # Project dependencies
├── main.py                     # Main application entry point
├── app/
│   ├── __init__.py
│   ├── cli.py                  # ANSI colored interactive CLI
│   ├── config.py               # Color palettes, typography, curated emojis & quotes
│   ├── models.py               # Habit data model & streak calculation logic
│   ├── storage.py              # JSON storage persistence & aggregate statistics
│   ├── utils/
│   │   ├── __init__.py
│   │   └── graphics.py         # Pillow anti-aliased rings, checkmarks & charts
│   └── views/
│       ├── __init__.py
│       ├── main_window.py      # Primary desktop GUI window
│       ├── habit_card.py       # Reusable Apple-style habit card component
│       ├── add_habit_modal.py  # Modal dialog to create & edit habits
│       └── stats_modal.py      # Analytics and insights sheet
└── data/
    └── habits.json             # Local JSON data store
```

---

## 🚀 Getting Started

### 1. Clone or Open the Repository

```bash
cd /path/to/Habit-Tracker
```

### 2. Set Up Virtual Environment (`venv`)

Create and activate a virtual environment:

```bash
# Create virtual environment
python3 -m venv .venv

# Activate on macOS / Linux:
source .venv/bin/activate

# (Or on Windows:)
# .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 💻 Running the App

### Launch Desktop GUI

Simply run:

```bash
python main.py
```

*or using the venv python directly:*

```bash
.venv/bin/python3 main.py
```

### Command Line Options

Bloom also includes convenient CLI commands for terminal workflows:

| Command | Description |
| :--- | :--- |
| `python main.py` | Launch full Apple-style Desktop GUI |
| `python main.py --list` | Print today's habit checklist in terminal |
| `python main.py --stats` | View streak records and completion totals |
| `python main.py --cli` | Interactive terminal habit tracker |
| `python main.py --reset` | Reset habits back to default starter pack |

---

## 🎨 Color Palette Reference

| Swatch | Color Name | Hex Code | Role |
| :---: | :--- | :--- | :--- |
| 🌸 | **Rose Pink** | `#FF5288` | Primary accent, completion buttons, progress arcs |
| 🪷 | **Soft Blush** | `#FDEBF1` | Card badges, icon containers, hover fills |
| 🥛 | **Porcelain Blush** | `#FAF6F8` | Light mode window background |
| ⚪️ | **Pure Card** | `#FFFFFF` | Light mode card surface with subtle hairline border |
| 🍇 | **Midnight Berry** | `#141013` | Dark mode window background |
| 🫐 | **Dark Mauve** | `#221A20` | Dark mode card surface |
| 🖤 | **Apple Charcoal** | `#1D191B` | High-contrast primary typography |

---