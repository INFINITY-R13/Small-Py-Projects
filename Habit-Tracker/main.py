#!/usr/bin/env python3
"""
Bloom Habit Tracker - Main Application Entrypoint
Aesthetic Apple-inspired minimalist habit tracker in Python.
"""

import argparse
import sys
from app.config import APP_NAME
from app.storage import HabitStore


def main():
    parser = argparse.ArgumentParser(
        description=f"{APP_NAME}: Aesthetic Apple-inspired Pink Habit Tracker"
    )
    parser.add_argument("--cli", action="store_true", help="Launch interactive CLI mode")
    parser.add_argument("--list", action="store_true", help="Print today's habit checklist and exit")
    parser.add_argument("--stats", action="store_true", help="Print overall habit analytics and exit")
    parser.add_argument("--reset", action="store_true", help="Reset habits to aesthetic defaults")

    args = parser.parse_args()
    store = HabitStore()

    if args.reset:
        store.reset_defaults()
        print("🌸 Habit tracker has been reset to default aesthetic starter habits.")
        return

    if args.list:
        from app.cli import display_habits_table
        display_habits_table(store)
        return

    if args.stats:
        from app.cli import print_header, PINK, RESET, BOLD
        overall = store.get_overall_stats()
        print_header("Habit Analytics & Consistency")
        print(f"  {BOLD}Total Habits:{RESET}       {overall['total_habits']}")
        print(f"  {BOLD}Total Check-ins:{RESET}    {overall['total_completions']}")
        print(f"  {BOLD}Longest Streak:{RESET}     {PINK}{overall['best_streak']} days{RESET}")
        print(f"  {BOLD}Active Streak:{RESET}      {PINK}{overall['current_max_streak']} days{RESET}\n")
        return

    if args.cli:
        from app.cli import run_cli_interactive
        run_cli_interactive(store)
        return

    # Default: Launch Apple-style GUI
    try:
        from app.views.main_window import MainWindow
        app = MainWindow(store=store)
        app.mainloop()
    except Exception as e:
        print(f"Error launching GUI: {e}")
        print("Falling back to CLI mode...")
        from app.cli import run_cli_interactive
        run_cli_interactive(store)


if __name__ == "__main__":
    main()
