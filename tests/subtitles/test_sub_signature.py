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

    def test_total_time(self):
        self.assertEqual(self.sig.total_time(), 48165)

    def test_eq(self):
        self.assertEqual(self.sig, self.sig)

        self.assertNotEqual(self.sig, self.sig + 0.1)

    def test_add(self):
        shifted = 22 + self.sig + 20
        self.assertAlmostEqual(shifted.intervals[0][0], self.sig.intervals[0][0] + 42)
        self.assertAlmostEqual(shifted.total_time(), self.sig.total_time())

    def test_mul(self):
        shifted = 2 * self.sig * 3
        self.assertAlmostEqual(shifted.intervals[0][0], self.sig.intervals[0][0] * 6)
        self.assertAlmostEqual(shifted.total_time(), self.sig.total_time() * 6)

    def test_simplify(self):
        sig = SubSignature(intervals=[(1, 2), (1.5, 3), (4, 5), (5, 6), (5.5, 6)])
        expected_simplified = SubSignature(intervals=[(1, 3), (4, 5), (5, 6)])
        self.assertEqual(sig._simplify(), expected_simplified)

    def test_sort(self):
        sig = SubSignature(intervals=[(1, 2), (1.5, 3), (0, 0.5), (-2, -1), (0.5, 16)])
        expected_sorted = SubSignature(intervals=[(-2, -1), (0, 0.5), (0.5, 16), (1, 2), (1.5, 3)])
        self.assertEqual(sig._sort(), expected_sorted)

    def test_dist_empty(self):
        empty = SubSignature()
        self.assertIsNone(self.sig.dist(empty))

    # def test_dist_same(self):
    #     self.assertEqual(1, self.sig.dist(self.sig))