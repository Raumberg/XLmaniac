from typing import Protocol
from pandas import DataFrame

class Decoder(Protocol):
    def decode(self) -> DataFrame:
        ...