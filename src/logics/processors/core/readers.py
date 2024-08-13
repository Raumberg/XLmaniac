import pandas as pd
import os
import json
import logging as lg
import pathlib

from logics.interfaces.xl import FileReaderProtocol
from logics.interfaces.paths import Path, Extension
from logics.namespaces.enums import Sheets

XLSX_EXTENSION = Extension.XLSX.value
CSV_EXTENSION = Extension.CSV.value
JSON_EXTENSION = Extension.JSON.value

class FileReader(FileReaderProtocol):
    def __init__(self, path: pathlib.Path):
        self.path = path

    # def _get_file_path(self) -> str:
    #     return os.path.join(self.path, f"{self.file}{self.ext}")

    def _read_excel_file(self, file_path: str) -> dict:
        try:
            excel = pd.ExcelFile(file_path, engine='openpyxl')
            sheets = excel.sheet_names
            lg.info(f"Reading excel, found sheets: {sheets}")

            dataframes = {}

            for sheet in Sheets:
                if sheet.value in sheets:
                    dataframes[sheet.name] = pd.read_excel(file_path, sheet_name=sheet.value)
            if not dataframes:
                dataframes['default'] = pd.read_excel(file_path, sheet_name=sheets[0])
            return dataframes
        except pd.errors.EmptyDataError as e:
            lg.error(f"Error reading Excel file: {e}")
        except pd.errors.ParserError as e:
            lg.error(f"Error reading Excel file: {e}")

    def _read_csv_file(self, file_path: str) -> pd.DataFrame:
        try:
            return pd.read_csv(file_path)
        except pd.errors.EmptyDataError as e:
            lg.error(f"Error reading CSV file: {e}")
        except pd.errors.ParserError as e:
            lg.error(f"Error reading CSV file: {e}")

    def _read_json_file(self, file_path: str) -> dict:
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            lg.error(f"Error reading JSON file: {e}")

    def read_file(self) -> pd.DataFrame | dict:
        file_path = pathlib.Path(self.path)
        if os.path.isfile(file_path):
            ext = file_path.suffix.lower()
            match ext:
                case Extension.XLSX.value:
                    return self._read_excel_file(file_path)
                case Extension.CSV.value:
                    return self._read_csv_file(file_path)
                case Extension.JSON.value:
                    return self._read_json_file(file_path)
                case _:
                    raise NotImplementedError(f"File extension not supported")
        else:
            raise FileNotFoundError(f"File not found in {self.path}")

class PathReader():
    def __init__(self, path: pathlib.Path):
        self.path = pathlib.Path(path)
    
    def get_recent_file(self) -> str:
        recent_file = None
        recent_time = 0
        for file in self.path.iterdir():
            if file.is_file():
                file_time = os.stat(file).st_mtime
                if file_time > recent_time:
                    recent_time = file_time
                    recent_file = file
        if recent_file:
            return str(recent_file)
        else:
            return ""