import unittest
import os
from tempfile import TemporaryDirectory

from tests.test_utils import run_integration_tests
from subsync.download.youtube_downloader import YoutubeDownloader


youtube_test_video_id = 'BaW_jenozKc'

youtube_test_config = {'format': 'bestaudio/best', 'quiet': True}


@unittest.skipUnless(run_integration_tests(), '')
class TestYoutubeDownloader(unittest.TestCase):
    def test_download(self):
        with TemporaryDirectory() as folder:
            path = os.path.join(folder, 'temp.mp3')

            downloader = YoutubeDownloader(youtube_test_config)
            downloader.download(youtube_test_video_id, path)

            self.assertTrue(os.path.exists(path))

            size_kb = int(os.stat(path).st_size / 1024)
            self.assertTrue(100 < size_kb < 200)
