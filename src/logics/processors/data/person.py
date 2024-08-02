import pandas as pd
import numpy as np
import logging as lg

from logics.interfaces.decoders import Decoder
from logics.namespaces.enums import Person, NameVariants
from logics.functions.std import expect, NullException

class PersonDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self) -> str:
        return "Person Decoder"

    def decode(self) -> pd.DataFrame:
        try:
            self.df = expect(self._name_splitter(), "Name splitter caused an error | ")
            self.df = expect(self._sex_finder(), "Sex finder caused an error | ")
            self.df = expect(self._workplace(), "Workplace finder caused an error | ")
            self.df = expect(self._mail(), "Mail finder caused an error | ")
            self.df = expect(self._regliv(), "RegLiv finder caused an error | ")
        except NullException as ex:
            lg.warning('Could not decode personal information')
            lg.error(f'Traceback: {ex}')
        return self.df

    def _name_splitter(self) -> pd.DataFrame:
        """
        FIO will be splitted into name, surname, lastname, addname
        IFO will be splitted into name, surname, lastname, addname, postfix
        """
        if NameVariants.FIO.value in self.df.columns:
            lg.info('[fio_full] found in columns, splitting names.')
            try:
                names = self.df[NameVariants.FIO.value].str.split(' ', n=4, expand=True)
                names.columns = [Person.NAME.value, Person.SURNAME.value, Person.LASTNAME.value, Person.ADDNAME.value]
                self.df = pd.concat([self.df, names], axis=1)
                lg.info("Names split successfully")
            except ValueError as e:
                lg.warning(f"Error splitting [fio_full]: {e}")
                lg.warning("Skipping data...")
                pass
        if NameVariants.IFO.value in self.df.columns:
            lg.info('[ifo_full] found in columns, splitting names...')
            try:
                names = self.df[NameVariants.IFO.value].str.split(' ', n=5, expand=True)
                names.columns = [Person.NAME.value, Person.SURNAME.value, Person.LASTNAME.value, Person.ADDNAME.value, Person.POSTFIX.value]
                self.df = pd.concat([self.df, names], axis=1)
                lg.info("Names split successfully")
            except ValueError as e:
                lg.warning(f"Error splitting [ifo_full]: {e}")
                lg.warning("Skipping data...")
                pass
        return self.df

    def _sex_finder(self) -> pd.DataFrame:
        if Person.SEX.value in self.df.columns:
            lg.info('[sex] found in columns, processing...')
            self.df[Person.SEX.value] = self.df[Person.SEX.value].apply(lambda x: 'Ж' if x == 'Женский' or x == 1 or x == 'Ж' else 'М')
        if Person.SEX.value not in self.df.columns and Person.LASTNAME.value in self.df.columns:
            lg.info('[sex] not found in columns, but [last_name] is present. Processing [sex] with respect to last name')
            self.df[Person.SEX.value] = self.df[Person.LASTNAME.value].apply(lambda x: x[-4:] if x is not None else '')
            self.df[Person.SEX.value] = self.df[Person.SEX.value].apply(lambda x: 'М' if x[-2:] in ['ич', 'ов', 'ин'] else 'Ж')
        return self.df

    def _workplace(self) -> pd.DataFrame:
        if Person.POSITION.value in self.df.columns:
            lg.info('Found [position] column. mapping workplace...')
            self.df[Person.WORK.value] = self.df[Person.POSITION.value].apply(lambda x: 'ООО' if pd.isna(x) or str(x).strip() == '' else str(x))
        return self.df

    def _mail(self) -> pd.DataFrame:
        if Person.MAIL.value in self.df.columns:
            lg.info('Found [mail] column (UNIQUE). mapping mail...')
            self.df[Person.MAIL.value] = self.df[Person.MAIL.value].str.lower()
            self.df[Person.MAIL.value] = self.df[Person.MAIL.value].apply(lambda x: '' if x == 'не задано' else x)
            self.df[Person.MAIL.value] = self.df[Person.MAIL.value].apply(lambda x: '' if x in ['null', 'NULL'] else x)
            self.df[Person.MAIL.value] = self.df[Person.MAIL.value].apply(self.fill_nans)
        if 'mails' in self.df.columns:
            lg.info('Found [mails] column (MULTIPLE). applying multiple mapping...')
            self.df = self.df.apply(self.split_mail, axis=1)
        return self.df

    def _regliv(self) -> pd.DataFrame:
        required_columns = ['rg_reg', 'np_reg', 'rg_liv', 'np_liv']
        if all(col in self.df.columns for col in required_columns):
            try:
                lg.info('Found registration and living related columns. concatenating results...')
                self.df[Person.REG_ADDRESS.value] = self.df[['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
                self.df[Person.HOME_ADDRESS.value] = self.df[['rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv']].apply(lambda x: ', '.join(x.astype(str)), axis=1)
                self.df = self.df.drop(['rg_reg', 'np_reg', 'st_reg', 'hs_reg', 'cp_reg', 'ft_reg',
                            'rg_liv', 'np_liv', 'st_liv', 'hs_liv', 'cp_liv', 'ft_liv',],
                            axis=1)
            except Exception as e:
                lg.warning(f"Error processing registration/living related columns: {e}")
                return self.df
            if Person.REG_ADDRESS.value in self.df.columns and Person.HOME_ADDRESS.value in self.df.columns:
                self.df[Person.HOME_ADDRESS.value] = np.where(self.df[Person.REG_ADDRESS.value] == self.df[Person.HOME_ADDRESS.value], '', self.df[Person.HOME_ADDRESS.value])
            return self.df
        else:
            lg.info("Reg/liv columns not found in dataframe")
            return self.df

    @staticmethod
    def split_mail(row):
        '''Split 'mails' column into separate ones'''
        mail_count = row['mails']
        split_mail = mail_count.split(',')
        for i, num in enumerate(split_mail):
            if len(num) > i:
                row[f'm{i+1}'] = num.strip()
        return row

    @staticmethod
    def fill_nans(row: str) -> str:
        """
        Fill NANs with empty string
        """
        if str(row) == ' null':
            return ''
        elif str(row) == 'nan':
            return ''
        else:
            return str(row).replace('nan| null|None|NULL|Null', '')