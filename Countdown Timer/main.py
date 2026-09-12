import tkinter as tk
from tkinter import messagebox


class CountdownTimer:
    def __init__(self, root):
        self.root = root
        self.root.title("Countdown Timer")
        self.root.geometry("400x350")
        self.root.resizable(False, False)

        self.total_seconds = 0
        self.remaining_seconds = 0
        self.running = False
        self.timer_id = None

        # Title
        title_label = tk.Label(
            root,
            text="⏰ Countdown Timer",
            font=("Arial", 24, "bold")
        )
        title_label.pack(pady=20)

        # Input frame
        input_frame = tk.Frame(root)
        input_frame.pack(pady=10)

        tk.Label(
            input_frame,
            text="Minutes",
            font=("Arial", 12)
        ).grid(row=0, column=0, padx=10)

        tk.Label(
            input_frame,
            text="Seconds",
            font=("Arial", 12)
        ).grid(row=0, column=1, padx=10)

        self.minutes_entry = tk.Entry(
            input_frame,
            width=8,
            font=("Arial", 16),
            justify="center"
        )
        self.minutes_entry.grid(row=1, column=0, padx=10)

        self.seconds_entry = tk.Entry(
            input_frame,
            width=8,
            font=("Arial", 16),
            justify="center"
        )
        self.seconds_entry.grid(row=1, column=1, padx=10)

        # Countdown display
        self.display = tk.Label(
            root,
            text="00:00",
            font=("Arial", 48, "bold")
        )
        self.display.pack(pady=20)

        # Buttons
        button_frame = tk.Frame(root)
        button_frame.pack(pady=10)

        self.start_button = tk.Button(
            button_frame,
            text="▶ Start",
            width=8,
            font=("Arial", 12),
            command=self.start
        )
        self.start_button.grid(row=0, column=0, padx=5)

        self.pause_button = tk.Button(
            button_frame,
            text="⏸ Pause",
            width=8,
            font=("Arial", 12),
            command=self.pause
        )
        self.pause_button.grid(row=0, column=1, padx=5)

        self.reset_button = tk.Button(
            button_frame,
            text="🔄 Reset",
            width=8,
            font=("Arial", 12),
            command=self.reset
        )
        self.reset_button.grid(row=0, column=2, padx=5)

    def start(self):
        # If already running, do nothing
        if self.running:
            return

        # If timer has not been started before, read input
        if self.remaining_seconds == 0:
            try:
                minutes = int(self.minutes_entry.get() or 0)
                seconds = int(self.seconds_entry.get() or 0)

                if minutes < 0 or seconds < 0:
                    raise ValueError

                if seconds >= 60:
                    messagebox.showerror(
                        "Invalid Input",
                        "Seconds must be between 0 and 59."
                    )
                    return

                self.total_seconds = minutes * 60 + seconds

                if self.total_seconds == 0:
                    messagebox.showerror(
                        "Invalid Input",
                        "Please enter a time greater than 0."
                    )
                    return

                self.remaining_seconds = self.total_seconds

            except ValueError:
                messagebox.showerror(
                    "Invalid Input",
                    "Please enter valid numbers."
                )
                return

        self.running = True
        self.update_timer()

    def update_timer(self):
        if not self.running:
            return

        if self.remaining_seconds <= 0:
            self.timer_finished()
            return

        minutes, seconds = divmod(self.remaining_seconds, 60)

        self.display.config(
            text=f"{minutes:02d}:{seconds:02d}"
        )

        self.remaining_seconds -= 1

        self.timer_id = self.root.after(
            1000,
            self.update_timer
        )

    def pause(self):
        if self.running:
            self.running = False

            if self.timer_id:
                self.root.after_cancel(self.timer_id)
                self.timer_id = None

    def reset(self):
        self.running = False

        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.remaining_seconds = 0
        self.total_seconds = 0

        self.display.config(text="00:00")

        self.minutes_entry.delete(0, tk.END)
        self.seconds_entry.delete(0, tk.END)

    def timer_finished(self):
        self.running = False
        self.remaining_seconds = 0

        self.display.config(text="00:00")

        # Alarm sound
        self.play_alarm()

        messagebox.showinfo(
            "Timer Finished",
            "⏰ Time's up!"
        )

    def play_alarm(self):
        # Windows
        try:
            import winsound
            winsound.Beep(1000, 500)
            winsound.Beep(1000, 500)
            winsound.Beep(1000, 500)
        except ImportError:
            # macOS / Linux
            self.root.bell()
            self.root.after(300, self.root.bell)
            self.root.after(600, self.root.bell)


def main():
    root = tk.Tk()
    CountdownTimer(root)
    root.mainloop()


if __name__ == "__main__":
    main()