from typing import List
from .sequencer import Sequencer
from .sampler import Sampler
from .basesynth import BaseSynth
from .fetch import AudioFetcher

def list_synths(fetcher: AudioFetcher) -> List[BaseSynth]:
    return [
        Sampler(fetcher),
        Sequencer(fetcher.samplerate)
    ]