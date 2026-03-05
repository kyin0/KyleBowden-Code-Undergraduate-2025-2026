from dataclasses import dataclass

@dataclass
class Finding:
    rule : str
    message : str