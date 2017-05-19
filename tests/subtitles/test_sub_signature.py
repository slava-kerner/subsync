import unittest

from subsync.subtitles.sub_signature import SubSignature
from subsync.subtitles.subtitle import Subtitles


class TestSubSignature(unittest.TestCase):
    def test_init_from_intervals(self):
        intervals = [(1, 2), (3, 4)]
        sig = SubSignature(intervals=intervals)
        self.assertEqual(sig.intervals, intervals)

    def test_init_from_subtitle(self):
        subtitle = Subtitles.open('data/persona.srt')
        sig = SubSignature(subtitle=subtitle)
        self.assertEqual(len(sig.intervals), 11)
        self.assertEqual(sig.intervals[0][1] - sig.intervals[0][0], 3753)
