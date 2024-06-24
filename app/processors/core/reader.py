import pandas as pd
import os
import zipfile

from interfaces.xl import FileReaderProtocol

class FileReader(FileReaderProtocol):
    def read_file(self) -> pd.DataFrame:
        for f in os.listdir('.'):
            if f.endswith('.xlsx') and os.path.isfile(f) and not os.path.isdir(f):
                with open(f, 'rb') as f_obj:
                    if zipfile.is_zipfile(f_obj):
                        return pd.read_excel(f, engine='openpyxl')
        return pd.DataFrame()