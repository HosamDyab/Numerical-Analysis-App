import sympy as sp
from .base import NumericalMethodBase
from typing import Tuple, List, Dict
import numpy as np

class NewtonRaphsonMethod(NumericalMethodBase):
    def solve(self, func_str: str, x0: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6,
              stop_criteria: str = "absolute", consecutive_check: bool = False, consecutive_tolerance: int = 3) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Newton-Raphson method.
        
        The Newton-Raphson method uses the formula:
            x_{i+1} = x_i - f(x_i)/f'(x_i)
        
        This represents finding where the tangent line at the current point crosses the x-axis.
        The method converges quadratically when close to the root, making it very efficient.
        
        Args:
            func_str: The function f(x) as a string (e.g., "-x**3 + 7.89*x + 11")
            x0: Initial guess
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            stop_criteria: Stopping criteria type ("absolute", "relative", "function")
                - "absolute": Stop based on absolute error |x_{i+1} - x_i|
                - "relative": Stop based on relative error |x_{i+1} - x_i|/|x_{i+1}| * 100%
                - "function": Stop based on function value |f(x_i)|
            consecutive_check: Whether to also check for convergence over consecutive iterations
            consecutive_tolerance: Number of consecutive iterations within tolerance to confirm convergence
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        try:
            f = self._create_function(func_str)
            f_prime = self._create_derivative(func_str)
            table = []
            error = "---"  # Initial error value
            
            # Check if initial guess is already a root
            fx = float(f(x0))
            if abs(fx) < 1e-10:
                return x0, [{"Message": f"Initial guess {x0} is already a root"}]

            # Store previous values to detect cycles
            previous_values = []
            
            # For consecutive iterations check
            consecutive_count = 0
            previous_error = float('inf')

            for i in range(max_iter):
                try:
                    # Evaluate function and its derivative at current point
                    fx = float(f(x0))
                    f_prime_x = float(f_prime(x0))
                    
                    # Check for division by zero or very small derivative
                    if abs(f_prime_x) < 1e-10:
                        return x0, table + [{"Warning": f"Derivative is close to zero at x = {x0}. Method may not converge."}]
                    
                    # Calculate next approximation using Newton-Raphson formula: x_{i+1} = x_i - f(x_i)/f'(x_i)
                    # This formula represents finding where the tangent line crosses the x-axis
                    x1 = x0 - (fx / f_prime_x)
                    
                    # Check for NaN or infinity results
                    if np.isnan(x1) or np.isinf(x1):
                        return x0, table + [{"Error": f"Numerical instability detected at iteration {i}. Try a different initial guess."}]
                    
                    # Calculate absolute difference for convergence check
                    abs_diff = abs(x1 - x0)
                    
                    # Calculate error based on selected criteria
                    if stop_criteria == "absolute":
                        error_value = abs_diff
                    elif stop_criteria == "relative":
                        if abs(x1) < 1e-10:
                            error_value = abs_diff  # Use absolute error for very small values
                        else:
                            error_value = abs_diff / abs(x1) * 100  # Percentage relative error
                    elif stop_criteria == "function":
                        error_value = abs(fx)  # Function value at current point
                    else:
                        error_value = abs_diff  # Default to absolute error
                    
                    # Calculate error percentage for display
                    if i > 0:
                        # Use absolute error for very small values
                        if abs(x1) < 1e-10:
                            error = abs_diff
                        else:
                            error = abs_diff / abs(x1) * 100  # Percentage error
                    
                    # Create row for the iteration table
                    row = {
                        "Iteration": i,
                        "Xi": self._round_value(x0, decimal_places),
                        "f(Xi)": self._round_value(fx, decimal_places),
                        "f'(Xi)": self._round_value(f_prime_x, decimal_places),
                        "Xi+1": self._round_value(x1, decimal_places),
                        "Error %": self._format_error(error, decimal_places)
                    }
                    table.append(row)

                    # Check if we found the exact root
                    f_x1 = float(f(x1))
                    if abs(f_x1) < 1e-10:
                        table.append({"Message": "Exact root found (within numerical precision)"})
                        return x1, table

                    # Check convergence criteria
                    if i > 0 and stop_by_eps:
                        # Direct comparison for absolute error - this is the most reliable approach
                        if eps_operator == "<=":
                            if abs_diff <= eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| <= {eps}"})
                                return x1, table
                        elif eps_operator == ">=":
                            if abs_diff >= eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| >= {eps}"})
                                return x1, table
                        elif eps_operator == "<":
                            if abs_diff < eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| < {eps}"})
                                return x1, table
                        elif eps_operator == ">":
                            if abs_diff > eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| > {eps}"})
                                return x1, table
                        elif eps_operator == "=":
                            if abs(abs_diff - eps) < 1e-10:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| = {eps}"})
                                return x1, table
                    
                    # Store previous error for consecutive check
                    previous_error = error_value
                    
                    # Check for cycles (oscillation)
                    if len(previous_values) > 2:
                        for prev_x in previous_values:
                            if abs(x1 - prev_x) < 1e-6:
                                return x1, table + [{"Warning": f"Method appears to be oscillating around the root. Stopping at iteration {i}."}]
                    
                    # Store current value for cycle detection
                    previous_values.append(x1)
                    if len(previous_values) > 5:  # Keep only the last 5 values
                        previous_values.pop(0)
                    
                    # Update value for next iteration
                    x0 = x1
                except Exception as e:
                    return None, table + [{"Error": f"Error in iteration {i}: {str(e)}"}]

            # Return the final approximation if max_iter is reached
            table.append({"Message": f"Stopped by reaching maximum iterations: {max_iter}"})
            return x0, table
        except Exception as e:
            return None, [{"Error": f"Failed to initialize Newton-Raphson method: {str(e)}"}]