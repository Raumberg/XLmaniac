import pandas as pd
import numpy as np
import logging as lg

from xlord.app.interfaces.decoders import Decoder
from app.functions import support

class PersonDecoder(Decoder):
    def __init__(self, dataset: pd.DataFrame) -> None:
        self.df = dataset

    def decode(self) -> pd.DataFrame:
        self.df = self._name_split()
        self.df = self._sex_finder()
        self.df = self._workplace()
        self.df = self._mail()
        self.df = self._regliv()
        return self.df

    def _name_split(self) -> pd.DataFrame:
        if 'fio_full' in self.df.columns:
            lg.info('fio_full found in columns, splitting names.')
            try:
                self.df[['surname', 'first_name', 'last_name']] = self.df['fio_full'].str.split(' ', expand=True)
            except ValueError as e:
                lg.info(f'Error splitting fio_full: {e}')
                lg.info('Trying to solve the problem...')
                names = self.df['fio_full'].str.split(' ')  
                names = names.apply(lambda x: [i for i in x if i != ''])
                self.df[['surname', 'first_name', 'last_name']] = pd.DataFrame(names.tolist(), columns=['first_name', 'surname', 'last_name'])
                lg.info("Problem solved.")
        if 'ifo_full' in self.df.columns:
            lg.info('ifo_full found in columns, splitting names.')
            try:
                self.df[['first_name', 'surname', 'last_name']] = self.df['ifo_full'].str.split(' ', expand=True)
            except ValueError as e:
                lg.info(f'Error splitting ifo_full: {e}')
                names = self.df['ifo_full'].str.split(' ').apply(lambda x: x[:3] + x[4:] if len(x) > 3 else x)
                self.df[['first_name', 'surname', 'last_name']] = pd.DataFrame(names.tolist(), columns=['first_name', 'surname', 'last_name'])
                lg.info('Trying to solve the problem...')
        return self.df

    def _sex_finder(self) -> pd.DataFrame:
        if 'sex' in self.df.columns:
            lg.info('sex found in columns, processing...')
            self.df['sex'] = self.df['sex'].apply(lambda x: 'Ж' if x == 'Женский' or x == 1 or x == 'Ж' else 'М')
        if 'sex' not in self.df.columns and 'last_name' in self.df.columns:
            lg.info('sex not found in columns, but last_name is present. Processing sex with respect to last name')
            self.df['sex'] = self.df['last_name'].apply(lambda x: x[-4:] if x is not None else '')
            self.df['sex'] = self.df['sex'].apply(lambda x: 'М' if x[-2:] in ['ич', 'ов', 'ин'] else 'Ж')
        return self.df

    def _workplace(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'position' in df.columns:
            lg.info('found position column. mapping workplace...')
            df['work'] = df['position'].apply(lambda x: 'ООО' if x is None or x == '' else x)
        return df

    def _mail(self, df: pd.DataFrame) -> pd.DataFrame:
        if 'mail' in df.columns:
            lg.info('found mail column (UNIQUE). mapping mail...')
            df['mail'] = df['mail'].str.lower()
            df['mail'] = df['mail'].apply(lambda x: '' if x == 'не задано' else x)
            df['mail'] = df['mail'].apply(lambda x: '' if x in ['null', 'NULL'] else x)
        if 'mails' in df.columns:
            lg.info('found mails column (MULTIPLE). applying multiple mapping...')
            df = df.apply(support.split_mail, axis=1)
        return df

    def _regliv(self, df: pd.DataFrame) -> pd.DataFrame:
        try:
            lg.info('found registration and living related columns. concatenating results...')
            df['registration'] = df[['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
            df['living'] = df[['rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
            df = df.drop(['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg',
                        'rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv',],
                        axis=1)
        except:
            pass
        if 'reg_addr' in df.columns and 'home_addr' in df.columns:
            df['home_addr'] = np.where(df['reg_addr'] == df['home_addr'], '', df['home_addr'])
        return df