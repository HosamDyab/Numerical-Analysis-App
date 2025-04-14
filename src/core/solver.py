from typing import Tuple, List, Dict, Optional, Any, Union
from src.core.methods import (BisectionMethod, FalsePositionMethod, 
                              FixedPointMethod, NewtonRaphsonMethod, SecantMethod,
                              GaussEliminationMethod, GaussEliminationPartialPivoting,
                              LUDecompositionMethod, LUDecompositionPartialPivotingMethod,
                              GaussJordanMethod, GaussJordanPartialPivotingMethod)
from src.core.history import HistoryManager
import sympy as sp
import numpy as np
import logging
import re
import ast

class Solver:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.methods = {
            "Bisection": BisectionMethod(),
            "False Position": FalsePositionMethod(),
            "Fixed Point": FixedPointMethod(),
            "Newton-Raphson": NewtonRaphsonMethod(),
            "Secant": SecantMethod(),
            "Gauss Elimination": GaussEliminationMethod(),
            "Gauss Elimination (Partial Pivoting)": GaussEliminationPartialPivoting(),
            "LU Decomposition": LUDecompositionMethod(),
            "LU Decomposition (Partial Pivoting)": LUDecompositionPartialPivotingMethod(),
            "Gauss-Jordan": GaussJordanMethod(),
            "Gauss-Jordan (Partial Pivoting)": GaussJordanPartialPivotingMethod()
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
        
        # Initialize history manager
        self.history_manager = HistoryManager()

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

    def validate_matrix_vector(self, matrix_str: str, vector_str: str) -> Optional[str]:
        """Validate the matrix and vector inputs for Gauss Elimination."""
        try:
            # Parse matrix and vector strings
            matrix = ast.literal_eval(matrix_str)
            vector = ast.literal_eval(vector_str)
            
            # Convert to numpy arrays for validation
            A = np.array(matrix, dtype=float)
            b = np.array(vector, dtype=float)
            
            # Check if matrix is square
            if A.shape[0] != A.shape[1]:
                return "Matrix must be square"
            
            # Check if dimensions match
            if A.shape[0] != len(b):
                return "Matrix and vector dimensions do not match"
            
            # Check for NaN or Inf values
            if np.any(np.isnan(A)) or np.any(np.isinf(A)):
                return "Matrix contains invalid values (NaN or Inf)"
            if np.any(np.isnan(b)) or np.any(np.isinf(b)):
                return "Vector contains invalid values (NaN or Inf)"
            
            return None
        except Exception as e:
            self.logger.error(f"Matrix/vector validation error: {str(e)}")
            if "could not parse" in str(e):
                return "Invalid matrix or vector format. Please use proper Python list syntax."
            else:
                return f"Error in matrix/vector input: {str(e)}"

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
            elif method_name == "Gauss Elimination":
                if not all(k in params for k in ["matrix", "vector"]):
                    return "Missing parameters: matrix and vector required"
                if not isinstance(params["matrix"], str) or not isinstance(params["vector"], str):
                    return "matrix and vector must be strings"
                matrix_error = self.validate_matrix_vector(params["matrix"], params["vector"])
                if matrix_error:
                    return matrix_error
            return None
        except Exception as e:
            self.logger.error(f"Parameter validation error: {str(e)}")
            return f"Parameter validation error: {str(e)}"

    def solve(self, method_name: str, func: str, params: dict, eps: float = None, eps_operator: str = "<=", max_iter: int = None, 
             stop_by_eps: bool = None, decimal_places: int = None) -> Tuple[Union[float, List[float], None], List[Dict]]:
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
                
            # Special handling for linear system methods
            if method_name in ["Gauss Elimination", "Gauss Elimination (Partial Pivoting)", 
                              "LU Decomposition", "LU Decomposition (Partial Pivoting)",
                              "Gauss-Jordan", "Gauss-Jordan (Partial Pivoting)"]:
                # Extract matrix and vector from params
                matrix = params.get("matrix")
                vector = params.get("vector")
                
                if not matrix or not vector:
                    return None, [{"Error": "Matrix and vector are required for linear system methods"}]
                    
                # Validate matrix and vector
                validation_error = self.validate_matrix_vector(matrix, vector)
                if validation_error:
                    return None, [{"Error": validation_error}]
                
                # Call the method
                result, table = self.methods[method_name].solve(matrix, vector, decimal_places)
                
                # Save to history with a placeholder function name
                if result is not None:
                    # For linear system methods, use "System of Linear Equations" as the function name
                    self.history_manager.save_solution(
                        "System of Linear Equations",
                        method_name,
                        result,
                        table
                    )
                
                return result, table
            else:
                # Validate function
                func_error = self.validate_function(func)
                if func_error:
                    return None, [{"Error": func_error}]
                
                # Validate parameters
                param_error = self.validate_parameters(method_name, params)
                if param_error:
                    return None, [{"Error": param_error}]
                
                # Call the method
                result, table = self.methods[method_name].solve(func, params, eps, max_iter, stop_by_eps, decimal_places)
                
                # Save to history
                if result is not None:
                    self.history_manager.save_solution(
                        func,
                        method_name,
                        result,
                        table
                    )
                
                return result, table
                
        except Exception as e:
            self.logger.error(f"Solver error: {str(e)}")
            return None, [{"Error": f"Solver error: {str(e)}"}]