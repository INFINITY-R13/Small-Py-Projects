"""
Core Calculator Engine
Provides safe mathematical expression parsing and evaluation.
"""

import ast
import math
import re
from typing import Any, Dict, Union


class CalculationError(Exception):
    """Custom exception for calculation errors."""
    pass


class SafeMathEvaluator:
    """
    Safely parses and evaluates mathematical expressions using Python's AST module.
    Prevents arbitrary code execution while supporting rich scientific operations.
    """

    ALLOWED_FUNCTIONS = {
        "sin", "cos", "tan",
        "asin", "acos", "atan",
        "sqrt", "cbrt",
        "log", "log10", "ln",
        "abs", "fact", "factorial",
        "exp", "rad", "deg"
    }

    CONSTANTS = {
        "pi": math.pi,
        "e": math.e,
    }

    def __init__(self, angle_unit: str = "DEG", last_answer: float = 0.0):
        """
        :param angle_unit: "DEG" (degrees) or "RAD" (radians)
        :param last_answer: value of 'ans' variable
        """
        self.angle_unit = angle_unit.upper()
        self.last_answer = float(last_answer)

    def set_angle_unit(self, unit: str) -> None:
        unit = unit.upper()
        if unit in ("DEG", "RAD"):
            self.angle_unit = unit
        else:
            raise ValueError(f"Invalid angle unit: {unit}. Use 'DEG' or 'RAD'.")

    def set_last_answer(self, value: float) -> None:
        self.last_answer = float(value)

    # Trig functions respecting angle_unit
    def _sin(self, x: float) -> float:
        val = math.radians(x) if self.angle_unit == "DEG" else x
        res = math.sin(val)
        return 0.0 if abs(res) < 1e-14 else res

    def _cos(self, x: float) -> float:
        val = math.radians(x) if self.angle_unit == "DEG" else x
        res = math.cos(val)
        return 0.0 if abs(res) < 1e-14 else res

    def _tan(self, x: float) -> float:
        val = math.radians(x) if self.angle_unit == "DEG" else x
        cos_val = math.cos(val)
        if abs(cos_val) < 1e-14:
            raise CalculationError("Undefined (tangent of 90° or π/2)")
        res = math.tan(val)
        return 0.0 if abs(res) < 1e-14 else res

    def _asin(self, x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise CalculationError("Domain error for asin: input must be in [-1, 1]")
        res = math.asin(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _acos(self, x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise CalculationError("Domain error for acos: input must be in [-1, 1]")
        res = math.acos(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _atan(self, x: float) -> float:
        res = math.atan(x)
        return math.degrees(res) if self.angle_unit == "DEG" else res

    def _sqrt(self, x: float) -> float:
        if x < 0:
            raise CalculationError("Domain error: square root of negative number")
        return math.sqrt(x)

    def _cbrt(self, x: float) -> float:
        return math.cbrt(x) if hasattr(math, "cbrt") else (abs(x) ** (1 / 3) * (-1 if x < 0 else 1))

    def _log10(self, x: float) -> float:
        if x <= 0:
            raise CalculationError("Domain error: log of non-positive number")
        return math.log10(x)

    def _ln(self, x: float) -> float:
        if x <= 0:
            raise CalculationError("Domain error: ln of non-positive number")
        return math.log(x)

    def _factorial(self, x: float) -> int:
        if not (isinstance(x, (int, float)) and float(x).is_integer() and x >= 0):
            raise CalculationError("Factorial requires a non-negative integer")
        if x > 1000:
            raise CalculationError("Number too large for factorial (max 1000)")
        return math.factorial(int(x))

    def _get_function(self, name: str):
        mapping = {
            "sin": self._sin,
            "cos": self._cos,
            "tan": self._tan,
            "asin": self._asin,
            "acos": self._acos,
            "atan": self._atan,
            "sqrt": self._sqrt,
            "cbrt": self._cbrt,
            "log": self._log10,
            "log10": self._log10,
            "ln": self._ln,
            "abs": abs,
            "fact": self._factorial,
            "factorial": self._factorial,
            "exp": math.exp,
            "rad": math.radians,
            "deg": math.degrees,
        }
        return mapping.get(name)

    def preprocess_expression(self, expr: str) -> str:
        """
        Sanitize and normalize user input into standard Python math syntax.
        """
        expr = expr.strip()
        if not expr:
            raise CalculationError("Empty expression")

        # Normalize symbols
        expr = expr.replace("×", "*").replace("÷", "/").replace("−", "-")
        expr = expr.replace("π", "pi")
        expr = expr.replace("√(", "sqrt(")
        expr = re.sub(r'√([0-9]+(?:\.[0-9]+)?|[a-zA-Z]+)', r'sqrt(\1)', expr)
        expr = expr.replace("√", "sqrt")
        expr = expr.replace("^", "**")

        # Handle factorials like 5! or (3+2)!
        # Replace postfix ! with factorial(...)
        expr = re.sub(r'(\d+(?:\.\d+)?)\!', r'fact(\1)', expr)
        expr = re.sub(r'(\))\!', r'fact\1', expr)

        # Handle percentages: e.g. 50% -> (50/100)
        expr = re.sub(r'(\d+(?:\.\d+)?)\%', r'(\1/100)', expr)

        # Implicit multiplication insertion:
        # 1) number followed by constant or function or variable: e.g. 2pi -> 2*pi, 2sqrt(9) -> 2*sqrt(9), 2ans -> 2*ans
        expr = re.sub(r'(\d+(\.\d+)?)(pi|e|ans|sin|cos|tan|asin|acos|atan|sqrt|cbrt|log|ln|abs|fact|exp)', r'\1*\3', expr)
        # 2) number followed by opening parenthesis: 2(3) -> 2*(3)
        expr = re.sub(r'(\d+(\.\d+)?)\(', r'\1*(', expr)
        # 3) closing parenthesis followed by opening parenthesis: (2)(3) -> (2)*(3)
        expr = re.sub(r'\)\(', r')*(', expr)
        # 4) closing parenthesis followed by number/constant/function: )2 -> )*2, )pi -> )*pi
        expr = re.sub(r'\)([\d]|pi|e|ans|sin|cos|tan|sqrt|log|ln)', r')*\1', expr)
        # 5) constant followed by opening parenthesis or number: pi(2) -> pi*(2)
        expr = re.sub(r'\b(pi|e|ans)\(', r'\1*(', expr)

        return expr

    def evaluate(self, expr_str: str) -> float:
        """
        Preprocesses and evaluates expression, returning float or int result.
        """
        cleaned = self.preprocess_expression(expr_str)

        try:
            node = ast.parse(cleaned, mode='eval')
        except SyntaxError as e:
            raise CalculationError(f"Syntax error in expression: {e.msg}")

        return self._eval_node(node.body)

    def _eval_node(self, node: ast.AST) -> Any:
        if isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise CalculationError(f"Unsupported constant type: {type(node.value).__name__}")

        elif isinstance(node, ast.Name):
            name = node.id.lower()
            if name in self.CONSTANTS:
                return self.CONSTANTS[name]
            elif name == "ans":
                return self.last_answer
            raise CalculationError(f"Undefined variable or symbol: '{node.id}'")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise CalculationError(f"Unsupported unary operator: {type(node.op).__name__}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left)
            right = self._eval_node(node.right)

            if isinstance(node.op, ast.Add):
                return left + right
            elif isinstance(node.op, ast.Sub):
                return left - right
            elif isinstance(node.op, ast.Mult):
                return left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise CalculationError("Cannot divide by zero")
                return left / right
            elif isinstance(node.op, ast.FloorDiv):
                if right == 0:
                    raise CalculationError("Cannot divide by zero")
                return left // right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise CalculationError("Cannot divide by zero (modulo 0)")
                return left % right
            elif isinstance(node.op, ast.Pow):
                # Guard against huge power exponent that freezes CPU
                if abs(right) > 10000:
                    raise CalculationError("Exponent too large (max ±10000)")
                if left < 0 and not float(right).is_integer():
                    raise CalculationError("Domain error: negative base with fractional exponent")
                try:
                    res = left ** right
                    if isinstance(res, complex):
                        raise CalculationError("Complex results are not supported")
                    return res
                except OverflowError:
                    raise CalculationError("Overflow: result too large")
            raise CalculationError(f"Unsupported binary operator: {type(node.op).__name__}")

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise CalculationError("Complex function calls are not allowed")

            func_name = node.func.id.lower()
            func = self._get_function(func_name)
            if not func:
                raise CalculationError(f"Unknown function: '{node.func.id}'")

            args = [self._eval_node(arg) for arg in node.args]
            try:
                return func(*args)
            except TypeError:
                raise CalculationError(f"Incorrect number of arguments for function '{func_name}'")
            except OverflowError:
                raise CalculationError("Overflow error in calculation")
            except CalculationError:
                raise
            except Exception as e:
                raise CalculationError(f"Error in {func_name}(): {str(e)}")

        else:
            raise CalculationError(f"Unsupported syntax or expression element: {type(node).__name__}")


def format_result(value: Union[int, float]) -> str:
    """
    Formats numeric result for clean user display.
    - Eliminates float rounding artifacts (e.g., 0.1 + 0.2 -> 0.3).
    - Renders whole numbers without decimal point (.0).
    - Uses scientific notation for very large or tiny numbers.
    """
    if math.isnan(value):
        return "NaN"
    if math.isinf(value):
        return "Infinity" if value > 0 else "-Infinity"

    # Treat near-zero as zero
    if abs(value) < 1e-14:
        return "0"

    # Whole number check
    if isinstance(value, int) or (isinstance(value, float) and value.is_integer() and abs(value) < 1e15):
        return f"{int(value):,}"

    # Very large or very small float
    abs_val = abs(value)
    if abs_val >= 1e14 or abs_val < 1e-6:
        # Use scientific notation
        formatted = f"{value:.8e}"
        # Clean trailing zeros in mantissa: 1.50000000e+05 -> 1.5e5
        mantissa, exp = formatted.split("e")
        mantissa = mantissa.rstrip("0").rstrip(".")
        exp_int = int(exp)
        return f"{mantissa}e{exp_int}"

    # Normal float: round to max 10 decimal digits
    rounded = round(value, 10)
    if isinstance(rounded, float) and rounded.is_integer() and abs(rounded) < 1e14:
        return f"{int(rounded):,}"

    s = str(rounded)
    if "e" in s or "E" in s:
        return s
    parts = s.split(".")
    # Preserve sign when formatting integer part with commas
    sign = "-" if parts[0].startswith("-") else ""
    abs_int_part = abs(int(parts[0]))
    int_part = f"{sign}{abs_int_part:,}"
    if len(parts) > 1 and parts[1] != "0":
        return f"{int_part}.{parts[1]}"
    return int_part
