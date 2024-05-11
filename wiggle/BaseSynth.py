from subprocess import PIPE, Popen
import numpy as np
from soundfile import SoundFile
from io import BytesIO
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

    def play(self, params: Any, wait_for_user_input=True) -> None:
        io = self.write(params, BytesIO())
        
        proc = Popen(f'aplay', shell=True, stdin=PIPE)
        
        if proc.stdin is not None:
            proc.stdin.write(io.read())
            proc.communicate()
        
        if wait_for_user_input:
            input('Next')

    def write(self, params: Any, flo: IO) -> IO:
        samples = self.render(params)
        with SoundFile(
                flo, 
                mode='w',
                samplerate=self.samplerate,
                format='wav',
                subtype='pcm_16',
                channels=1) as sf:

            sf.write(samples)
        flo.seek(0)
        return flo