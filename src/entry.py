import logging as lg

from src.processors.core.readers import FileReader
from src.processors.core.data import DataProcessor
from src.processors.core.writers import DataWriter

from src.interfaces.paths import Extension

def execute() -> None:
    lg.info('Executing |main|')
    try:
        path = r"C:\Users\nikita.shestopalov\Documents\PY\conture"
        file = r"fasp-1"
        extension = r".xlsx"

        file_reader = FileReader(path, file, extension)
        data_processor = DataProcessor()
        data_writer = DataWriter()

        dataset = file_reader.read_file()
        assert dataset is not None, lg.error("Reading failed")

        dataset = data_processor.process_data(dataset)

        data_writer.save_file(dataset, method=Extension.XLSX)
    except Exception as e:
        lg.exception('Err in |main|')
        lg.error(f'Err::{e}')