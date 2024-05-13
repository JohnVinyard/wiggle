from unittest import TestCase
from wiggle import Sampler, Sequencer, SamplerParameters, SequencerParams, AudioFetcher
import numpy as np

class FakeAudioFetcher(AudioFetcher):
    def __init__(self):
        super().__init__(22050)
    
    def __call__(self, url):
        return np.random.uniform(-1, 1, (2**15))
    
    def fetch(self, url):
        return np.random.uniform(-1, 1, (2**15))

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
    
    def test_sampler_produces_audio(self):
        self.fail()
    
    def test_returns_validation_error_for_sequencer(self):
        self.fail()
        
    def test_sequencer_returns_audio(self):
        self.fail()