#!/usr/bin/env python3
"""
Scientific Calculator App
Entry point supporting both Desktop GUI mode (default) and Terminal CLI mode.
"""

import argparse
import sys
import tkinter as tk

from calculator.engine import SafeMathEvaluator, CalculationError, format_result
from calculator.ui import CalculatorUI


def run_gui():
    """Launch the Tkinter Desktop GUI application."""
    root = tk.Tk()
    app = CalculatorUI(root)
    # Center window on screen
    root.update_idletasks()
    width = 640
    height = 560
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.mainloop()


def run_cli():
    """Launch an interactive Command Line REPL for the calculator."""
    engine = SafeMathEvaluator(angle_unit="DEG")
    print("=" * 55)
    print(" 🧮 Python Scientific Calculator (CLI Mode)")
    print(" Type expressions (e.g. '2 + 3 * 4', 'sin(30)', 'sqrt(64)', '5!')")
    print(" Commands: 'deg' / 'rad' (toggle angle), 'help', 'exit' or 'quit'")
    print("=" * 55)

    while True:
        try:
            prompt = f"[{engine.angle_unit}] calc > "
            user_input = input(prompt).strip()

            if not user_input:
                continue

            cmd = user_input.lower()
            if cmd in ("exit", "quit", "q"):
                print("Goodbye!")
                break
            elif cmd in ("deg", "rad"):
                engine.set_angle_unit(cmd.upper())
                print(f"Angle mode switched to: {cmd.upper()}")
                continue
            elif cmd == "help":
                print("\nSupported functions & constants:")
                print("  Arithmetic : +, -, *, /, %, ^ (power), ()")
                print("  Scientific : sin, cos, tan, asin, acos, atan")
                print("  Roots/Logs : sqrt(x), cbrt(x), log(x), ln(x)")
                print("  Special    : abs(x), x!, 1/x")
                print("  Constants  : pi, e, ans (previous result)")
                print("  Angle Mode : type 'deg' or 'rad'\n")
                continue

            result = engine.evaluate(user_input)
            engine.set_last_answer(result)
            print(f"= {format_result(result)}\n")

        except (CalculationError, ValueError) as err:
            print(f"Error: {err}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nExiting...")
            break


def main():
    parser = argparse.ArgumentParser(description="Python Scientific Calculator App")
    parser.add_argument(
        "--cli",
        "-c",
        action="store_true",
        help="Run in interactive command-line interface (CLI) mode instead of GUI",
    )
    parser.add_argument(
        "--eval",
        "-e",
        type=str,
        help="Evaluate a single mathematical expression and print the result",
    )
    args = parser.parse_args()

    if args.eval:
        engine = SafeMathEvaluator()
        try:
            val = engine.evaluate(args.eval)
            print(format_result(val))
            sys.exit(0)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if args.cli:
        run_cli()
    else:
        run_gui()


if __name__ == "__main__":
    main()
