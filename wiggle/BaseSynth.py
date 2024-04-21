import numpy as np
from soundfile import SoundFile


from abc import ABC, abstractmethod
from typing import IO, Any


class BaseSynth(ABC):
    def __init__(self):
        super().__init__()

    @property
    @abstractmethod
    def samplerate(self) -> int:
        pass

    @abstractmethod
    def render(self, params: Any) -> np.ndarray:
        pass

    @abstractmethod
    def play(self, params: Any) -> None:
        pass

    def write(self, params: Any, flo: IO) -> IO:
        samples = self.render(params)
        with SoundFile(
                flo, mode='w',
                samplerate=self.samplerate,
                format='wav',
                subtype='pcm_16',
                channels=1) as sf:

            sf.write(samples)
        flo.seek(0)
        return flo