import unittest

from subsync.subtitles.subtitle import Subtitles


class TestSubtitles(unittest.TestCase):
    def test_open(self):
        sub = Subtitles.open('data/persona.srt', language='swedish')

        self.assertEqual(len(sub), 11)
        self.assertEqual(sub.lang, 'swedish')

    def test_shift_gain(self):
        sub = Subtitles.open('data/persona.srt', language='swedish')
        transformed = 2 * sub + 3000

        self.assertEqual(len(sub), len(transformed))
        self.assertEqual(2 * sub[3].start.ordinal + 3000, transformed[3].start.ordinal)
        self.assertEqual(2 * sub[3].end.ordinal + 3000, transformed[3].end.ordinal)
