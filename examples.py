from wiggle import Sampler, SamplerParameters, FilterParameters, \
    GainParameters, GainKeyPoint, ReverbParameters, AudioFetcher
from io import BytesIO

if __name__ == '__main__':
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
    