"""
Unit tests for the Calculator UI and user interaction simulation.
"""

import os
import unittest
import tkinter as tk
from calculator.ui import CalculatorUI


class TestCalculatorUI(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()
        self.app = CalculatorUI(self.root)

    def tearDown(self):
        self.root.destroy()

    def test_basic_arithmetic_ui(self):
        self.app.clear_all()
        self.app.insert_token("15")
        self.app.insert_token(" + ")
        self.app.insert_token("25")
        self.app.calculate_result()
        self.assertEqual(self.app.display_var.get(), "40")

    def test_scientific_calculation_ui(self):
        self.app.clear_all()
        self.app.insert_token("sin(")
        self.app.insert_token("30")
        self.app.insert_token(")")
        self.app.calculate_result()
        self.assertEqual(self.app.display_var.get(), "0.5")

    def test_backspace(self):
        self.app.clear_all()
        self.app.insert_token("123")
        self.app.backspace()
        self.assertEqual(self.app.display_var.get(), "12")

    def test_toggle_negation(self):
        self.app.clear_all()
        self.app.insert_token("50")
        self.app.toggle_negation()
        self.assertEqual(self.app.display_var.get(), "-50")
        self.app.toggle_negation()
        self.assertEqual(self.app.display_var.get(), "50")

    def test_mode_and_history_toggles(self):
        initial_mode = self.app.is_scientific_mode
        self.app._toggle_mode()
        self.assertNotEqual(self.app.is_scientific_mode, initial_mode)

        self.assertFalse(self.app.is_history_open)
        self.app._toggle_history_drawer()
        self.assertTrue(self.app.is_history_open)
        self.app._toggle_history_drawer()
        self.assertFalse(self.app.is_history_open)


if __name__ == "__main__":
    unittest.main()
