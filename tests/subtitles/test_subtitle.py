import unittest
from pysrt import SubRipFile

from subsync.subtitles.subtitle import Subtitles


class TestSubtitles(unittest.TestCase):
    def test_open(self):
        sub = Subtitles.open('data/persona.srt', language='swedish')

        self.assertEqual(len(sub), 11)
        self.assertEqual(sub.lang, 'swedish')
