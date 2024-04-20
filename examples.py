from wiggle import Sampler, SamplerParameters, FilterParameters, \
    GainParameters, GainKeyPoint, ReverbParameters, AudioFetcher, Event, Sequencer, SequencerParams
from io import BytesIO
import numpy as np
from copy import deepcopy

def sequencer_example():
    kick = SamplerParameters(
        url='https://one-laptop-per-child.s3.amazonaws.com/tamtam44old/drum1kick.wav',
        start_seconds=0,
        reverb=ReverbParameters(
            url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
            mix=0.5
        )
    )
    
    samplerate = 22050
    speed = 0.25
    
    sampler = Sampler(fetcher = AudioFetcher(samplerate))
    events = [
        # TODO: _render should not be a private-ish method
        Event(time=i, synth=sampler._render, params=kick, gain=1) 
        for i in np.arange(start=0, stop=1, step=0.25)
    ]
    sequencer = Sequencer(samplerate)
    sequencer_params = SequencerParams(events=events, speed=speed, normalize=True)
    
    seq_events = [
        Event(time=i, synth=sequencer._render, params=sequencer_params, gain=1)
        for i in range(4)
    ]
    
    echoed = deepcopy(seq_events)
    for echo in echoed:
        echo.time = echo.time + np.random.uniform(0, 0.05)
        echo.gain = 0.1
    
    top_level_params = SequencerParams(events=[*seq_events, *echoed], speed=speed, normalize=True)
    
    bio = BytesIO()
    sequencer.render(top_level_params, bio)
    bio.seek(0)
    
    with open('result.wav', 'wb') as f:
        f.write(bio.read())


def sampler_example():
    fetcher = AudioFetcher(22050)
    sampler = Sampler(fetcher)
    
    bio = BytesIO()
    
    sampled = sampler.render(
        SamplerParameters(
            url='https://one-laptop-per-child.s3.amazonaws.com/AnthonyKozar16/vocalStretch_it-8x-30x.wav',
            start_seconds=1,
            duration_seconds=0.5,
            gain=GainParameters(
                interpolation='linear',
                keypoints=[
                    GainKeyPoint(time_seconds=0, gain_value=0),
                    GainKeyPoint(time_seconds=0.01, gain_value=1),
                    GainKeyPoint(time_seconds=0.011, gain_value=0.001),
                    GainKeyPoint(time_seconds=0.012, gain_value=0.0001),
                    GainKeyPoint(time_seconds=1, gain_value=0),
                ]
            ),
            normalize=True,
            filter=FilterParameters(
                center_frequency=0.01,
                bandwidth=0.06
            ),
            pitch_shift=4,
            reverb=ReverbParameters(
                url='https://matching-pursuit-reverbs.s3.amazonaws.com/Nice+Drum+Room.wav',
                mix=0.99
            )
        ), 
        bio)
    bio.seek(0)
    
    with open('result.wav', 'wb') as f:
        f.write(bio.read())
    

if __name__ == '__main__':
    sequencer_example()