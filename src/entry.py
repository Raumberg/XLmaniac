import logging as lg

from src.processors.core.readers import FileReader
from src.processors.core.data import DataProcessor
from src.processors.core.writers import DataWriter
from src.namespaces.enums import Datasets

from src.interfaces.paths import Extension

def execute() -> None:
    lg.info('Executing |main|')
    try:
        path = r"C:\Users\nikita.shestopalov\Documents\PY\conture"
        file = r"post"
        extension = r".xlsx"

        file_reader = FileReader(path, file, extension)
        data_processor = DataProcessor()
        data_writer = DataWriter()

        dataset_hash = file_reader.read_file()
        assert dataset_hash is not None, "Reading failed"

        datasets = []
        for sheet, dataset in dataset_hash.items():
            if sheet == 'default':
                processed_dataset = data_processor.process_data(dataset)
                data_writer.save_file(processed_dataset, method=Extension.XLSX)
            if sheet != 'default':
                datasets.append(dataset)
        if datasets:
            contracts, phones, addresses = datasets
            processed_dataset = data_processor.process_post(contracts=contracts, phones=phones, addresses=addresses)
            data_writer.save_file(processed_dataset, method=Extension.XLSX)
    except Exception as e:
        lg.exception('Err in |main|')
        lg.error(f'Err::{e}')
