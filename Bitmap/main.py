import tkinter as tk
from tkinter import messagebox
import sys


BITMAP = """
 ....................................................................
    **************   *  *** **  *      ******************************
   ********************* ** ** *  * ****************************** *
  **      *****************       ******************************
           *************          **  * **** ** ************** *
            *********            *******   **************** * *
             ********           ***************************  *
    *        * **** ***         *************** ******  ** *
                ****  *         ***************   *** ***  *
                  ******         *************    **   **  *
                  ********        *************    *  ** ***
                    ********         ********          * *** ****
                    *********         ******  *        **** ** * **
                    *********         ****** * *           *** *   *
                      ******          ***** **             *****   *
                      *****            **** *            ********
                     *****             ****              *********
                     ****              **                 *******   *
                     ***                                       *    *
                     **     *                    *
 ....................................................................
"""


def generate_bitmap():
    """Display the bitmap using the entered message."""
    message = message_entry.get()

    if not message:
        messagebox.showwarning("Input Required", "Please enter a message.")
        return

    output = []

    for line in BITMAP.splitlines():
        bitmap_line = ""

        for i, bit in enumerate(line):
            if bit == " ":
                bitmap_line += " "
            else:
                bitmap_line += message[i % len(message)]

        output.append(bitmap_line)

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, "\n".join(output))
    output_text.config(state=tk.DISABLED)


def clear_bitmap():
    """Clear the message and bitmap output."""
    message_entry.delete(0, tk.END)

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)

    message_entry.focus()


def exit_program():
    """Close the application."""
    root.destroy()


# Create the main window
root = tk.Tk()
root.title("Bitmap")
root.geometry("850x650")
root.minsize(700, 550)

# Header
title_label = tk.Label(
    root,
    text="Bitmap",
    font=("Arial", 24, "bold")
)
title_label.pack(pady=(15, 5))

subtitle_label = tk.Label(
    root,
    text="Display a message inside an ASCII bitmap pattern",
    font=("Arial", 11)
)
subtitle_label.pack(pady=(0, 15))


# Input section
input_frame = tk.Frame(root)
input_frame.pack(fill="x", padx=20)

message_label = tk.Label(
    input_frame,
    text="Enter your message:",
    font=("Arial", 12, "bold")
)
message_label.pack(side="left", padx=(0, 10))

message_entry = tk.Entry(
    input_frame,
    font=("Arial", 12)
)
message_entry.pack(
    side="left",
    fill="x",
    expand=True
)


# Buttons
button_frame = tk.Frame(root)
button_frame.pack(pady=15)

generate_button = tk.Button(
    button_frame,
    text="Generate",
    font=("Arial", 11, "bold"),
    width=12,
    command=generate_bitmap
)
generate_button.pack(side="left", padx=5)

clear_button = tk.Button(
    button_frame,
    text="Clear",
    font=("Arial", 11),
    width=12,
    command=clear_bitmap
)
clear_button.pack(side="left", padx=5)

exit_button = tk.Button(
    button_frame,
    text="Exit",
    font=("Arial", 11),
    width=12,
    command=exit_program
)
exit_button.pack(side="left", padx=5)


# Output section
output_frame = tk.Frame(root)
output_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=(0, 20)
)

output_label = tk.Label(
    output_frame,
    text="Bitmap Output",
    font=("Arial", 12, "bold")
)
output_label.pack(anchor="w", pady=(0, 5))


# Scrollbar
scrollbar = tk.Scrollbar(output_frame)
scrollbar.pack(side="right", fill="y")


# Bitmap output
output_text = tk.Text(
    output_frame,
    font=("Courier New", 10),
    wrap="none",
    yscrollcommand=scrollbar.set,
    bg="black",
    fg="white",
    insertbackground="white"
)
output_text.pack(fill="both", expand=True)

scrollbar.config(command=output_text.yview)

output_text.config(state=tk.DISABLED)


# Press Enter to generate
message_entry.bind("<Return>", lambda event: generate_bitmap())

# Put cursor in input field
message_entry.focus()

# Start the application
root.mainloop()