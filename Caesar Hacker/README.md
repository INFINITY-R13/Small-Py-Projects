# Caesar Hacker

A simple Python program that **brute-forces a Caesar cipher** by trying every possible key from `0` to `25`.

Instead of knowing the encryption key beforehand, the program decrypts the message using every possible key and displays all the results. You can then identify the correct plaintext by looking for the meaningful output.

## How It Works

A Caesar cipher shifts each letter of the alphabet by a fixed number of positions.

For example, with a key of `3`:

```text
A → D
B → E
C → F
```

To decrypt, the program shifts the letters in the opposite direction.

The Caesar Hacker tries all 26 possible keys:

```text
Key #0
Key #1
Key #2
...
Key #25
```

One of the results should reveal the original message.

## Example

### Input

```text
L NQRZ WKDW
```

### Output

```text
Key #0: L NQRZ WKDW
Key #1: K MPQY VJCV
Key #2: J LOPX UIBU
Key #3: I KNOW THAT
...
```

The meaningful result is:

```text
Key #3: I KNOW THAT
```

Therefore, the encryption key was **3**.

## Features

* Tries all 26 Caesar cipher keys.
* Works with uppercase letters.
* Preserves spaces and other characters.
* Uses f-strings for modern Python formatting.
* Simple command-line interface.


## Requirements

* Python 3.x

No external libraries are required.

## How to Run

1. Make sure Python 3 is installed.
2. Open a terminal in the project directory.
3. Run:

```bash
python3 main.py
```

4. Enter an encrypted Caesar cipher message.
5. Check the output for the meaningful decrypted message.

## Concepts Practiced

This project helps practice:

* `for` loops
* Nested loops
* `if` / `else` statements
* Strings
* String indexing
* `str.find()`
* User input
* The modulo-style wraparound logic
* f-strings
* Brute-force techniques

## Limitations

This program is specifically designed for the basic Caesar cipher using the 26 uppercase English letters.

It does not automatically determine which output is correct. The user must inspect the results and identify the meaningful plaintext.

## License

This project is for learning and educational purposes.