import pandas as pd
import logging as lg
import phonenumbers as pn
import re
from enum import Enum

from app.functions import support
from xlord.app.interfaces.decoders import Decoder

class Phones(Enum):
    ZAIM = 'phone_num_zaim'
    PHONES = 'phones'

class Clients(Enum):
    DEFAULT = 'default'
    POST = 'post'

class PhoneDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame, client: Clients) -> None:
        self.df = dataframe.copy()

    def decode(self, strategy: Phones) -> pd.DataFrame:
        if strategy.value == strategy.PHONES:
            if 'phones' in self.df.columns:
                lg.info('found phones column (MULTIPLE), applying multiple mapping')
                delimiter = support.get_delimiter(self.df['phones'])
                lg.info('Getting delimiter of phones..')
                lg.info(f'Delimiter is: {delimiter}')
                self.df['phones'] = self.df['phones'].astype(str)
                self.df = self.df.apply(lambda row: support.split_phone_numbers(row, delimiter=delimiter), axis=1)
            for col in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13']:
                if col in self.df.columns:
                    lg.info(f'Added {col} based on phone numbers')
                    self.df[col].dropna(inplace=True)
                    self.df[col] = self.df[col].astype(str)
                    for i, row in self.df.iterrows():
                        if row[col].endswith('.0'):
                            self.df.at[i, col] = row[col][:-2]
                        if row[col].startswith('8'):
                            self.df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                            self.df.at[i, col + '_code'] = row[col][1:4]
                            self.df.at[i, col + '_rest'] = row[col][4:11]
                        elif row[col].startswith('+7'):
                            self.df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                            self.df.at[i, col + '_code'] = re.sub(r"^7", "", self.df.at[i, col])[:3]
                            self.df.at[i, col + '_rest'] = re.sub(r"^7", "", self.df.at[i, col])[3:11]
                        elif row[col].startswith('7'):
                            self.df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                            self.df.at[i, col + '_code'] = re.sub(r"^7", "", self.df.at[i, col])[:3]
                            self.df.at[i, col + '_rest'] = re.sub(r"^7", "", self.df.at[i, col])[3:11]
                        elif row[col].startswith('9'):
                            self.df.at[i, col + '_code'] = self.df.at[i, col][:3]
                            self.df.at[i, col + '_rest'] = self.df.at[i, col][3:]
                        elif row[col].startswith('мт'):
                            self.df.at[i, col + '_code'] = self.df.at[i, col][4:7]
                            self.df.at[i, col + '_rest'] = self.df.at[i, col][7:15]
            self.df = self.df.replace(['nan', 'an'], '', regex=True)
            return self.df
        else:
            return self._zaim_fetch(strategy)

    def _zaim_fetch(self, strategy: Phones) -> pd.DataFrame:
        if strategy.value == strategy.ZAIM:
            if strategy.value in self.df.columns:
                lg.info(f'found {strategy.value} column (UNIQUE), applying zaim express mapping')
                self.df[strategy.value].dropna(inplace=True) 
                self.df[strategy.value] = self.df[strategy.value].astype(str)
                if not self.df[strategy.value].apply(lambda x: isinstance(x, str)).all():
                    raise ValueError("Failed to convert to string")
                try:
                    lg.info("Finding person by phone number..")
                    self.df['contact_person'] = self.df[strategy.value].apply(support.find_person_by_number)
                    lg.info("Person found.")
                except Exception as e:
                    lg.exception("Couldn't find person, moving on..")
                try:
                    self.df[strategy.value] = self.df[strategy.value].apply(support.phone_numbers)
                    self.df['zaim_phone_code'] = self.df[strategy.value].str.slice(1, 4)
                    self.df['zaim_phone_rest'] = self.df[strategy.value].str.slice(4)
                except Exception as e:
                    lg.exception("Couldn't split phone numbers [ZAIM]. Please, rename them to p1, p2..p(n)")
                    lg.error(f"Err::{e}")
            return self.df

    @staticmethod
    def delete_symbols(row: str) -> str:
        '''Deletes symbols from string except for actual phone number'''
        for sym in row:
            if sym not in '0123456789;,':
                row = row.replace(sym, '')
        return row
    
    @staticmethod
    def remove_zeroes(df: pd.DataFrame) -> None:
        '''Removes zeroes across all dataframe [Phones]'''
        for col in df.columns:
            df[col] = df[col].astype(str)
            for i, row in df.iterrows():
                if row[col].endswith('0') and len(row[col]) >= 7:
                    df.at[i, col] = row[col][:-2]

    @staticmethod
    def numbers_iteration(df: pd.DataFrame, col: str) -> None:
        '''Iteration through rows and casting new columns'''
        for i, row in df.iterrows():
            lg.debug(f'Iterating.. {i} /ph/')
            if row[col].endswith('.0'):
                df.at[i, col] = row[col][:-2]
            if row[col].startswith('8'):
                df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                df.at[i, col + '_code'] = row[col][1:4]
                df.at[i, col + '_rest'] = row[col][4:11]
            elif row[col].startswith('+7'):
                df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                df.at[i, col + '_code'] = re.sub(r"^7", "", df.at[i, col])[:3]
                df.at[i, col + '_rest'] = re.sub(r"^7", "", df.at[i, col])[3:11]
            elif row[col].startswith('7'):
                df.at[i, col] = re.sub(r'\D', '', row[col]) if len(row[col]) >= 13 else row[col]
                df.at[i, col + '_code'] = re.sub(r"^7", "", df.at[i, col])[:3]
                df.at[i, col + '_rest'] = re.sub(r"^7", "", df.at[i, col])[3:11]
            elif row[col].startswith('9'):
                df.at[i, col + '_code'] = df.at[i, col][:3]
                df.at[i, col + '_rest'] = df.at[i, col][3:]

    @staticmethod
    def split_phone_numbers(row: str, delimiter: str) -> str:
        '''Split phone numbers in 'phones' column by passing delimiter'''
        numbers_count = row['phones']
        split_numbers = numbers_count.split(delimiter)
        for i, num in enumerate(split_numbers):
            if len(num) > i:
                row[f'p{i+1}'] = num.strip()
        return row

    @staticmethod
    def get_delimiter(column) -> str:
        '''Obtain a delimiter for future split of phone numbers'''
        for delimiter in [',', ';']:
            if column.str.contains(delimiter).any():
                return delimiter
        return '\t'

    @staticmethod
    def phone_numbers(row):
        '''Parse and format phone numbers'''
        try:
            row = row.replace(' ', '')
            phone_number = pn.parse(row, 'CH')
            fmt_number = pn.format_number(phone_number, pn.PhoneNumberFormat.E164)
            fmt_number = fmt_number[1:]
            return fmt_number
        except Exception as e:
            lg.info(f'Error parsing phone number by lib.: {e}')
            return ''