from dataclasses import dataclass
from typing import Optional, Sequence

allowed_interpolation_types = set([
    "linear", "quadratic", "cubic"
])

def get_interpolation(name: str) -> str:
    if name not in allowed_interpolation_types:
        raise ValueError(f'{name} is not an allowed interpolation type')
    return name

@dataclass
class ReverbParameters:
    url: str
    mix: float
    
    def __hash__(self) -> int:
        return hash((self.url, self.mix))

@dataclass
class FilterParameters:
    center_frequency: float
    bandwidth: float
    
    def __hash__(self) -> int:
        return hash((self.center_frequency, self.bandwidth))

@dataclass
class GainKeyPoint:
    time_seconds: float
    gain_value: float
    
    def __hash__(self) -> int:
        return hash((self.time_seconds, self.gain_value))

@dataclass
class GainParameters:
    interpolation: str
    keypoints: Sequence[GainKeyPoint]
    
    def __hash__(self) -> int:
        return hash((self.interpolation, *[hash(k) for k in self.keypoints]))

@dataclass
class SamplerParameters:
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
    
    
