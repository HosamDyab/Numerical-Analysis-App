from .base import NumericalMethodBase
from typing import Tuple, List, Dict

class BisectionMethod(NumericalMethodBase):
    def solve(self, func_str: str, xl: float, xu: float, eps: float, max_iter: int, stop_by_eps: bool, decimal_places: int = 6) -> Tuple[float, List[Dict]]:
        f = self._create_function(func_str)
        table = []
        fx_l = float(f(xl))  # تحويل القيمة لعدد حقيقي
        fx_u = float(f(xu))  # تحويل القيمة لعدد حقيقي
        if fx_l * fx_u >= 0:
            return None, [{"Error": "No root in this interval"}]

        xr_old = None
        for i in range(max_iter):
            xr = (xl + xu) / 2
            fx_r = float(f(xr))
            error = "---" if i == 0 else abs((xr - xr_old) / xr) * 100
            row = {
                "Iteration": i,
                "Xl": self._round_values(xl, decimal_places),
                "f(Xl)": self._round_values(fx_l, decimal_places),
                "Xu": self._round_values(xu, decimal_places),
                "f(Xu)": self._round_values(fx_u, decimal_places),
                "Xr": self._round_values(xr, decimal_places),
                "f(Xr)": self._round_values(fx_r, decimal_places),
                "Error": self._format_error(error, decimal_places)
            }
            table.append(row)

            if stop_by_eps and abs(fx_r) < eps:
                return xr, table
            if not stop_by_eps and i == max_iter - 1:
                return xr, table

            if fx_l * fx_r < 0:
                xu = xr
                fx_u = fx_r
            else:
                xl = xr
                fx_l = fx_r
            xr_old = xr

        return xr, table