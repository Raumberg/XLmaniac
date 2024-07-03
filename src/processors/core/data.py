import pandas as pd
import logging as lg

from src.namespaces.namespace import *
from src.interfaces.xl import DataProcessorProtocol

from src.processors.data.dates import DateDecoder
from src.processors.data.debt import DebtDecoder
from src.processors.data.person import PersonDecoder
from src.processors.data.passport import PassportDecoder
from src.processors.data.register import RegisterDecoder
from src.processors.data.phones import PhoneParser, Clients
from src.processors.data.dataframe import DataframeDecoder

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