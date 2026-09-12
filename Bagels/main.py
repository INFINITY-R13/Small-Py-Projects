import random
import tkinter as tk
from tkinter import messagebox

NUM_DIGITS = 3
MAX_GUESSES = 10


def get_secret_num():
    """Returns a string containing NUM_DIGITS unique random digits."""
    numbers = list("0123456789")
    random.shuffle(numbers)
    return "".join(numbers[:NUM_DIGITS])


def get_clues(guess, secret_num):
    """Returns Pico, Fermi, or Bagels clues."""
    if guess == secret_num:
        return "You got it!"

    clues = []

    for i in range(len(guess)):
        if guess[i] == secret_num[i]:
            clues.append("Fermi")
        elif guess[i] in secret_num:
            clues.append("Pico")

    if not clues:
        return "Bagels"

    clues.sort()
    return " ".join(clues)


class BagelsGame:
    def __init__(self, root):
        self.root = root
        self.root.title("Bagels")
        self.root.geometry("450x550")
        self.root.resizable(False, False)

        self.secret_num = ""
        self.guesses = 0

        self.create_widgets()
        self.new_game()

    def create_widgets(self):
        # Title
        title = tk.Label(
            self.root,
            text="🥯 BAGELS",
            font=("Arial", 28, "bold")
        )
        title.pack(pady=(20, 5))

        subtitle = tk.Label(
            self.root,
            text="Pico • Fermi • Bagels",
            font=("Arial", 12)
        )
        subtitle.pack()

        # Instructions
        instructions = tk.Label(
            self.root,
            text=(
                "Guess the 3-digit number with no repeated digits.\n\n"
                "Fermi  → Correct digit, correct position\n"
                "Pico   → Correct digit, wrong position\n"
                "Bagels → No correct digits"
            ),
            font=("Arial", 11),
            justify="left"
        )
        instructions.pack(pady=20)

        # Guess entry
        self.guess_entry = tk.Entry(
            self.root,
            font=("Arial", 24),
            justify="center",
            width=5
        )
        self.guess_entry.pack(pady=10)

        self.guess_entry.bind("<Return>", lambda event: self.make_guess())

        # Guess button
        self.guess_button = tk.Button(
            self.root,
            text="Guess",
            font=("Arial", 13, "bold"),
            width=12,
            command=self.make_guess
        )
        self.guess_button.pack(pady=5)

        # Guess counter
        self.guess_label = tk.Label(
            self.root,
            text="Guesses: 0 / 10",
            font=("Arial", 12, "bold")
        )
        self.guess_label.pack(pady=10)

        # Clue display
        self.clue_label = tk.Label(
            self.root,
            text="Make your first guess!",
            font=("Arial", 16, "bold"),
            wraplength=400
        )
        self.clue_label.pack(pady=15)

        # History
        history_title = tk.Label(
            self.root,
            text="Guess History",
            font=("Arial", 12, "bold")
        )
        history_title.pack()

        self.history_list = tk.Listbox(
            self.root,
            font=("Arial", 11),
            width=35,
            height=7
        )
        self.history_list.pack(pady=5)

        # New Game button
        self.new_game_button = tk.Button(
            self.root,
            text="New Game",
            font=("Arial", 11),
            width=12,
            command=self.new_game
        )
        self.new_game_button.pack(pady=10)

    def new_game(self):
        """Start a new game."""
        self.secret_num = get_secret_num()
        self.guesses = 0

        self.guess_entry.config(state="normal")
        self.guess_button.config(state="normal")

        self.guess_entry.delete(0, tk.END)
        self.history_list.delete(0, tk.END)

        self.guess_label.config(
            text=f"Guesses: 0 / {MAX_GUESSES}"
        )

        self.clue_label.config(
            text="Make your first guess!"
        )

        self.guess_entry.focus()

    def make_guess(self):
        """Process the player's guess."""
        guess = self.guess_entry.get().strip()

        # Validate length
        if len(guess) != NUM_DIGITS:
            messagebox.showwarning(
                "Invalid Guess",
                f"Please enter exactly {NUM_DIGITS} digits."
            )
            return

        # Validate digits
        if not guess.isdigit():
            messagebox.showwarning(
                "Invalid Guess",
                "Please enter numbers only."
            )
            return

        # Validate repeated digits
        if len(set(guess)) != NUM_DIGITS:
            messagebox.showwarning(
                "Invalid Guess",
                "Please enter digits without repetition."
            )
            return

        self.guesses += 1

        clues = get_clues(guess, self.secret_num)

        # Add guess to history
        self.history_list.insert(
            tk.END,
            f"{guess}  →  {clues}"
        )

        self.guess_label.config(
            text=f"Guesses: {self.guesses} / {MAX_GUESSES}"
        )

        self.clue_label.config(text=clues)

        self.guess_entry.delete(0, tk.END)

        # Player won
        if guess == self.secret_num:
            messagebox.showinfo(
                "🎉 Congratulations!",
                f"You guessed the number!\n\n"
                f"The answer was {self.secret_num}."
            )
            self.disable_game()
            return

        # Player ran out of guesses
        if self.guesses >= MAX_GUESSES:
            messagebox.showinfo(
                "Game Over",
                f"You ran out of guesses!\n\n"
                f"The answer was {self.secret_num}."
            )
            self.disable_game()
            return

        self.guess_entry.focus()

    def disable_game(self):
        """Disable input after the game ends."""
        self.guess_entry.config(state="disabled")
        self.guess_button.config(state="disabled")


if __name__ == "__main__":
    root = tk.Tk()
    game = BagelsGame(root)
    root.mainloop()
