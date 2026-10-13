#!/usr/bin/env python3
"""
Aura Text Editor
An aesthetic, lightweight, distraction-free code and text editor in Python.
"""

import sys
import tkinter as tk
from editor.app import AuraApp


def main():
    root = tk.Tk()

    # Enable high-DPI scaling on macOS / Windows
    try:
        from ctypes import windll
        windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass

    # Launch application
    app = AuraApp(root)

    # If file paths were passed as CLI arguments, open them
    if len(sys.argv) > 1:
        for filepath in sys.argv[1:]:
            app.open_file_path(filepath)

    root.mainloop()


if __name__ == "__main__":
    main()
