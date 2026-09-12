# 🥯 Bagels

A simple **Pico, Fermi, Bagels** number-guessing game built with **Python and Tkinter**.

The goal is to guess a randomly generated 3-digit number with no repeated digits. Use the clues provided after each guess to figure out the secret number.

## 🎮 How to Play

The game generates a random **3-digit number** with unique digits.

You have **10 guesses** to find the secret number.

After each guess, the game provides one or more of these clues:

| Clue       | Meaning                                           |
| ---------- | ------------------------------------------------- |
| **Fermi**  | One digit is correct and in the correct position. |
| **Pico**   | One digit is correct but in the wrong position.   |
| **Bagels** | No digit is correct.                              |

### Example

Suppose the secret number is:

```text
427
```

And your guess is:

```text
472
```

The result would contain:

```text
Fermi Pico Pico
```

* `4` is correct and in the correct position → **Fermi**
* `7` is correct but in the wrong position → **Pico**
* `2` is correct but in the wrong position → **Pico**

## ✨ Features

* 🖥️ Tkinter graphical user interface
* 🔢 Random 3-digit secret number
* 🚫 No repeated digits
* 🎯 Maximum of 10 guesses
* 💡 Pico, Fermi, and Bagels clues
* 📜 Guess history
* 🔄 New Game button
* ⚠️ Input validation
* ⌨️ Press **Enter** to submit a guess
* 🏆 Win and Game Over notifications

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter**
* **Random module**

Tkinter is included with most standard Python installations, so no external packages are required.

## 📂 Project Structure

```text
Bagels/
│
├── main.py
└── README.md
```

## ▶️ How to Run

### 1. Clone the repository

```bash
git clone https://github.com/your-username/Small-Py-Projects.git
```

### 2. Navigate to the Bagels project

```bash
cd Small-Py-Projects/Bagels
```

### 3. Run the program

```bash
python main.py
```

On some systems, you may need:

```bash
python3 main.py
```

## 🎯 Game Rules

1. The computer generates a random 3-digit number.
2. Every digit in the secret number is unique.
3. Enter a 3-digit guess.
4. The game checks your guess against the secret number.
5. Use the **Pico** and **Fermi** clues to narrow down the answer.
6. You have **10 attempts** to guess the number.
7. Guess correctly to win!

## 📌 Input Requirements

A valid guess must:

* Contain exactly **3 digits**
* Contain **numbers only**
* Have **no repeated digits**

For example:

```text
123  ✅
507  ✅
112  ❌ Repeated digit
12   ❌ Too short
1234 ❌ Too long
abc  ❌ Not a number
```

## 🧠 How It Works

The program first generates the secret number by shuffling the digits `0-9` and selecting the required number of digits.

For every guess, the program compares each digit with the secret number:

```text
Correct digit + correct position
            ↓
          Fermi

Correct digit + wrong position
            ↓
           Pico

No matching digits
            ↓
          Bagels
```

The Tkinter interface then displays the resulting clues and adds the guess to the guess history.

## 🚀 Possible Improvements

Some ideas for future versions:

* 🎨 Add a dark/light mode
* 🔊 Add sound effects
* 🏅 Add a scoring system
* 📊 Track wins and losses
* ⚙️ Allow different difficulty levels
* 🔢 Allow 4 or 5-digit numbers
* 💾 Save game statistics
* 🎭 Add animations and visual effects

## 📄 License

This project is open-source and available for learning and personal use.

````

You can place this directly in:

```text
Small-Py-Projects/Bagels/README.md
````

If you're keeping all your projects stylistically consistent, this README also matches the kind of structure you'd want across your **Small-Py-Projects** collection.
