import pandas as pd
import logging as lg
from dataclasses import dataclass

from src.logics.namespaces.namespace import REG_REG
from src.logics.interfaces.decoders import Decoder
from src.logics.namespaces.enums import Passport, PassportVariants

@dataclass
class PassportFields:
    series: str
    number: str
    date: str | pd.Timestamp
    organization: str 

class PassportDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self) -> str:
        return "Passport Decoder"

    def decode(self) -> pd.DataFrame:
        """
        Extract and process passport information from the dataframe.
        """
        try:
            self._process_passport_column(PassportVariants.DEFAULT.value, self.split_passport)
            self._process_passport_column(PassportVariants.FULL.value, self.split_passport_full)

            if PassportVariants.DIVISION.value in self.df.columns:
                self.df[[Passport.SERIES.value, Passport.NUMBER.value]] = self.df[[PassportVariants.DIVISION.value, Passport.SERIES.value]].apply(self.split_passport_number, axis=1)

            if Passport.NUMBER.value in self.df.columns:
                self.df[Passport.NUMBER.value] = self.df[Passport.NUMBER.value].astype(str)
                self.df[Passport.TYPE.value] = self.df[Passport.NUMBER.value].astype(str).apply(self.find_passport)

            if Passport.SERIES.value in self.df.columns:
                self.df[Passport.SERIES.value] = self.df[Passport.SERIES.value].astype(str).apply(self.truncate_floated)
                self.df[Passport.SERIES.value] = self.df[Passport.SERIES.value].astype(str).apply(self.format_passport_series)
                self.df[Passport.REGION.value] = self.df[Passport.SERIES.value].astype(str).apply(lambda x: REG_REG.get(x[:2], 'UNKNOWN'))

            self._clean_up_passport_data()

        except Exception as ex:
            lg.warning('Could not decode passport information')
            lg.error(f'Traceback: {ex}')
        return self.df

    def _process_passport_column(self, column_name, func):
        if column_name in self.df.columns:
            match column_name:
                case PassportVariants.DEFAULT.value:
                    self.df[[Passport.SERIES.value, Passport.NUMBER.value, Passport.DATE.value, Passport.ORGANIZATION.value]] = self.df[column_name].apply(func)
                case PassportVariants.FULL.value:
                    self.df[[Passport.SERIES.value, Passport.NUMBER.value]] = self.df[column_name].apply(func)

    def _clean_up_passport_data(self):
        try:
            lg.info('Checking for zeroes in [passport_num]..')
            self.df[Passport.NUMBER.value] = self.df[Passport.NUMBER.value].astype(str).apply(lambda row: self.add_cumulative_zeroes(row, 6))
            lg.info('Seeking nulls in [passport_org]..')
            self.df[Passport.ORGANIZATION.value] = self.df[Passport.ORGANIZATION.value].apply(self.fill_nans)
        except Exception:
            lg.warn('Could not drop nulls in [passport_org]')
            pass

    @staticmethod
    def split_passport_number(row: pd.Series) -> pd.Series:
        """
        Split passport to passport series and passport number (when every exists in column)
        """
        if len(row[PassportVariants.DIVISION.value]) >= 11:
            passport_series = row[PassportVariants.DIVISION.value][:5]
            passport_num = row[PassportVariants.DIVISION.value][5:]
        else:
            passport_series = row[Passport.SERIES.value]
            passport_num = row[PassportVariants.DIVISION.value]
        return pd.Series([passport_series, passport_num])

    @staticmethod
    def split_passport_full(row: str) -> pd.Series:
        """
        Passport split when having passport_series+passport_num concatenated 
        """
        row = str(row)
        if len(row) <= 6 and not PassportDecoder.check_passport(row):
            return pd.Series(['', row])
        elif len(row) < 10 and not PassportDecoder.check_passport(row):
            row = PassportDecoder.add_cumulative_zeroes(row, 10)
            passport_series = row[:4]
            passport_num = row[4:]
            return pd.Series([passport_series, passport_num])
        else:
            passport_series = row[:4]
            passport_num = row[4:]
            return pd.Series([passport_series, passport_num])

    @staticmethod
    def truncate_floated(row: str) -> str:
        """
        Truncate floated number in passport series to string
        """
        row = str(row)
        if isinstance(row, str):
            if row.endswith('.0'):
                row = row.replace('.0', '')
            if row == 'nan':
                row = ''
        return row

    @staticmethod
    def split_passport(row: str) -> pd.Series:
        """
        Splitting full passport with format series/number/org/date
        """
        passport_series = row[:4]
        passport_num = row[4:11]
        passport_date = row[-11:]
        passport_org = row[len(passport_series) + len(passport_num) + 2:-len(passport_date)]
        return pd.Series([passport_series, passport_num, passport_date, passport_org])

    @staticmethod
    def add_zeroes(row: str) -> str:
        """
        Adding zeroes to passport number
        """
        if len(row) <= 5:
            return '0' + row
        else:
            return row

    @staticmethod
    def add_cumulative_zeroes(row: str, length: int) -> str:
        """
        Adding zeroes with length specified
        """
        while len(row) < length:
            row = '0' + row
        return str(row)

    @staticmethod
    def check_passport(row: str) -> bool:
        """
        Checking passport for non-russian validity
        """
        row = str(row)
        if row[0].isalpha(): 
            return True
        if len(row) >= 8: #>=
            return True
        else:
            return False

    @staticmethod
    def find_passport(row: str) -> str:
        """
        Mapping passport according to country. In if True, Ru if False
        """
        return 'Паспорт ин. гос.' if PassportDecoder.check_passport(row) else 'Паспорт РФ'

    @staticmethod
    def format_passport_series(row: str) -> str:
        """
        Format passport series from 5555 to 55 55
        """
        if isinstance(row, str):
            if row == "":
                return row
            elif not row.isdigit():
                return row
            elif len(row) <= 4:
                row = PassportDecoder.add_cumulative_zeroes(row, 4)
                return f"{row[:2]} {row[2:]}"
            elif len(row) > 4:
                return row

    @staticmethod
    def fill_nans(row: str) -> str:
        """
        Fill NANs with empty string
        """
        if str(row) == ' null' or str(row) == 'nan':
            return ''
        else:
            return str(row).replace('nan| null|None|NULL|Null', '')