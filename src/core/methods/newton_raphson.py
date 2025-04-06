import sympy as sp
from .base import NumericalMethodBase
from typing import Tuple, List, Dict

class NewtonRaphsonMethod(NumericalMethodBase):
    def solve(self, func_str: str, xi: float, eps: float, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        f = self._create_function(func_str)
        df = self._create_function(str(sp.diff(sp.sympify(func_str), self.x)))
        table = []

        xi_old = xi
        for i in range(max_iter):
            fx_i = float(f(xi_old))
            dfx_i = float(df(xi_old))
            if dfx_i == 0:
                return None, [{"Error": "Derivative is zero"}]
            xi_new = xi_old - fx_i / dfx_i
            error = "---" if i == 0 else abs((xi_new - xi_old) / xi_new) * 100
            row = {
                "Iteration": i,
                "Xi": self._round_values(xi_old, decimal_places),
                "f(Xi)": self._round_values(fx_i, decimal_places),
                "f'(Xi)": self._round_values(dfx_i, decimal_places),
                "Xi+1": self._round_values(xi_new, decimal_places),
                "Error": self._format_error(error, decimal_places)
            }
            table.append(row)

            if stop_by_eps and abs(xi_new - xi_old) < eps:
                return xi_new, table
            if not stop_by_eps and i == max_iter - 1:
                return xi_new, table

            xi_old = xi_new

        return xi_new, table