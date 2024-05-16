from subprocess import PIPE, Popen
import numpy as np
from soundfile import SoundFile
from io import BytesIO
from abc import ABC, abstractmethod
from typing import IO, Any, Protocol
import jsonschema
import jsonschema.exceptions
import os
import json

class DictSerializable(Protocol):
    def to_dict(self) -> dict:
        raise NotImplementedError('')


class HasId(Protocol):
    @property
    def id(self):
        raise NotImplementedError('')

def iter_sample_chunks(arr: np.ndarray, chunksize: int = 1024):
    for i in range(0, len(arr), chunksize):
        yield arr[i: i + chunksize]

def write_samples(
        flo: IO, 
        samples: np.ndarray, 
        samplerate: int, 
        format='WAV', 
        subtype='PCM_16') -> IO:
    
    with SoundFile(flo, 'w', samplerate=samplerate, format=format, subtype=subtype) as sf:
        for chunk in iter_sample_chunks(samples):
            flo.write(chunk)
    
    return flo


def encode_samples(
        samples: np.ndarray, 
        samplerate: int, 
        format='WAV', 
        subtype='PCM_16') -> bytes:
    
    io = write_samples(
        BytesIO(), 
        samples, 
        samplerate=samplerate, 
        format=format, 
        subtype=subtype)
    io.seek(0)
    return io.read()

class BaseSynth(ABC):
    def __init__(self):
        super().__init__()
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def id(self) -> int:
        pass
    
    @property
    def schema(self) -> dict:
        module_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(module_dir, f'{self.name}.json')
        with open(path, 'r') as f:
            return json.load(f)
    
    def validate(self, params: DictSerializable):
        params_dict = params.to_dict()
        
        try:
            jsonschema.validate(params_dict, self.schema)
        except jsonschema.exceptions.ValidationError as e:
            raise ValueError(f'The provided sampler parameters are not valid with error {e}')
        except jsonschema.exceptions.SchemaError as e:
            raise ValueError(f'The provided _schema_ was itself not valid')
    
    @property
    @abstractmethod
    def samplerate(self) -> int:
        pass
    
    def __call__(self, params: Any) -> np.ndarray:
        return self.render(params)

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

            for chunk in iter_sample_chunks(samples, chunksize=2048):
                sf.write(chunk)
        
        flo.seek(0)
        return flo