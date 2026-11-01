"""
Command Line Interface for Bloom Habit Tracker.
Provides aesthetic ANSI terminal support for quick checks, additions, and logging.
"""

import sys
from datetime import date
from app.models import Habit
from app.storage import HabitStore

# ANSI TrueColor pink codes
PINK = "\033[38;2;255;82;136m"
SOFT_PINK = "\033[38;2;254;216;226m"
GRAY = "\033[38;2;140;130;136m"
WHITE = "\033[38;2;255;255;255m"
BOLD = "\033[1m"
RESET = "\033[0m"


def print_header(title: str) -> None:
    print(f"\n{PINK}{BOLD}🌸 Bloom Habit Tracker{RESET} — {GRAY}{title}{RESET}\n")


def display_habits_table(store: HabitStore) -> None:
    today_iso = date.today().isoformat()
    stats = store.get_stats_for_date(today_iso)

    print_header(f"Today's Overview ({stats['completed']}/{stats['total']} • {stats['percentage']:.0f}%)")

    if not store.habits:
        print(f"  {GRAY}No habits tracked yet. Use --add to create one!{RESET}\n")
        return

    print(f"  {BOLD}{'#':<3} {'STATUS':<8} {'HABIT':<32} {'ROUTINE':<12} {'STREAK':<10}{RESET}")
    print(f"  {GRAY}{'─'*68}{RESET}")

    for idx, h in enumerate(store.habits, 1):
        done = h.is_completed(today_iso)
        status_symbol = f"{PINK}[✓] Done{RESET}" if done else f"{GRAY}[ ] Todo{RESET}"
        streak, _ = h.calculate_streaks()
        streak_str = f"🔥 {streak}d" if streak > 0 else f"{GRAY}0d{RESET}"
        name_display = f"{h.emoji} {h.name}"
        if len(name_display) > 30:
            name_display = name_display[:28] + ".."

        print(f"  {GRAY}{idx:<3}{RESET} {status_symbol:<17} {name_display:<32} {h.routine:<12} {streak_str:<10}")

    print(f"  {GRAY}{'─'*68}{RESET}\n")


def run_cli_interactive(store: HabitStore) -> None:
    while True:
        display_habits_table(store)
        print(f"  {PINK}[1-{len(store.habits)}]{RESET} Toggle Habit  |  {PINK}[a]{RESET} Add  |  {PINK}[s]{RESET} Stats  |  {PINK}[q]{RESET} Quit")
        try:
            choice = input(f"  {BOLD}Select an option: {RESET}").strip()
        except (KeyboardInterrupt, EOFError):
            print("\n")
            break

        if choice.lower() == "q":
            break
        elif choice.lower() == "a":
            name = input("  Habit name: ").strip()
            if name:
                emoji = input("  Emoji (default ✨): ").strip() or "✨"
                routine = input("  Routine (Morning/Afternoon/Evening/Anytime): ").strip().capitalize() or "Anytime"
                h = Habit(name=name, emoji=emoji, routine=routine)
                store.add_habit(h)
                print(f"  {PINK}✓ Added '{name}'!{RESET}")
        elif choice.lower() == "s":
            overall = store.get_overall_stats()
            print(f"\n  {PINK}🏆 Best Streak:{RESET} {overall['best_streak']} days")
            print(f"  {PINK}🔥 Active Streak:{RESET} {overall['current_max_streak']} days")
            print(f"  {PINK}✨ Total Completions:{RESET} {overall['total_completions']} times\n")
            input(f"  {GRAY}Press Enter to continue...{RESET}")
        elif choice.isdigit():
            num = int(choice)
            if 1 <= num <= len(store.habits):
                target = store.habits[num - 1]
                new_state = target.toggle()
                store.save()
                state_str = "completed" if new_state else "unmarked"
                print(f"  {PINK}✓ {target.name} {state_str}!{RESET}")
            else:
                print("  Invalid habit number.")
        else:
            print("  Unknown option.")
