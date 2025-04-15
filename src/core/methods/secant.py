from .base import NumericalMethodBase
from typing import Tuple, List, Dict, Optional, Callable
import sympy as sp
import numpy as np
import math
import json
import os

class SecantMethod(NumericalMethodBase):
    def __init__(self):
        super().__init__()
        self.history_file = "secant_history.json"
        self.last_solution = None
        self._load_history()
    
    def _load_history(self):
        """Load the history of solutions from the history file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            else:
                self.history = []
        except Exception:
            self.history = []
    
    def _save_history(self):
        """Save the history of solutions to the history file."""
        try:
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=4)
        except Exception as e:
            print(f"Error saving history: {str(e)}")
    
    def solve(self, func_str: str, x0: float, x1: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Secant method.
        
        The Secant method uses the formula:
            x_{i+1} = x_i - f(x_i)(x_i - x_{i-1})/(f(x_i) - f(x_{i-1}))
        
        This is similar to Newton's method but approximates the derivative using
        the slope of the secant line between two points instead of calculating
        the derivative directly. This makes it useful when derivatives are difficult
        to compute or expensive to evaluate.
        
        The method has superlinear convergence (faster than linear but slower than quadratic).
        
        Args:
            func_str: The function f(x) as a string (e.g., "-x**3 + 7.89*x + 11")
            x0: First initial guess
            x1: Second initial guess
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        f = self._create_function(func_str)
        table = []
        error = "---"  # Initial error value
        
        # Evaluate function at initial points
        f_x0 = float(f(x0))
        f_x1 = float(f(x1))
        
        # Check if either initial guess is already a root
        if abs(f_x0) < 1e-10:
            return x0, [{"Message": f"Initial guess x0 = {x0} is already a root"}]
        if abs(f_x1) < 1e-10:
            return x1, [{"Message": f"Initial guess x1 = {x1} is already a root"}]
        
        # Check if initial guesses are too close
        if abs(x1 - x0) < 1e-10:
            return None, [{"Error": "Initial guesses are too close to each other. Please provide distinct values."}]

        for i in range(max_iter):
            # Check for division by zero
            if abs(f_x1 - f_x0) < 1e-10:
                return None, table + [{"Error": f"Division by zero encountered at iteration {i}. The secant line is nearly horizontal."}]
            
            # Calculate next approximation using Secant formula: x_{i+1} = x_i - f(x_i)(x_i - x_{i-1})/(f(x_i) - f(x_{i-1}))
            # This formula approximates the derivative using the slope of the secant line between two points
            # It represents finding where the secant line crosses the x-axis
            xi_plus_1 = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
            f_xi_plus_1 = float(f(xi_plus_1))
            
            # Check for NaN or infinity results
            if np.isnan(xi_plus_1) or np.isinf(xi_plus_1):
                return x1, table + [{"Error": f"Numerical instability detected at iteration {i}."}]
            
            # Calculate error
            if i > 0:
                # Use absolute error for very small values
                if abs(xi_plus_1) < 1e-10:
                    error = abs(xi_plus_1 - x1)
                else:
                    error = abs((xi_plus_1 - x1) / xi_plus_1) * 100
            
            # Create row for the iteration table
            row = {
                "Iteration": i,
                "Xi-1": self._round_value(x0, decimal_places),
                "Xi": self._round_value(x1, decimal_places),
                "f(Xi-1)": self._round_value(f_x0, decimal_places),
                "f(Xi)": self._round_value(f_x1, decimal_places),
                "Xi+1": self._round_value(xi_plus_1, decimal_places),
                "f(Xi+1)": self._round_value(f_xi_plus_1, decimal_places),
                "Error %": self._format_value(error, decimal_places)
            }
            table.append(row)
            
            # Check if we found the exact root (within numerical precision)
            if abs(f_xi_plus_1) < 1e-10:
                return xi_plus_1, table
            
            # Check convergence criteria
            if i > 0:
                # Calculate absolute difference between consecutive iterations
                abs_diff = abs(xi_plus_1 - x1)
                
                # If stop_by_eps is True, check if error meets the epsilon condition
                if stop_by_eps and self._check_convergence(abs_diff, eps, eps_operator):
                    # Add a message to the table indicating we stopped by epsilon
                    table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| {eps_operator} {eps}"})
                    return xi_plus_1, table
                # If stop_by_eps is False, we continue until max_iter is reached
            
            # Check for divergence (if values are getting too large)
            if abs(xi_plus_1) > 1e10:
                return None, table + [{"Error": f"Method is diverging at iteration {i}."}]
            
            # Update values for next iteration
            x0, f_x0 = x1, f_x1
            x1, f_x1 = xi_plus_1, f_xi_plus_1

        # Return the final approximation if max_iter is reached
        # Add a message to the table indicating we stopped by max iterations
        table.append({"Message": f"Stopped by reaching maximum iterations: {max_iter}"})
        return xi_plus_1, table
    
    def get_last_solution(self) -> Optional[Dict]:
        """Get the last solution from the history."""
        return self.last_solution
    
    def get_history(self) -> List[Dict]:
        """Get the entire history of solutions."""
        return self.history
    
    def edit_solution(self, index: int, **kwargs) -> bool:
        """
        Edit a solution in the history.
        
        Args:
            index: The index of the solution to edit in the history
            **kwargs: The parameters to update
            
        Returns:
            True if the edit was successful, False otherwise
        """
        try:
            if 0 <= index < len(self.history):
                for key, value in kwargs.items():
                    if key in self.history[index]:
                        self.history[index][key] = value
                
                # If the edited solution is the last one, update last_solution
                if index == len(self.history) - 1:
                    self.last_solution = self.history[index]
                
                self._save_history()
                return True
            return False
        except Exception:
            return False
    
    def _round_value(self, value, decimal_places):
        """Round a value to the specified number of decimal places."""
        return super()._round_value(value, decimal_places)
    
    def _format_value(self, value, decimal_places):
        """Format the value with the specified number of decimal places."""
        return super()._format_value(value, decimal_places)