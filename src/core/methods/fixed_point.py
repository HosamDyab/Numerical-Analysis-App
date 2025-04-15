from .base import NumericalMethodBase
from typing import Tuple, List, Dict
import numpy as np

class FixedPointMethod(NumericalMethodBase):
    def solve(self, func_str: str, x0: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6, 
              stop_criteria: str = "absolute", consecutive_check: bool = False, consecutive_tolerance: int = 3) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Fixed Point Iteration method.
        
        The Fixed Point method works by reformulating the equation f(x) = 0 as x = g(x),
        then iterating using the formula:
            x_{i+1} = g(x_i)
        
        For convergence, the function g(x) must satisfy |g'(x)| < 1 near the root.
        If this condition is met, the method will converge linearly to the fixed point.
        
        The algorithm follows these steps:
        1. Start with an initial guess x0
        2. Compute x1 = g(x0)
        3. Calculate the approximate relative error: |x1 - x0|/|x1| * 100%
        4. Check if error satisfies the stopping criterion
        5. If not, set x0 = x1 and repeat from step 2
        
        Key considerations:
        1. The choice of g(x) is critical - different reformulations can lead to
           different convergence behaviors
        2. If |g'(x)| >= 1 near the root, the method may diverge
        3. The method is simple to implement but may converge slowly
        
        Args:
            func_str: The function g(x) as a string (e.g., "sqrt(2-x)")
            x0: Initial guess
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            stop_criteria: Stopping criteria type ("absolute", "relative", "function")
                - "absolute": Stop based on absolute error |x_{i+1} - x_i|
                - "relative": Stop based on relative error |x_{i+1} - x_i|/|x_{i+1}| * 100%
                - "function": Stop based on function value |g(x_i) - x_i|
            consecutive_check: Whether to also check for convergence over consecutive iterations
            consecutive_tolerance: Number of consecutive iterations within tolerance to confirm convergence
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        g = self._create_function(func_str)
        table = []
        error = "---"  # Initial error value
        x_current = x0
        
        # Check if initial guess is already a fixed point
        g_x0 = float(g(x0))
        if abs(g_x0 - x0) < 1e-10:
            return x0, [{"Message": f"Initial guess {x0} is already a fixed point"}]

        # Store the previous iterations to detect cycles
        previous_values = []
        
        # For consecutive iterations check
        consecutive_count = 0
        previous_error = float('inf')

        for i in range(max_iter):
            # Calculate next approximation using Fixed Point formula: x_{i+1} = g(x_i)
            # In fixed point iteration, we directly apply the function g(x) to find the next approximation
            # For convergence, |g'(x)| < 1 should be satisfied near the root
            try:
                x_next = float(g(x_current))
                
                # Check for NaN or infinity results
                if np.isnan(x_next) or np.isinf(x_next):
                    return x_current, table + [{"Error": f"Numerical instability detected at iteration {i}. The function g(x) may not be suitable for fixed point iteration."}]
                
                # Calculate absolute difference for convergence check
                abs_diff = abs(x_next - x_current)
                
                # Calculate function value error
                func_error = abs(x_next - x_current)
                
                # Calculate error based on selected criteria
                if stop_criteria == "absolute":
                    error_value = abs_diff
                elif stop_criteria == "relative":
                    if abs(x_next) < 1e-10:
                        error_value = abs_diff  # Use absolute error for very small values
                    else:
                        error_value = abs_diff / abs(x_next) * 100  # Percentage relative error
                elif stop_criteria == "function":
                    error_value = func_error
                else:
                    error_value = abs_diff  # Default to absolute error
                
                # Calculate error for display - using the textbook formula
                if i > 0:
                    # Use relative error as in the textbook: |x_{i+1} - x_i|/|x_{i+1}| * 100%
                    if abs(x_next) < 1e-10:
                        error = abs_diff  # Use absolute error for very small values
                    else:
                        error = abs_diff / abs(x_next) * 100  # Percentage relative error
                
                # Create row for the iteration table
                row = {
                    "Iteration": i,
                    "Xi": self._round_value(x_current, decimal_places),
                    "g(Xi)": self._round_value(x_next, decimal_places),
                    "Error %": self._format_error(error, decimal_places)
                }
                table.append(row)
                
                # Check if we found a fixed point (within numerical precision)
                if abs_diff < 1e-10:
                    table.append({"Message": "Exact fixed point found (within numerical precision)"})
                    return x_next, table
                
                # Check convergence criteria
                if i > 0 and stop_by_eps:
                    # For percentage-based epsilon (when eps > 1), use relative error
                    if eps > 1:
                        # Calculate relative error as percentage
                        rel_error = abs_diff / abs(x_next) * 100 if abs(x_next) > 1e-10 else abs_diff
                        
                        # Direct comparison for relative error
                        if eps_operator == "<=":
                            if rel_error <= eps:
                                table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% <= {eps}%"})
                                return x_next, table
                        elif eps_operator == ">=":
                            if rel_error >= eps:
                                table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% >= {eps}%"})
                                return x_next, table
                        elif eps_operator == "<":
                            if rel_error < eps:
                                table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% < {eps}%"})
                                return x_next, table
                        elif eps_operator == ">":
                            if rel_error > eps:
                                table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% > {eps}%"})
                                return x_next, table
                        elif eps_operator == "=":
                            if abs(rel_error - eps) < 1e-10:
                                table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% = {eps}%"})
                                return x_next, table
                    else:
                        # Direct comparison for absolute error - this is the most reliable approach
                        if eps_operator == "<=":
                            if abs_diff <= eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| <= {eps}"})
                                return x_next, table
                        elif eps_operator == ">=":
                            if abs_diff >= eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| >= {eps}"})
                                return x_next, table
                        elif eps_operator == "<":
                            if abs_diff < eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| < {eps}"})
                                return x_next, table
                        elif eps_operator == ">":
                            if abs_diff > eps:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| > {eps}"})
                                return x_next, table
                        elif eps_operator == "=":
                            if abs(abs_diff - eps) < 1e-10:
                                table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| = {eps}"})
                                return x_next, table
                
                # Store previous error for consecutive check
                previous_error = error_value
                
                # Check for divergence (if values are getting too large)
                if abs(x_next) > 1e10:
                    return None, table + [{"Error": f"Method is diverging. The function g(x) may not satisfy the convergence criteria for fixed point iteration."}]
                
                # Check for cycles (oscillation)
                if len(previous_values) > 2:
                    for prev_x in previous_values:
                        if abs(x_next - prev_x) < 1e-6:
                            return x_next, table + [{"Warning": f"Method appears to be oscillating. The function g(x) may not be suitable for fixed point iteration."}]
                
                # Store current value to detect cycles
                previous_values.append(x_next)
                if len(previous_values) > 5:  # Keep only the last 5 values
                    previous_values.pop(0)
                
                # Update value for next iteration
                x_current = x_next
            except Exception as e:
                return None, table + [{"Error": f"Error in iteration {i}: {str(e)}"}]

        # Add a message to the table indicating we stopped by max iterations
        table.append({"Message": f"Stopped by reaching maximum iterations: {max_iter}"})
        return x_current, table

    def _check_convergence(self, error: float, eps: float, eps_operator: str) -> bool:
        """
        Check if the error satisfies the convergence criteria.
        
        Args:
            error: The current error value
            eps: The error tolerance
            eps_operator: The comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            
        Returns:
            True if the error satisfies the convergence criteria, False otherwise
        """
        try:
            if eps_operator == "<=":
                return error <= eps
            elif eps_operator == ">=":
                return error >= eps
            elif eps_operator == "<":
                return error < eps
            elif eps_operator == ">":
                return error > eps
            elif eps_operator == "=":
                return abs(error - eps) < 1e-10  # Use a small tolerance for floating-point comparison
            else:
                raise ValueError(f"Invalid epsilon operator: {eps_operator}")
        except Exception as e:
            self.logger.error(f"Error in convergence check: {str(e)}")
            return False

    def _round_value(self, value: float, decimal_places: int) -> float:
        """
        Round a value to the specified number of decimal places.
        
        Args:
            value: The value to round
            decimal_places: The number of decimal places
            
        Returns:
            The rounded value
        """
        return round(value, decimal_places)

    def _format_error(self, error, decimal_places: int) -> str:
        """
        Format the error value with the specified number of decimal places.
        
        Args:
            error: The error value
            decimal_places: The number of decimal places
            
        Returns:
            The formatted error value
        """
        if isinstance(error, (int, float)):
            return f"{error:.{decimal_places}f}"
        return str(error)