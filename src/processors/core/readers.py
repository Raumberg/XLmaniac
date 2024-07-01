import pandas as pd
import os
import json
import logging as lg

from src.interfaces.xl import FileReaderProtocol
from src.interfaces.paths import Path, Extension

class FileReader(FileReaderProtocol):
    def __init__(self, path: Path.PATH, file: Path.FILE, ext: Path.EXTENSION):
        self.path = path
        self.file = file
        self.ext = ext

    def read_file(self) -> pd.DataFrame | dict:
        file_path = os.path.join(self.path, f"{self.file}{self.ext}")
        if os.path.isfile(file_path):
            match self.ext:
                case Extension.XLSX.value:
                    try:
                        return pd.read_excel(file_path, engine='openpyxl')
                    except Exception as e:
                        lg.error(f"Error reading Excel file: {e}")
                case Extension.CSV.value:
                    try:
                        return pd.read_csv(file_path)
                    except Exception as e:
                        lg.error(f"Error reading CSV file: {e}")
                case Extension.JSON.value:
                    try:
                        with open(file_path, 'r') as f:
                            return json.load(f)
                    except Exception as e:
                        lg.error(f"Error reading JSON file: {e}")
                case _:
                    raise NotImplementedError(f"File extension {self.ext} not supported")
        else:
            raise FileNotFoundError(f"File {self.file}{self.ext} not found in {self.path}")