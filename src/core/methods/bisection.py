from .base import NumericalMethodBase
from typing import Tuple, List, Dict

class BisectionMethod(NumericalMethodBase):
    def solve(self, func_str: str, xl: float, xu: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Bisection method.
        
        Args:
            func_str: The function f(x) as a string (e.g., "-x**3 + 7.89*x + 11")
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
        xr_old = 0.0  # Initialize xr_old for error calculation

        for i in range(max_iter):
            # Calculate midpoint using Bisection formula: xr = (xl + xu) / 2
            xr = (xl + xu) / 2
            
            # Evaluate function at interval bounds and midpoint
            fl = float(f(xl))
            fu = float(f(xu))
            fr = float(f(xr))
            
            # Calculate error percentage (only after first iteration)
            if i > 0:
                error = abs((xr - xr_old) / xr) * 100
            
            # Create row for the iteration table
            row = {
                "Iteration": i,
                "Xl": self._round_value(xl, decimal_places),
                "f(Xl)": self._round_value(fl, decimal_places),
                "Xu": self._round_value(xu, decimal_places),
                "f(Xu)": self._round_value(fu, decimal_places),
                "Xr": self._round_value(xr, decimal_places),
                "f(Xr)": self._round_value(fr, decimal_places),
                "Error %": self._format_value(error, decimal_places)
            }
            table.append(row)

            # Check if we found the exact root
            m = fl * fr
            if m == 0:
                return xr, table
            
            # Update interval bounds
            if m > 0:
                xl = xr
            else:
                xu = xr
                
            # Store current xr for next iteration's error calculation
            xr_old = xr

            # Check convergence criteria (matches C++ implementation)
            if stop_by_eps and i > 0 and error <= eps:
                return xr, table

        # Return the final approximation if max_iter is reached
        return xr, table