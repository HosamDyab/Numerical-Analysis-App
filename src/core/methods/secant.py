from .base import NumericalMethodBase
from typing import Tuple, List, Dict

class SecantMethod(NumericalMethodBase):
    def solve(self, func_str: str, xi_minus_1: float, xi: float, eps: float, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        f = self._create_function(func_str)
        table = []

        for i in range(max_iter):
            fx_i = float(f(xi))
            fx_i_minus_1 = float(f(xi_minus_1))
            if fx_i - fx_i_minus_1 == 0:
                return None, [{"Error": "Division by zero"}]
            xi_plus_1 = xi - fx_i * (xi - xi_minus_1) / (fx_i - fx_i_minus_1)
            error = "---" if i == 0 else abs((xi_plus_1 - xi) / xi_plus_1) * 100
            row = {
                "Iteration": i,
                "Xi-1": self._round_values(xi_minus_1, decimal_places),
                "f(Xi-1)": self._round_values(fx_i_minus_1, decimal_places),
                "Xi": self._round_values(xi, decimal_places),
                "f(Xi)": self._round_values(fx_i, decimal_places),
                "Xi+1": self._round_values(xi_plus_1, decimal_places),
                "Error": self._format_error(error, decimal_places)
            }
            table.append(row)

            if stop_by_eps and abs(xi_plus_1 - xi) < eps:
                return xi_plus_1, table
            if not stop_by_eps and i == max_iter - 1:
                return xi_plus_1, table

            xi_minus_1 = xi
            xi = xi_plus_1

        return xi_plus_1, table