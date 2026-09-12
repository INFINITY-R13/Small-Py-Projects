# Caesar Cipher

A simple **Caesar Cipher** application built with Python and Tkinter. It allows users to encrypt and decrypt messages using a customizable shift key through an easy-to-use graphical interface.

## Features

* 🔐 Encrypt messages using a Caesar Cipher
* 🔓 Decrypt encrypted messages
* 🔢 Supports keys from `0` to `25`
* 📝 Supports letters, spaces, numbers, and punctuation
* 📋 Copy encrypted/decrypted results to the clipboard
* 🧹 Clear message, key, and result fields
* ⚠️ Input validation for invalid or missing keys/messages
* 🖥️ Simple Tkinter-based graphical user interface

## How Caesar Cipher Works

The Caesar Cipher is a substitution cipher where each letter in the message is shifted by a fixed number of positions in the alphabet.

For example, with a key of `3`:

```text
A → D
B → E
C → F
...
X → A
Y → B
Z → C
```

### Example

Original message:

```text
HELLO WORLD
```

Key:

```text
3
```

Encrypted message:

```text
KHOOR ZRUOG
```

Decrypting `KHOOR ZRUOG` with the same key produces:

```text
HELLO WORLD
```

## Requirements

* Python 3.x
* Tkinter

Tkinter is included with most standard Python installations.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/Small-Py-Projects.git
```

2. Navigate to the project directory:

```bash
cd Small-Py-Projects/Caesar-Cipher
```

3. Run the program:

```bash
python main.py
```

## Usage

1. Launch the application.
2. Select **Encrypt** or **Decrypt**.
3. Enter a key between `0` and `25`.
4. Enter your message.
5. Click **Process**.
6. The encrypted or decrypted message will appear in the **Result** section.
7. Use **Copy Result** to copy the result to your clipboard.
8. Use **Clear** to reset the fields.

## Project Structure

```text
Caesar-Cipher/
│
├── main.py
└── README.md
```

## Technologies Used

* **Python**
* **Tkinter**

## Learning Objectives

This project demonstrates:

* String manipulation
* Functions
* Loops
* Conditional statements
* Modular arithmetic
* Input validation
* Exception-free GUI input handling
* Tkinter widgets and layouts
* Clipboard operations

## Disclaimer

The Caesar Cipher is a simple historical encryption technique and is **not suitable for protecting sensitive or confidential information**. It is primarily useful for learning the fundamentals of cryptography and programming.

## License

This project is open-source and available for educational purposes.
