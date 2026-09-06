# Calendar Maker

A simple interactive Python program that generates monthly and yearly calendars in the terminal.

## Features

- Display any single month
- Display a full year calendar
- Quickly show the current month
- Input validation for year and month
- Clean and easy-to-use menu

## Requirements

- Python 3.6 or higher
- No external packages needed (uses only the standard library)

## How to Run

1. Save the program as `calendar_maker.py`
2. Open a terminal in the same folder
3. Run:

```bash
python calendar_maker.py
```

or

```bash
python3 calendar_maker.py
```

## Usage

When you start the program you will see this menu:

```
========================================
       CALENDAR MAKER
========================================
1. Show one month
2. Show full year
3. Show current month
4. Exit
========================================
```

### Options

| Option | Description                          |
|--------|--------------------------------------|
| 1      | Enter a year and month to view       |
| 2      | Enter a year to view the full calendar |
| 3      | Instantly show the current month     |
| 4      | Exit the program                     |

## Example

```
Choose an option (1-4): 1
Enter year (e.g. 2026): 2026
Enter month (1-12): 9

   September 2026
Mo Tu We Th Fr Sa Su
    1  2  3  4  5  6
 7  8  9 10 11 12 13
14 15 16 17 18 19 20
21 22 23 24 25 26 27
28 29 30
```

## License

Free to use and modify.