import pandas as pd
import os

from logics.interfaces.xl import DataWriterProtocol
from logics.interfaces.paths import Extension 
from logics.entities.program import ProgramPaths

class DataWriter(DataWriterProtocol):
    def __init__(self, output_path: str = ProgramPaths.output_path):
        self._output_path = output_path

    def save_file(self, df: pd.DataFrame, method: Extension, name: str) -> None:
        filepath = os.path.join(self._output_path, name)
        match method:
            case Extension.XLSX:
                df.to_excel(f'{filepath}.xlsx', sheet_name='Main', index=False, engine='openpyxl')
            case Extension.CSV:
                df.to_csv(f'{filepath}.csv', index=False)
            case Extension.JSON:
                df.to_json(f'{filepath}.json', orient='records')
            case _:
                raise ValueError("Invalid file type")

    @property
    def get_output_path(self):
        return self._output_path