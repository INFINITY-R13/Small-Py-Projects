# 🎲 Dice Roller

A simple graphical **Dice Roller** built with Python and Tkinter. Click the **Roll Dice** button to randomly roll a six-sided die and display the result using Unicode dice faces.

## ✨ Features

* 🎲 Simple and beginner-friendly GUI
* 🔢 Generates a random number from 1 to 6
* ⚀ Displays actual Unicode dice faces
* 🖱️ Roll the dice with a button click
* 🐍 Built entirely with Python's standard library

## 🖼️ Dice Faces

The program uses these Unicode characters to represent the six sides of a die:

| Number | Face |
| ------ | ---- |
| 1      | ⚀    |
| 2      | ⚁    |
| 3      | ⚂    |
| 4      | ⚃    |
| 5      | ⚄    |
| 6      | ⚅    |

## 🛠️ Technologies Used

* **Python 3**
* **Tkinter** for the graphical user interface
* **Random** module for generating dice rolls

No external Python packages are required.

## 📁 Project Structure

```text
Dice-Roller/
│
├── dice_roller.py
└── README.md
```

## ▶️ How to Run

### 1. Install Python

Make sure Python 3 is installed on your computer.

Check your Python installation:

```bash
python --version
```

or:

```bash
python3 --version
```

### 2. Run the Program

Open a terminal in the project directory and run:

```bash
python dice_roller.py
```

On some systems:

```bash
python3 dice_roller.py
```

A window titled **Dice Roller** will appear.

### 3. Roll the Dice

Click the:

**Roll Dice**

button.

The program will randomly select one of the six dice faces.

## 🧠 How It Works

The program stores the six Unicode dice faces in a list:

```python
DICE_FACES = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]
```

When the button is clicked, Python generates a random number between 1 and 6:

```python
result = random.randint(1, 6)
```

The number is then used to select the corresponding dice face:

```python
dice_label.config(text=DICE_FACES[result - 1])
```

For example:

```text
Random number → 4
              ↓
DICE_FACES[3]
              ↓
             ⚃
```

## 🎯 Learning Objectives

This project is useful for practicing:

* Python functions
* Lists
* Random number generation
* Indexing
* Tkinter widgets
* Button events
* Callback functions
* Basic GUI development

## 🚀 Possible Improvements

You can expand this project by adding:

* 🎞️ Dice rolling animation
* 🔊 Rolling sound effects
* 📜 Roll history
* 🔢 Total number of rolls
* 📊 Roll statistics
* 🎲 Multiple dice
* 🏆 Highest and lowest roll tracking
* 🌙 Dark mode
* 🎨 Custom GUI themes
* ⌨️ Keyboard shortcut for rolling
* 🖼️ Image-based dice faces

## 📄 License

This project is intended for learning and experimentation. Feel free to modify and expand it.
