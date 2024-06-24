import os
import logging as lg
import zipfile
from openpyxl import load_workbook
from win32com.client import DispatchEx

from entities import ExcelFile

class PrepareExcel:
    def __init__(self, directory: str):
        self.directory = directory

    def execute(self) -> ExcelFile:
        lg.info('Reading file')
        for f in os.listdir(self.directory):
            if f.endswith('.xlsx') and os.path.isfile(f) and not os.path.isdir(f):
                lg.info('Absolute path: ' + os.path.abspath(f))
                lg.info('File: ' + f)
                try:
                    with open(f, 'rb') as f_obj:
                        if zipfile.is_zipfile(f_obj):
                            xl = DispatchEx("Excel.Application")
                            return ExcelFile(path=f, workbook=xl)
                except Exception as e:
                    lg.info(f"Error reading file {f}: {e}")
        return None