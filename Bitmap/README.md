# Bitmap

A simple **Tkinter GUI application** that displays a user-entered message inside a predefined ASCII bitmap pattern.

This project is a graphical version of the classic Bitmap program, where characters from the entered message are repeatedly placed wherever the bitmap contains a `*`.

## Features

* 🖥️ Simple graphical user interface built with Tkinter
* ✍️ Custom message input
* 🖼️ Generates an ASCII bitmap using the entered message
* 🔁 Repeats the message automatically across the bitmap
* ▶️ Generate button
* 🧹 Clear button
* ❌ Exit button
* ⌨️ Press **Enter** to generate the bitmap
* 📜 Scrollable output area
* 💻 Uses a monospaced font for proper bitmap alignment

## How It Works

The application contains a predefined bitmap pattern made from spaces and `*` characters.

For every character in the bitmap:

* If the character is a space, a space is displayed.
* If the character is `*`, a character from the user's message is displayed.
* When the end of the message is reached, the program starts from the beginning again.

For example, if the message is:

```text
HELLO
```

the characters will be repeatedly placed across the bitmap:

```text
H E L L O H E L L O ...
```

This creates a text-filled ASCII image.

## Requirements

* Python 3.x
* Tkinter

Tkinter is included with most standard Python installations.

## How to Run

1. Clone the repository:

```bash
git clone https://github.com/your-username/Small-Py-Projects.git
```

2. Navigate to the Bitmap project:

```bash
cd Small-Py-Projects/Bitmap
```

3. Run the program:

```bash
python main.py
```

On some systems, you may need:

```bash
python3 main.py
```

## Usage

1. Launch the application.
2. Enter a message in the input field.
3. Click **Generate** or press **Enter**.
4. The bitmap will be displayed in the output area.
5. Click **Clear** to remove the current message and output.
6. Click **Exit** to close the application.

## Example

Input:

```text
PYTHON
```

The program uses the characters from `PYTHON` repeatedly wherever the bitmap contains a `*`.

The result is an ASCII-art pattern filled with the message.

## Project Structure

```text
Bitmap/
├── main.py
└── README.md
```

## Concepts Used

This project demonstrates several Python and GUI programming concepts:

* `tkinter`
* Functions
* Loops
* String manipulation
* String indexing
* Modulo operator (`%`)
* Event handling
* Widgets
* Text areas
* Scrollbars
* Message boxes

## Learning Goals

This project is useful for learning how to:

* Build a basic GUI with Tkinter
* Handle user input
* Respond to button clicks
* Work with multiline strings
* Manipulate strings character by character
* Connect Python logic to GUI events
* Display formatted text in a GUI

## License

This project is intended for learning and educational purposes.
