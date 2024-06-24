from __future__ import annotations
from typing import Protocol

from entities.excel import *

class ExcelMacroRunner(Protocol):
    def prepare_excel(self, directory: str) -> ExcelFile:
        """Prepare an Excel file for macro execution."""
        ...

    def start_macros(self, excel_file: ExcelFile, macro_config: MacroConfig) -> None:
        """Start the Excel macro execution on the prepared file."""
        ...