from __future__ import annotations

import logging as lg
import pythoncom
import os

from usecases.prepare_excel import PrepareExcelUseCase
from usecases.start_macros import StartMacrosUseCase
from entities import MacroConfig

class MacroController:
    def __init__(self, directory: str, macro_config: MacroConfig):
        self.directory = directory
        self.macro_config = macro_config

    def execute(self, text_value: str) -> None:
        pythoncom.CoInitialize()
        prepare_excel_usecase = PrepareExcelUseCase(self.directory)
        excel_file = prepare_excel_usecase.execute()
        if excel_file is not None:
            start_macros_usecase = StartMacrosUseCase(self.macro_config)
            start_macros_usecase.execute(excel_file)
        else:
            lg.error(f'No Excel file found in the current directory {os.getcwd()}. Found files: {os.listdir(".")}')
        pythoncom.CoUninitialize()