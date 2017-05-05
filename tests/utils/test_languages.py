import unittest

from subsync.subtitles.subtitle import Subtitles
from subsync.utils.languages import detect_subtitle_language


class TestLanguages(unittest.TestCase):
    def test_detect_subtitle_language(self):
        subtitle = Subtitles.open('data/persona.srt')
        self.assertEqual(detect_subtitle_language(subtitle), 'sv')
