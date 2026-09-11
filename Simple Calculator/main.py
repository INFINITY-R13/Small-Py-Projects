import tkinter as tk


def button_click(value):
    current = display.get()
    display.delete(0, tk.END)
    display.insert(0, current + value)


def clear():
    display.delete(0, tk.END)


def calculate():
    try:
        result = eval(display.get())
        display.delete(0, tk.END)
        display.insert(0, str(result))
    except Exception:
        display.delete(0, tk.END)
        display.insert(0, "Error")


# Create main window
root = tk.Tk()
root.title("Simple Calculator")
root.geometry("300x400")
root.resizable(False, False)

# Display
display = tk.Entry(
    root,
    font=("Arial", 24),
    justify="right",
    bd=10
)
display.pack(fill="both", padx=10, pady=10, ipady=10)

# Button layout
buttons = [
    ["7", "8", "9", "/"],
    ["4", "5", "6", "*"],
    ["1", "2", "3", "-"],
    ["0", ".", "=", "+"],
]

# Create buttons
for row in buttons:
    frame = tk.Frame(root)
    frame.pack(expand=True, fill="both")

    for button in row:
        if button == "=":
            command = calculate
        else:
            command = lambda value=button: button_click(value)

        tk.Button(
            frame,
            text=button,
            font=("Arial", 18),
            command=command
        ).pack(
            side="left",
            expand=True,
            fill="both",
            padx=2,
            pady=2
        )

# Clear button
tk.Button(
    root,
    text="Clear",
    font=("Arial", 18),
    command=clear
).pack(fill="both", padx=10, pady=5, ipady=5)

# Start application
root.mainloop()