# Bitmap

A simple Python program that displays a user-entered message inside an ASCII-art bitmap.

## Description

**Bitmap** takes a message from the user and uses it to replace the non-space characters in a predefined bitmap pattern.

The message is repeated as necessary using the modulo operator, creating a text-based visual effect.

## How It Works

1. The program stores an ASCII-art bitmap in the `bitmap` variable.
2. The user enters a message.
3. If the message is empty, the program exits.
4. The bitmap is processed line by line.
5. Spaces in the bitmap remain unchanged.
6. Other characters are replaced with characters from the user's message.
7. The `%` operator makes the message repeat when necessary.

## Example

If the user enters:

```text
infinity
```

The program produces an output similar to:

```text
 nfinityinfinityinfinityinfinityinfinity...
    nityinfinityin   i  inf ni  i      ...
   inityinfinityinfinity nf ni y  f ...
```

The exact appearance depends on the bitmap pattern.

## Requirements

* Python 3.x
* No external libraries are required.

## How to Run

From the project directory, run:

```bash
python3 main.py
```

Then enter the message you want to display.

## Code Concepts

This project demonstrates:

* Variables
* Strings
* User input with `input()`
* `if` statements
* `for` loops
* `enumerate()`
* `splitlines()`
* String indexing
* The modulo (`%`) operator
* `sys.exit()`
* ASCII art

## Project Structure

```text
Bitmap/
└── main.py
```

## Learning Purpose

This project is useful for practicing **loops, string manipulation, indexing, and the modulo operator** while creating a simple ASCII-art effect.

## Reference

Inspired by the **Bitmap Message** project from *The Big Book of Small Python Projects* by Al Sweigart.
