"""
Unit tests for the SafeMathEvaluator engine.
"""

import math
import unittest
from calculator.engine import SafeMathEvaluator, CalculationError, format_result


class TestSafeMathEvaluator(unittest.TestCase):
    def setUp(self):
        self.engine = SafeMathEvaluator()

    def test_basic_arithmetic(self):
        self.assertEqual(self.engine.evaluate("2 + 3"), 5)
        self.assertEqual(self.engine.evaluate("10 - 4"), 6)
        self.assertEqual(self.engine.evaluate("3 * 7"), 21)
        self.assertEqual(self.engine.evaluate("15 / 3"), 5.0)
        self.assertEqual(self.engine.evaluate("2 + 3 * 4"), 14)
        self.assertEqual(self.engine.evaluate("(2 + 3) * 4"), 20)

    def test_unicode_operators(self):
        self.assertEqual(self.engine.evaluate("6 × 7"), 42)
        self.assertEqual(self.engine.evaluate("50 ÷ 2"), 25.0)
        self.assertEqual(self.engine.evaluate("10 − 3"), 7)

    def test_powers_and_roots(self):
        self.assertEqual(self.engine.evaluate("2 ^ 3"), 8)
        self.assertEqual(self.engine.evaluate("sqrt(16)"), 4.0)
        self.assertEqual(self.engine.evaluate("√25"), 5.0)
        self.assertEqual(self.engine.evaluate("cbrt(27)"), 3.0)

    def test_percentage(self):
        self.assertAlmostEqual(self.engine.evaluate("50%"), 0.5)
        self.assertAlmostEqual(self.engine.evaluate("200 * 15%"), 30.0)

    def test_implicit_multiplication(self):
        self.assertEqual(self.engine.evaluate("2(3 + 4)"), 14)
        self.assertEqual(self.engine.evaluate("(2 + 3)(4 + 1)"), 25)
        self.assertAlmostEqual(self.engine.evaluate("2pi"), 2 * math.pi)
        self.assertEqual(self.engine.evaluate("3sqrt(9)"), 9.0)

    def test_factorial(self):
        self.assertEqual(self.engine.evaluate("5!"), 120)
        self.assertEqual(self.engine.evaluate("0!"), 1)
        self.assertEqual(self.engine.evaluate("fact(4)"), 24)

    def test_trigonometry_deg(self):
        self.engine.set_angle_unit("DEG")
        self.assertAlmostEqual(self.engine.evaluate("sin(30)"), 0.5)
        self.assertAlmostEqual(self.engine.evaluate("cos(60)"), 0.5)
        self.assertAlmostEqual(self.engine.evaluate("tan(45)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("asin(0.5)"), 30.0)
        self.assertAlmostEqual(self.engine.evaluate("atan(1)"), 45.0)

    def test_trigonometry_rad(self):
        self.engine.set_angle_unit("RAD")
        self.assertAlmostEqual(self.engine.evaluate("sin(pi / 2)"), 1.0)
        self.assertAlmostEqual(self.engine.evaluate("cos(pi)"), -1.0)

    def test_logarithms(self):
        self.assertAlmostEqual(self.engine.evaluate("log(100)"), 2.0)
        self.assertAlmostEqual(self.engine.evaluate("ln(e)"), 1.0)

    def test_constants_and_ans(self):
        self.assertAlmostEqual(self.engine.evaluate("pi"), math.pi)
        self.assertAlmostEqual(self.engine.evaluate("e"), math.e)
        self.engine.set_last_answer(42)
        self.assertEqual(self.engine.evaluate("ans + 8"), 50)
        self.assertEqual(self.engine.evaluate("2ans"), 84)

    def test_errors(self):
        with self.assertRaises(CalculationError):
            self.engine.evaluate("5 / 0")

        with self.assertRaises(CalculationError):
            self.engine.evaluate("sqrt(-4)")

        with self.assertRaises(CalculationError):
            self.engine.evaluate("log(0)")

        with self.assertRaises(CalculationError):
            self.engine.evaluate("__import__('os').system('ls')")

        with self.assertRaises(CalculationError):
            self.engine.evaluate("2 ++-- invalid")

    def test_formatting(self):
        self.assertEqual(format_result(5.0), "5")
        self.assertEqual(format_result(0.1 + 0.2), "0.3")
        self.assertEqual(format_result(1000000), "1,000,000")
        self.assertEqual(format_result(1234567.89), "1,234,567.89")
        self.assertEqual(format_result(-1234.5), "-1,234.5")
        self.assertEqual(format_result(0), "0")

    def test_advanced_operations(self):
        self.assertEqual(self.engine.evaluate("-5 + 12"), 7)
        self.assertEqual(self.engine.evaluate("-(4 * 3)"), -12)
        self.assertEqual(self.engine.evaluate("abs(-42)"), 42)
        self.assertEqual(self.engine.evaluate("10 % 3"), 1)
        self.assertEqual(self.engine.evaluate("((1 + 2) * (3 + 4))"), 21)
        self.assertEqual(self.engine.evaluate("2 ^ (1 + 2)"), 8)


if __name__ == "__main__":
    unittest.main()
