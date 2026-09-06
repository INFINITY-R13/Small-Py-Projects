import calendar
from datetime import datetime


def print_month(year: int, month: int) -> None:
    """Print a nicely formatted calendar for one month."""
    print()
    print(calendar.month(year, month))


def print_year(year: int) -> None:
    """Print a full-year calendar."""
    print()
    print(calendar.calendar(year))


def get_valid_year() -> int:
    """Ask the user for a year and validate it."""
    while True:
        try:
            year = int(input("Enter year (e.g. 2026): "))
            if 1 <= year <= 9999:
                return year
            print("Please enter a year between 1 and 9999.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def get_valid_month() -> int:
    """Ask the user for a month and validate it."""
    while True:
        try:
            month = int(input("Enter month (1-12): "))
            if 1 <= month <= 12:
                return month
            print("Please enter a month between 1 and 12.")
        except ValueError:
            print("Invalid input. Please enter a number.")


def main() -> None:
    print("=" * 40)
    print("       CALENDAR MAKER")
    print("=" * 40)
    print("1. Show one month")
    print("2. Show full year")
    print("3. Show current month")
    print("4. Exit")
    print("=" * 40)

    while True:
        choice = input("\nChoose an option (1-4): ").strip()

        if choice == "1":
            year = get_valid_year()
            month = get_valid_month()
            print_month(year, month)

        elif choice == "2":
            year = get_valid_year()
            print_year(year)

        elif choice == "3":
            now = datetime.now()
            print_month(now.year, now.month)

        elif choice == "4":
            print("\nGoodbye!")
            break

        else:
            print("Invalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()