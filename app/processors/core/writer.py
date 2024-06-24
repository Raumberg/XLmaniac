import pandas as pd

from interfaces.xl import DataWriterProtocol, FileType

class DataWriter(DataWriterProtocol):
    def save_file(self, df: pd.DataFrame, method: FileType) -> None:
        if method == FileType.EXCEL:
            df.to_excel('output.xlsx', sheet_name='Main', index=False, engine='openpyxl')
        elif method == FileType.CSV:
            df.to_csv('output.csv', index=False)
        elif method == FileType.JSON:
            df.to_json('output.json', orient='records')
        else:
            raise ValueError("Invalid file type")