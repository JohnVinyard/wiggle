from typing import List
from .sequencer import Sequencer
from .sampler import Sampler
from .basesynth import BaseSynth
from .fetch import AudioFetcher

def materialize_synths(fetcher: AudioFetcher) -> List[BaseSynth]:
    return [
        Sampler(fetcher),
        Sequencer(fetcher.samplerate)
    ]

def list_synths(fetcher: AudioFetcher) -> List[BaseSynth]:
    return materialize_synths(fetcher)

def get_synths_by_id(fetcher: AudioFetcher, id: int) -> BaseSynth:
    synths = list_synths(fetcher)
    synth = list(filter(lambda x: x.id == id, synths))
    if len(synth) == 0:
        raise KeyError(id)
    
    return synth[0]

def get_synths_by_name(fetcher: AudioFetcher, name: str) -> BaseSynth:
    synths = list_synths(fetcher)
    synth = list(filter(lambda x: x.name == name, synths))
    if len(synth) == 0:
        raise KeyError(id)
    return synth[0]