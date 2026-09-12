import tkinter as tk
from tkinter import ttk, messagebox

SYMBOLS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


def caesar_cipher(message, key, mode):
    translated = ''

    for symbol in message.upper():
        if symbol in SYMBOLS:
            num = SYMBOLS.find(symbol)

            if mode == 'encrypt':
                num += key
            else:
                num -= key

            num %= len(SYMBOLS)
            translated += SYMBOLS[num]
        else:
            translated += symbol

    return translated


def process_message():
    message = message_entry.get("1.0", tk.END).strip()
    key_text = key_entry.get().strip()
    mode = mode_var.get()

    if not message:
        messagebox.showwarning("Missing Message", "Please enter a message.")
        return

    if not key_text.isdigit():
        messagebox.showerror("Invalid Key", "Please enter a number from 0 to 25.")
        return

    key = int(key_text)

    if not 0 <= key <= 25:
        messagebox.showerror("Invalid Key", "Key must be between 0 and 25.")
        return

    result = caesar_cipher(message, key, mode)

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.insert(tk.END, result)
    output_text.config(state=tk.DISABLED)


def clear_fields():
    message_entry.delete("1.0", tk.END)
    key_entry.delete(0, tk.END)

    output_text.config(state=tk.NORMAL)
    output_text.delete("1.0", tk.END)
    output_text.config(state=tk.DISABLED)


def copy_result():
    result = output_text.get("1.0", tk.END).strip()

    if not result:
        messagebox.showwarning("Nothing to Copy", "There is no result to copy.")
        return

    root.clipboard_clear()
    root.clipboard_append(result)
    root.update()

    messagebox.showinfo("Copied", "Result copied to clipboard!")


# Main window
root = tk.Tk()
root.title("Caesar Cipher")
root.geometry("600x500")
root.resizable(False, False)

# Title
title_label = ttk.Label(
    root,
    text="Caesar Cipher",
    font=("Arial", 24, "bold")
)
title_label.pack(pady=(20, 5))

subtitle_label = ttk.Label(
    root,
    text="Encrypt or decrypt messages using a Caesar cipher",
    font=("Arial", 11)
)
subtitle_label.pack(pady=(0, 20))


# Mode selection
mode_frame = ttk.LabelFrame(root, text="Mode")
mode_frame.pack(fill="x", padx=30, pady=10)

mode_var = tk.StringVar(value="encrypt")

encrypt_radio = ttk.Radiobutton(
    mode_frame,
    text="Encrypt",
    variable=mode_var,
    value="encrypt"
)
encrypt_radio.pack(side="left", padx=30, pady=10)

decrypt_radio = ttk.Radiobutton(
    mode_frame,
    text="Decrypt",
    variable=mode_var,
    value="decrypt"
)
decrypt_radio.pack(side="left", padx=30, pady=10)


# Key input
key_frame = ttk.Frame(root)
key_frame.pack(fill="x", padx=30, pady=10)

key_label = ttk.Label(
    key_frame,
    text="Key (0-25):"
)
key_label.pack(side="left")

key_entry = ttk.Entry(key_frame, width=10)
key_entry.pack(side="left", padx=10)


# Message input
message_label = ttk.Label(
    root,
    text="Message:"
)
message_label.pack(anchor="w", padx=30)

message_entry = tk.Text(
    root,
    height=5,
    width=60
)
message_entry.pack(padx=30, pady=5)


# Buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

process_button = ttk.Button(
    button_frame,
    text="Process",
    command=process_message
)
process_button.pack(side="left", padx=5)

clear_button = ttk.Button(
    button_frame,
    text="Clear",
    command=clear_fields
)
clear_button.pack(side="left", padx=5)

copy_button = ttk.Button(
    button_frame,
    text="Copy Result",
    command=copy_result
)
copy_button.pack(side="left", padx=5)


# Output
output_label = ttk.Label(
    root,
    text="Result:"
)
output_label.pack(anchor="w", padx=30)

output_text = tk.Text(
    root,
    height=5,
    width=60,
    state=tk.DISABLED
)
output_text.pack(padx=30, pady=5)


root.mainloop()