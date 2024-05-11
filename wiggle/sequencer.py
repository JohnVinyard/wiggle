from dataclasses import dataclass
from typing import Any, Callable, Sequence
import numpy as np
from wiggle.BaseSynth import BaseSynth
from copy import deepcopy
import numpy as np


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
    synth: Callable
    params: Any
    
    def translate(self, amt: float) -> 'Event':
        return Event(
            time=self.time + amt, 
            synth=self.synth, 
            params=deepcopy(self.params), 
            gain=self.gain)
    
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
    


def repeat(every: float, fur: float, evt: Event) -> Sequence[Event]:
    return [evt >> x for x in np.arange(start=0, stop=fur, step=every)]

class TransformContext:
    pass


Transform = Callable[['SequencerParams', TransformContext], 'SequencerParams']

@dataclass
class SequencerParams:
    # TODO: how to handle circular/nested type definitions?
    events: Sequence[Event]
    speed: float
    normalize: bool = True
    
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
    
    


class Sequencer(BaseSynth):
    def __init__(self, samplerate: int):
        super().__init__()
        self._samplerate = samplerate
    
    @property
    def samplerate(self):
        return self._samplerate
    
    def _calculate_time(self, event_time: float, speed: float):
        return event_time / speed
    
    
    def render(self, params: SequencerParams) -> np.ndarray:
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
    