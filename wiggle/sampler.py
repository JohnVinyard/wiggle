from typing import Set, Tuple
import numpy as np
from scipy.interpolate import interp1d
from wiggle.basesynth import BaseSynth
from wiggle.fetch import AudioFetcher
from wiggle.samplerparams import FilterParameters, GainParameters, SamplerParameters, get_interpolation
from librosa.effects import time_stretch, pitch_shift
from scipy.stats import norm
from functools import lru_cache

def ensure_length(samples: np.ndarray, desired_length: int) -> np.ndarray:
    if len(samples) == desired_length:
        return samples
    
    if len(samples) > desired_length:
        raise ValueError(f'This method only supports lengthening, not shortening')

    diff = desired_length - len(samples)
    samples = np.pad(samples, pad_width=[(0, diff)])
    return samples


def normalize_lengths(a: np.ndarray, b: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    max_len = max(len(a), len(b))
    
    if len(a) < max_len:
        a = ensure_length(a, max_len)
    elif len(b) < max_len:
        b = ensure_length(b, max_len)
    
    return a, b
    

def fft_convolve(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    if len(a.shape) > 1 or len(b.shape) > 1:
        raise ValueError('1D arrays only are supported')
    
    a, b = normalize_lengths(a, b)
    
    a_spec = np.fft.rfft(a, axis=-1, norm='ortho')
    b_spec = np.fft.rfft(b, axis=-1, norm='ortho')
    
    conv = a_spec * b_spec
    final = np.fft.irfft(conv, axis=-1, norm='ortho')
    return final

def apply_envelope(samples: np.ndarray, params: GainParameters) -> np.ndarray:
    points = np.array([[x.time_seconds, x.gain_value] for x in params.keypoints])
    
    deltas = np.diff(points[:, 0], axis=0)
    
    if np.any(deltas < 0):
        raise ValueError('Times must be monotonically increasing')

    func = interp1d(points[:, 1], points[:, 0], kind=get_interpolation(params.interpolation))
    evaluation_times = np.linspace(0, 1, len(samples))
    envelope = func(evaluation_times)
    
    result = samples * envelope
    
    return result

def normalize(samples: np.ndarray) -> np.ndarray:
    return samples / (samples.max() + 1e-8)

def bandpass_filter(samples: np.ndarray, params: FilterParameters) -> np.ndarray:
    n_coeffs = len(samples) // 2 + 1
    domain = np.linspace(0, 1, n_coeffs)
    frozen = norm(params.center_frequency, params.bandwidth)
    pdf = frozen.pdf(domain)
    
    spec = np.fft.rfft(samples, axis=-1, norm='ortho')
    spec = spec * pdf
    samples = np.fft.irfft(spec, axis=-1, norm='ortho')
    return samples


def reverb(dry: np.ndarray, impulse_response: np.ndarray, mix: float) -> np.ndarray:
    wet = fft_convolve(dry, impulse_response)
    dry, wet = normalize_lengths(dry, wet)
    samples = (dry * (1 - mix)) + (wet * mix)
    return samples


# TODO: In-memory cache size should be configurable.  Also, the size of
# cache items can be highly variable, so an approach that expresses
# storage limits in bytes is probably more appropriate
@lru_cache(maxsize=1024)
def render(params: SamplerParameters, samplerate: int, fetcher: AudioFetcher) -> np.ndarray:
    # first, get the audio
    samples = fetcher(params.url)
    
    # slice the audio if start and duration are provided
    start_sample = params.start_seconds * samplerate
    
    # If the duration is zero, then we assume we'd like all available samples
    # after the start
    duration = (params.duration_seconds * samplerate) or (len(samples) * samplerate)
    
    samples = samples[int(start_sample): int(start_sample + duration)]
    
    if params.time_stretch:
        samples = time_stretch(samples, params.time_stretch)
    
    if params.pitch_shift:
        samples = pitch_shift(
            samples, samplerate, n_steps=params.pitch_shift)
    
    if params.filter:
        samples = bandpass_filter(samples, params.filter)
    
    if params.reverb:
        impulse_response = fetcher(params.reverb.url)
        samples = reverb(samples, impulse_response, mix=params.reverb.mix)
    
    if params.gain:
        samples = apply_envelope(samples, params.gain)
    
    if params.normalize:
        samples = normalize(samples)
    
    return samples

class Sampler(BaseSynth):
    
    def __init__(self, fetcher: AudioFetcher):
        super().__init__()
        self.fetcher = fetcher
    
    def __eq__(self, other: 'Sampler'):
        return self.id == other.id
    
    def __hash__(self) -> int:
        return hash(self.id)
        
    @property
    def samplerate(self):
        return self.fetcher.samplerate
    
    def render(self, params: SamplerParameters) -> np.ndarray:
        # self.validate(params)
        return render(params, self.samplerate, self.fetcher)

    @property
    def name(self) -> str:
        return 'sampler'

    @property
    def id(self) -> int:
        return 1

