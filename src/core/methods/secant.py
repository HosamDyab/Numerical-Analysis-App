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
    
    def solve(self, func_str: str, x_minus_1: float, x0: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[Optional[float], List[Dict]]:
        """
        Solve for the root of a function using the Secant method.
        
        The Secant method uses two initial guesses x-1 and x0 to approximate the root.
        It iteratively computes a new approximation using the formula:
        x_{i+1} = x_i - f(x_i) * (x_{i-1} - x_i) / (f(x_{i-1}) - f(x_i))
        
        Args:
            func_str: The function f(x) as a string (e.g., "x**2 - 4")
            x_minus_1: First initial guess (x_{-1})
            x0: Second initial guess (x_0)
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        try:
            # Create the function from the string
            f = self._create_function(func_str)
            
            # Initialize variables
            table = []
            xi_minus_1 = x_minus_1  # x_{i-1}
            xi = x0                 # x_i
            iter_count = 0
            error = 100.0    # Initial error value
            
            # Main iteration loop
            while True:
                try:
                    # Calculate f(x_{i-1}) and f(x_i)
                    f_xi_minus_1 = float(f(xi_minus_1))
                    f_xi = float(f(xi))
                    
                    # Calculate the new approximation using the secant formula
                    # x_{i+1} = x_i - f(x_i) * (x_{i-1} - x_i) / (f(x_{i-1}) - f(x_i))
                    denominator = f_xi_minus_1 - f_xi
                    
                    # Check for division by zero
                    if abs(denominator) < 1e-10:
                        return None, [{"Error": "Division by zero encountered. The secant method failed to converge. Try different initial guesses."}]
                    
                    xi_plus_1 = xi - (f_xi * (xi_minus_1 - xi)) / denominator
                    
                    # Calculate error percentage (only after first iteration)
                    if iter_count > 0:
                        error = abs((xi_plus_1 - xi) / xi_plus_1) * 100
                    
                    # Create row for the iteration table
                    row = {
                        "Iteration": iter_count,
                        "Xi-1": self._round_value(xi_minus_1, decimal_places),
                        "f(Xi-1)": self._round_value(f_xi_minus_1, decimal_places),
                        "Xi": self._round_value(xi, decimal_places),
                        "f(Xi)": self._round_value(f_xi, decimal_places),
                        "Xi+1": self._round_value(xi_plus_1, decimal_places),
                        "Error %": "---" if iter_count == 0 else self._format_value(error, decimal_places)
                    }
                    table.append(row)
                    
                    # Update values for next iteration
                    xi_minus_1 = xi
                    xi = xi_plus_1
                    iter_count += 1
                    
                    # Check convergence criteria
                    # Continue if error > eps OR if it's the first iteration (iter_count == 1)
                    if not (error > eps or iter_count == 1) or iter_count >= max_iter:
                        break
                        
                except Exception as e:
                    # Handle any errors during iteration
                    return None, [{"Error": f"Error during iteration: {str(e)}"}]
            
            # Store the solution in history
            solution = {
                "func_str": func_str,
                "x_minus_1": x_minus_1,
                "x0": x0,
                "eps": eps,
                "eps_operator": eps_operator,
                "max_iter": max_iter,
                "stop_by_eps": stop_by_eps,
                "decimal_places": decimal_places,
                "root": xi,
                "iterations": table
            }
            self.last_solution = solution
            self.history.append(solution)
            self._save_history()
            
            # Return the final approximation
            return xi, table
            
        except Exception as e:
            return None, [{"Error": f"Error in secant method: {str(e)}"}]
    
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