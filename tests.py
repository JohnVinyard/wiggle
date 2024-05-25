from unittest import TestCase, skip
from wiggle import Sampler, Sequencer, SamplerParameters, SequencerParams, AudioFetcher, Event, encode_samples
import numpy as np
from wiggle.samplerparams import ReverbParameters
from wiggle.sourcematerial import SourceMaterial
from wiggle.synths import get_synth, get_synth_by_id, get_synth_by_name, list_synths, render, restore_params_from_dict
import json
from soundfile import SoundFile
from io import BytesIO

class FakeAudioFetcher(AudioFetcher):
    def __init__(self, get_duration_func = lambda url: 30):
        super().__init__(22050)
        self.get_duration_func = get_duration_func
    
    def __call__(self, url):
        duration = self.get_duration_func(url)
        return np.random.uniform(-1, 1, 22050 * duration)
    
    def fetch(self, url):
        return self.__call__(url)

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
    
    
    def test_sampler_audio_render_is_as_long_as_impulse_response(self):
        def get_duration(url: str) -> int:
            if 'ir' in url:
                return 10
            else:
                return 2
        
        fetcher = FakeAudioFetcher(get_duration)
        sampler = Sampler(fetcher)
            
        samples = sampler.render(SamplerParameters(
            url='https://example.com/sound', 
            start_seconds=0, 
            duration_seconds=2,
            reverb=ReverbParameters(
                url='https://example.com/ir',
                mix=0.5
            )))
        self.assertEqual(samples.shape, (fetcher.samplerate * 10,))
    
    
    def test_sampler_params_from_dict_infers_start_0(self):
        params = SamplerParameters.from_dict(
            dict(duration_seconds=10, url='https://example.com/sound'))
        self.assertEqual(0, params.start_seconds)
    
    def test_sampler_params_from_dict_infers_duration_0(self):
        params = SamplerParameters.from_dict(
            dict(start_seconds=1, url='https://example.com/sound'))
        self.assertEqual(0, params.duration_seconds)
    
    def test_sampler_produces_audio_with_inferred_duration(self):
        
        def get_duration(url: str) -> int:
            return 12
        
        fetcher = FakeAudioFetcher(get_duration)
        sampler = Sampler(fetcher)
        samples = sampler.render(SamplerParameters(
            url='https://example.com/sound', 
            start_seconds=0))
        
        self.assertEqual(samples.shape, (fetcher.samplerate * 12,))
    
    def test_sampler_produces_audio_from_dict_parameters_with_inferred_duration(self):
        
        def get_duration(url: str) -> int:
            return 12
        
        fetcher = FakeAudioFetcher(get_duration)
        sampler = Sampler(fetcher)
        params = SamplerParameters.from_dict(
            dict(url='https://example.com/sound', start_seconds=0))
        samples = sampler.render(params)
        
        self.assertEqual(samples.shape, (fetcher.samplerate * 12,))
    
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
    
    def test_source_material_from_sampler_includes_convolution_url(self):
        url = 'https//example.com/sound'
        ir = 'https//example.com/ir'
        
        sampler_params = SamplerParameters(
            url=url, 
            start_seconds=1, 
            duration_seconds=10,
            reverb=ReverbParameters(
                url=ir,
                mix=0.6
            ))
        
        sm = sampler_params.source_material
        
        self.assertEqual(2, len(sm))
        self.assertTrue(SourceMaterial(url) in sm)
        self.assertTrue(SourceMaterial(ir) in sm)
    
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
    
    def test_can_encode_mono_samples(self):
        samples = np.random.uniform(-1, 1, (2**15,))
        encoded_samples = encode_samples(samples, samplerate=22050)
        self.assertGreater(len(encoded_samples), 0)
    
    def test_can_encode_stereo_channels(self):
        samples = np.random.uniform(-1, 1, (2**15, 2))
        encoded_samples = encode_samples(samples, samplerate=22050)
        self.assertGreater(len(encoded_samples), 0)
    
    
    def test_can_encode_and_decode_samples(self):
        samples = np.random.uniform(-1, 1, (44100 * 10,))
        encoded_sample_bytes = encode_samples(
            samples, samplerate=44100, format='OGG', subtype='VORBIS')
        
        bio = BytesIO(encoded_sample_bytes)
        bio.seek(0)
        
        with SoundFile(bio, mode='r') as sf:
            retrieved = sf.read()
        
        self.assertEqual(len(samples), len(retrieved))
        
        
        
        