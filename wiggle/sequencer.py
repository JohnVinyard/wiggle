from dataclasses import dataclass
from typing import Any, Callable, Optional, Sequence
import numpy as np
from wiggle.synth import BaseSynth

@dataclass
class Event:
    time: float
    synth: Callable
    params: Any
    gain: float


@dataclass
class SequencerParams:
    # TODO: how to handle circular/nested type definitions?
    events: Sequence[Event]
    speed: float
    normalize: Optional[bool]


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
    
    def play(self, params: SequencerParams):
        raise NotImplementedError()
    
    