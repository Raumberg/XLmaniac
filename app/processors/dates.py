import pandas as pd
import logging as lg

from xlord.app.interfaces.decoders import Decoder

class DateDecoder(Decoder):
    def __init__(self, dataset: pd.DataFrame) -> None:
        self.df = dataset

    def decode(self) -> pd.DataFrame:
        try:
            self._format_date('birth_date')
            self._format_date('passport_date')
            self._format_date('credit_start_date')
            self._format_date('credit_end_date')
        except:
            lg.warn("Could not fetch dates.")
        return self.df

    def _format_date(self, column: str) -> None:
        if column in self.df.columns:
            lg.info(f"{column} in columns, formatting dates...")
            self.df[column] = pd.to_datetime(self.df[column], format='%d.%m.%Y').dt.date

