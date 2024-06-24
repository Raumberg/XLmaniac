import pandas as pd
import logging as lg

from xlord.app.interfaces.decoders import Decoder

class DebtDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        self.df = dataframe.copy()

    def decode(self) -> pd.DataFrame:
        self._clean_total_debt()
        if self._has_fcd_and_fcp():
            self._calculate_total_sum_with_fcd_and_fcp()
        elif not self._has_current_debt_and_percent():
            self._calculate_total_sum_without_fcd_and_fcp()
        else:
            self._calculate_total_sum_with_current_debt_and_percent()
        self._set_scheme()
        return self.df

    def _clean_total_debt(self) -> None:
        if 'total_debt' in self.df.columns:
            self.df['total_debt'] = self.df['total_debt'].apply(lambda x: 0 if x in ['null', 'NULL', None, ''] else x)

    def _has_fcd_and_fcp(self) -> bool:
        return 'fcd' in self.df.columns and 'fcp' in self.df.columns

    def _has_current_debt_and_percent(self) -> bool:
        return 'current_debt' in self.df.columns and 'current_percent' in self.df.columns

    def _calculate_total_sum_with_fcd_and_fcp(self) -> None:
        lg.info('found fcd and fcp columns, updating total_sum and setting up scheme...')
        self.df['total_sum'] = (self.df.get('fcd', 0)) + (self.df.get('fcp', 0)) + (self.df.get('overdue_debt', 0)) + (self.df.get('overdue_percent', 0)) + (self.df.get('fines', 0)) + (self.df.get('comission', 0)) + (self.df.get('gp', 0))

    def _calculate_total_sum_without_fcd_and_fcp(self) -> None:
        lg.info('current_debt and current_percent not found in columns, applying FULL_COLLECT scheme...')
        self.df['total_sum'] = self.df.get('overdue_debt', 0) + (self.df.get('overdue_percent', 0)) + (self.df.get('comission', 0)) + (self.df.get('fines', 0))

    def _calculate_total_sum_with_current_debt_and_percent(self) -> None:
        lg.info('current_debt and current_percent found in columns, calculating scheme...')
        self.df['current_debt_calc'] = self.df['current_debt'] - self.df.get('overdue_debt', 0)
        self.df['current_percent_calc'] = self.df['current_percent'] - self.df.get('overdue_percent', 0)
        self.df['total_sum'] = (self.df.get('current_debt_calc', 0)) + self.df.get('overdue_debt', 0) + self.df.get('current_percent_calc', 0) + (self.df.get('overdue_percent', 0)) + (self.df.get('comission', 0)) + (self.df.get('fines', 0))

    def _set_scheme(self) -> None:
        self.df['scheme'] = self.df.apply(self.set_scheme, axis=1)

    @staticmethod
    def set_scheme(row: pd.Series) -> None:
        '''Set the scheme for the client based on calculation results'''
        try:
            if 'total_debt' in row.index and 'total_sum' in row.index:
                if round(row['total_debt'], 0) == round(row['total_sum'], 0):
                    return 'FULL_COLLECT'
                elif round(row['total_debt'], 0) != round(row['total_sum'], 0):
                    return 'BACK_TO_SCHEDULE'
                else:
                    return 'FULL_COLLECT'
        except Exception as ex:
            lg.warn(f"ERR::{ex}")
            lg.warn("Unable to set fileds for scheme.")
            return 'UNABLE TO SET FIELDS'