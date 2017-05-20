import unittest
import os
import json
import warnings

from pysrt import SubRipFile
from tempfile import TemporaryDirectory
from tqdm import tqdm

from tests.test_utils import run_integration_tests
from subsync.subtitles.sub_signature import SubSignature
from subsync.subtitles.subtitle import Subtitles
from subsync.download.youtube_downloader import YoutubeDownloader


youtube_test_video_id = 'BaW_jenozKc'

youtube_test_config = {'format': 'bestaudio/best', 'quiet': True}


# @unittest.skip('slow real test')
class Download(unittest.TestCase):
    def test_download_audio(self):
        ids = ['rNj-giwqn8c', 'RuBbvBPYCDU', 'ySa4fK9SqII']
        out_folder = '/home/slava/data/subs/persona/audio'
        downloader = YoutubeDownloader(youtube_test_config)
        for id in tqdm(ids, desc='downloading all videos'):
            path = os.path.join(out_folder, '%s.mp3' % id)
            downloader.download(id, path)


@unittest.skip('slow real test')
class Fit(unittest.TestCase):
    @unittest.skip('slow real test')
    def test_fit_persona(self):
        warnings.simplefilter("ignore")
        index_path = '/home/slava/data/subs/subs.json'
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
