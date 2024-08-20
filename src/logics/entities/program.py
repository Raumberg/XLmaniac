from dataclasses import dataclass
import pathlib

@dataclass(frozen=False)
class ProgramPaths:
    input_path: str = ""
    output_path: str = pathlib.Path.home() / "Downloads"

@dataclass
class ProgramConfig:
    pass

program = ProgramPaths()