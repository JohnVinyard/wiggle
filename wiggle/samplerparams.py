from dataclasses import dataclass
from typing import Any, Optional, Sequence

from wiggle.basesynth import DictSerializable
from .sequencer import Event
from copy import deepcopy

allowed_interpolation_types = set([
    "linear", "quadratic", "cubic"
])

def get_interpolation(name: str) -> str:
    if name not in allowed_interpolation_types:
        raise ValueError(f'{name} is not an allowed interpolation type')
    return name

@dataclass
class NullObject(DictSerializable):
    
    def to_dict(self) -> dict:
        return {}

@dataclass
class ReverbParameters(DictSerializable):
    url: str
    mix: float
    
    def __hash__(self) -> int:
        return hash((self.url, self.mix))

    def to_dict(self) -> dict:
        return self.__dict__


@dataclass
class FilterParameters:
    center_frequency: float
    bandwidth: float
    
    def __hash__(self) -> int:
        return hash((self.center_frequency, self.bandwidth))
    
    def to_dict(self) -> dict:
        return self.__dict__

@dataclass
class GainKeyPoint:
    time_seconds: float
    gain_value: float
    
    def __hash__(self) -> int:
        return hash((self.time_seconds, self.gain_value))
    
    def to_dict(self) -> dict:
        return self.__dict__

@dataclass
class GainParameters:
    interpolation: str
    keypoints: Sequence[GainKeyPoint]
    
    def __hash__(self) -> int:
        return hash((self.interpolation, *[hash(k) for k in self.keypoints]))
    
    def to_dict(self) -> dict:
        return self.__dict__

@dataclass
class SamplerParameters(DictSerializable):
    url: str
    start_seconds: float = 0
    duration_seconds: float = 0
    time_stretch: Optional[float] = None
    pitch_shift: Optional[float] = None
    filter: Optional[FilterParameters] = None
    normalize: Optional[bool] = None
    gain: Optional[GainParameters] = None
    reverb: Optional[ReverbParameters] = None

    
    def __hash__(self) -> int:
        return hash((
            self.url, 
            self.start_seconds, 
            self.duration_seconds, 
            self.time_stretch, 
            self.pitch_shift, 
            hash(self.filter), 
            self.normalize, 
            hash(self.gain), 
            hash(self.reverb)))
    
    def once(self, sampler: Any):
        return Event(
            gain=1, time=0, synth=sampler.render, params=deepcopy(self))

    def to_dict(self) -> dict:
        return dict(
            url=self.url,
            start_seconds=self.start_seconds,
            duration_seconds=self.duration_seconds,
            time_stretch=self.time_stretch,
            pitch_shift=self.pitch_shift,
            filter=(self.filter or NullObject()).to_dict(),
            normalize=self.normalize,
            gain=(self.gain or NullObject()).to_dict(),
            reverb=(self.reverb or NullObject()).to_dict()
        )

    
    
