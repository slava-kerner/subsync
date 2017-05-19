import unittest

from subsync.subtitles.sub_signature import SubSignature
from subsync.subtitles.subtitle import Subtitles


class TestSubSignature(unittest.TestCase):
    def setUp(self):
        self.subtitle = Subtitles.open('data/persona.srt')
        self.sig = SubSignature(subtitle=self.subtitle)

    def test_init_from_intervals(self):
        intervals = [(1, 2), (3, 4)]
        self.assertEqual(SubSignature(intervals=intervals).intervals, intervals)

    def test_init_from_subtitle(self):
        self.assertEqual(len(self.sig.intervals), 11)
        self.assertEqual(self.sig.intervals[0][1] - self.sig.intervals[0][0], 3753)

    def test_len(self):
        self.assertEqual(len(self.sig), len(self.sig.intervals))

    def test_iter(self):
        self.assertEqual(len(list(self.sig)), len(self.sig))
