import logging as lg
import os
from win32com.client import DispatchEx

from entities import MacroConfig, ExcelFile

class StartMacrosUseCase:
    def __init__(self, macro_config: MacroConfig):
        self.macro_config = macro_config

    def execute(self, excel_file: ExcelFile) -> None:
        lg.info('Starting macros')
        wb = excel_file.workbook.Workbooks.Open(os.path.abspath(excel_file.path))
        ws = wb.Worksheets[0]
        lg.info(f"Columns are: %s" % self.macro_config.columns)
        try:
            vba = wb.VBProject
            vba_module = vba.VBComponents.Import(self.macro_config.vba_module_path)
            wb.Save()
        except Exception as e:
            lg.error(f'Failed to load the VBA macro. Error: {e}')
            if wb is not None:
                wb.Close(SaveChanges=True)
            return
        try:
            selection = ws.Range("B1:C20")
            lg.info(f"Selection: {selection}") 
            lg.info(f"Running on coordinates: {selection}") 
            excel_file.workbook.Application.Run(self.macro_config.macro_name, selection) 
            wb.Save()
        except Exception as e:
            lg.error(f'Error: {e}')
            if wb is not None:
                wb.Close(SaveChanges=True)
        finally:
            excel_file.workbook.Quit()
            del excel_file.workbook