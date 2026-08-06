# 🥯 Bagels

A simple command-line deductive logic game written in Python. The computer generates a secret number with unique digits, and your goal is to guess it using the clues provided after each attempt.

---

## 📖 About

Bagels is a number guessing game where the player must deduce a randomly generated number based on logical clues.

After each guess, the game provides one of the following clues:

- **Fermi** – A digit is correct and in the correct position.
- **Pico** – A digit is correct but in the wrong position.
- **Bagels** – None of the digits are correct.

The game continues until the player guesses the secret number or runs out of attempts.

---

## 🎮 How to Play

1. Run the program.
2. The computer generates a secret **3-digit number** with **no repeated digits**.
3. Enter your guesses one at a time.
4. Use the clues to determine the correct number.
5. Guess the number within **10 attempts** to win.

### Example

**Secret Number (hidden):**

```
248
```

**Player Guess:**

```
843
```

**Output:**

```
Fermi Pico
```

Explanation:

- **Fermi** → `4` is correct and in the correct position.
- **Pico** → `8` is correct but in the wrong position.

---

## ✨ Features

- Randomly generated secret number
- No repeated digits in the secret number
- Input validation
- Helpful logical clues
- Configurable number of digits
- Configurable maximum guesses
- Option to play multiple rounds

---

## ⚙️ Configuration

You can easily change the game's difficulty by modifying these constants:

```python
NUM_DIGITS = 3
MAX_GUESSES = 10
```

For example:

```python
NUM_DIGITS = 4
MAX_GUESSES = 12
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x

### Run

```bash
python bagels.py
```

---

## 📂 Project Structure

```
Bagels/
│── main.py
└── README.md
```

---

## 🛠 Concepts Practiced

This project demonstrates:

- Functions
- Loops
- Conditional statements
- Lists
- Strings
- Input validation
- Random number generation
- String methods
- List methods
- Basic game logic

---

## 📚 Learning Source

This project is based on the **Bagels** game from *The Big Book of Small Python Projects* by **Al Sweigart**, with personal modifications and refactoring for learning purposes.

---

## 📄 License

This project is intended for educational and learning purposes.
