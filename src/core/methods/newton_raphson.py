import sympy as sp
from .base import NumericalMethodBase
from typing import Tuple, List, Dict, Optional, Union
import numpy as np
import math
from enum import Enum
import pandas as pd
from dataclasses import dataclass
from collections import OrderedDict

class ConvergenceStatus(str, Enum):
    """Enumeration for different convergence statuses."""
    CONVERGED = "converged"
    DIVERGED = "diverged"
    MAX_ITERATIONS = "max_iterations"
    ZERO_DERIVATIVE = "zero_derivative"
    NUMERICAL_ERROR = "numerical_error"
    DOMAIN_ERROR = "domain_error"
    OSCILLATING = "oscillating"
    ERROR = "error"

@dataclass
class NewtonRaphsonResult:
    """Data class to hold the result of a Newton-Raphson iteration."""
    root: Union[float, str]
    iterations: List[Dict]
    status: ConvergenceStatus
    messages: List[str]
    iterations_table: pd.DataFrame
    
    def __iter__(self):
        """
        Allow the NewtonRaphsonResult to be unpacked as a tuple.
        This maintains backward compatibility with code that expects (root, iterations) tuple.
        
        Returns:
            Iterator that yields root and iterations
        """
        yield self.root
        yield self.iterations

class NewtonRaphsonMethod(NumericalMethodBase):
    def __init__(self):
        """Initialize the Newton-Raphson method."""
        super().__init__()
        self.divergence_threshold = 1e15
        
    def _create_function(self, func_str: str):
        """
        Creates a callable function from a string with domain checking.
        
        Args:
            func_str: The function as a string
            
        Returns:
            A callable function with domain validation
        """
        import numpy as np
        
        # IMPORTANT: Using eval is a security risk if func_str comes from untrusted input
        allowed_names = {
            "np": np,
            "sqrt": np.sqrt, "sin": np.sin, "cos": np.cos, "tan": np.tan,
            "exp": np.exp, "log": np.log, "log10": np.log10,
            "abs": np.abs, "pi": np.pi, "e": np.e,
        }
        
        try:
            # Prepare the function string with domain checks
            safe_func_str = func_str
            
            # Check for sqrt to add domain validation
            if "sqrt" in safe_func_str:
                # Create a wrapper function that checks domain for sqrt
                func_code = f"""
def _user_func(x):
    # Handle scalar case
    if isinstance(x, (int, float)):
        # Domain check for sqrt
        if {"np.sqrt" in safe_func_str and "x < 0" or "sqrt(x)" in safe_func_str and "x < 0"}:
            return float('nan')  # Return NaN for invalid domain
        return {safe_func_str}
    else:
        # Handle array case (assume numpy array)
        import numpy as np
        result = np.full_like(x, np.nan, dtype=float)
        valid_mask = (x >= 0)  # Valid domain for sqrt
        result[valid_mask] = {safe_func_str.replace('x', 'x[valid_mask]')}
        return result
"""
            else:
                # Regular function without domain restrictions
                func_code = f"def _user_func(x): return {safe_func_str}"
            
            # Prepare the execution environment
            local_namespace = {}
            global_namespace = {"np": np}
            global_namespace.update(allowed_names)
            
            exec(func_code, global_namespace, local_namespace)
            return local_namespace['_user_func']
            
        except Exception as e:
            self.logger.error(f"Error creating function from '{func_str}': {e}")
            # Return a function that returns NaN to indicate error
            return lambda x: float('nan')

    def _create_derivative(self, func_str: str):
        """
        Creates a callable function for the derivative of a function string with domain checking.
        
        Args:
            func_str: The function as a string
            
        Returns:
            A callable function that evaluates the derivative with domain validation
        """
        import sympy as sp
        import numpy as np
        
        try:
            # Define symbolic variable
            x = sp.Symbol('x')
            
            # Fix common numpy functions before parsing
            preprocessed_func = func_str
            
            # Replace numpy functions with sympy equivalents
            replacements = {
                'np.sqrt': 'sqrt',
                'np.sin': 'sin',
                'np.cos': 'cos',
                'np.tan': 'tan',
                'np.exp': 'exp',
                'np.log': 'log'
            }
            
            for np_func, sp_func in replacements.items():
                preprocessed_func = preprocessed_func.replace(np_func, sp_func)
            
            # Replace ** with ^ for sympy
            preprocessed_func = preprocessed_func.replace('**', '^')
            
            # Parse the function using sympy
            try:
                f_sympy = sp.sympify(preprocessed_func)
            except Exception as parse_error:
                self.logger.error(f"Error parsing function: {parse_error}")
                raise ValueError(f"Could not parse function: {func_str}. Error: {parse_error}")
            
            # Calculate the derivative symbolically
            try:
                f_prime_sympy = sp.diff(f_sympy, x)
            except Exception as diff_error:
                self.logger.error(f"Error calculating derivative: {diff_error}")
                raise ValueError(f"Could not calculate derivative: {func_str}. Error: {diff_error}")
            
            # Convert back to a string with Python syntax
            f_prime_str = str(f_prime_sympy)
            
            # Replace sympy functions with numpy equivalents
            inverse_replacements = {
                'sqrt': 'np.sqrt',
                'sin': 'np.sin', 
                'cos': 'np.cos',
                'tan': 'np.tan',
                'exp': 'np.exp',
                'log': 'np.log'
            }
            
            for sp_func, np_func in inverse_replacements.items():
                f_prime_str = f_prime_str.replace(sp_func, np_func)
            
            # Replace ^ with ** for Python
            f_prime_str = f_prime_str.replace('^', '**')
            
            self.logger.debug(f"Original function: {func_str}")
            self.logger.debug(f"Calculated derivative: {f_prime_str}")
            
            # Create a domain-aware callable function
            # The derivative of a function with sqrt will have sqrt in denominator
            # which requires additional domain checking
            if "sqrt" in f_prime_str:
                code = f"""
def _derivative_func(x):
    # Handle scalar case
    if isinstance(x, (int, float)):
        # Domain check for sqrt and division by zero
        if x <= 0:  # Undefined at x=0 (division) and x<0 (sqrt)
            return float('nan')
        return {f_prime_str}
    else:
        # Handle array case (assume numpy array)
        import numpy as np
        result = np.full_like(x, np.nan, dtype=float)
        valid_mask = (x > 0)  # Valid domain for sqrt in denominator
        x_valid = x[valid_mask]
        try:
            result[valid_mask] = {f_prime_str.replace('x', 'x_valid')}
        except Exception as e:
            # Handle calculation errors
            pass  # Can't access self.logger from generated code
        return result
"""
                local_namespace = {}
                global_namespace = {"np": np}
                exec(code, global_namespace, local_namespace)
                return local_namespace['_derivative_func']
            else:
                # Use regular function creation for derivatives without domain issues
                return self._create_function(f_prime_str)
            
        except Exception as e:
            self.logger.error(f"Error creating derivative function: {str(e)}")
            # Return a function that returns NaN to indicate error
            return lambda x: float('nan')

    def solve(self, func_str: str, x0: float, eps: float = None, eps_operator: str = "<=", 
              max_iter: int = None, stop_by_eps: bool = True, decimal_places: int = 6,
              stop_criteria: str = "relative", consecutive_check: bool = False, 
              consecutive_tolerance: int = 3) -> NewtonRaphsonResult:
        """
        Solve for the root of a function using the Newton-Raphson method.
        
        The Newton-Raphson method uses the formula:
            x_{i+1} = x_i - f(x_i)/f'(x_i)
        
        This represents finding where the tangent line at the current point crosses the x-axis.
        The method converges quadratically when close to the root, making it very efficient.
        It works well with a wide range of functions including trigonometric (sin, cos, tan),
        exponential (exp), logarithmic (log), square roots (sqrt), and combinations thereof.
        
        Args:
            func_str: The function f(x) as a string (e.g., "-x**3 + 7.89*x + 11", "cos(x) - x", "exp(x) - 5")
            x0: Initial guess
            eps: Error tolerance (used if stop_by_eps is True)
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            max_iter: Maximum number of iterations
            stop_by_eps: Whether to stop when error satisfies epsilon condition
            decimal_places: Number of decimal places for rounding
            stop_criteria: Stopping criteria type ("absolute", "relative", "function")
                - "absolute": Stop based on absolute error |x_{i+1} - x_i|
                - "relative": Stop based on approximate relative error |(x_{i+1} - x_i)/x_{i+1}| * 100%
                - "function": Stop based on function value |f(x_i)|
            consecutive_check: Whether to also check for convergence over consecutive iterations
            consecutive_tolerance: Number of consecutive iterations within tolerance to confirm convergence
            
        Returns:
            NewtonRaphsonResult containing the root, a list of dictionaries with iteration details,
            convergence status, messages, and a pandas DataFrame with the iterations table
        """
        # Ensure all required imports are available within the method
        import numpy as np
        
        # Use default values if not provided
        max_iter = max_iter if max_iter is not None else 50
        eps = eps if eps is not None else 0.0001
        
        # Initialize result table
        table = OrderedDict()
        
        try:
            self.logger.debug(f"Starting NewtonRaphsonMethod.solve with: func_str='{func_str}', x0={x0}, eps={eps}, max_iter={max_iter}")
            
            # Create function and its derivative
            try:
                f = self._create_function(func_str)
                f_prime = self._create_derivative(func_str)
            except Exception as e:
                self.logger.error(f"Failed to create function or derivative: {str(e)}")
                table["Iteration 0"] = OrderedDict([
                    ("Iteration", "Error"),
                    ("Xi", "Function Creation"),
                    ("f(Xi)", str(e)),
                    ("f'(Xi)", "---"),
                    ("Error %", "---"),
                    ("Xi+1", "---")
                ])
                return NewtonRaphsonResult(None, [], ConvergenceStatus.ERROR, [f"Failed to create function or derivative: {str(e)}"], pd.DataFrame(table))
            
            # Initialize variables
            x_current = float(x0)
            iter_count = 0
            relative_error = float('inf')
            error_display = "---"  # Initial error display
            consecutive_count = 0
            previous_values = []  # For cycle detection
            status = ConvergenceStatus.DIVERGED  # Default status
            
            # Check if initial guess is already a root
            try:
                fx_initial = float(f(x_current))
                if abs(fx_initial) < 1e-10:
                    table["Iteration 0"] = OrderedDict([
                        ("Iteration", "Info"),
                        ("Xi", self._round_value(x_current, decimal_places)),
                        ("f(Xi)", "≈ 0"),
                        ("f'(Xi)", "---"),
                        ("Error %", "---"),
                        ("Xi+1", "---")
                    ])
                    table["Iteration 1"] = OrderedDict([
                        ("Iteration", "Result"),
                        ("Xi", self._round_value(x_current, decimal_places)),
                        ("f(Xi)", "Initial guess is already a root (within numerical precision)"),
                        ("f'(Xi)", "---"),
                        ("Error %", "---"),
                        ("Xi+1", "---")
                    ])
                    return NewtonRaphsonResult(x_current, [], ConvergenceStatus.CONVERGED, ["Initial guess is already a root (within numerical precision)"], pd.DataFrame(table))
            except Exception as e:
                self.logger.error(f"Error evaluating function at initial guess: {str(e)}")
                table["Iteration 0"] = OrderedDict([
                    ("Iteration", "Error"),
                    ("Xi", self._round_value(x_current, decimal_places)),
                    ("f(Xi)", f"Error evaluating function: {str(e)}"),
                    ("f'(Xi)", "---"),
                    ("Error %", "---"),
                    ("Xi+1", "---")
                ])
                return NewtonRaphsonResult(None, [], ConvergenceStatus.ERROR, [f"Error evaluating function at initial guess: {str(e)}"], pd.DataFrame(table))
            
            # Main iteration loop
            for i in range(max_iter):
                iter_count = i + 1
                x_old = x_current
                
                try:
                    # Step 1: Evaluate function and its derivative
                    fx = float(f(x_old))
                    fpx = float(f_prime(x_old))
                    
                    # Step 2: Check for zero or very small derivative (to avoid division by zero)
                    if abs(fpx) < 1e-10 or math.isnan(fpx):
                        status = ConvergenceStatus.ZERO_DERIVATIVE
                        # Add current iteration to table
                        table[f"Iteration {iter_count}"] = OrderedDict([
                            ("Iteration", iter_count),
                            ("Xi", self._round_value(x_old, decimal_places)),
                            ("f(Xi)", self._round_value(fx, decimal_places)),
                            ("f'(Xi)", "≈0" if abs(fpx) < 1e-10 else "NaN"),
                            ("Error %", error_display),
                            ("Xi+1", "---")
                        ])
                        # Add warning about zero derivative
                        table[f"Iteration {iter_count + 1}"] = OrderedDict([
                            ("Iteration", iter_count + 1),
                            ("Warning", "Derivative is zero or very close to zero"),
                            ("Details", f"{'Derivative is zero or very close to zero' if abs(fpx) < 1e-10 else 'Invalid derivative (NaN)'} at x = {self._round_value(x_old, decimal_places)}"),
                            ("f'(Xi)", "---"),
                            ("Error %", "---"),
                            ("Xi+1", "---")
                        ])
                        return NewtonRaphsonResult(x_old, [], status, [f"{'Derivative is zero or very close to zero' if abs(fpx) < 1e-10 else 'Invalid derivative (NaN)'} at x = {self._round_value(x_old, decimal_places)}"], pd.DataFrame(table))
                    
                    # Check if function value is NaN (domain error)
                    if math.isnan(fx):
                        status = ConvergenceStatus.NUMERICAL_ERROR
                        # Add current iteration to table
                        table[f"Iteration {iter_count}"] = OrderedDict([
                            ("Iteration", iter_count),
                            ("Xi", self._round_value(x_old, decimal_places)),
                            ("f(Xi)", "NaN"),
                            ("f'(Xi)", self._round_value(fpx, decimal_places)),
                            ("Error %", error_display),
                            ("Xi+1", "---")
                        ])
                        # Add warning about domain error
                        table[f"Iteration {iter_count + 1}"] = OrderedDict([
                            ("Iteration", iter_count + 1),
                            ("Warning", "Function value is invalid (NaN)"),
                            ("Details", f"Function value is invalid (NaN) at x = {self._round_value(x_old, decimal_places)}, likely outside domain"),
                            ("f'(Xi)", "---"),
                            ("Error %", "---"),
                            ("Xi+1", "---")
                        ])
                        return NewtonRaphsonResult(None, [], status, [f"Function value is invalid (NaN) at x = {self._round_value(x_old, decimal_places)}, likely outside domain"], pd.DataFrame(table))
                    
                    # Step 3: Apply Newton-Raphson formula: x_{i+1} = x_i - f(x_i)/f'(x_i)
                    x_current = x_old - (fx / fpx)
                    
                    # Check for numerical issues (NaN, Inf)
                    if math.isnan(x_current) or math.isinf(x_current):
                        status = ConvergenceStatus.NUMERICAL_ERROR
                        # Add current iteration to table
                        table[f"Iteration {iter_count}"] = OrderedDict([
                            ("Iteration", iter_count),
                            ("Xi", self._round_value(x_old, decimal_places)),
                            ("f(Xi)", self._round_value(fx, decimal_places)),
                            ("f'(Xi)", self._round_value(fpx, decimal_places)),
                            ("Error %", error_display),
                            ("Xi+1", "NaN/Inf")
                        ])
                        # Add error message
                        table[f"Iteration {iter_count + 1}"] = OrderedDict([
                            ("Iteration", iter_count + 1),
                            ("Error", "Error"),
                            ("Details", f"Numerical error occurred at iteration {iter_count}")
                        ])
                        return NewtonRaphsonResult(None, [], status, [f"Numerical error occurred at iteration {iter_count}"], pd.DataFrame(table))
                    
                    # Step 4: Calculate absolute difference and relative error
                    abs_diff = abs(x_current - x_old)
                    
                    # Calculate error based on selected criteria
                    if abs(x_current) > 1e-15:
                        relative_error = (abs_diff / abs(x_current)) * 100  # percentage
                    elif abs_diff < 1e-15:
                        relative_error = 0.0  # both x_current and diff tiny, error is effectively zero
                    else:
                        relative_error = float('inf')  # x_current near zero but diff is significant
                    
                    # Choose error for convergence check based on stop_criteria
                    if stop_criteria == "absolute":
                        error_for_check = abs_diff
                    elif stop_criteria == "relative":
                        error_for_check = relative_error
                    elif stop_criteria == "function":
                        error_for_check = abs(fx)
                    else:
                        error_for_check = relative_error  # default to relative
                    
                    # Format error for display
                    error_display = self._format_error(relative_error, decimal_places)
                    
                    # Add iteration details to table
                    table[f"Iteration {iter_count}"] = OrderedDict([
                        ("Iteration", iter_count),
                        ("Xi", self._round_value(x_old, decimal_places)),
                        ("f(Xi)", self._round_value(fx, decimal_places)),
                        ("f'(Xi)", self._round_value(fpx, decimal_places)),
                        ("Error %", error_display),
                        ("Xi+1", self._round_value(x_current, decimal_places))
                    ])
                    
                    # Step 5: Check if the function value is very close to zero (found exact root)
                    f_at_current = float(f(x_current))
                    if abs(f_at_current) < 1e-10:
                        status = ConvergenceStatus.CONVERGED
                        table[f"Iteration {iter_count + 1}"] = OrderedDict([
                            ("Iteration", iter_count + 1),
                            ("Result", "Exact root found (within numerical precision)"),
                            ("Details", f"f(x) ≈ 0 at x = {self._round_value(x_current, decimal_places)}")
                        ])
                        return NewtonRaphsonResult(x_current, [], status, ["Function value is zero within numerical precision"], pd.DataFrame(table))
                    
                    # Step 6: Check for convergence based on error criteria
                    if i > 0 and stop_by_eps:
                        if self._check_convergence(error_for_check, eps, eps_operator):
                            if consecutive_check:
                                consecutive_count += 1
                                if consecutive_count >= consecutive_tolerance:
                                    status = ConvergenceStatus.CONVERGED
                                    stop_msg = f"Converged: {stop_criteria} error below {eps} for {consecutive_tolerance} consecutive iterations"
                                    table[f"Iteration {iter_count + 1}"] = OrderedDict([
                                        ("Iteration", iter_count + 1),
                                        ("Result", stop_msg),
                                        ("Details", "Converged: Achieved desired accuracy based on relative error")
                                    ])
                                    return NewtonRaphsonResult(x_current, [], status, [stop_msg], pd.DataFrame(table))
                            else:
                                status = ConvergenceStatus.CONVERGED
                                stop_msg = f"Converged: {stop_criteria} error {eps_operator} {eps}"
                                table[f"Iteration {iter_count + 1}"] = OrderedDict([
                                    ("Iteration", iter_count + 1),
                                    ("Result", stop_msg),
                                    ("Details", "Converged: Achieved desired accuracy based on absolute error")
                                ])
                                return NewtonRaphsonResult(x_current, [], status, [stop_msg], pd.DataFrame(table))
                        else:
                            consecutive_count = 0  # Reset if not meeting criteria
                    
                    # Step 7: Check for divergence (very large values)
                    if abs(x_current) > self.divergence_threshold:
                        status = ConvergenceStatus.DIVERGED
                        table[f"Iteration {iter_count}"] = OrderedDict([
                            ("Iteration", iter_count),
                            ("Warning", "Method is diverging"),
                            ("Details", f"Root estimate exceeds safe bounds (|x| > {self.divergence_threshold:.2e})")
                        ])
                        return NewtonRaphsonResult(None, [], status, [f"Method is diverging (value too large: {x_current:.2e})"], pd.DataFrame(table))
                    
                    # Step 8: Check for oscillation/cycles
                    if len(previous_values) >= 2:
                        for prev_x in previous_values:
                            if abs(x_current - prev_x) < 1e-6:
                                table[f"Iteration {iter_count}"] = OrderedDict([
                                    ("Iteration", iter_count),
                                    ("Warning", "Method is oscillating between values"),
                                    ("Details", f"Consider using a different initial guess or method")
                                ])
                                return NewtonRaphsonResult(x_current, [], ConvergenceStatus.OSCILLATING, [f"Method is oscillating between values. Stopping at iteration {iter_count}."], pd.DataFrame(table))
                    
                    # Store value for cycle detection
                    previous_values.append(x_current)
                    if len(previous_values) > 5:  # Keep only the last 5 values
                        previous_values.pop(0)
                
                except Exception as e:
                    self.logger.error(f"Error in iteration {iter_count}: {str(e)}")
                    table[f"Iteration {iter_count}"] = OrderedDict([
                        ("Iteration", iter_count),
                        ("Error", "Error"),
                        ("Details", f"Error in iteration {iter_count}: {str(e)}")
                    ])
                    return NewtonRaphsonResult(None, [], ConvergenceStatus.ERROR, [f"Error in iteration {iter_count}: {str(e)}"], pd.DataFrame(table))
            
            # If we reach here, max iterations were reached
            status = ConvergenceStatus.MAX_ITERATIONS
            table[f"Iteration {iter_count}"] = OrderedDict([
                ("Iteration", iter_count),
                ("Result", "Maximum iterations reached"),
                ("Details", f"Maximum iterations ({max_iter}) reached")
            ])
            return NewtonRaphsonResult(None, [], status, [f"Maximum iterations ({max_iter}) reached"], pd.DataFrame(table))
            
        except Exception as e:
            # Handle any unexpected errors
            self.logger.error(f"Error in Newton-Raphson solve method: {str(e)}")
            table[f"Iteration 0"] = OrderedDict([
                ("Error", "Error"),
                ("Details", f"Newton-Raphson method failed: {str(e)}")
            ])
            return NewtonRaphsonResult(None, [], ConvergenceStatus.ERROR, [f"Newton-Raphson method failed: {str(e)}"], pd.DataFrame(table))
            
    def _check_convergence(self, error_value: Union[float, str], eps: float, eps_operator: str) -> bool:
        """
        Check if the error satisfies the convergence criteria.
        
        Args:
            error_value: The error value (float or string)
            eps: Error tolerance
            eps_operator: Comparison operator for epsilon check ("<=", ">=", "<", ">", "=")
            
        Returns:
            bool: True if the error satisfies the convergence criteria, False otherwise
        """
        # Handle string error values or non-numeric values
        if not isinstance(error_value, (int, float)):
            return False
            
        # Convert error_value to float to ensure comparison works
        try:
            error_float = float(error_value)
        except (ValueError, TypeError):
            return False
            
        # Handle NaN and infinity
        if math.isnan(error_float) or math.isinf(error_float):
            return False
            
        # Ensure eps is a float
        try:
            eps_float = float(eps)
        except (ValueError, TypeError):
            return False
            
        self.logger.debug(f"Checking convergence: {error_float} {eps_operator} {eps_float}")
        
        # Perform the comparison
        try:
            if eps_operator == "<=":
                return error_float <= eps_float
            elif eps_operator == ">=":
                return error_float >= eps_float
            elif eps_operator == "<":
                return error_float < eps_float
            elif eps_operator == ">":
                return error_float > eps_float
            elif eps_operator == "=":
                return abs(error_float - eps_float) < 1e-9  # Tolerance for float equality
            else:
                self.logger.error(f"Invalid epsilon operator '{eps_operator}' in _check_convergence")
                return False
        except Exception as e:
            self.logger.exception(f"Error in convergence check: {str(e)}")
            return False
            
    def _round_value(self, value, decimal_places: int):
        """
        Rounds a value to the specified number of decimal places.
        Handles special cases like NaN and infinity.
        
        Args:
            value: The value to round
            decimal_places: Number of decimal places
            
        Returns:
            Rounded value or string representation for special cases
        """
        if not isinstance(value, (int, float)):
            return str(value)
            
        if math.isnan(value):
            return "NaN"
            
        if math.isinf(value):
            return "Inf" if value > 0 else "-Inf"
            
        return round(value, decimal_places)
        
    def _format_error(self, error, decimal_places: int) -> str:
        """
        Formats the error value, adding '%' for relative error.
        Handles special cases like NaN and infinity.
        
        Args:
            error: The error value
            decimal_places: Number of decimal places
            
        Returns:
            Formatted error string
        """
        if not isinstance(error, (int, float)):
            return str(error)
            
        if math.isnan(error):
            return "NaN"
            
        if math.isinf(error):
            return "Inf%" if error > 0 else "-Inf%"
            
        return f"{error:.{decimal_places}f}%"