from dataclasses import dataclass
from typing import Any, Optional, Sequence, Set

from wiggle.sourcematerial import SourceMaterial

from .dictserialiazable import DictSerializable

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
    
    def __eq__(self, other: 'ReverbParameters'):
        return self.url == other.url and self.mix == other.mix

    def to_dict(self) -> dict:
        return self.__dict__
    
    @staticmethod
    def from_dict(data: dict) -> 'ReverbParameters':
        return ReverbParameters(**data)


@dataclass
class FilterParameters:
    center_frequency: float
    bandwidth: float
    
    def __hash__(self) -> int:
        return hash((self.center_frequency, self.bandwidth))
    
    def __eq__(self, other: 'FilterParameters'):
        return self.center_frequency == other.center_frequency and self.bandwidth == other.bandwidth
    
    def to_dict(self) -> dict:
        return self.__dict__

    @staticmethod
    def from_dict(data: dict) -> 'FilterParameters':
        return FilterParameters(**data)

@dataclass
class GainKeyPoint:
    time_seconds: float
    gain_value: float
    
    def __hash__(self) -> int:
        return hash((self.time_seconds, self.gain_value))
    
    def __eq__(self, other: 'GainKeyPoint'):
        return self.time_seconds == other.time_seconds and self.gain_value == other.gain_value
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @staticmethod
    def from_dict(data: dict) -> 'GainKeyPoint':
        return GainKeyPoint(**data)


@dataclass
class GainParameters:
    interpolation: str
    keypoints: Sequence[GainKeyPoint]
    
    def __hash__(self) -> int:
        return hash((self.interpolation, *[hash(k) for k in self.keypoints]))
    
    def __eq__(self, other: 'GainParameters'):
        if len(self.keypoints) != len(other.keypoints):
            return False
        
        return \
            self.interpolation == other.interpolation \
            and all(a == b for a, b in zip(self.keypoints, other.keypoints))
    
    def to_dict(self) -> dict:
        return self.__dict__
    
    @staticmethod
    def from_dict(data: dict) -> 'GainParameters':
        return GainParameters(
            interpolation=data['interpolation'], 
            keypoints=[GainKeyPoint.from_dict(x) for x in data['keypoints']])

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
    
    @property
    def source_material(self) -> Set[SourceMaterial]:
        return set([SourceMaterial(url=self.url)])
    
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
    
    def __eq__(self, other: 'SamplerParameters'):
        return self.url == other.url \
            and self.start_seconds == other.start_seconds \
            and self.duration_seconds == other.duration_seconds \
            and self.time_stretch == other.time_stretch \
            and self.pitch_shift == other.pitch_shift \
            and self.filter == other.filter \
            and self.normalize == other.normalize \
            and self.gain == other.gain \
            and self.reverb == other.reverb
    
    @staticmethod
    def from_dict(data: dict) -> 'SamplerParameters':
        return SamplerParameters(
            url=data['url'],
            start_seconds=data.get('start_seconds', None),
            duration_seconds=data.get('duration_seconds', None),
            time_stretch=data.get('time_stretch', None),
            pitch_shift=data.get('pitch_shift', None),
            filter=FilterParameters.from_dict(data['filter_parameters']) if 'filter_parameters' in data else None,
            normalize=data.get('normalize', None),
            gain=GainParameters.from_dict(data['gain_parameters']) if 'gain_parameters' in data else None,
            reverb=ReverbParameters.from_dict(data['reverb_parameters']) if 'reverb_parameters' in data else None
        )

    def to_dict(self) -> dict:
        d = dict(
            url=self.url,
            start_seconds=self.start_seconds,
            duration_seconds=self.duration_seconds,
            time_stretch=self.time_stretch or None,
            pitch_shift=self.pitch_shift or None,
            filter=self.filter.to_dict() if self.filter is not None else None,
            normalize=self.normalize,
            gain=self.gain.to_dict() if self.gain is not None else None,
            reverb=self.reverb.to_dict() if self.reverb is not None else None
        )
        return {k: v for k, v in d.items() if v is not None}

    
    
