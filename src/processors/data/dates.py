import pandas as pd
import logging as lg

from src.interfaces.decoders import Decoder
from src.namespaces.enums import Passport, Debt, Person

class DateDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self) -> str:
        return "Date Decoder"

    def decode(self) -> pd.DataFrame:
        try:
            self._format_date(Person.BIRTH_DATE.value)
            self._format_date(Passport.DATE.value)
            self._format_date(Debt.START_DATE.value)
            self._format_date(Debt.END_DATE.value)
        except Exception as ex:
            lg.warning("Could not decode dates")
            lg.error(f"Traceback: {ex}")
        return self.df

    def _format_date(self, column: str) -> None:
        if column in self.df.columns:
            lg.info(f"[{column}] in columns, formatting dates...")
            self.df[column] = pd.to_datetime(self.df[column], format='%d.%m.%Y').dt.date

