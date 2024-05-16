from typing import Protocol
from dataclasses import dataclass

@dataclass
class SourceMaterial:
    url: str
    
    def __hash__(self):
        return hash(self.url)

    def __eq__(self, other: 'SourceMaterial'):
        return self.url == other.url