from .base import NumericalMethodBase
from typing import Tuple, List, Dict
import numpy as np

class FalsePositionMethod(NumericalMethodBase):
    def solve(self, func_str: str, xl: float, xu: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the False Position method.
        
        The False Position (Regula Falsi) method uses linear interpolation to find
        better approximations to the root. It works by connecting the endpoints of the
        interval with a straight line and finding where this line crosses the x-axis.
        
        The method uses the formula:
            xr = xl - (f(xl) * (xu - xl)) / (f(xu) - f(xl))
        
        Key advantages:
        1. Like Bisection, it's a bracketing method that guarantees convergence
           if the initial interval contains a root
        2. Often converges faster than Bisection because it uses function values
           to make more intelligent guesses
        3. Can be more reliable than open methods like Newton-Raphson or Secant
        
        Key limitations:
        1. May converge slowly if the function is highly nonlinear
        2. One endpoint often remains fixed, causing slow convergence in some cases
        
        Args:
            func_str: The function f(x) as a string (e.g., "x**2 - 4")
            xl: Lower bound of the interval
            xu: Upper bound of the interval
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
        xr_old = 0  # Initialize previous root approximation
        
        # Check if the interval contains a root
        f_xl = float(f(xl))
        f_xu = float(f(xu))
        
        if f_xl * f_xu > 0:
            return None, [{"Error": "The interval does not bracket a root"}]
        
        # Check if either bound is already a root
        if abs(f_xl) < 1e-10:
            return xl, [{"Message": f"Lower bound {xl} is already a root"}]
        if abs(f_xu) < 1e-10:
            return xu, [{"Message": f"Upper bound {xu} is already a root"}]
        
        for i in range(max_iter):
            # Save previous approximation
            if i > 0:
                xr_old = xr
            
            # Calculate root approximation using False Position formula
            # The correct formula is: xr = xu - (f(xu) * (xl - xu)) / (f(xl) - f(xu))
            # This represents the x-intercept of the line connecting (xl, f(xl)) and (xu, f(xu))
            xr = xl - (f_xl * (xu - xl)) / (f_xu - f_xl)
            f_xr = float(f(xr))
            
            # Calculate absolute difference for convergence check
            abs_diff = abs(xr - xr_old) if i > 0 else "---"
            
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
                "Error %": self._format_error(error, decimal_places)
            }
            table.append(row)
            
            # Check if we found the exact root
            if abs(f_xr) < 1e-10:
                table.append({"Message": "Exact root found (within numerical precision)"})
                return xr, table
            
            # Check convergence criteria
            if i > 0 and stop_by_eps:
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