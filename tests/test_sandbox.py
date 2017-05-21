import unittest
import os
import json
import warnings
from tqdm import tqdm
from tempfile import TemporaryDirectory

from pysrt import SubRipFile
from pydub import AudioSegment

from tests.test_utils import run_integration_tests
from subsync.subtitles.sub_signature import SubSignature
from subsync.subtitles.subtitle import Subtitles
from subsync.download.youtube_downloader import YoutubeDownloader
from subsync.vad.vad_marsbroshok import VADMarsbroshok


youtube_test_config = {'format': 'bestaudio/best', 'quiet': True}

base_folder = '/home/slava/data/subs'
persona_youtube_ids = ['rNj-giwqn8c', 'RuBbvBPYCDU', 'ySa4fK9SqII']

@unittest.skip('slow real test')
class Download(unittest.TestCase):
    def test_download_audio(self):
        out_folder = os.path.join(base_folder, 'persona', 'audio')
        downloader = YoutubeDownloader(youtube_test_config)
        for id in tqdm(persona_youtube_ids , desc='downloading all videos'):
            path = os.path.join(out_folder, '%s.wav' % id)
            downloader.download(id, path)


# @unittest.skip('slow real test')
class VAD(unittest.TestCase):
    def test_vad_marsbroshok(self):
        signature = dict()
        for id in persona_youtube_ids:
            # audio_path = os.path.join(base_folder, 'persona/audio/%s.mp3' % id)
            # audio = AudioSegment.from_file(audio_path)
            # audio[:10 * 60 * 1000].export(os.path.join(base_folder, 'persona/audio/crop_%s.wav' % id), format='wav')

            audio_path = os.path.join(base_folder, 'persona/audio/crop_RuBbvBPYCDU.wav')
            signature[id] = VADMarsbroshok(audio_path).signature()
            print(signature[id])
        # VADMarsbroshok(audio_path).plot_detected_speech_regions()


@unittest.skip('slow real test')
class Fit(unittest.TestCase):
    @unittest.skip('slow real test')
    def test_fit_persona(self):
        warnings.simplefilter("ignore")
        index_path = os.path.join(base_folder, 'subs.json')
        with open(index_path) as f:
            index = json.load(f)

        for sub1_path, sub1_props in index.items():
            # print(Subtitles.open(path=sub1_path, language=sub1_lng))
            try:
                sub1 = Subtitles.open(path=sub1_path, language=sub1_props['lang'])
            except:
                continue
            sig1 = SubSignature(subtitle=sub1)
            for sub2_path, sub2_props in index.items():
                if sub1_path == sub2_path:
                    continue
                try:
                    sub2 = Subtitles.open(path=sub2_path, language=sub2_props['lang'])
                except:
                    continue
                sig2 = SubSignature(subtitle=sub2)
                a, b, dist = sig1.fit(sig2, attempts=10)
                fps1 = float(sub1_props['fps'])
                fps2 = float(sub2_props['fps'])
                expected_fps_ratio = fps1 / fps2 if fps1 != 0 and fps2 != 0 else None
                print('fitting %s to %s (expected fps ratio =%s): \ndist=%f, a=%f, b=%f' %
                      (sub1_path, sub2_path, expected_fps_ratio, dist, a, b))
