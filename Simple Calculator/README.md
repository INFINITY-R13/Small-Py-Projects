# 🧮 Simple Calculator

A simple desktop calculator application built with **Python** and **Tkinter**.

This project is part of the **Small Py Projects** collection and is designed to demonstrate the basics of building a graphical user interface (GUI) in Python.

## 📌 Features

* Addition `+`
* Subtraction `-`
* Multiplication `*`
* Division `/`
* Decimal numbers
* Clear button
* Error handling for invalid expressions
* Simple and easy-to-use graphical interface

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** - Python's standard GUI library

## 📂 Project Structure

```text
Simple Calculator/
├── main.py
└── README.md
```

### `main.py`

Contains the complete source code for the calculator application, including:

* GUI window creation
* Calculator display
* Number and operator buttons
* Calculation logic
* Clear functionality
* Basic error handling

## 🚀 Getting Started

### Prerequisites

Make sure **Python 3** is installed on your system.

You can check your Python version using:

```bash
python --version
```

On some systems, you may need:

```bash
python3 --version
```

### ▶️ Run the Calculator

Navigate to the project directory:

```bash
cd "Simple Calculator"
```

Then run:

```bash
python main.py
```

Or:

```bash
python3 main.py
```

The calculator window should open.

## 🖥️ Usage

Use the buttons on the calculator to enter an expression.

For example:

```text
7 + 3 =
```

The calculator will display:

```text
10
```

Other examples:

```text
10 - 4 = 6
5 * 8 = 40
20 / 4 = 5
```

You can use the **Clear** button to reset the calculator display.

## 📖 What I Learned

This project demonstrates several fundamental Python concepts:

* Creating a GUI using Tkinter
* Creating and configuring Tkinter widgets
* Using functions to handle button events
* Using loops to generate GUI elements
* Working with lambda functions
* Handling exceptions with `try` / `except`
* Organizing a small Python project

## ⚠️ Note

The calculator uses Python's `eval()` function to evaluate mathematical expressions. This is convenient for a small learning project, but `eval()` should not be used with arbitrary or untrusted input in production applications.

## 🔮 Future Improvements

Some possible improvements for this project are:

* [ ] Add keyboard support
* [ ] Add percentage `%` functionality
* [ ] Add `+/-` functionality
* [ ] Add parentheses
* [ ] Add backspace functionality
* [ ] Add calculation history
* [ ] Improve the user interface
* [ ] Add a dark mode
* [ ] Replace `eval()` with a safer expression parser

## 📄 License

This project is open source and available for learning and personal use.

---

**Part of the `Small-Py-Projects` collection. 🐍**
