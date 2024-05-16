from dataclasses import dataclass
from typing import Any, Callable, Sequence, Set, Union
import numpy as np
from wiggle.dictserialiazable import DictSerializable
from wiggle.basesynth import BaseSynth, HasId
from copy import deepcopy
import numpy as np

from wiggle.sourcematerial import SourceMaterial


class FourFourInterval:
    whole= 4
    measure = 4
    half = 2
    quarter = 1
    eighth = 0.5
    triplet = 1 / 3
    sixteenth = 0.25
    thirtysecond = 0.125
    sixtyfourth = 0.0625

whole = FourFourInterval.whole
measure = FourFourInterval.measure
half = FourFourInterval.half
quarter = FourFourInterval.quarter
eighth = FourFourInterval.eighth
sixteenth = FourFourInterval.sixteenth
thirtysecond = FourFourInterval.thirtysecond
sixtyfourth = FourFourInterval.sixtyfourth
triplet = FourFourInterval.triplet

@dataclass
class HasTime:
    time: float

@dataclass
class HasGain:
    gain: float

@dataclass
class Event(HasTime, HasGain):
    synth: Union[Callable, HasId]
    params: DictSerializable
    
    
    def translate(self, amt: float) -> 'Event':
        return Event(
            time=self.time + amt, 
            synth=self.synth, 
            params=deepcopy(self.params), 
            gain=self.gain)
    
    def __eq__(self, other: 'Event') -> bool:
        return self.params == other.params and self.synth == other.synth
    
    def time_scale(self, factor: float):
        return Event(
            time = self.time * factor, 
            synth=self.synth, 
            params=deepcopy(self.params), 
            gain=self.gain)
    
    def __lshift__(self, other: float) -> 'Event':
        return self.translate(-other)
    
    def __rshift__(self, other: float) -> 'Event':
        return self.translate(other)
    
    def to_dict(self):
        return dict(
            synth=self.synth.id if hasattr(self.synth, 'id') else self.synth, 
            params=self.params.to_dict())
    
    @staticmethod
    def from_dict(data: dict, restore_params: Callable, restore_synth: Callable) -> 'Event':
        synth_name_or_id = data['synth']
        params = restore_params(synth_name_or_id, data['params'])
        synth = restore_synth(synth_name_or_id)
        return Event(
            synth=synth, 
            params=params, 
            gain=data.get('gain', None), 
            time=data.get('time', None))
    


def repeat(every: float, fur: float, evt: Event) -> Sequence[Event]:
    return [evt >> x for x in np.arange(start=0, stop=fur, step=every)]

class TransformContext:
    pass


Transform = Callable[['SequencerParams', TransformContext], 'SequencerParams']



@dataclass
class SequencerParams(DictSerializable):
    # TODO: how to handle circular/nested type definitions?
    events: Sequence[Event]
    speed: float
    normalize: bool = True
        
    
    @property
    def source_material(self) -> Set[SourceMaterial]:
        
        def has_url(event: Event):
            return hasattr(event.params, 'url')
        
        sampler_params = filter(has_url, self.walk())
        return set(SourceMaterial(url=x.params.url) for x in sampler_params)
    
    def walk(self):
        
        def get_child_events(evt):
            p = getattr(evt, 'params', None)
            if p is None:
                return []
            
            nested = getattr(p, 'events', None)
            if nested is None:
                return []
            
            return nested
        
        
        to_walk = [*self.events]    
        
        while to_walk:
            nxt = to_walk.pop()
            
            for event in get_child_events(nxt):
                to_walk.append(event)
                

            yield nxt
        
    def once(self, synth: 'Sequencer') -> 'Event':
        return Event(gain=1, time=0, synth=synth.render, params=deepcopy(self))
    
    def __add__(self, other: 'SequencerParams') -> 'SequencerParams':
        """
        Overlay two patterns
        """
        return SequencerParams(
            events=[*self.events, *other.events], 
            speed=self.speed, 
            normalize=self.normalize)
    
    def time_scale(self, factor: float) -> 'SequencerParams':
        c = deepcopy(self)
        c.events = [e.time_scale(factor) for e in c.events]
        return c
    
    def translate(self, amt: float) -> 'SequencerParams':
        c = deepcopy(self)
        c.events = [e.translate(amt) for e in c.events]
        return c
    
    def __lshift__(self, other: float) -> 'SequencerParams':
        return self.translate(-other)
    
    def __rshift__(self, other: float) -> 'SequencerParams':
        return self.translate(other)
        
    def transform(self, t: Transform) -> 'SequencerParams':
        c = deepcopy(self)
        ctxt = TransformContext()
        transformed = t(c, ctxt)
        return transformed
    
    @staticmethod
    def from_dict(data: dict, restore_func: Callable, restore_synth: Callable) -> 'SequencerParams':
        return SequencerParams(
            events=[Event.from_dict(x, restore_func, restore_synth) for x in data['events']],
            speed=data.get('speed', None),
            normalize=data.get('normalize', None)
        )

    def to_dict(self) -> dict:
        return dict(
            speed=self.speed, 
            normalize=self.normalize, 
            events=[e.to_dict() for e in self.events])


class Sequencer(BaseSynth):
    def __init__(self, samplerate: int):
        super().__init__()
        self._samplerate = samplerate
    
    @property
    def name(self) -> str:
        return 'sequencer'
    
    def __eq__(self, other: 'Sequencer'):
        return self.id == other.id
    
    def hash(self):
        return hash(self.id)

    @property
    def id(self) -> int:
        return 2
        
    @property
    def samplerate(self):
        return self._samplerate
    
    def _calculate_time(self, event_time: float, speed: float):
        return event_time / speed
    
    
    def render(self, params: SequencerParams) -> np.ndarray:
        self.validate(params)
        
        renders: Sequence[np.ndarray] = [event.synth(event.params) * event.gain for event in params.events]
        
        end_times = [
            self._calculate_time(event.time, params.speed) + len(renders[i]) / self.samplerate 
            for i, event in enumerate(params.events)
        ]
        
        end_time = max(end_times)
        end_sample = int(end_time * self.samplerate)
        
        canvas = np.zeros((end_sample,), dtype=np.float32)
        
        # TODO: consider just using fft shift here
        for event, render in zip(params.events, renders):
            start_sample = int((event.time / params.speed) * self.samplerate)
            if start_sample < 0:
                raise ValueError('Negative samples not supported')
            end_sample = start_sample + len(render)
            duration = end_sample - start_sample
            canvas[start_sample: end_sample] += render[:duration]
        
        if params.normalize:
            canvas = canvas / (canvas.max() + 1e-8)
        
        print(f'Generated {len(canvas) / self.samplerate} seconds of audio')
        return canvas

    
    
    