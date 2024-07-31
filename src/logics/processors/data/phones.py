import pandas as pd
import logging as lg
import phonenumbers as pn
import re
from typing import List, Tuple, Dict

from src.logics.interfaces.decoders import Decoder
from src.logics.namespaces.enums import Phones, Clients, PhoneEnum, Register
from src.logics.functions.std import expect, unwrap, Some

class PhoneParser(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df: pd.DataFrame = dataframe
        self.columns: List[str] = self._find_columns()
        self.multiple_phones, self.single_phones = self._classify_columns()

    def decode(self) -> pd.DataFrame:
        self.prepare()
        return self.parse()

    def process_phones(self) -> pd.DataFrame:
        """
        POST BANK specific method
        """
        self.prepare()
        lg.info("Processing post::phones")
        if Phones.TYPE.value in self.df.columns:
            # temp_df = ..
            self.df = self.df[[Register.ID.value] + self.columns + [Phones.TYPE.value]].copy()
            self.df[Phones.PHONE_NUM.value] = self.df.groupby(Register.ID.value).cumcount() + 1
            pivot = self.df.pivot(index='id', columns=Phones.PHONE_NUM.value, values=PhoneEnum.P1.value)
            pivot.reset_index(inplace=True)
            for col in pivot.columns:
                if isinstance(col, int):
                    pivot[f"p{col}"] = pivot[col]
                    pivot = pivot.drop(columns=col, axis=1)
            self.df = pivot
            self._refind()
            result = self.parse()
            return result
        else:
            raise ValueError(f"Column '{Phones.TYPE.value}' not found in axis")

    def _refind(self) -> None:
        self.columns: List[str] = self._find_columns()
        self.multiple_phones, self.single_phones = self._classify_columns()

    def prepare(self) -> None:
        for column in self.columns:
            self.df[column] = self.df[column].astype(str)
    
    def parse(self) -> pd.DataFrame:
        if self.multiple_phones:
            self._multiple_strategy()
        if self.single_phones:
            self._single_strategy()
        self.df = self._drop_nulls()
        return self.df

    def _multiple_strategy(self) -> None:
        delimiters = self._delimiters()
        if delimiters:
            lg.info('Delimiters found.')
            for phones_column, delimiter in delimiters.items():
                result = self.df[phones_column].apply(lambda row: self.split_phone_numbers(row, delimiter))
                max_len = max(len(x) for x in result)
                for i in range(max_len):
                    self.df[f'{phones_column}|p{i+1}'] = result.apply(lambda x: x[i] if i < len(x) else None)
        lg.info("Phones created.")
        self._single_after_multiple()
        lg.info("Phones submerged.")

    def _single_strategy(self) -> None:
        for phone in self.single_phones:
            self.df[phone] = self.df[phone].apply(self.find)
            self.df[[f'{phone}_code', f'{phone}_body']] = self.df[phone].apply(
                lambda row: pd.Series(self.format_phones(row))
                )

    def _single_after_multiple(self) -> None:
        new_cols = {}
        for col in self.df.columns:
            if re.match(r"^phones_\d+|p\d+", col):
                self.df[col] = self.df[col].apply(self.find)
                new_cols[f'{col}_code'] = self.df[col].apply(lambda row: self.format_phones(row)[0])
                new_cols[f'{col}_body'] = self.df[col].apply(lambda row: self.format_phones(row)[1])
        self.df = pd.concat([self.df, pd.DataFrame(new_cols)], axis=1)
            
    def _delimiters(self) -> Dict[str, str]:
        if self.multiple_phones is None:
            pass
        else:
            delimiter_stack: dict = {}
            for phone_column in self.multiple_phones:
                if phone_column in self.df.columns:
                    delimiter = self.get_delimiter(self.df[phone_column])
                    if delimiter:
                        delimiter_stack[phone_column] = delimiter
            return delimiter_stack

    def _find_columns(self) -> List[str]:
        columns: list = []
        for column in list(PhoneEnum):
            if column.value in self.df.columns:
                columns.append(column.value)
        lg.info(f"Phone Parser found columns: {columns}")
        return columns

    def _classify_columns(self) -> Tuple[List[str], List[str]]:
        columns: list = expect(self.columns, "Phone related columns are null")
        multiple_phones: list = [col for col in columns if col.startswith('phones')]
        single_phones: list = [col for col in columns if col.startswith('p') and len(col) == 2]
        return multiple_phones, single_phones

    def _drop_nulls(self) -> pd.DataFrame:
        for col in self.df.columns:
            if col.startswith("phones_"):
                self.df[col] = self.df[col].apply(self.repl)
        return self.df

    def repl(self, row: str) -> str:
        if pd.isna(row) or row in ['nan', 'Нет']:
            return ''
        return row

    @staticmethod
    def find(row: str) -> str:
        row = str(row)
        if row.endswith('.0'):
            row = row.replace('.0', '')
        try:
            phone_number: str = pn.parse(row, "RU")
            if phone_number:
                return PhoneParser.format(phone_number)
        except pn.NumberParseException:
            phone_number: Some[str] = PhoneParser.match(row)
            match phone_number:
                case None:
                    return ''
                case _:
                    return PhoneParser.format(phone_number)

    @staticmethod
    def match(row: str) -> Some[str]:
        numbers: list = []
        for match in pn.PhoneNumberMatcher(row, "RU"):
            number = match.number
            numbers.append(number)
        if numbers:
            return numbers[0]
        else:
            return None

    @staticmethod
    def format(number: str) -> str:
        return pn.format_number(number, pn.PhoneNumberFormat.E164)

    @staticmethod
    def get_delimiter(column: str) -> str:
        for delimiter in [',', ';']:
            if column.str.contains(delimiter).any():
                return delimiter
        return '\t'

    @staticmethod
    def split_phone_numbers(row: str, delimiter: str) -> List[str]:
        splitted_numbers = row.split(delimiter)
        return [num.strip() for num in splitted_numbers]
    
    @staticmethod
    def format_phones(row: str) -> tuple:
        match row:
            case '':
                return '', ''
            case _:
                code = row[2:5]
                body = row[5:]
                return code, body

    @staticmethod
    def delete_symbols(row):
        '''Deletes symbols from string except for actual phone number'''
        for sym in row:
            if sym not in '0123456789;,':
                row = row.replace(sym, '')
        return row