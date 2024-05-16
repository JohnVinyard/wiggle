from typing import List, Union

from wiggle.samplerparams import SamplerParameters
from .sequencer import Sequencer, SequencerParams
from .sampler import Sampler
from .basesynth import BaseSynth
from .fetch import AudioFetcher
import numpy as np

def materialize_synths(fetcher: AudioFetcher) -> List[BaseSynth]:
    return [
        Sampler(fetcher),
        Sequencer(fetcher.samplerate)
    ]

def get_synth(fetcher: AudioFetcher, id_or_name: Union[str, int]) -> BaseSynth:
    if isinstance(id_or_name, str):
        try:
            return get_synth_by_id(fetcher, int(id_or_name))
        except ValueError:
            return get_synth_by_name(fetcher, id_or_name)
    elif isinstance(id_or_name, int):
        return get_synth_by_id(fetcher, id_or_name)
    else:
        raise ValueError(f'id_or_name must be str or int but was {id_or_name.__class__.__name__}')

def list_synths(fetcher: AudioFetcher) -> List[BaseSynth]:
    return materialize_synths(fetcher)

def get_synth_by_id(fetcher: AudioFetcher, id: int) -> BaseSynth:
    synths = list_synths(fetcher)
    synth = list(filter(lambda x: x.id == id, synths))
    if len(synth) == 0:
        raise KeyError(id)
    
    return synth[0]

def get_synth_by_name(fetcher: AudioFetcher, name: str) -> BaseSynth:
    synths = list_synths(fetcher)
    synth = list(filter(lambda x: x.name == name, synths))
    if len(synth) == 0:
        raise KeyError(id)
    return synth[0]

def render(
        synth: Union[int, str, BaseSynth], 
        params: Union[SamplerParameters, SequencerParams], 
        fetcher: AudioFetcher) -> np.ndarray:
    
    if isinstance(synth, int):
        synth = get_synth_by_id(fetcher, synth)
    elif isinstance(synth, str):
        synth = get_synth_by_name(fetcher, synth)
    else:
        # synth is already an instance
        pass
    
    samples = synth.render(params)
    return samples
    