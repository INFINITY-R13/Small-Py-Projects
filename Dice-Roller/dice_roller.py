import tkinter as tk
import random


# Dice faces
DICE_FACES = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


def roll_dice():
    result = random.randint(1, 6)
    dice_label.config(text=DICE_FACES[result - 1])


# Create the main window
window = tk.Tk()
window.title("Dice Roller")
window.geometry("300x250")


# Title
title_label = tk.Label(
    window,
    text="🎲 Dice Roller",
    font=("Arial", 24)
)
title_label.pack(pady=20)


# Dice result
dice_label = tk.Label(
    window,
    text="⚀",
    font=("Arial", 60)
)
dice_label.pack()


# Roll button
roll_button = tk.Button(
    window,
    text="Roll Dice",
    font=("Arial", 16),
    command=roll_dice
)
roll_button.pack(pady=20)


# Start the GUI
window.mainloop()