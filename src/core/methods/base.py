from typing import Union, Callable, Dict, Any, Tuple, List, Optional
import sympy as sp
import numpy as np
import math
import logging

class NumericalMethodBase:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.x = sp.Symbol('x')

    def _create_function(self, func_str: str) -> Callable:
        """
        Create a callable function from a string representation.
        
        Args:
            func_str: The function as a string (e.g., "x**2 - 4" or "sin(sqrt(x))")
            
        Returns:
            A callable function that can be evaluated with a numeric value
        """
        try:
            # Replace common math functions with sympy equivalents
            func_str = func_str.replace("math.sin", "sin")
            func_str = func_str.replace("math.cos", "cos")
            func_str = func_str.replace("math.tan", "tan")
            func_str = func_str.replace("math.log", "log")
            func_str = func_str.replace("math.log10", "log10")
            func_str = func_str.replace("math.exp", "exp")
            func_str = func_str.replace("math.sqrt", "sqrt")
            
            # Parse the function string into a sympy expression
            expr = sp.sympify(func_str)
            
            # Create a callable function using lambdify with both numpy and math modules
            # Add error handling for domain errors
            def safe_eval(x):
                try:
                    # Ensure trigonometric functions use radians
                    if "sin" in func_str or "cos" in func_str or "tan" in func_str:
                        # Convert x to radians if it's in degrees
                        x_rad = x * (math.pi / 180.0)
                        return float(expr.subs(self.x, x_rad))
                    else:
                        return float(expr.subs(self.x, x))
                except (ValueError, TypeError, ZeroDivisionError):
                    return float('nan')
            
            return safe_eval
        except Exception as e:
            self.logger.error(f"Error creating function from {func_str}: {str(e)}")
            raise ValueError(f"Invalid function: {func_str}. Error: {str(e)}")

    def _create_derivative(self, func_str: str) -> Callable:
        """
        Create a callable derivative function from a string representation.
        
        Args:
            func_str: The function as a string (e.g., "x**2 - 4" or "sin(sqrt(x))")
            
        Returns:
            A callable function representing the derivative that can be evaluated with a numeric value
        """
        try:
            # Replace common math functions with sympy equivalents
            func_str = func_str.replace("math.sin", "sin")
            func_str = func_str.replace("math.cos", "cos")
            func_str = func_str.replace("math.tan", "tan")
            func_str = func_str.replace("math.log", "log")
            func_str = func_str.replace("math.log10", "log10")
            func_str = func_str.replace("math.exp", "exp")
            func_str = func_str.replace("math.sqrt", "sqrt")
            
            # Parse the function string into a sympy expression
            expr = sp.sympify(func_str)
            
            # Compute the derivative
            derivative = sp.diff(expr, self.x)
            
            # Create a callable function using lambdify with both numpy and math modules
            # Add error handling for domain errors
            def safe_eval(x):
                try:
                    # Ensure trigonometric functions use radians
                    if "sin" in func_str or "cos" in func_str or "tan" in func_str:
                        # Convert x to radians if it's in degrees
                        x_rad = x * (math.pi / 180.0)
                        return float(derivative.subs(self.x, x_rad))
                    else:
                        return float(derivative.subs(self.x, x))
                except (ValueError, TypeError, ZeroDivisionError):
                    return float('nan')
            
            return safe_eval
        except Exception as e:
            self.logger.error(f"Error creating derivative from {func_str}: {str(e)}")
            raise ValueError(f"Invalid function for derivative: {func_str}. Error: {str(e)}")

    def _round_value(self, value: Union[int, float], decimal_places: int) -> float:
        """
        Round a numeric value to the specified number of decimal places.
        
        This method implements a standardized rounding algorithm that:
        1. Multiplies the value by 10^decimal_places
        2. Rounds to the nearest integer
        3. Divides by 10^decimal_places
        
        Args:
            value: The number to round
            decimal_places: The number of decimal places to round to
            
        Returns:
            The rounded value as a float
        """
        if not isinstance(value, (int, float)):
            return value
            
        # Handle special cases
        if math.isnan(value) or math.isinf(value):
            return value
            
        # Apply the rounding algorithm
        multiplier = 10 ** decimal_places
        rounded = round(value * multiplier) / multiplier
        return rounded

    def _format_value(self, value: Union[int, float], decimal_places: int) -> str:
        """
        Format a numeric value as a string with the specified number of decimal places.
        
        This method formats the value for display purposes, removing trailing zeros
        after the decimal point if the number has no fractional part.
        
        Args:
            value: The number to format
            decimal_places: The number of decimal places to display
            
        Returns:
            A formatted string representation of the value
        """
        if not isinstance(value, (int, float)):
            return str(value)
            
        # Handle special cases
        if math.isnan(value):
            return "NaN"
        if math.isinf(value):
            return "Inf" if value > 0 else "-Inf"
            
        # Format with the specified precision
        formatted = f"{value:.{decimal_places}f}"
        
        # Remove trailing zeros and decimal point if needed
        if '.' in formatted:
            formatted = formatted.rstrip('0').rstrip('.')
            
        return formatted

    def _format_error(self, error: Union[float, str], decimal_places: int) -> str:
        """
        Format an error value for display.
        
        Args:
            error: The error value or "---" for first iteration
            decimal_places: Number of decimal places to round to
            
        Returns:
            A formatted string representation of the error
        """
        if error == "---":
            return error
            
        # Round the error value
        if decimal_places < 0:
            return f"{error}%"
            
        # Format with up to 3 decimal places and remove trailing zeros
        rounded = round(error, min(3, decimal_places))
        str_value = f"{rounded:.{min(3, decimal_places)}f}"
        str_value = str_value.rstrip('0').rstrip('.')
        
        return f"{str_value}%"

    def _check_convergence(self, error: float, eps: float, eps_operator: str) -> bool:
        """
        Check if the error satisfies the convergence criterion.
        
        Args:
            error: The current error value
            eps: The error tolerance
            eps_operator: The comparison operator ("<=", ">=", "<", ">", "=")
            
        Returns:
            True if the error satisfies the criterion, False otherwise
        """
        if eps_operator == "<=":
            return error <= eps
        elif eps_operator == ">=":
            return error >= eps
        elif eps_operator == "<":
            return error < eps
        elif eps_operator == ">":
            return error > eps
        elif eps_operator == "=":
            return abs(error - eps) < 1e-10
        else:
            # Default to "<=" if the operator is not recognized
            return error <= eps

    def solve(self, *args, **kwargs) -> Tuple[float, List[Dict]]:
        """
        Solve the numerical method. This method should be overridden by subclasses.
        
        Returns:
            A tuple containing the root and a list of dictionaries with iteration details
        """
        raise NotImplementedError("Subclasses must implement the solve method")