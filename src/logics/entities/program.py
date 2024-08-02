from dataclasses import dataclass

@dataclass
class ProgramPaths:
    input_path: str = 'assets/uploads'
    output_path: str = 'assets/downloads'

@dataclass
class ProgramConfig:
    pass