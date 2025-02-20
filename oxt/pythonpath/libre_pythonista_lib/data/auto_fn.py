from __future__ import annotations
from typing import TYPE_CHECKING
from ooodev.calc import CalcCellRange

from .tbl_data_obj import TblDataObj

if TYPE_CHECKING:
    from ....___lo_pip___.oxt_logger import OxtLogger
else:
    from ___lo_pip___.oxt_logger import OxtLogger


class AutoFn:
    """Class that generates the lp function"""

    def __init__(self, cell_rng: CalcCellRange):
        """
        Constructor

        Args:
            cell_rng (CalcCellRange): The cell range to get the table information from.
        """
        self._log = OxtLogger(log_name=self.__class__.__name__)
        if self._log.is_debug:
            self._log.debug(f"init: {cell_rng.range_obj}")
        self._cell_rng = cell_rng
        self._data_info = TblDataObj(cell_rng)
        self._log.debug("init complete.")

    def generate_fn(self) -> str:
        """Generates the lp function"""
        self._log.debug("generate_fn() Entered")

        s = f'lp("{self._cell_rng.range_obj}"'
        if self._data_info.has_headers:
            # headers = self._data_info.headers
            s += ", headers=True"
        if self._get_include_collapse():
            s += ", collapse=True"
        s += ")"

        self._log.debug(f"generate_fn() returning '{s}'")
        return s

    def _get_include_collapse(self) -> bool:
        """Determines if the collapse parameter should be included"""
        ro_orig = self._cell_rng.range_obj
        try:
            ro = self._cell_rng.find_used_range()
            if ro_orig != ro.range_obj:
                return True
        except Exception as e:
            self._log.exception(f"Error: {e}")
        return False
