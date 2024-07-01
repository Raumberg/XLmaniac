from __future__ import annotations

from typing import Protocol
from enum import Enum

from pandas import DataFrame

class FileType(Enum):
    EXCEL = 'excel'
    CSV = 'csv'
    JSON = 'json'

class FileReaderProtocol(Protocol):
    def read_file(self) -> DataFrame:
        ...

class DataProcessorProtocol(Protocol):
    def process_data(self, df: DataFrame) -> DataFrame:
        ...

class DataWriterProtocol(Protocol):
    def save_file(self, df: DataFrame, method: FileType) -> None:
        ...