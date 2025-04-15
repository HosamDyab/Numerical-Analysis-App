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
            
            # Create a lambda function for faster evaluation
            f_lambda = sp.lambdify(self.x, expr, modules=['numpy', 'sympy'])
            
            # Create a callable function with comprehensive error handling
            def safe_eval(x):
                try:
                    # Suppress numpy warnings temporarily
                    with np.errstate(all='ignore'):
                        # Use the lambda function for faster evaluation
                        result = f_lambda(x)
                        
                        # Check for complex results (e.g., sqrt of negative numbers)
                        if isinstance(result, complex):
                            self.logger.warning(f"Complex result at x={x}")
                            return float('nan')
                            
                        # Check for NaN or infinity
                        if result is None or (hasattr(np, 'isnan') and np.isnan(result)) or (hasattr(np, 'isinf') and np.isinf(result)):
                            self.logger.warning(f"Invalid result at x={x}")
                            return float('nan')
                            
                        # Convert to float to ensure consistent return type
                        return float(result)
                except (ValueError, TypeError, ZeroDivisionError, OverflowError, RuntimeWarning) as e:
                    self.logger.warning(f"Function evaluation error at x={x}")
                    return float('nan')
            
            return safe_eval
        except Exception as e:
            self.logger.error(f"Error creating function from {func_str}")
            raise ValueError(f"Invalid function: {func_str}")

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
            
            # Create a lambda function for faster evaluation
            f_prime_lambda = sp.lambdify(self.x, derivative, modules=['numpy', 'sympy'])
            
            # Create a callable function with comprehensive error handling
            def safe_eval(x):
                try:
                    # Suppress numpy warnings temporarily
                    with np.errstate(all='ignore'):
                        # Use the lambda function for faster evaluation
                        result = f_prime_lambda(x)
                        
                        # Check for complex results (e.g., sqrt of negative numbers)
                        if isinstance(result, complex):
                            self.logger.warning(f"Complex derivative result at x={x}")
                            return float('nan')
                            
                        # Check for NaN or infinity
                        if result is None or (hasattr(np, 'isnan') and np.isnan(result)) or (hasattr(np, 'isinf') and np.isinf(result)):
                            self.logger.warning(f"Invalid derivative result at x={x}")
                            return float('nan')
                            
                        # Convert to float to ensure consistent return type
                        return float(result)
                except (ValueError, TypeError, ZeroDivisionError, OverflowError, RuntimeWarning) as e:
                    self.logger.warning(f"Derivative evaluation error at x={x}")
                    return float('nan')
            
            return safe_eval
        except Exception as e:
            self.logger.error(f"Error creating derivative from {func_str}")
            raise ValueError(f"Invalid function for derivative: {func_str}")

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
            True if the error satisfies the convergence criteria, False otherwise
        """
        try:
            # For each operator, return True when the stopping condition is met
            if eps_operator == "<=":
                return error <= eps  # Stop when error <= epsilon
            elif eps_operator == ">=":
                return error >= eps  # Stop when error >= epsilon
            elif eps_operator == "<":
                return error < eps   # Stop when error < epsilon
            elif eps_operator == ">":
                return error > eps   # Stop when error > epsilon
            elif eps_operator == "=":
                return abs(error - eps) < 1e-10  # Stop when error = epsilon (within tolerance)
            else:
                raise ValueError(f"Invalid epsilon operator: {eps_operator}")
        except Exception as e:
            self.logger.error(f"Error in convergence check")
            return False

    def solve(self, *args, **kwargs) -> Tuple[float, List[Dict]]:
        """
        Solve the numerical method. This method should be overridden by subclasses.
        
        Returns:
            A tuple containing the root and a list of dictionaries with iteration details
        """
        raise NotImplementedError("Subclasses must implement the solve method")