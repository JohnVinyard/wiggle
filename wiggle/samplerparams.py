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

@dataclass
class FilterParameters:
    center_frequency: float
    bandwidth: float

@dataclass
class GainKeyPoint:
    time_seconds: float
    gain_value: float

@dataclass
class GainParameters:
    interpolation: str
    keypoints: Sequence[GainKeyPoint]

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
    
    
