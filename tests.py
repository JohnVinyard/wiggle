from unittest import TestCase
from wiggle import Sampler, Sequencer, SamplerParameters, SequencerParams, AudioFetcher, Event
import numpy as np
from wiggle.sourcematerial import SourceMaterial
from wiggle.synths import get_synth, get_synth_by_id, get_synth_by_name, list_synths, render, restore_params_from_dict
import json

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
    
    def test_can_roundtrip_serialize_sampler_params(self):
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        d = sampler_params.to_dict()
        j = json.dumps(d)
        d = json.loads(j)
        
        restored = SamplerParameters.from_dict(d)
        
        self.assertEqual(sampler_params, restored)
    
    def test_can_roundtrip_serialize_sequencer_params(self):
        sampler = Sampler(FakeAudioFetcher())
        sampler_params = SamplerParameters(
            url='https//example.com/sound', 
            start_seconds=1, 
            duration_seconds=10)
        event = Event(gain=1, time=1, synth=sampler, params=sampler_params)
        event2 = Event(gain=1, time=2, synth=sampler, params=sampler_params)
        sequencer_params = SequencerParams(events=[event, event2], speed=1, normalize=True)
        
        d = sequencer_params.to_dict()
        j = json.dumps(d)
        d = json.loads(j)
        
        fetcher = AudioFetcher(22050)
        restored = SequencerParams.from_dict(
            d, 
            restore_params_from_dict, 
            lambda id: get_synth(fetcher, id))
        
        self.assertEqual(sequencer_params, restored)
    
    def test_can_get_source_material_from_sampler(self):
        url = 'https//example.com/sound'
        sampler_params = SamplerParameters(
            url=url, 
            start_seconds=1, 
            duration_seconds=10)
        
        sm = sampler_params.source_material
        
        self.assertEqual(1, len(sm))
        self.assertTrue(SourceMaterial(url) in sm)
    
    def test_can_get_source_material_from_sequencer(self):
        
        url1 = 'https//example.com/sound'
        url2 = 'https//example.com/sound2'
        url3 = 'https//example.com/sound3'
        
        sampler_params = SamplerParameters(
            url=url1, 
            start_seconds=1, 
            duration_seconds=10)
        
        sampler_params2 = SamplerParameters(
            url=url2, 
            start_seconds=1, 
            duration_seconds=10)
        
        sampler_params3 = SamplerParameters(
            url=url3, 
            start_seconds=1, 
            duration_seconds=10)
        
        event = Event(gain=1, time=1, synth=1, params=sampler_params)
        event2 = Event(gain=1, time=2, synth=1, params=sampler_params2)
        sequencer_params = SequencerParams(events=[event, event2], speed=1, normalize=True)
        
        event2a = Event(gain=1, time=0, synth=2, params=sequencer_params)
        
        event3 = Event(gain=1, time=3, synth=1, params=sampler_params3)
        
        seq_params_top = SequencerParams(events=[event2a, event3], speed=1, normalize=True)
        
        display = json.dumps(seq_params_top.to_dict(), indent=4)
        
        sm = seq_params_top.source_material
        
        self.assertEqual(3, len(sm))
        self.assertTrue(SourceMaterial(url1) in sm)
        self.assertTrue(SourceMaterial(url2) in sm)
        self.assertTrue(SourceMaterial(url3) in sm)
    
    def test_list_synths_returns_two_items(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertEqual(2, len(synths))
    
    def test_list_synths_returns_items_with_correct_samplerate(self):
        synths = list_synths(FakeAudioFetcher())
        self.assertTrue(all([s.samplerate == 22050 for s in synths]))
    
    def test_can_get_synth_by_id(self):
        synth = get_synth_by_id(FakeAudioFetcher(), 1)
        self.assertEqual(synth.name, 'sampler')
        
    def test_can_get_synth_by_inferred_id(self):
        synth = get_synth(FakeAudioFetcher(), 1)
        self.assertEqual(synth.id, 1)
    
    def test_can_get_synth_by_inferred_name(self):
        synth = get_synth(FakeAudioFetcher(), 'sequencer')
        self.assertEqual(synth.id, 2)
    
    def test_can_get_synth_by_str_id(self):
        synth = get_synth(FakeAudioFetcher(), '1')
        self.assertEqual(synth.id, 1)
    
    def test_can_get_synth_by_name(self):
        synth = get_synth_by_name(FakeAudioFetcher(), 'sampler')
        self.assertEqual(synth.id, 1)
    
    def test_errant_id_returns_key_error(self):
        self.assertRaises(KeyError, lambda: get_synth_by_id(FakeAudioFetcher(), 9999))
    
    def test_errant_nane_returns_key_error(self):
        self.assertRaises(KeyError, lambda: get_synth_by_name(FakeAudioFetcher(), 'blah'))