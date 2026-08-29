# Fibonacci Sequence Generator

A simple Python program that generates the first **n** numbers of the Fibonacci sequence, with a maximum limit of **n = 13**.

## Fibonacci Sequence
The sequence starts with:
```
0, 1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144
```

## Features
- Generates the first `n` Fibonacci numbers
- Maximum allowed value of `n` is **13**
- Input validation (rejects values outside 1–13)
- Handles invalid (non-integer) inputs gracefully

## How to Run

1. Make sure you have Python 3 installed.
2. Save the code as `fibonacci.py`.
3. Run the program:

```bash
python fibonacci.py
```

4. Enter a number between **1 and 13** when prompted.

### Example

```
Enter how many Fibonacci numbers you want (1 to 13): 8
First 8 Fibonacci numbers:
[0, 1, 1, 2, 3, 5, 8, 13]
```

### Invalid Input Examples

```
Enter how many Fibonacci numbers you want (1 to 13): 15
Error: n must be between 1 and 13.
```

```
Enter how many Fibonacci numbers you want (1 to 13): abc
Invalid input. Please enter an integer.
```

## Requirements
- Python 3.x
- No external libraries required

## License
This project is free to use and modify.