# 🧮 Modern Python Scientific Calculator

A modern, desktop Scientific Calculator application built with Python and Tkinter, featuring a dark macOS-inspired theme, safe expression evaluation engine, calculation history drawer, and full physical keyboard support.

---

## ✨ Features

- **Dual Modes (Standard & Scientific)**:
  - **Standard View**: Clean 4-column layout for everyday arithmetic (`+`, `-`, `×`, `÷`, `%`, `±`, `⌫`, `AC`).
  - **Scientific View**: Expandable panel with trigonometry (`sin`, `cos`, `tan`, `asin`, `acos`, `atan`), logarithms (`log`, `ln`), powers (`x²`, `xʸ`), roots (`√x`, `∛x`), factorials (`n!`), absolute values (`|x|`), and reciprocal (`1/x`).
- **Angle Unit Switching**: Seamlessly toggle between **DEG** (Degrees) and **RAD** (Radians) with automatic precision correction.
- **Collapsible History Drawer**:
  - Automatically records previous calculations with timestamps.
  - Click on any saved entry to recall the formula or result directly back into the calculator.
  - Clear history with a single click.
- **Physical Keyboard Support**: Use your physical keyboard for digits, arithmetic operators, parentheses, backspace, and evaluation without touching the mouse.
- **Safe Math Evaluation Engine**: Built with Python's Abstract Syntax Tree (`ast`) module to safely evaluate complex expressions without `eval()` vulnerabilities.
- **Zero External Dependencies**: Works out-of-the-box on standard Python 3.

---

## 🚀 Quick Start

### 1. Launch Desktop GUI (Default)
```bash
python3 main.py
```

### 2. Interactive Terminal REPL (CLI Mode)
If you prefer calculating directly inside your terminal:
```bash
python3 main.py --cli
```

### 3. One-Liner Evaluation
Evaluate an expression directly from the command line:
```bash
python3 main.py --eval "sin(30) + sqrt(16) * 2"
# Output: 8.5
```

---

## ⌨️ Keyboard Shortcuts

| Key / Shortcut | Action |
| :--- | :--- |
| `0` - `9`, `.` | Insert numbers and decimal point |
| `+`, `-`, `*`, `/` | Insert arithmetic operators (`+`, `−`, `×`, `÷`) |
| `^` | Exponentiation (Power) |
| `%` | Percentage |
| `(`, `)` | Parentheses |
| `Enter` / `Return` | Calculate result (`=`) |
| `Backspace` | Delete last character (`⌫`) |
| `Escape` | Clear display (`AC`) |
| `Cmd + C` / `Ctrl + C` | Copy current display value to clipboard |
| `Cmd + H` / `Ctrl + H` | Toggle History drawer |

---

## 📁 Project Structure

```
Calculator/
├── calculator/
│   ├── __init__.py       # Package exports
│   ├── engine.py         # Safe AST-based math evaluator & formatting
│   ├── history.py        # Calculation history manager (with JSON persistence)
│   └── ui.py             # Modern Tkinter dark-mode GUI
├── tests/
│   ├── test_engine.py    # Math engine & edge-case unit tests
│   └── test_ui.py        # UI interaction & widget tests
├── main.py               # Application entry point (GUI / CLI)
└── README.md             # Documentation & guide
```

---

## 🧪 Running Tests

Run the complete test suite:
```bash
python3 -m unittest discover tests
```
