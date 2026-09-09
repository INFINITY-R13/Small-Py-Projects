import tkinter as tk
from time import strftime

def update_time():
    current_time = strftime('%I:%M:%S %p')
    label.config(text=current_time)
    root.after(1000, update_time)

# Create the main window
root = tk.Tk()
root.title("Digital Clock")
root.resizable(False, False)
root.configure(background="black")

# Create the clock display
label = tk.Label(
    root,
    font=('Courier New', 80, 'bold'),
    background='black',
    foreground="#00E5FF"
)
label.pack(anchor='center', padx=40, pady=30)

# Start the clock
update_time()

# Run the application
root.mainloop()