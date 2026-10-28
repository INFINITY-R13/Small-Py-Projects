#!/usr/bin/env python3
"""
Aesthetic Contact Book Application
Features:
- Name, Email, Phone, Birth Date, Instagram
- Live search & group filters
- Birthday countdowns & reminders
- Light Grey Modern Theme
- CSV & JSON Backup and Restore
"""

import sys
import os
from database import Database
from ui.main_window import MainWindow


def configure_high_dpi():
    """Enable high-DPI awareness on Windows platforms if applicable."""
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass


def main():
    configure_high_dpi()

    # Determine database path in same directory as app
    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, "contacts.db")

    db = Database(db_path=db_path)
    app = MainWindow(db=db)
    app.mainloop()


if __name__ == "__main__":
    main()
