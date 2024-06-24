import pandas as pd
import numpy as np
import logging as lg

from xlord.app.interfaces.decoders import Decoder
from app.namespaces.namespace import Namespace, CARD_GROUP
from app.functions import support

class RegisterDecoder(Decoder):
    def __init__(self, dataset: pd.DataFrame) -> None:
        self.df = dataset

    def decode(self) -> pd.DataFrame:
        self.df = self._currency()
        self.df = self._concatenate_ids()
        self.df = self._product_group()
        self.df = self._lifetimes()
        return self.df

    def _currency(self) -> pd.DataFrame: 
        if 'currency' in self.df.columns:
            lg.info('Mapping currency...')
            if self.df['currency'].isin(['RUB', 'RUR']).any():
                self.df['currency'] = getattr(Namespace, 'currency')
            else:
                self.df['currency'] = 'ERROR_CHECK_CURRENCY'
        if 'currency' not in self.df.columns:
            lg.info('adding currency...')
            self.df['currency'] = getattr(Namespace, 'currency')
        return self.df

    def _concatenate_ids(self) -> pd.DataFrame:
        if 'client_id' in self.df.columns and 'credit_id' in self.df.columns and 'outer_id' in self.df.columns:
            lg.info('found client_id, credit_id and outer_id columns. concatenating results...')
            self.df['extend'] = self.df.apply(support.concat_values, axis=1)
            self.df = self.df.drop(['client_id', 'credit_id', 'outer_id'], axis=1)
        return self.df

    def _product_group(self) -> pd.DataFrame:
        if 'product_group' in self.df.columns:
            lg.info('found product_group column. mapping product...')
            self.df['product'] = np.where(self.df['product_group'].isin(CARD_GROUP), 'CARD',
                            np.where(self.df['product_group'] == 'Автокредит', 'CAR',
                            np.where(self.df['product_group'] == 'Целевой потребительский кредит', 'POS',
                            np.where(self.df['product_group'] == 'Нецелевой потребительский кредит', 'CASH', np.nan))))
            self.df['product_name'] = np.where(self.df['product'].isin(['CARD']), 'Карточные продукты',
                            np.where(self.df['product'] == 'CAR', 'Автокредит',
                            np.where(self.df['product'] == 'POS', 'Потребительский целевой кредит',
                            np.where(self.df['product'] == 'CASH', 'Потребительский нецелевой кредит', np.nan))))
        return self.df

    def _lifetimes(self) -> pd.DataFrame:
        lg.info('Setting lifetime attributes...')
        if 'placement' not in self.df.columns:
            self.df['placement'] = getattr(Namespace, 'placement')
        if 'placement' in self.df.columns:
            self.df['placement'] = self.df['placement'].apply(support.extract_int)
        self.df['reg_name'] = getattr(Namespace, 'eg_name')
        self.df['reg_date'] = getattr(Namespace, 'eg_date')
        return self.df

