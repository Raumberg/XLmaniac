import pandas as pd

from src.logics.interfaces.xl import DataWriterProtocol
from src.logics.interfaces.paths import Extension 

class DataWriter(DataWriterProtocol):
    def save_file(self, df: pd.DataFrame, method: Extension) -> None:
        match method:
            case Extension.XLSX:
                df.to_excel('output.xlsx', sheet_name='Main', index=False, engine='openpyxl')
            case Extension.CSV:
                df.to_csv('output.csv', index=False)
            case Extension.JSON:
                df.to_json('output.json', orient='records')
            case _:
                raise ValueError("Invalid file type")