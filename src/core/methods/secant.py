from .base import NumericalMethodBase
from typing import Tuple, List, Dict, Optional
import sympy as sp
import numpy as np
import math
import json
import os
from collections import OrderedDict

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
        
        The Secant method is a variation of Newton's method that approximates the derivative
        using a finite difference approximation. It uses two previous points to estimate the
        next point.
        
        Key steps:
        1. Start with two initial guesses x0 and x1
        2. Compute the next approximation using: x2 = x1 - f(x1) * (x1 - x0) / (f(x1) - f(x0))
        3. Update x0 = x1 and x1 = x2
        4. Repeat until convergence criteria are met
        
        Args:
            func_str: The function f(x) as a string (e.g., "x**2 - 4")
            x0: First initial guess
            x1: Second initial guess
            eps: Error tolerance (epsilon)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        try:
            f = self._create_function(func_str)
            table = []
            error = "---"  # Initial error value
            
            # Calculate function values at initial points
            f_x0 = float(f(x0))
            f_x1 = float(f(x1))
            
            # Check if either initial guess is already a root
            if abs(f_x0) < 1e-10:
                result_row = OrderedDict([
                    ("Message", f"First initial guess {x0} is already a root"),
                    ("Status", "SUCCESS"),
                    ("Details", f"f(x0) ≈ 0")
                ])
                return x0, [result_row]
            if abs(f_x1) < 1e-10:
                result_row = OrderedDict([
                    ("Message", f"Second initial guess {x1} is already a root"),
                    ("Status", "SUCCESS"),
                    ("Details", f"f(x1) ≈ 0")
                ])
                return x1, [result_row]
            
            # Initial row with function values
            initial_row = OrderedDict([
                ("Initial Points", "Values"),
                ("x0", self._round_value(x0, decimal_places)),
                ("f(x0)", self._round_value(f_x0, decimal_places)),
                ("x1", self._round_value(x1, decimal_places)),
                ("f(x1)", self._round_value(f_x1, decimal_places))
            ])
            table.append(initial_row)
            
            # Add the first row for the initial points
            row = OrderedDict([
                ("Iteration", 0),
                ("Xi-1", self._round_value(x0, decimal_places)),
                ("Xi", self._round_value(x1, decimal_places)),
                ("f(Xi-1)", self._round_value(f_x0, decimal_places)),
                ("f(Xi)", self._round_value(f_x1, decimal_places)),
                ("Xi+1", "---"),
                ("Error %", "---"),
                ("Status", "Starting...")
            ])
            table.append(row)
            
            # Main iteration loop
            for i in range(1, max_iter + 1):
                # Check if we can compute the next iteration (avoid division by zero)
                if abs(f_x1 - f_x0) < 1e-10:
                    warning_row = OrderedDict([
                        ("Warning", f"Secant denominator (f(x1) - f(x0)) is too close to zero: {f_x1 - f_x0}"),
                        ("Status", "ZERO_DENOMINATOR"),
                        ("Details", "The function values at x0 and x1 are too close, causing numerical instability")
                    ])
                    table.append(warning_row)
                    return x1, table  # Return the current best approximation
                
                # Calculate the next approximation using the secant formula
                x_next = x1 - f_x1 * (x1 - x0) / (f_x1 - f_x0)
                
                try:
                    f_x_next = float(f(x_next))
                except (ValueError, ZeroDivisionError, OverflowError, RuntimeError) as e:
                    error_row = OrderedDict([
                        ("Error", f"Function evaluation error at x = {x_next}"),
                        ("Status", "EVALUATION_ERROR"),
                        ("Details", str(e))
                    ])
                    table.append(error_row)
                    return x1, table  # Return the previous approximation
                
                # Check for NaN or Inf
                if math.isnan(x_next) or math.isinf(x_next):
                    error_row = OrderedDict([
                        ("Error", f"Invalid value: {'NaN' if math.isnan(x_next) else 'Infinity'}"),
                        ("Status", "INVALID_VALUE"),
                        ("Details", "The method has diverged or encountered a numeric issue")
                    ])
                    table.append(error_row)
                    return x1, table
                    
                # Calculate error for this iteration
                if abs(x_next) < 1e-10:
                    error = abs(x_next - x1)  # Absolute error for values close to zero
                else:
                    error = abs((x_next - x1) / x_next) * 100  # Relative percent error
                
                # Add row for this iteration
                row = OrderedDict([
                    ("Iteration", i),
                    ("Xi-1", self._round_value(x0, decimal_places)),
                    ("Xi", self._round_value(x1, decimal_places)),
                    ("f(Xi-1)", self._round_value(f_x0, decimal_places)),
                    ("f(Xi)", self._round_value(f_x1, decimal_places)),
                    ("Xi+1", self._round_value(x_next, decimal_places)),
                    ("f(Xi+1)", self._round_value(f_x_next, decimal_places)),
                    ("Error %", self._format_error(error, decimal_places)),
                    ("Status", "Searching..." if i < max_iter else "Max iterations reached")
                ])
                table.append(row)
                
                # Check if we found the exact root
                if abs(f_x_next) < 1e-10:
                    result_row = OrderedDict([
                        ("Message", "Exact root found (within numerical precision)"),
                        ("Status", "SUCCESS"),
                        ("Details", f"f(x) ≈ 0 at x = {self._round_value(x_next, decimal_places)}")
                    ])
                    table.append(result_row)
                    return x_next, table
                
                # Check convergence based on epsilon if stop_by_eps is True
                if stop_by_eps:
                    abs_diff = abs(x_next - x1)
                    
                    # For percentage-based epsilon (when eps > 1), use relative error
                    if eps > 1:
                        # Calculate relative error as percentage
                        rel_error = abs_diff / abs(x_next) * 100 if abs(x_next) > 1e-10 else abs_diff
                        
                        # Check based on the epsilon operator
                        converged = False
                        message = ""
                        
                        if eps_operator == "<=" and rel_error <= eps:
                            converged = True
                            message = f"Relative Error {rel_error:.6f}% <= {eps}%"
                        elif eps_operator == ">=" and rel_error >= eps:
                            converged = True
                            message = f"Relative Error {rel_error:.6f}% >= {eps}%"
                        elif eps_operator == "<" and rel_error < eps:
                            converged = True
                            message = f"Relative Error {rel_error:.6f}% < {eps}%"
                        elif eps_operator == ">" and rel_error > eps:
                            converged = True
                            message = f"Relative Error {rel_error:.6f}% > {eps}%"
                        elif eps_operator == "=" and abs(rel_error - eps) < 1e-10:
                            converged = True
                            message = f"Relative Error {rel_error:.6f}% = {eps}%"
                        
                        if converged:
                            result_row = OrderedDict([
                                ("Message", f"Stopped by Epsilon: {message}"),
                                ("Status", "CONVERGED"),
                                ("Details", f"Achieved desired accuracy based on relative error")
                            ])
                            table.append(result_row)
                            return x_next, table
                    else:
                        # Use absolute error for small epsilon values
                        converged = False
                        message = ""
                        
                        if eps_operator == "<=" and abs_diff <= eps:
                            converged = True
                            message = f"|x{i+1} - x{i}| <= {eps}"
                        elif eps_operator == ">=" and abs_diff >= eps:
                            converged = True
                            message = f"|x{i+1} - x{i}| >= {eps}"
                        elif eps_operator == "<" and abs_diff < eps:
                            converged = True
                            message = f"|x{i+1} - x{i}| < {eps}"
                        elif eps_operator == ">" and abs_diff > eps:
                            converged = True
                            message = f"|x{i+1} - x{i}| > {eps}"
                        elif eps_operator == "=" and abs(abs_diff - eps) < 1e-10:
                            converged = True
                            message = f"|x{i+1} - x{i}| = {eps}"
                        
                        if converged:
                            result_row = OrderedDict([
                                ("Message", f"Stopped by Epsilon: {message}"),
                                ("Status", "CONVERGED"),
                                ("Details", f"Achieved desired accuracy based on absolute error")
                            ])
                            table.append(result_row)
                            return x_next, table
                
                # Update values for next iteration
                x0, f_x0 = x1, f_x1
                x1, f_x1 = x_next, f_x_next
            
            # If we reach here, we've hit the maximum number of iterations
            result_row = OrderedDict([
                ("Message", f"Maximum iterations reached ({max_iter})"),
                ("Status", "MAX_ITERATIONS"),
                ("Details", f"Consider increasing the maximum iterations or trying different initial points")
            ])
            table.append(result_row)
            return x1, table
            
        except Exception as e:
            # Handle any unexpected exceptions
            error_row = OrderedDict([
                ("Error", f"An unexpected error occurred: {str(e)}"),
                ("Status", "ERROR"),
                ("Details", "Check your inputs and try again")
            ])
            return None, [error_row]
    
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
    
    def _format_error(self, value, decimal_places):
        """Format the error with the specified number of decimal places."""
        return super()._format_error(value, decimal_places)