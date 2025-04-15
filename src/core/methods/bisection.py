from .base import NumericalMethodBase
from typing import Tuple, List, Dict
import numpy as np

class BisectionMethod(NumericalMethodBase):
    def solve(self, func_str: str, xl: float, xu: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6,
              stop_criteria: str = "absolute", consecutive_check: bool = False, consecutive_tolerance: int = 3) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Bisection method.
        
        The Bisection method works by repeatedly halving the interval and selecting
        the subinterval where the function changes sign. This guarantees convergence
        if the initial interval contains a root.
        
        Key steps:
        1. Start with interval [xl, xu] where f(xl) and f(xu) have opposite signs
        2. Compute midpoint xr = (xl + xu)/2
        3. If f(xl) * f(xr) < 0, the root is in [xl, xr], so set xu = xr
        4. Otherwise, the root is in [xr, xu], so set xl = xr
        5. Repeat until convergence criteria are met
        
        Args:
            func_str: The function f(x) as a string (e.g., "x**2 - 4")
            xl: Lower bound of the interval
            xu: Upper bound of the interval
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            stop_criteria: Stopping criteria type ("absolute", "relative", "function", "interval")
                - "absolute": Stop based on absolute error |x_{i+1} - x_i|
                - "relative": Stop based on relative error |x_{i+1} - x_i|/|x_{i+1}| * 100%
                - "function": Stop based on function value |f(x_i)|
                - "interval": Stop based on interval width |xu - xl|
            consecutive_check: Whether to also check for convergence over consecutive iterations
            consecutive_tolerance: Number of consecutive iterations within tolerance to confirm convergence
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        f = self._create_function(func_str)
        table = []
        error = "---"  # Initial error value
        xr_old = 0  # Initialize previous root approximation
        
        # For consecutive iterations check
        consecutive_count = 0
        previous_error = float('inf')
        
        # Check if the interval contains a root
        f_xl = float(f(xl))
        f_xu = float(f(xu))
        
        if f_xl * f_xu > 0:
            return None, [{"Error": "The interval does not bracket a root. Ensure f(xl) and f(xu) have opposite signs."}]
        
        # Check if either bound is already a root
        if abs(f_xl) < 1e-10:
            return xl, [{"Message": f"Lower bound {xl} is already a root"}]
        if abs(f_xu) < 1e-10:
            return xu, [{"Message": f"Upper bound {xu} is already a root"}]
        
        for i in range(max_iter):
            # Save previous approximation
            if i > 0:
                xr_old = xr
            
            # Calculate midpoint - this is the key step in the bisection method
            # It halves the interval in each iteration, ensuring linear convergence
            xr = (xl + xu) / 2
            f_xr = float(f(xr))
            
            # Calculate absolute difference for convergence check
            abs_diff = abs(xr - xr_old) if i > 0 else "---"
            
            # Calculate interval width
            interval_width = abs(xu - xl)
            
            # Calculate error based on selected criteria
            if i > 0:
                if stop_criteria == "absolute":
                    error_value = abs_diff
                elif stop_criteria == "relative":
                    if abs(xr) < 1e-10:
                        error_value = abs_diff  # Use absolute error for very small values
                    else:
                        error_value = abs_diff / abs(xr) * 100  # Percentage relative error
                elif stop_criteria == "function":
                    error_value = abs(f_xr)  # Function value at current point
                elif stop_criteria == "interval":
                    error_value = interval_width  # Width of the current interval
                else:
                    error_value = abs_diff  # Default to absolute error
            else:
                error_value = float('inf')  # No error for first iteration
            
            # Calculate error for display
            if i > 0:
                # Use absolute error for very small values
                if abs(xr) < 1e-10:
                    error = abs_diff
                else:
                    error = abs_diff / abs(xr) * 100  # Percentage error
            
            # Create row for the iteration table
            row = {
                "Iteration": i,
                "Xl": self._round_value(xl, decimal_places),
                "Xu": self._round_value(xu, decimal_places),
                "Xr": self._round_value(xr, decimal_places),
                "f(Xr)": self._round_value(f_xr, decimal_places),
                "Error %": self._format_error(error, decimal_places),
            }
            table.append(row)
            
            # Check if we found the exact root
            if abs(f_xr) < 1e-10:
                table.append({"Message": "Exact root found (within numerical precision)"})
                return xr, table
            
            # Check convergence criteria
            if i > 0 and stop_by_eps:
                # For percentage-based epsilon (when eps > 1), use relative error
                if eps > 1:
                    # Calculate relative error as percentage
                    rel_error = abs_diff / abs(xr) * 100 if abs(xr) > 1e-10 else abs_diff
                    
                    # Direct comparison for relative error
                    if eps_operator == "<=":
                        if rel_error <= eps:
                            table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% <= {eps}%"})
                            return xr, table
                    elif eps_operator == ">=":
                        if rel_error >= eps:
                            table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% >= {eps}%"})
                            return xr, table
                    elif eps_operator == "<":
                        if rel_error < eps:
                            table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% < {eps}%"})
                            return xr, table
                    elif eps_operator == ">":
                        if rel_error > eps:
                            table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% > {eps}%"})
                            return xr, table
                    elif eps_operator == "=":
                        if abs(rel_error - eps) < 1e-10:
                            table.append({"Message": f"Stopped by Epsilon: Relative Error {rel_error:.6f}% = {eps}%"})
                            return xr, table
                else:
                    # Direct comparison for absolute error - this is the most reliable approach
                    if eps_operator == "<=":
                        if abs_diff <= eps:
                            table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| <= {eps}"})
                            return xr, table
                    elif eps_operator == ">=":
                        if abs_diff >= eps:
                            table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| >= {eps}"})
                            return xr, table
                    elif eps_operator == "<":
                        if abs_diff < eps:
                            table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| < {eps}"})
                            return xr, table
                    elif eps_operator == ">":
                        if abs_diff > eps:
                            table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| > {eps}"})
                            return xr, table
                    elif eps_operator == "=":
                        if abs(abs_diff - eps) < 1e-10:
                            table.append({"Message": f"Stopped by Epsilon: |x{i+1} - x{i}| = {eps}"})
                            return xr, table
            
            # Store previous error for consecutive check
            previous_error = error_value
            
            # Update the interval
            if f_xl * f_xr < 0:
                xu = xr
                f_xu = f_xr
            else:
                xl = xr
                f_xl = f_xr
        
        # Return the final approximation if max_iter is reached
        table.append({"Message": f"Stopped by reaching maximum iterations: {max_iter}"})
        return xr, table