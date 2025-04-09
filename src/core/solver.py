from typing import Tuple, List, Dict, Optional
from src.core.methods import (BisectionMethod, FalsePositionMethod, 
                              FixedPointMethod, NewtonRaphsonMethod, SecantMethod)
import sympy as sp
import numpy as np
import logging
import re

class Solver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.methods = {
            "Bisection": BisectionMethod(),
            "False Position": FalsePositionMethod(),
            "Fixed Point": FixedPointMethod(),
            "Newton-Raphson": NewtonRaphsonMethod(),
            "Secant": SecantMethod()
        }
        self.MAX_EPS = 100.0  # Maximum allowed epsilon value
        self.settings = {
            "decimal_places": 4,
            "max_iterations": 100,
            "error_tolerance": 0.0001,
            "stop_by_eps": True
        }
        
        # Default settings
        self.decimal_places = 6
        self.max_iter = 50
        self.eps = 0.0001
        self.max_eps = 100.0  # Maximum allowed epsilon value
        self.stop_by_eps = True

    def validate_function(self, func: str) -> Optional[str]:
        """Validate the mathematical function expression."""
        try:
            # Clean up the function string
            func = func.strip()
            
            # Replace common math functions with sympy equivalents
            func = func.replace("math.sin", "sin")
            func = func.replace("math.cos", "cos")
            func = func.replace("math.tan", "tan")
            func = func.replace("math.log", "log")
            func = func.replace("math.log10", "log10")
            func = func.replace("math.exp", "exp")
            func = func.replace("math.sqrt", "sqrt")
            
            # Add multiplication operator between number and variable
            func = re.sub(r'(\d)x', r'\1*x', func)
            func = re.sub(r'x(\d)', r'x*\1', func)
            
            # Create symbolic variable and parse expression
            x = sp.symbols('x')
            expr = sp.sympify(func)
            
            # Test if the function can be evaluated
            expr.subs(x, 1.0)
            return None
        except Exception as e:
            self.logger.error(f"Function validation error: {str(e)}")
            if "could not parse" in str(e):
                return "Invalid mathematical expression. Please check the syntax."
            elif "invalid syntax" in str(e):
                return "Invalid syntax in the mathematical expression. Please check for missing operators or parentheses."
            else:
                return f"Error in function expression: {str(e)}"

    def validate_parameters(self, method_name: str, params: dict) -> Optional[str]:
        """Validate the parameters for the specific method."""
        try:
            if method_name in ["Bisection", "False Position"]:
                if not all(k in params for k in ["xl", "xu"]):
                    return "Missing parameters: xl and xu required"
                if not isinstance(params["xl"], (int, float)) or not isinstance(params["xu"], (int, float)):
                    return "xl and xu must be numbers"
                if params["xl"] >= params["xu"]:
                    return "xl must be less than xu"
            elif method_name in ["Fixed Point", "Newton-Raphson"]:
                if "xi" not in params:
                    return "Missing parameter: xi required"
                if not isinstance(params["xi"], (int, float)):
                    return "xi must be a number"
            elif method_name == "Secant":
                if not all(k in params for k in ["xi_minus_1", "xi"]):
                    return "Missing parameters: xi_minus_1 and xi required"
                if not isinstance(params["xi_minus_1"], (int, float)) or not isinstance(params["xi"], (int, float)):
                    return "xi_minus_1 and xi must be numbers"
                if params["xi_minus_1"] == params["xi"]:
                    return "xi_minus_1 must be different from xi"
            return None
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return f"Parameter validation error: {str(e)}"

    def solve(self, method_name: str, func: str, params: dict, eps: float = None, eps_operator: str = "<=", max_iter: int = None, 
             stop_by_eps: bool = None, decimal_places: int = None) -> Tuple[Optional[float], List[Dict]]:
        """
        Solve the equation using the specified method with enhanced error handling.
        
        Args:
            method_name: Name of the numerical method to use
            func: Mathematical function as a string
            params: Dictionary of parameters required by the method
            eps: Error tolerance (optional, uses default if not provided)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations (optional, uses default if not provided)
            stop_by_eps: Whether to stop by error tolerance (optional, uses default if not provided)
            decimal_places: Number of decimal places for rounding (optional, uses default if not provided)
            
        Returns:
            Tuple of (root, table_data) where root is the solution or None if not found,
            and table_data is a list of dictionaries containing iteration details
        """
        try:
            # Use default values if not provided
            eps = eps if eps is not None else self.eps
            max_iter = max_iter if max_iter is not None else self.max_iter
            stop_by_eps = stop_by_eps if stop_by_eps is not None else self.stop_by_eps
            decimal_places = decimal_places if decimal_places is not None else self.decimal_places

            # Validate inputs
            if method_name not in self.methods:
                return None, [{"Error": f"Unknown method: {method_name}"}]
                
            func_error = self.validate_function(func)
            if func_error:
                return None, [{"Error": func_error}]
                
            param_error = self.validate_parameters(method_name, params)
            if param_error:
                return None, [{"Error": param_error}]
                
            if not isinstance(eps, (int, float)) or eps <= 0:
                return None, [{"Error": "Error tolerance must be a positive number"}]
                
            if eps_operator not in ["<=", ">=", "<", ">", "="]:
                return None, [{"Error": "Invalid epsilon operator"}]
                
            # Check epsilon against max_eps based on operator
            if eps_operator == "<=" and eps > self.max_eps:
                return None, [{"Error": f"Error tolerance must be less than or equal to {self.max_eps}"}]
            elif eps_operator == ">=" and eps < self.max_eps:
                return None, [{"Error": f"Error tolerance must be greater than or equal to {self.max_eps}"}]
            elif eps_operator == "<" and eps >= self.max_eps:
                return None, [{"Error": f"Error tolerance must be less than {self.max_eps}"}]
            elif eps_operator == ">" and eps <= self.max_eps:
                return None, [{"Error": f"Error tolerance must be greater than {self.max_eps}"}]
            elif eps_operator == "=" and eps > self.max_eps:
                return None, [{"Error": f"Error tolerance must be less than or equal to {self.max_eps}"}]
                
            if not isinstance(max_iter, int) or max_iter <= 0:
                return None, [{"Error": "Maximum iterations must be a positive integer"}]

            # Log the epsilon value and operator being used
            self.logger.info(f"Using epsilon value: {eps} with operator {eps_operator}")

            method = self.methods[method_name]
            if method_name in ["Bisection", "False Position"]:
                return method.solve(func, params["xl"], params["xu"], eps, eps_operator, max_iter, stop_by_eps, decimal_places)
            elif method_name in ["Fixed Point", "Newton-Raphson"]:
                return method.solve(func, params["xi"], eps, eps_operator, max_iter, stop_by_eps, decimal_places)
            elif method_name == "Secant":
                return method.solve(func, params["xi_minus_1"], params["xi"], eps, eps_operator, max_iter, stop_by_eps, decimal_places)
        except Exception as e:
            self.logger.error(f"Error in solve method: {str(e)}")
            return None, [{"Error": f"Error during solution: {str(e)}"}]