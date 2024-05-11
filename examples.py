from wiggle import Sampler, SamplerParameters, FilterParameters, \
    GainParameters, GainKeyPoint, ReverbParameters, AudioFetcher, \
    Sequencer, SequencerParams, eighth, quarter, thirtysecond, measure

import numpy as np
from copy import deepcopy

from wiggle.sequencer import repeat

def sequencer_example():
    hihat = SamplerParameters(
        url='https://one-laptop-per-child.s3.amazonaws.com/tamtamDrumKits16/drum4tr808closed.wav',
        reverb=ReverbParameters(
            url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
            mix=0.1,
        ),
        filter=FilterParameters(
            center_frequency=0.1,
            bandwidth=0.2
        )
    )
    
    kick = SamplerParameters(
        url='https://one-laptop-per-child.s3.amazonaws.com/tamtam44old/drum1kick.wav',
        reverb=ReverbParameters(
            url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
            mix=0.5
        ),
        filter=FilterParameters(
            center_frequency=0.02,
            bandwidth=0.05
        )
        
    )
    
    samplerate = 22050
    
    # TODO: Bpm class
    speed = 1
    
    sampler = Sampler(fetcher = AudioFetcher(samplerate))
    sequencer = Sequencer(samplerate)
    
    hat_params = SequencerParams(
        events=repeat(every=eighth, fur=measure, evt=hihat.once(sampler)),
        speed=speed,
        normalize=True) >> thirtysecond
    

    kick_params = SequencerParams(
        events=repeat(every=quarter, fur=measure, evt=kick.once(sampler)),
        speed=speed,
        normalize=True
    )
    
    # overlay the two sequences
    sequencer_params = hat_params + kick_params
    
    # repeat the entire pattern four times
    seq_params = SequencerParams(
        events=repeat(every=measure, fur=measure * 4, evt=sequencer_params.once(sequencer)),
        speed=speed,
        normalize=True
    )
    
    # TODO: nice way to visit each node in the graph and transform
    echoed = deepcopy(seq_params.events)
    for echo in echoed:
        echo.time = echo.time + np.random.uniform(0, 0.2)
        echo.gain = np.random.uniform(0.01, 0.4)
    echoed_params = SequencerParams(echoed, speed=speed, normalize=sequencer_params.normalize)
    
    top_level_params = seq_params + echoed_params
    
    sequencer.play(top_level_params)


def sampler_example():
    fetcher = AudioFetcher(22050)
    sampler = Sampler(fetcher)
    
    params = SamplerParameters(
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
    )
        
    
    
    with open('result.wav', 'wb') as f:
        sampler.write(params, f)
    

if __name__ == '__main__':
    sequencer_example()