from unittest import TestCase
from wiggle import Sampler, Sequencer, SamplerParameters, SequencerParams, AudioFetcher, Event
import numpy as np
from wiggle.synths import get_synth_by_id, get_synth_by_name, list_synths, render

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
        
        # sampler produces 10 seconds of audio, which begins at second 1
        self.assertEqual(samples.shape, (fetcher.samplerate * 11,))
    
    def test_can_render_sampler_using_synth_name(self):
        fetcher = FakeAudioFetcher()
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        
        samples = render('sampler', sampler_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 10,))
    
    def test_can_render_sampler_using_synth_id(self):
        fetcher = FakeAudioFetcher()
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        
        samples = render(1, sampler_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 10,))
    
    def test_can_render_sampler_using_synth_instance(self):
        fetcher = FakeAudioFetcher()
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        
        synth = Sampler(fetcher)
        samples = render(synth, sampler_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 10,))
    
    def test_can_render_sequencer_using_synth_name(self):
        fetcher = FakeAudioFetcher()
        sampler = Sampler(FakeAudioFetcher())
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        event = Event(gain=1, time=1, synth=sampler, params=sampler_params)
        sequencer_params = SequencerParams(events=[event], speed=1, normalize=True)
        samples = render('sequencer', sequencer_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 11,))
    
    def test_can_render_sequencer_using_synth_id(self):
        fetcher = FakeAudioFetcher()
        sampler = Sampler(FakeAudioFetcher())
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        event = Event(gain=1, time=1, synth=sampler, params=sampler_params)
        sequencer_params = SequencerParams(events=[event], speed=1, normalize=True)
        samples = render(2, sequencer_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 11,))
    
    def test_can_render_sequencer_using_synth_instance(self):
        fetcher = FakeAudioFetcher()
        sampler = Sampler(FakeAudioFetcher())
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        event = Event(gain=1, time=1, synth=sampler, params=sampler_params)
        sequencer_params = SequencerParams(events=[event], speed=1, normalize=True)
        synth = Sequencer(fetcher.samplerate)
        samples = render(synth, sequencer_params, fetcher)
        self.assertEqual(samples.shape, (fetcher.samplerate * 11,))
    
    
    def test_list_synths_returns_two_items(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertEqual(2, len(synths))
    
    def test_list_synths_returns_items_with_correct_samplerate(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertTrue(all([s.samplerate == 22050 for s in synths]))
    
    def test_can_get_synth_by_id(self):
        synth = get_synth_by_id(FakeAudioFetcher(), 1)
        self.assertEqual(synth.name, 'sampler')
    
    def test_can_get_synth_by_name(self):
        synth = get_synth_by_name(FakeAudioFetcher(), 'sampler')
        self.assertEqual(synth.id, 1)
    
    def test_errant_id_returns_key_error(self):
        self.assertRaises(KeyError, lambda: get_synth_by_id(FakeAudioFetcher(), 9999))
    
    def test_errant_nane_returns_key_error(self):
        self.assertRaises(KeyError, lambda: get_synth_by_name(FakeAudioFetcher(), 'blah'))