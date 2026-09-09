# Digital Clock 🕐

A simple digital clock application built with **Python** and **Tkinter**.

The clock displays the current local time in a 12-hour format with AM/PM and updates automatically every second. It features a black background with a bright cyan digital-style display.

## Features

* 🕐 Displays the current time
* ⏱️ Updates automatically every second
* 🌓 Uses 12-hour format with AM/PM
* 🎨 Black background with cyan text
* 🖥️ Simple and lightweight graphical interface
* 🚫 Non-resizable window
* 🐍 Built entirely with Python and Tkinter

## Project Structure

```text
Digital Clock/
│
├── digital_clock.py
└── README.md
```

### `digital_clock.py`

The main Python program that creates and runs the digital clock application.

### `README.md`

Documentation for the project, including setup instructions and usage information.

## Requirements

You need:

* Python 3.x
* Tkinter

Tkinter is included with most standard Python installations.

## How to Run

1. Download or clone the project.

2. Open a terminal or command prompt.

3. Navigate to the project folder:

```bash
cd "Digital Clock"
```

4. Run the Python file:

```bash
python digital_clock.py
```

On some systems, you may need to use:

```bash
python3 digital_clock.py
```

The Digital Clock window will open and display the current time.

## Time Format

The application uses the following format:

```text
HH:MM:SS AM/PM
```

For example:

```text
09:15:42 PM
```

The clock uses:

* `%I` → 12-hour format
* `%M` → Minutes
* `%S` → Seconds
* `%p` → AM/PM

## How It Works

The application uses Python's built-in `time.strftime()` function to retrieve and format the current system time.

The `update_time()` function updates the text displayed by the Tkinter label and schedules itself to run again after one second.

```python
def update_time():
    current_time = strftime('%I:%M:%S %p')
    label.config(text=current_time)
    root.after(1000, update_time)
```

The `root.after(1000, update_time)` statement tells Tkinter to call the function again after **1000 milliseconds**, or one second.

## Customization

You can easily customize the appearance of the clock.

### Change the Text Color

The current text color is cyan:

```python
foreground="#00E5FF"
```

You can replace it with another color, for example:

```python
foreground="lime"
```

### Change the Background

The current background is black:

```python
background="black"
```

You can change it to another color:

```python
background="white"
```

If you change the background, you may also want to change the text color.

### Change the Font Size

The current font is:

```python
font=('Courier New', 80, 'bold')
```

You can make the clock smaller:

```python
font=('Courier New', 50, 'bold')
```

or larger:

```python
font=('Courier New', 100, 'bold')
```

## Stopping the Clock

Close the Digital Clock window to stop the application.

## License

This project is free to use, modify, and learn from.