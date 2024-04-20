from dataclasses import dataclass
from typing import IO, Any, Callable, Optional, Sequence, Union
import numpy as np
from soundfile import SoundFile
from wiggle.samplerparams import SamplerParameters

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


class Sequencer(object):
    def __init__(self, samplerate: int):
        super().__init__()
        self.samplerate = samplerate
    
    def _calculate_time(self, event_time: float, speed: float):
        return event_time / speed
    
    
    def _render(self, params: SequencerParams) -> np.ndarray:
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
    
    def render(self, params: SequencerParams, flo: IO) -> IO:
        # TODO: this should be factored out into a common base class
        # or helper function
        samples = self._render(params)
        with SoundFile(
                flo, mode='w', 
                samplerate=self.samplerate, 
                format='wav', 
                subtype='pcm_16', 
                channels=1) as sf:
            
            sf.write(samples)
        flo.seek(0)
        return flo
        
    
    def play(self, params: SequencerParams):
        raise NotImplementedError()
    
    