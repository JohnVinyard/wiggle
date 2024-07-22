from typing import List
from wiggle import Sampler, SamplerParameters, FilterParameters, \
    GainParameters, GainKeyPoint, ReverbParameters, AudioFetcher, \
    Sequencer, SequencerParams, eighth, quarter, thirtysecond, measure, sixteenth

import numpy as np
from copy import deepcopy
from itertools import chain

from wiggle.sequencer import Event, repeat

def mesh_example():
    
    samplerate = 22050
    
    # TODO: Bpm class
    speed = 1
    
    sampler = Sampler(fetcher = AudioFetcher(samplerate))
    sequencer = Sequencer(samplerate)
    
    def tom(t: float) -> SequencerParams:
        
        tm = SamplerParameters(
            url='https://one-laptop-per-child.s3.amazonaws.com/tamtam44old/drum1floortom.wav',
            reverb=ReverbParameters(
                url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
                mix=0.9,
            ),
            filter=FilterParameters(
                center_frequency=float(np.random.uniform(0.08, 0.12)),
                bandwidth=float(np.random.uniform(0.15, 0.25))
            ),
        )
        
        event = Event(
            gain=float(np.random.uniform(1, 2)), 
            time=t + float(np.random.uniform(0, 0.01)), 
            params=tm, 
            synth=sampler
        )
        
        tom_params = SequencerParams(
            events=[event, event >> sixteenth] if t % 4 == 0 else [],
            speed=speed,
            normalize=True)
        
        return tom_params
    
    
    
    def hat(t: float) -> SequencerParams:
        hihat = SamplerParameters(
            url='https://one-laptop-per-child.s3.amazonaws.com/tamtamDrumKits16/drum4tr808closed.wav',
            reverb=ReverbParameters(
                url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
                mix=0.1,
            ),
            filter=FilterParameters(
                center_frequency=float(np.random.uniform(0.08, 0.12)),
                bandwidth=float(np.random.uniform(0.15, 0.25))
            ),
        )
        
        event = Event(gain=float(np.random.uniform(0.9, 1)), time=t + float(np.random.uniform(0, 0.01)), params=hihat, synth=sampler)
        
        hat_params = SequencerParams(
            events=[event],
            speed=speed,
            normalize=True)
        
        return hat_params
    
    def kick(t: float) -> SequencerParams:
        kick = SamplerParameters(
            url='https://one-laptop-per-child.s3.amazonaws.com/tamtam44old/drum1kick.wav',
            reverb=ReverbParameters(
                url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
                mix=0.5
            ),
            filter=FilterParameters(
                center_frequency=float(np.random.uniform(0.01, 0.03)),
                bandwidth=float(np.random.uniform(0.05, 0.2))
            ),
            
            
        )
        
        event = Event(gain=float(np.random.uniform(0.9, 1)), time=t, params=kick, synth=sampler)
        
        kick_params = SequencerParams(
            events=[event] if t % 1 == 0 else [],
            speed=speed,
            normalize=True)
        
        return kick_params
        
    
    def snare(t: float) -> SequencerParams:
        snare = SamplerParameters(
            url='https://one-laptop-per-child.s3.amazonaws.com/tamtam44old/drum1snare.wav',
            reverb=ReverbParameters(
                url='https://matching-pursuit-reverbs.s3.amazonaws.com/St+Nicolaes+Church.wav',
                mix=0.5
            ),
            filter=FilterParameters(
                center_frequency=float(np.random.uniform(0.02, 0.04)),
                bandwidth=float(np.random.uniform(0.05, 0.3))
            ),
        )
        
        event = Event(gain=float(np.random.uniform(0.9, 1)), time=t, params=snare, synth=sampler)
        
        snare_params = SequencerParams(
            events=[event] if t!= 0 and t % 2 == 0 else [],
            speed=speed,
            normalize=True)
        
        return snare_params
    
    
    times = np.arange(0, 16, step=0.25)
    
    # pythonic way to aggregate these
    k = [kick(t).events for t in times]
    kicks = SequencerParams(
        events=list(chain(*k)), 
        normalize=True, 
        speed=speed
    )
    
    h = [hat(t).events for t in times]
    hats = SequencerParams(
        events=list(chain(*h)),
        normalize=True,
        speed=speed
    )

    s = [snare(t).events for t in times]
    snares = SequencerParams(
        events=list(chain(*s)),
        normalize=True,
        speed=speed
    )     
    
    t = [tom(t).events for t in times]
    toms = SequencerParams(
        events=list(chain(*t)),
        normalize=True,
        speed=speed
    )     
    
    final = SequencerParams(
        speed=speed,
        normalize=True,
        events = (kicks + hats + snares + toms).events
    )
    
    import json
    print(json.dumps(final.to_dict(), indent=4))
    
    sequencer.play(final)
    
    

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
    # sequencer_example()
    mesh_example()