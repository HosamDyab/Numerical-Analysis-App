from typing import Union, Callable
import sympy as sp
import numpy as np

class NumericalMethodBase:
    def __init__(self):
        self.x = sp.symbols('x')

    def _create_function(self, func_str: str) -> Callable:
        """Create a callable function from a string expression."""
        expr = sp.sympify(func_str)
        return sp.lambdify(self.x, expr, 'numpy')

    def _round_values(self, value: Union[float, str], decimal_places: int) -> Union[float, str]:
        """Round numerical values to specified decimal places."""
        if isinstance(value, (int, float)):
            return round(value, decimal_places)
        return value

    def _format_error(self, error: Union[float, str], decimal_places: int) -> str:
        """Format error value with percentage symbol and proper rounding."""
        if isinstance(error, (int, float)):
            return f"{round(error, decimal_places)}%"
        return str(error)