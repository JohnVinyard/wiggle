import requests
import conjure
from soundfile import SoundFile
from io import BytesIO
import numpy as np
import librosa


# TODO: Fix conjure typing
collection = conjure.LmdbCollection(path='audio-data')

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


class AudioFetcher(object):
    def __init__(self, samplerate: int):
        super().__init__()
        self.samplerate = samplerate
    
    def __call__(self, url: str):
        return self.fetch(url)
    
    def fetch(self, url: str):
        return fetch_audio_data_at_samplerate(url, self.samplerate)