from dataclasses import dataclass

@dataclass
class ExcelFile:
    path: str
    workbook: object

@dataclass
class MacroConfig:
    columns: list
    vba_module_path: str
    macro_name: str