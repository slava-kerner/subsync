import unittest
import os
from tempfile import TemporaryDirectory

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

    def test_intersect(self):
        sub1 = SubSignature(intervals=[(-2, -1), (0, 0.5), (1.5, 3)])
        sub2 = SubSignature(intervals=[(-1.6, -1.4), (0.6, 1.4), (2, 4)])
        expected_intersection = SubSignature(intervals=[(-1.6, -1.4), (2, 3)])
        self.assertEqual(sub1.intersect(sub2), expected_intersection)

        self.assertEqual(sub1.intersect(SubSignature()), SubSignature())  # intersecting empty results empty

    def test_merge(self):
        sub1 = SubSignature(intervals=[(-2, -1), (0, 0.5), (1.5, 3)])
        sub2 = SubSignature(intervals=[(-1.6, -1.4), (0.6, 1.4), (2, 4)])
        expected_merge = SubSignature(intervals=[(-2, -1), (0, 0.5), (0.6, 1.4), (1.5, 4)])
        self.assertEqual(sub1.merge(sub2), expected_merge)

        self.assertEqual(sub1.merge(SubSignature()), sub1)
        self.assertEqual(SubSignature().merge(sub1), sub1)

    def test_dist_empty(self):
        empty = SubSignature()
        self.assertIsNone(self.sig.dist(empty))

    def test_dist_same(self):
        self.assertEqual(0, self.sig.dist(self.sig))

    def test_dist_shifted(self):
        dist_shifted_by_1_sec = self.sig.dist(self.sig + 1000)
        self.assertTrue(.1 < dist_shifted_by_1_sec < .9)

    def test_densify(self):
        sub1 = SubSignature(intervals=[(0, 1), (2, 3)])
        self.assertEqual(sub1.densify(.9), sub1)
        self.assertEqual(sub1.densify(1.1), SubSignature(intervals=[(0, 3)]))

    def test_read_write(self):
        with TemporaryDirectory() as folder:
            path = os.path.join(folder, 'sig.txt')
            self.sig.write(path)
            read = self.sig.read(path)
            self.assertEqual(self.sig, read)

    def test_fit(self):
        a, b, dist = self.sig.fit(1.1 * self.sig + 1000)
        self.assertAlmostEqual(a, 1.1)
        self.assertAlmostEqual(b, 1000)
        self.assertAlmostEqual(dist, 0)
