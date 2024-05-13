from unittest import TestCase
from wiggle import Sampler, Sequencer, SamplerParameters, SequencerParams, AudioFetcher, Event
import numpy as np

from wiggle.synths import list_synths

class FakeAudioFetcher(AudioFetcher):
    def __init__(self):
        super().__init__(22050)
    
    def __call__(self, url):
        return np.random.uniform(-1, 1, 22050 * 30)
    
    def fetch(self, url):
        return np.random.uniform(-1, 1, 22050 * 30)

class Tests(TestCase):
    
    def test_can_get_schema_for_sampler(self):
        sampler = Sampler(FakeAudioFetcher())
        schema = sampler.schema
        self.assertEqual(schema['title'], 'Sampler input model')
        self.assertEqual(schema['type'], 'object')
    
    def test_can_get_schema_for_sequencer(self):
        sequencer = Sequencer(22050)
        schema = sequencer.schema
        self.assertEqual(schema['title'], 'Sequencer input model')
        self.assertEqual(schema['type'], 'object')
    
    def test_returns_validation_error_for_sampler(self):
        sampler = Sampler(FakeAudioFetcher())
        self.assertRaises(
            ValueError, 
            lambda: sampler.render(SamplerParameters(url='https://example.com/sound', start_seconds=-1)))
    
    def test_returns_validation_error_for_sequencer(self):
        sequencer = Sequencer(22050)
        self.assertRaises(
            ValueError,
            lambda: sequencer.render(SequencerParams(speed=-1, normalize=False, events=[]))
        )
    
    def test_sampler_produces_audio(self):
        fetcher = FakeAudioFetcher()
        sampler = Sampler(fetcher)
        samples = sampler.render(SamplerParameters(
            url='https://example.com/sound', 
            start_seconds=1, 
            duration_seconds=10))
        self.assertEqual(samples.shape, (fetcher.samplerate * 10,))
    
        
    def test_sequencer_returns_audio(self):
        fetcher = FakeAudioFetcher()
        sampler = Sampler(FakeAudioFetcher())
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        event = Event(gain=1, time=1, synth=sampler, params=sampler_params)
        sequencer = Sequencer(22050)
        sequencer_params = SequencerParams(events=[event], speed=1, normalize=True)
        samples = sequencer.render(sequencer_params)
        
        # sampler produces 9 seconds of audio, which begins at second 1
        self.assertEqual(samples.shape, (fetcher.samplerate * 11,))
    
    def test_list_synths_returns_two_items(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertEqual(2, len(synths))
    
    def test_list_synths_returns_items_with_correct_samplerate(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertTrue(all([s.samplerate == 22050 for s in synths]))