import pandas as pd
import logging as lg
import phonenumbers as pn
import re

from src.interfaces.decoders import Decoder
from src.namespaces.enums import Phones, Clients
from src.functions.std import expect

class PhoneDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame, client: Clients) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe
        self.client = client
    
    def __str__(self):
        return "Phone Decoder"

    def decode(self, strategy: Phones) -> pd.DataFrame:
        try:
            if strategy == Phones.MULTIPLE.value:
                expect(self._process_multiple_phones(), "Multiple phones decoder failed | ")
            else:
                return expect(self._zaim_fetch(strategy), "Zaim phone fetch failed | ")
        except Exception as ex:
            lg.warning('Could not decode phone information')
            lg.error(f'Traceback: {ex}')
        finally:
            return self.df

    def _process_multiple_phones(self) -> None:
        if Phones.MULTIPLE.value in self.df.columns:
            lg.info('Found [phones] column (MULTIPLE), applying multiple mapping')
            delimiter = self.get_delimiter(self.df[Phones.MULTIPLE.value])
            lg.info(f'Delimiter is: {delimiter}')
            self.df[Phones.MULTIPLE.value] = self.df[Phones.MULTIPLE.value].astype(str)
            self.df = self.df.apply(lambda row: self.split_phone_numbers(row, delimiter=delimiter), axis=1)
            self._clean_up_phone_numbers()
        if Phones.MULTIPLE.value not in self.df.columns:
            try:
                _clean_up_phone_numbers(self)
            except Exception as ex:
                lg.warning(f"Error caught in phone processing. Err::{e}")

    def _clean_up_phone_numbers(self) -> None:
        for col in ['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'p8', 'p9', 'p10', 'p11', 'p12', 'p13']:
            if col in self.df.columns:
                lg.info(f'Added [{col}] based on phone numbers')
                self.df[col].dropna(inplace=True)
                self.df[col] = self.df[col].astype(str)
                self.df[col] = self.df[col].apply(self._format_phone_number)

    def _format_phone_number(self, phone_number: str) -> str:
        phone_number = re.sub(r'\D', '', phone_number) if len(phone_number) >= 13 else phone_number
        if phone_number.startswith('8'):
            code = phone_number[1:4]
            rest = phone_number[4:11]
        elif phone_number.startswith('+7'):
            code = re.sub(r"^7", "", phone_number)[:3]
            rest = re.sub(r"^7", "", phone_number)[3:11]
        elif phone_number.startswith('7'):
            code = re.sub(r"^7", "", phone_number)[:3]
            rest = re.sub(r"^7", "", phone_number)[3:11]
        elif phone_number.startswith('9'):
            code = phone_number[:3]
            rest = phone_number[3:]
        else:
            code = ''
            rest = ''
        return code, rest

    def _zaim_fetch(self, strategy: Phones) -> pd.DataFrame:
        if strategy.value == strategy.ZAIM.value:
            if strategy.value in self.df.columns:
                lg.info(f'Found [{strategy.value}] column (UNIQUE), applying zaim express mapping')
                self.df[strategy.value].dropna(inplace=True)
                self.df[strategy.value] = self.df[strategy.value].astype(str)
                self.df[Phones.CONTACT] = self.df[strategy.value].apply(self.find_person_by_number)
                self.df[strategy.value] = self.df[strategy.value].apply(self.phone_numbers)
                self.df['zaim_phone_code'] = self.df[strategy.value].str.slice(1, 4)
                self.df['zaim_phone_rest'] = self.df[strategy.value].str.slice(4)
            return self.df

    @staticmethod
    def get_delimiter(column) -> str:
        for delimiter in [',', ';']:
            if column.str.contains(delimiter).any():
                return delimiter
        return '\t'

    @staticmethod
    def split_phone_numbers(row: str, delimiter: str) -> str:
        numbers_count = row[Phones.MULTIPLE.value]
        split_numbers = numbers_count.split(delimiter)
        for i, num in enumerate(split_numbers):
            if len(num) > i:
                row[f'p{i+1}'] = num.strip()
        return row

    @staticmethod
    def phone_numbers(row):
        try:
            row = row.replace(' ', '')
            phone_number = pn.parse(row, 'CH')
            fmt_number = pn.format_number(phone_number, pn.PhoneNumberFormat.E164)
            fmt_number = fmt_number[1:]
            return fmt_number
        except Exception as e:
            lg.info(f'Error parsing phone number by lib.: {e}')
            return ''

    @staticmethod
    def find_person_by_number(row) -> str:
        row = str(row)[20:].rstrip(')')
        return row
