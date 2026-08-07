# Caesar Cipher

A simple Python implementation of the classic **Caesar Cipher** encryption technique. This program allows users to encrypt or decrypt messages using a shift key.

## Features

- Encrypt text using a Caesar Cipher.
- Decrypt previously encrypted text.
- User-defined shift key (0–25).
- Preserves spaces, numbers, and punctuation.
- Validates user input for both mode and key.

## How It Works

The Caesar Cipher is a substitution cipher where each letter in the message is shifted by a fixed number of positions in the alphabet.

For example, using a key of **3**:

| Original | Encrypted |
|----------|-----------|
| A | D |
| B | E |
| C | F |
| X | A |
| Y | B |
| Z | C |

The program uses modulo (`%`) arithmetic to wrap around the alphabet when the shift goes past **Z**.

## Requirements

- Python 3.x

No external libraries are required.

## Running the Program

Run the program using:

```bash
python main.py
```

or


## Example

```
This is a caesar cipher program.

Do you want to encrypt or decrypt?
encrypt

Please enter key from 0 - 25.
3

Enter the message to encrypt:
HELLO WORLD

KHOOR ZRUOG
```

### Decryption Example

```
Do you want to encrypt or decrypt?
decrypt

Please enter key from 0 - 25.
3

Enter the message to decrypt:
KHOOR ZRUOG

HELLO WORLD
```

## Project Structure

```
.
├── main.py
└── README.md
```

## Concepts Practiced

This project demonstrates:

- Variables and constants
- Strings
- String indexing
- Loops (`while` and `for`)
- Conditional statements (`if`, `elif`, `else`)
- Input validation
- Functions like `find()`, `isdigit()`, and `startswith()`
- Modulo (`%`) operator
- Basic encryption algorithms

## Limitations

- Supports only English uppercase letters (`A–Z`).
- Converts all input to uppercase before processing.
- Does not preserve the original letter casing.

## Future Improvements

- Preserve uppercase and lowercase letters.
- Support custom alphabets.
- Allow repeated encryption without restarting the program.
- Add file encryption and decryption.
- Refactor the code into reusable functions.

## License

This project is open source and available under the MIT License.