from typing import Protocol, Tuple
from enum import Enum

class Path(Enum):
    PATH = "path"
    FILE = "file"
    EXTENSION = "ext"
    FULL_PATH = ""

class Extension(Enum):
    XLSX = ".xlsx"
    CSV = ".csv"
    JSON = ".json"
    PDF = ".pdf"
    DOCX = ".docx"

class PathReader(Protocol):
    def find(self) -> Tuple[Path, str]:
        ...

class PathWriter(Protocol):
    def write(self) -> Tuple[Path, str]:
        ...