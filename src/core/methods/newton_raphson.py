import sympy as sp
from .base import NumericalMethodBase
from typing import Tuple, List, Dict

class NewtonRaphsonMethod(NumericalMethodBase):
    def solve(self, func_str: str, x0: float, eps: float, eps_operator: str, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        """
        Solve for the root of a function using the Newton-Raphson method.
        
        Args:
            func_str: The function f(x) as a string (e.g., "-x**3 + 7.89*x + 11")
            x0: Initial guess
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            
        Returns:
            Tuple containing the root and a list of dictionaries with iteration details
        """
        f = self._create_function(func_str)
        f_prime = self._create_derivative(func_str)
        table = []
        error = "---"  # Initial error value

        for i in range(max_iter):
            # Evaluate function and its derivative at current point
            fx = float(f(x0))
            f_prime_x = float(f_prime(x0))
            
            # Check for division by zero
            if abs(f_prime_x) < 1e-10:
                return x0, table
            
            # Calculate next approximation using Newton-Raphson formula: xiPlus1 = xi - (f(xi) / fDash(xi))
            x1 = x0 - (fx / f_prime_x)
            
            # Calculate error percentage (only after first iteration)
            if i > 0:
                error = abs((x1 - x0) / x1) * 100
            
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

            # Check convergence criteria
            if stop_by_eps and i > 0 and self._check_convergence(error, eps, eps_operator):
                return x1, table
                
            # Update value for next iteration
            x0 = x1

        # Return the final approximation if max_iter is reached
        return x0, table