import requests
import conjure
from soundfile import SoundFile
from io import BytesIO
import numpy as np
import librosa
from functools import lru_cache
from typing import IO

# TODO: Fix conjure typing
# TODO: Make sure that the path is configurable
collection = conjure.LmdbCollection(path='audio-data')

def audio_io(
        samples: np.ndarray, 
        samplerate: int, 
        format: str = 'WAV', 
        subtype: str = 'PCM_16'):
    io = BytesIO()
    
    with SoundFile(io, mode='w', samplerate=samplerate, format=format, subtype=subtype) as sf:
        sf.write(samples)
    
    io.seek(0)
    return io

def audio_bytes(
        samples: np.ndarray, 
        samplerate: int, 
        format: str='WAV', 
        subtype: str='PCM_16') -> bytes:
    
    io = audio_io(samples, samplerate, format, subtype)
    return io.read()

@conjure.conjure(
    content_type='application/octet-stream',
    storage=collection,
    func_identifier=conjure.LiteralFunctionIdentifier('fetchaudio'),
    param_identifier=conjure.ParamsHash(),
    serializer=conjure.IdentitySerializer(),
    deserializer=conjure.IdentityDeserializer(),
    prefer_cache=True,
    read_from_cache_hook=lambda x: print(f'Reading from cache for url {x}')
)
def fetch_audio_from_url(url: str) -> bytes:
    resp = requests.get(url)
    resp.raise_for_status()
    print(f'fetched audio from URL {url} with len {len(resp.content)}')
    return resp.content
    

@conjure.numpy_conjure(
    storage=collection,
    content_type='application/octet-stream',
    read_hook=lambda x: print(f'Resampled version already cached'))
def fetch_audio_data_at_samplerate(url: str, samplerate: int) -> np.ndarray:
    audio_bytes = fetch_audio_from_url(url)
    with SoundFile(BytesIO(audio_bytes)) as sf:
        sf.seek(0)
        samples = sf.read()
        
        if sf.samplerate != samplerate:
            samples = librosa.resample(
                samples, 
                orig_sr=sf.samplerate, 
                target_sr=samplerate,
                res_type='fft')
        
        if sf.channels > 1:
            samples = np.sum(samples, axis=1) * 0.5
            
        print(f'Returned samples from url {url} with sample length {len(samples)}')
        return samples

# TODO: In-memory cache size should be configurable.  Also, the size of
# cache items can be highly variable, so an approach that expresses
# storage limits in bytes is probably more appropriate
@lru_cache(maxsize=1024)
def fetch_audio_data(url: str, samplerate: int):
    return fetch_audio_data_at_samplerate(url, samplerate)

class AudioFetcher(object):
    """
    Class for fetching audio over HTTP with multiple levels
    of caching, both on-disk and in-memory.    
    """
    def __init__(self, samplerate: int, format: str='WAV', subtype: str='PCM_16'):
        super().__init__()
        self.samplerate = samplerate
        self.format = format
        self.subtype = subtype
    
    def __call__(self, url: str) -> np.ndarray:
        return self.fetch(url)
    
    def fetch(self, url: str) -> np.ndarray:
        return fetch_audio_data(url, self.samplerate)
    
    def fetch_io(self, url: str) -> IO:
        samples = self.fetch(url)
        return audio_io(
            samples, 
            self.samplerate, 
            format=self.format, 
            subtype=self.subtype)
    
    def fetch_bytes(self, url: str) -> bytes:
        samples = self.fetch(url)
        return audio_bytes(
            samples, 
            self.samplerate, 
            format=self.format, 
            subtype=self.subtype)
        