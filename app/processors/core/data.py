import pandas as pd

from app.namespaces.namespace import *
from interfaces.xl import DataProcessorProtocol
from app.processors import (PhoneDecoder, Clients, Phones, 
                            PassportDecoder, DebtDecoder, 
                            DateDecoder, PersonDecoder, 
                            RegisterDecoder)

class DataProcessor(DataProcessorProtocol):
    def __init__(self):
        self.decoders = [
            PersonDecoder,
            DateDecoder,
            PhoneDecoder,
            PassportDecoder,
            DebtDecoder,
            RegisterDecoder
        ]

    def process_data(self, df: pd.DataFrame) -> pd.DataFrame:
        for decoder in self.decoders:
            if decoder is PhoneDecoder:
                df = decoder(df, client=Clients.DEFAULT).decode(strategy=Phones.PHONES)
            else:
                df = decoder(df).decode()
        return df