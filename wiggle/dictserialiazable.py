from typing import Protocol


class DictSerializable(Protocol):
    def to_dict(self) -> dict:
        raise NotImplementedError('')