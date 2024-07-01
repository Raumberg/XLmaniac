import pandas as pd
import logging as lg

from src.interfaces.decoders import Decoder
from src.namespaces.enums import  Debt, Register

class DebtDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self) -> str:
        return "Debt Decoder"

    def decode(self) -> pd.DataFrame:
        try:
            self._clean_total_debt()
            if self._has_fcd_and_fcp():
                self._calculate_total_sum_with_fcd_and_fcp()
            elif not self._has_current_debt_and_percent():
                self._calculate_total_sum_without_fcd_and_fcp()
            else:
                self._calculate_total_sum_with_current_debt_and_percent()
            self._set_scheme()
        except Exception as ex:
            lg.warning('Could not decode debt information')
            lg.error(f'Traceback: {ex}')
        return self.df

    def _clean_total_debt(self) -> None:
        if Debt.TOTAL.value in self.df.columns:
            self.df[Debt.TOTAL.value] = self.df[Debt.TOTAL.value].apply(lambda x: 0 if x in ['null', 'NULL', None, ''] else x)

    def _has_fcd_and_fcp(self) -> bool:
        return Debt.FINAL_CURRENT.value in self.df.columns and Debt.FINAL_CURRENT_PERCENT.value in self.df.columns

    def _has_current_debt_and_percent(self) -> bool:
        return Debt.CURRENT.value in self.df.columns and Debt.CURRENT_PERCENT.value in self.df.columns

    def _calculate_total_sum_with_fcd_and_fcp(self) -> None:
        lg.info('Found [fcd] and [fcp] columns, updating [total_sum] and setting up scheme...')
        self.df[Debt.TOTAL_SUM.value] = (self.df.get(Debt.FINAL_CURRENT.value, 0)) + (self.df.get(Debt.FINAL_CURRENT_PERCENT.value, 0)) + (self.df.get(Debt.OVERDUE.value, 0)) + (self.df.get(Debt.OVERDUE_PERCENT.value, 0)) + (self.df.get(Debt.FINES.value, 0)) + (self.df.get(Debt.COMISSIONS.value, 0)) + (self.df.get(Debt.STATE_DUTY.value, 0))

    def _calculate_total_sum_without_fcd_and_fcp(self) -> None:
        lg.info('[current_debt] and [current_percent] not found in columns, applying FULL_COLLECT scheme...')
        self.df[Debt.TOTAL_SUM.value] = self.df.get(Debt.OVERDUE.value, 0) + (self.df.get(Debt.OVERDUE_PERCENT.value, 0)) + (self.df.get(Debt.COMISSIONS.value, 0)) + (self.df.get(Debt.FINES.value, 0))

    def _calculate_total_sum_with_current_debt_and_percent(self) -> None:
        lg.info('[current_debt] and [current_percent] found in columns, calculating scheme...')
        self.df[Debt.CURRENT_CALCULATED.value] = self.df[Debt.CURRENT.value] - self.df.get(Debt.OVERDUE.value, 0)
        self.df[Debt.CURRENT_PERCENT_CALCULATED.value] = self.df[Debt.CURRENT_PERCENT.value] - self.df.get(Debt.OVERDUE_PERCENT.value, 0)
        self.df[Debt.TOTAL_SUM.value] = (self.df.get(Debt.CURRENT_CALCULATED.value, 0)) + self.df.get(Debt.OVERDUE.value, 0) + self.df.get(Debt.CURRENT_PERCENT_CALCULATED.value, 0) + (self.df.get(Debt.OVERDUE_PERCENT.value, 0)) + (self.df.get(Debt.COMISSIONS.value, 0)) + (self.df.get(Debt.FINES.value, 0))

    def _set_scheme(self) -> None:
        self.df[Register.COLLECT_SCHEME.value] = self.df.apply(self.set_scheme, axis=1)

    @staticmethod
    def set_scheme(row: pd.Series) -> None:
        '''Set the scheme for the client based on calculation results'''
        try:
            if Debt.TOTAL.value in row.index and Debt.TOTAL_SUM.value in row.index:
                if round(row[Debt.TOTAL.value], 0) == round(row[Debt.TOTAL_SUM.value], 0):
                    return 'FULL_COLLECT'
                elif round(row[Debt.TOTAL.value], 0) != round(row[Debt.TOTAL_SUM.value], 0):
                    return 'BACK_TO_SCHEDULE'
                else:
                    return 'FULL_COLLECT'
        except Exception as ex:
            lg.warn(f"ERR::{type(ex)}::{ex}")
            lg.warn(f"Unable to set fileds for scheme.")
            return 'UNABLE TO SET FIELDS'