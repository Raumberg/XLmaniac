import pandas as pd
import logging as lg
import phonenumbers as pn
import re
from typing import List, Tuple, Dict

from src.interfaces.decoders import Decoder
from src.namespaces.enums import Phones, Clients, PhoneEnum
from src.functions.std import expect, unwrap, Some

class PhoneDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame, client: Clients) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe
        self.client = client
    
    def __str__(self):
        return "Phone Decoder"

    def decode(self) -> pd.DataFrame:
        try:
            expect(self._process_multiple_phones(), "Multiple phones decoder failed | ")
            expect(self._zaim_fetch(), "Zaim phone fetch failed | ")
            self._clean_up_phone_numbers()
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

    def _zaim_fetch(self) -> pd.DataFrame:
        if Phones.ZAIM.value in self.df.columns:
            lg.info(f'Found [{Phones.ZAIM.value}] column (UNIQUE), applying zaim express mapping')
            self.df[Phones.ZAIM.value].dropna(inplace=True)
            self.df[Phones.ZAIM.value] = self.df[Phones.ZAIM.value].astype(str)
            self.df[Phones.CONTACT] = self.df[Phones.ZAIM.value].apply(self.find_person_by_number)
            self.df[Phones.ZAIM.value] = self.df[Phones.ZAIM.value].apply(self.phone_numbers)
            self.df['zaim_phone_code'] = self.df[Phones.ZAIM.value].str.slice(1, 4)
            self.df['zaim_phone_rest'] = self.df[Phones.ZAIM.value].str.slice(4)
        return self.df

    @staticmethod
    def get_delimiter(column) -> str:
        for delimiter in [',', ';']:
            if column.str.contains(delimiter).any():
                return delimiter
        return '\t'

    @staticmethod
    def split_phone_numbers(row: str, delimiter: str) -> List[str]:
        splitted_numbers = row.split(delimiter)
        return [num.strip() for num in splitted_numbers]

    @staticmethod
    def phone_numbers(row):
        try:
            row = row.replace(' ', '')
            if row.endswith('.0'):
                row = row.replace('.0', '')
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