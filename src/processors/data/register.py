import pandas as pd
import numpy as np
import logging as lg
import re

from src.interfaces.decoders import Decoder
from src.namespaces.namespace import Namespace, CARD_GROUP
from src.namespaces.enums import Register

class RegisterDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self):
        return "Register Decoder"

    def decode(self) -> pd.DataFrame:
        try:
            self.df = self._currency()
            self.df = self._concatenate_ids()
            self.df = self._product_group()
            self.df = self._lifetimes()
        except Exception as ex:
            lg.warning('Could not decode register information')
            lg.error(f'Traceback: {ex}')
        return self.df

    def _currency(self) -> pd.DataFrame: 
        if Register.CURRENCY.value in self.df.columns:
            lg.info('Mapping currency...')
            if self.df[Register.CURRENCY.value].isin(['RUB', 'RUR']).any():
                self.df[Register.CURRENCY.value] = getattr(Namespace, 'currency')
            else:
                self.df[Register.CURRENCY.value] = 'ERROR_CHECK_CURRENCY'
        if Register.CURRENCY.value not in self.df.columns:
            lg.info('Adding currency...')
            self.df[Register.CURRENCY.value] = getattr(Namespace, 'currency')
        return self.df

    def _concatenate_ids(self) -> pd.DataFrame:
        if Register.CLIENT_ID.value in self.df.columns and Register.CREDIT_ID.value in self.df.columns and Register.OUTER_ID.value in self.df.columns:
            lg.info('Found [client_id], [credit_id] and [outer_id] columns. concatenating results...')
            self.df[Register.EXTENSION.value] = self.df.apply(self.concat_values, axis=1)
            self.df = self.df.drop([Register.CLIENT_ID.value, Register.CREDIT_ID.value, Register.OUTER_ID.value], axis=1)
        return self.df

    def _product_group(self) -> pd.DataFrame:
        if Register.PRODUCT_GROUP.value in self.df.columns:
            lg.info('Found [product_group] column. mapping product...')
            self.df[Register.PRODUCT.value] = np.where(self.df[Register.PRODUCT_GROUP.value].isin(CARD_GROUP), 'CARD',
                            np.where(self.df[Register.PRODUCT_GROUP.value] == 'Автокредит', 'CAR',
                            np.where(self.df[Register.PRODUCT_GROUP.value] == 'Целевой потребительский кредит', 'POS',
                            np.where(self.df[Register.PRODUCT_GROUP.value] == 'Нецелевой потребительский кредит', 'CASH', np.nan))))
            self.df[Register.PRODUCT_NAME.value] = np.where(self.df[Register.PRODUCT].isin(['CARD']), 'Карточные продукты',
                            np.where(self.df[Register.PRODUCT.value] == 'CAR', 'Автокредит',
                            np.where(self.df[Register.PRODUCT.value] == 'POS', 'Потребительский целевой кредит',
                            np.where(self.df[Register.PRODUCT.value] == 'CASH', 'Потребительский нецелевой кредит', np.nan))))
        return self.df

    def _lifetimes(self) -> pd.DataFrame:
        lg.info('Setting lifetime attributes...')
        if Register.PLACEMENT.value not in self.df.columns:
            self.df[Register.PLACEMENT.value] = getattr(Namespace, 'placement')
        if Register.PLACEMENT.value in self.df.columns:
            self.df[Register.PLACEMENT.value] = self.df[Register.PLACEMENT.value].apply(self.extract_int)
        self.df[Register.NAME.value] = getattr(Namespace, 'reg_name')
        self.df[Register.DATE.value] = getattr(Namespace, 'reg_date')
        return self.df

    @staticmethod
    def concat_values(row) -> str:
        '''Value concatenation for client'''
        return str(row[Register.CLIENT_ID]) + '|' + str(row[Register.CREDIT_ID]) + '|' + str(row[Register.OUTER_ID])

    @staticmethod
    def extract_int(row) -> int:
        '''Extract integer from placement column'''
        if row is None:
            return 0
        match = re.search(r'\d+', row)
        if match:
            return int(match.group())
        else:
            return 0

