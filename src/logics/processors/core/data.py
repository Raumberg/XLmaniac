import pandas as pd
import logging as lg

from logics.namespaces.namespace import *
from logics.interfaces.xl import DataProcessorProtocol

from logics.processors.data.dates import DateDecoder
from logics.processors.data.debt import DebtDecoder
from logics.processors.data.person import PersonDecoder
from logics.processors.data.passport import PassportDecoder
from logics.processors.data.register import RegisterDecoder
from logics.processors.data.phones import PhoneParser, Clients
from logics.processors.data.dataframe import DataframeDecoder
from logics.namespaces.enums import Sheets, Datasets

class DataProcessor(DataProcessorProtocol):
    def __init__(self):
        self.decoders = [
            PersonDecoder,
            DateDecoder,
            PhoneParser,
            PassportDecoder,
            DebtDecoder,
            RegisterDecoder,
            DataframeDecoder
        ]

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for decoder in self.decoders:
            lg.debug(f"_Call_::{decoder.__name__}")
            decoded_df = decoder(df).decode()
            if decoded_df is None:
                raise ValueError(f"Decoder::{decoder} returned Null")
            lg.debug(f"_Exit_::{decoder.__name__}")
            df = decoded_df
        return df

    def process_post(self, contracts: pd.DataFrame, addresses: pd.DataFrame, phones: pd.DataFrame) -> pd.DataFrame:
        """
        POST BANK specific method
        """
        contracts = self._process_contracts(contracts)
        addresses = self._process_addresses(addresses)
        phones = self._process_phones(phones)
        mrg = self._merge_dataframes(contracts, addresses, phones)
        result = self._clear_dataframe(mrg)
        return result

    def _process_contracts(self, df: pd.DataFrame) -> pd.DataFrame:
        contracts_decoders = [PersonDecoder, DateDecoder, PassportDecoder, DebtDecoder, RegisterDecoder]
        for decoder in contracts_decoders:
            lg.debug(f"_Call_::post::{decoder.__name__}")
            decoded_df = decoder(df).decode()
            if decoded_df is None:
                raise ValueError(f"Decoder::{decoder} returned Null")
            lg.debug(f"_Exit_::{decoder.__name__}")
            df = decoded_df
        return df

    def _process_phones(self, df: pd.DataFrame) -> pd.DataFrame:
        lg.debug(f"_Call_::post::phones")
        decoded_df = PhoneParser(df).process_phones()
        if decoded_df is None:
            raise ValueError(f"Decoder returned Null")
        lg.debug(f"_Exit_::post::phones")
        df = decoded_df
        return df

    def _process_addresses(self, df: pd.DataFrame) -> pd.DataFrame:
        lg.debug(f"_Call_::post::addr")
        decoded_df = RegisterDecoder(df).process_addresses()
        if decoded_df is None:
            raise ValueError(f"Decoder returned Null")
        lg.debug(f"_Exit_::post::phones")
        df = decoded_df
        return df

    def _merge_dataframes(self, contracts: pd.DataFrame, addresses: pd.DataFrame, phones: pd.DataFrame) -> pd.DataFrame:
        lg.info(f"Merging post bank dataframes")
        initial_merge = pd.merge(contracts, phones, on='id')
        final_merge = pd.merge(initial_merge, addresses, on='id')
        return final_merge

    def _clear_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        lg.info(f"Cleaning resulting dataframe")
        decoded_df = DataframeDecoder(df).decode()
        if decoded_df is None:
            raise ValueError(f"Cleaner returned Null")
        lg.info(f"Cleaning finished")
        df = decoded_df
        return df