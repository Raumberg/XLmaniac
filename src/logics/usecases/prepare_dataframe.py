from pandas import DataFrame

from xlord.src.processors.core.readers import FileReader
from interfaces.paths import Path, PathReader

class PrepareDataframe():
    def __init__(self, path: Path.FULL_PATH):
        self.path = path
        self.reader = FileReader(self.path)

    def cast(self) -> DataFrame:
        dataframe = self.reader.read_file()
        return dataframe


class PathFinder(PathReader):
    def __init__(self, path: Path):
        ...
