from wiggle.basesynth import BaseSynth
from wiggle.fetch import AudioFetcher
from wiggle.sequencer import Sequencer
from wiggle.synth import Sampler
from wiggle.synthtype import SynthType
from typing import Any, IO, Union
import numpy as np
from dataclasses import dataclass

@dataclass
class Permissions:
    fetch_external: bool


class Wiggle(object):
    
    def __init__(
            self, 
            samplerate: int, 
            fetcher: AudioFetcher, 
            permissons: Permissions):

        super().__init__()
        self.samplerate = samplerate
        self.fetcher = fetcher
        self.permissions = permissons
    
    def store_media(self, audio_resource: Union[str, IO]) -> str:
        if isinstance(audio_resource, str):
            data = self.fetcher.fetch(audio_resource)
        else:
            pass
    
    def store_preset(self, synth_type: SynthType, params: Any) -> str:
        """
        Store the preset metadata, and return task data which can
        render the preset and store the associated media and 
        render records
        """
        raise NotImplementedError('')
    
    def get_preset(self, preset_id: int):
        raise NotImplementedError('')
    
    def get_preset_audio(self, preset_id: int):
        raise NotImplementedError('')
    
    def list_presets(self):
        raise NotImplementedError()
    
    def list_synths(self):
        return [
            Sampler(self.fetcher),
            Sequencer(self.samplerate)
        ]
    
    def get_synth(self, synth_type: SynthType) -> BaseSynth:
        if synth_type == SynthType.Sampler:
            return Sampler(self.fetcher)
        elif synth_type == SynthType.Sequencer:
            return Sequencer(self.samplerate)
        else:
            raise ValueError(f'Unknown synth type {synth_type}')
    
    def render(self, synth_type: SynthType, params: Any) -> np.ndarray:
        synth = self.get_synth(synth_type)
        samples = synth.render(params)
        return samples
    
    def write(self, synth_type: SynthType, params: Any, io: IO) -> IO:
        synth = self.get_synth(synth_type)
        written = synth.write(params, io)
        return written
    
    