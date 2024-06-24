import pandas as pd
import logging as lg
from enum import Enum
from dataclasses import dataclass

from namespaces.namespace import REG_REG
from xlord.app.interfaces.decoders import Decoder

class PassportColumn(Enum):
    SERIES = 'passport_series'
    NUMBER = 'passport_number'
    ORGANIZATION = 'passport_org'
    DATE = 'passport_date'

class PassportVariants(Enum):
    DIVISION = 'passport_div'
    FULL = 'passport_full'
    DEFAULT = 'passport'

@dataclass
class Passport:
    series: str
    number: str
    date: str | pd.Timestamp
    organization: str 

class PassportDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe.copy()

    def decode(self) -> pd.DataFrame:  
        """
        Extract and process passport information from the dataframe.
        """
        if 'passport' in self.df.columns:
            lg.info('Found passport column, trying to migrate data...')
            self.df[['passport_series', 'passport_num', 'passport_date', 'passport_org']] = self.df['passport'].apply(self.split_passport)

        if 'passport_full' in self.df.columns:
            lg.info('Found passport_full column, using split_passport_full')
            self.df['passport_full'] = self.df['passport_full'].astype(str)
            self.df[['passport_series', 'passport_num']] = self.df['passport_full'].apply(self.split_passport_full)

        if 'passport_series' in self.df.columns and 'passport_div' not in self.df.columns:
            lg.info('Looking to passport_series. Applying format_passport_series')
            self.df['passport_series'] = self.df['passport_series'].apply(self.format_passport_series)
            lg.info('Adding zeroes to passport_num..')
            self.df['passport_num'] = self.df['passport_num'].astype(str).apply(self.add_zeroes)
            self.df['passport_num'] = self.df['passport_num'].apply(self.add_zeroes)

        if 'passport_div' in self.df.columns:
            lg.info('Found passport_div column, using split_passport_number')
            self.df[['passport_series', 'passport_num']] = self.df[['passport_div', 'passport_series']].apply(self.split_passport_number, axis=1)

        if 'passport_num' in self.df.columns:
            lg.info('Found passport_series column, formatting document type')
            self.df['doctype'] = self.df['passport_num'].astype(str).apply(self.find_passport)

        if 'passport_series' in self.df.columns:
            lg.info('Found passport_series column, mapping the region based on passport series')
            self.df['region'] = self.df['passport_series'].astype(str).apply(lambda x: REG_REG.get(x[:2], 'UNKNOWN'))

        try:
            lg.info('Checking for zeroes in passport_num..')
            self.df['passport_num'] = self.df['passport_num'].astype(str).apply(lambda row: self.add_cumulative_zeroes(row, 6))
            lg.info('Seeking nulls in passport_org..')
            self.df['passport_org'] = self.df['passport_org'].apply(lambda x: '' if x in ['null', 'NULL'] else x)
        except Exception as e:
            lg.warn('Could not drop nulls in passport_org')
            pass

        return self.df

    @staticmethod
    def split_passport_number(row: pd.Series) -> pd.Series[str]:
        """
        Split passport to passport series and passport number (when every exists in column)
        """
        if len(row['passport_div']) >= 11:
            passport_series = row['passport_div'][:5]
            passport_num = row['passport_div'][5:]
        else:
            passport_series = row['passport_series']
            passport_num = row['passport_div']
        return pd.Series([passport_series, passport_num])

    @staticmethod
    def split_passport_full(row: str) -> pd.Series[str]:
        """
        Another split for different situation occuring
        """
        row = str(row)
        if len(row) <= 6 and not PassportDecoder.check_passport(row):
            return pd.Series(['', row])
        else:
            passport_series = row[:4]
            passport_num = row[4:]
            return pd.Series([passport_series, passport_num])

    @staticmethod
    def split_passport(row: str) -> pd.Series[str]:
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
        row = str(row)
        if len(row) == length:
            return row
        else:
            while len(row) < length:
                row = '0' + row
                return row

    @staticmethod
    def check_passport(row: str) -> bool:
        """
        Checking passport for non-russian validity
        """
        row = str(row)
        if row[0].isalpha(): 
            return True
        if len(row) >= 8: 
            return True
        else:
            return False

    @staticmethod
    def find_passport(row: str) -> str:
        """
        Mapping passport according to country
        """
        return 'Паспорт ин. гос.' if PassportDecoder.check_passport(row) else 'Паспорт РФ'