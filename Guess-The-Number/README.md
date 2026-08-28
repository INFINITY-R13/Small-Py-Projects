# Guess the Number Game

A simple console-based number guessing game written in Python.

## Description

The computer randomly selects a number between **1 and 100**.  
Your goal is to guess the number. After each guess, the game tells you whether your guess is **too high** or **too low**.  

The game continues until you guess the correct number and then shows how many attempts you took.

## Requirements

- Python 3.6 or higher

No external libraries are needed (only the built-in `random` module is used).

## How to Run

1. Save the game code as `guess_number.py`
2. Open a terminal / command prompt
3. Navigate to the folder containing the file
4. Run the game:

```bash
python guess_number.py
```

## Example Gameplay

```
=== Guess the Number Game ===
I'm thinking of a number between 1 and 100.
Enter your guess: 50
Too low! Try again.
Enter your guess: 75
Too high! Try again.
Enter your guess: 63
🎉 Correct! You guessed it in 3 attempts.
```

## Features

- Random number generation between 1–100
- Input validation (handles non-number inputs gracefully)
- Attempt counter
- Clear high/low feedback
