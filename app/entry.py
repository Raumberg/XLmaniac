import logging as lg

from xlord.app.processors.core.reader import FileReader
from xlord.app.processors.core.data import DataProcessor
from xlord.app.processors.core.writer import DataWriter

def execute() -> None:
    lg.info('Executing $main')
    try:
        file_reader = FileReader()
        data_processor = DataProcessor()
        data_writer = DataWriter()
        dataset = file_reader.read_file()
        dataset = data_processor.process_data(dataset)
        data_writer.save_file(dataset)
    except Exception as e:
        lg.exception('Error in $main')
        lg.error(f'Err::{e}')