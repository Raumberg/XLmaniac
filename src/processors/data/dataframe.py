import pandas as pd
import logging as lg

from src.interfaces.decoders import Decoder

class DataframeDecoder(Decoder):
    def __init__(self, dataframe: pd.DataFrame) -> None:
        if dataframe is None:
            raise ValueError("Dataframe is null")
        self.df = dataframe

    def __str__(self):
        return "Dataframe Decoder"

    def decode(self) -> pd.DataFrame:
        """
        Process the mechanical parts of the dataframe.
        """
        try:
            self.drop_unnamed()
            self.replace_null_values()
            #self.drop_null_rows()
        except Exception as ex:
            lg.warning('Could not process dataframe mechanics')
            lg.error(f"Traceback: {ex}")
        return self.df

    def drop_unnamed(self) -> None:
        '''Dropping unused columns in the dataframe'''
        lg.info('Dropping unused fields')
        #self.df.dropna(subset=self.df.columns[self.df.columns.str.contains('^Unnamed')], how='all', inplace=True)
        self.df.drop(self.df.filter(regex='^Unnamed').columns, axis=1, inplace=True)

    def drop_null_rows(self) -> None:
        '''Dropping rows with null values in the dataframe'''
        lg.info('Dropping rows with null values')
        self.df = self.df.dropna(inplace=True)
        self.df = self.df.dropna(how=any, axis=0)
        return self.df

    def replace_null_values(self) -> None:
        '''Replacing null values in the dataframe'''
        lg.info('Replacing null values')
        self.df = self.df.apply(lambda x: x.replace('null|NULL|Null|nan', '') if x.dtype == 'object' else x)
        self.df = self.df.apply(lambda x: x.fillna('') if x.dtype == 'object' else x.fillna(0))
        #self.df = self.df.fillna('', inplace=True)