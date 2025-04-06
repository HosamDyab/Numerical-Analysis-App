from typing import Tuple, List, Dict, Optional
from src.core.methods import (BisectionMethod, FalsePositionMethod, 
                              FixedPointMethod, NewtonRaphsonMethod, SecantMethod)
import sympy as sp
import numpy as np
import logging

class Solver:
    def __init__(self):
        self.methods = {
            "Bisection": BisectionMethod(),
            "False Position": FalsePositionMethod(),
            "Fixed Point": FixedPointMethod(),
            "Newton-Raphson": NewtonRaphsonMethod(),
            "Secant": SecantMethod()
        }
        self.logger = logging.getLogger(__name__)
        
        # Default settings
        self.decimal_places = 6
        self.max_iter = 50
        self.eps = 0.0001
        self.stop_by_eps = True

    def validate_function(self, func: str) -> Optional[str]:
        """Validate the mathematical function expression."""
        try:
            x = sp.symbols('x')
            expr = sp.sympify(func)
            # Test if the function can be evaluated
            expr.subs(x, 1.0)
            return None
        except Exception as e:
            self.logger.error(f"Function validation error: {str(e)}")
            return f"Invalid function expression: {str(e)}"

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

    def solve(self, method_name: str, func: str, params: dict, eps: float = None, max_iter: int = None, 
             stop_by_eps: bool = None, decimal_places: int = None) -> Tuple[Optional[float], List[Dict]]:
        """
        Solve the equation using the specified method with enhanced error handling.
        
        Args:
            method_name: Name of the numerical method to use
            func: Mathematical function as a string
            params: Dictionary of parameters required by the method
            eps: Error tolerance (optional, uses default if not provided)
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
                
            if not isinstance(max_iter, int) or max_iter <= 0:
                return None, [{"Error": "Maximum iterations must be a positive integer"}]

            method = self.methods[method_name]
            if method_name in ["Bisection", "False Position"]:
                return method.solve(func, params["xl"], params["xu"], eps, max_iter, stop_by_eps, decimal_places)
            elif method_name in ["Fixed Point", "Newton-Raphson"]:
                return method.solve(func, params["xi"], eps, max_iter, stop_by_eps, decimal_places)
            elif method_name == "Secant":
                return method.solve(func, params["xi_minus_1"], params["xi"], eps, max_iter, stop_by_eps, decimal_places)
        except Exception as e:
            self.logger.error(f"Error in solve method: {str(e)}")
            return None, [{"Error": f"Error during solution: {str(e)}"}]