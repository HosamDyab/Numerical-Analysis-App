import unittest
import sys
import os
import math

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.solver import Solver

class TestSolver(unittest.TestCase):
    def setUp(self):
        self.solver = Solver()
        
    def test_bisection_method(self):
        """Test the bisection method with a simple function."""
        func = "x**2 - 4"
        params = {"a": 0, "b": 3}
        root, _ = self.solver.solve("Bisection", func, params, 0.0001, 50, True)
        self.assertAlmostEqual(root, 2.0, places=4)
        
    def test_newton_method(self):
        """Test the Newton-Raphson method with a simple function."""
        func = "x**2 - 4"
        params = {"x0": 3}
        root, _ = self.solver.solve("Newton-Raphson", func, params, 0.0001, 50, True)
        self.assertAlmostEqual(root, 2.0, places=4)
        
    def test_secant_method(self):
        """Test the secant method with a simple function."""
        func = "x**2 - 4"
        params = {"x0": 3, "x1": 4}
        root, _ = self.solver.solve("Secant", func, params, 0.0001, 50, True)
        self.assertAlmostEqual(root, 2.0, places=4)
        
    def test_fixed_point_method(self):
        """Test the fixed point method with a simple function."""
        func = "x - (x**2 - 4)/(2*x)"  # g(x) = x - f(x)/f'(x) for f(x) = x^2 - 4
        params = {"x0": 3}
        root, _ = self.solver.solve("Fixed Point", func, params, 0.0001, 50, True)
        self.assertAlmostEqual(root, 2.0, places=4)
        
    def test_false_position_method(self):
        """Test the false position method with a simple function."""
        func = "x**2 - 4"
        params = {"a": 0, "b": 3}
        root, _ = self.solver.solve("False Position", func, params, 0.0001, 50, True)
        self.assertAlmostEqual(root, 2.0, places=4)

if __name__ == '__main__':
    unittest.main() 