import random
import os
import logging
from tqdm import tqdm


logger = logging.getLogger(__name__)


class SubSignature:
    """
    describes signature of a subtitle (later, maybe, will describe also signature of a movie).
    signature is active intervals, in milliseconds.
    TODO implement efficient state
    """
    def __init__(self, intervals=None, subtitle=None):
        """
        :param intervals: list of (start_ms, end_ms). assumes ordered, not intersecting 
        :param subtitle: SubRipFile (or Subtitle) . deduces intervals from it 
        """
        if intervals:
            self.intervals = intervals
        elif subtitle:
            self.intervals = self._from_subtitle(subtitle).intervals
        else:
            self.intervals = []

    @classmethod
    def _from_subtitle(cls, subtitle):
        """
        :param subtitle: SubRipFile (or Subtitle) 
        :return: SubSignature 
        """
        intervals = [(item.start.ordinal, item.end.ordinal) for item in subtitle]
        return SubSignature(intervals=intervals)

    def __getitem__(self, item):
        return self.intervals[item]

    def __setitem__(self, key, value):
        self.intervals[key] = value

    def __len__(self):
        return len(self.intervals)

    def __iter__(self):
        for interval in self.intervals:
            yield interval

    def __eq__(self, other):
        """ equals if intervals are exactly the same"""
        return self.intervals == other.intervals

    def __add__(self, shift_ms):
        """ shifts signature forward by that many milliseconds. """
        intervals = [(interval[0] + shift_ms, interval[1] + shift_ms) for interval in self]
        return SubSignature(intervals=intervals)

    def __radd__(self, shift_ms):
        return self.__add__(shift_ms)

    def __mul__(self, factor):
        """ applies gains on signature. """
        intervals = [(interval[0] * factor, interval[1] * factor) for interval in self]
        return SubSignature(intervals=intervals)

    def __rmul__(self, factor):
        return self.__mul__(factor)

    def __str__(self):
        return '\n'.join(['%2.2f,%2.2f' % (interval[0] / 1000, interval[1] / 1000) for interval in self.intervals])

    def _sort(self):
        """ sorts by start times, increasing. """
        intervals_sorted = self.intervals.copy()
        intervals_sorted.sort(key=lambda interval: interval[0])
        return SubSignature(intervals=intervals_sorted)

    def _simplify(self):
        """ merges overlapping intervals. assumes sorted. updates self. """
        simple = []
        for interval in self:
            if len(simple) == 0:
                simple += [interval]
            else:
                if interval[0] < simple[-1][1]:  # intersect last interval => merging
                    simple[-1] = (simple[-1][0], interval[1])
                else:
                    simple += [interval]
        return SubSignature(intervals=simple)

    def total_time(self):
        return sum([interval[1] - interval[0] for interval in self])

    def merge(self, other):
        if not self.intervals:
            return other
        if not other.intervals:
            return self

        it_self = iter(self.intervals)
        it_other = iter(other.intervals)
        current_self = next(it_self)
        current_other = next(it_other)
        merged = []
        while current_self is not None and current_other is not None:
            if current_self[1] < current_other[0]:  # self ends before other starts
                merged += [current_self]
                current_self = next(it_self, None)
            elif current_other[1] < current_self[0]:  # other ends before self starts
                merged += [current_other]
                current_other = next(it_other, None)
            elif current_self[0] < current_other[0]:
                if current_self[1] < current_other[1]:  # overlap: self starts, ends before other start, ends resp.
                    current_other = (current_self[0], current_other[1])
                    current_self = next(it_self, None)
                else:  # self contains other
                    current_other = next(it_other, None)
            else:
                if current_other[1] < current_self[1]:  # overlap: self starts, ends after other start, ends resp.
                    current_self = (current_other[0], current_self[1])
                    current_other = next(it_other, None)
                else:  # other contains self 
                    current_self = next(it_self, None)

        while current_self is not None:
            merged += [current_self]
            current_self = next(it_self, None)
        while current_other is not None:
            merged += [current_other]
            current_other = next(it_other, None)

        return SubSignature(intervals=merged)

    def intersect(self, other):
        if not self.intervals or not other.intervals:
            return SubSignature()

        it_self = iter(self.intervals)
        it_other = iter(other.intervals)
        current_self = next(it_self)
        current_other = next(it_other)
        intersected = []
        while current_self is not None and current_other is not None:
            if current_self[1] < current_other[0]:  # self ends before other starts
                current_self = next(it_self, None)
            elif current_other[1] < current_self[0]:  # other ends before self starts
                current_other = next(it_other, None)
            elif current_self[0] < current_other[0]:
                if current_self[1] < current_other[1]:  # overlap: self starts, ends before other start, ends resp.
                    intersected += [(current_other[0], current_self[1])]
                    current_other = (current_self[1], current_other[1])
                    current_self = next(it_self, None)
                else:  # self contains other
                    intersected += [current_other]
                    current_self = (current_other[1], current_self[1])
                    current_other = next(it_other, None)
            else:
                if current_other[1] < current_self[1]:  # overlap: self starts, ends after other start, ends resp.
                    intersected += [(current_self[0], current_other[1])]
                    current_self = (current_other[1], current_self[1])
                    current_other = next(it_other, None)
                else:  # other contains self
                    intersected += [current_self]
                    current_other = (current_self[1], current_other[1])
                    current_self = next(it_self, None)

        return SubSignature(intervals=intersected)

    def dist(self, other):
        """
        metric between signatures - intersection over union, Jaccard index
        :param other: SubSignature
        :return: [0..1], or None if any of signatures is empty
        """
        if not self.intervals or not other.intervals:
            return None

        intersection_time = self.intersect(other).total_time()
        union_time = self.merge(other).total_time()
        if union_time < 1e-10:
            return None

        return (union_time - intersection_time) / union_time

    def densify(self, threshold_ms):
        if len(self) == 0:
            return SubSignature()

        densified = [self[0]]
        for item in self[1:]:
            if item[0] < densified[-1][1] + threshold_ms:  # close => densify
                densified[-1] = (densified[-1][0], item[1])
            else:
                densified += [item]

        return SubSignature(intervals=densified)

    def write(self, filename):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'w') as f:
            text = '\n'.join(['%2.2f,%2.2f' % (interval[0], interval[1]) for interval in self.intervals])
            f.write(text)

    @classmethod
    def read(self, filename):
        with open(filename) as f:
            intervals = [(float(line.split(',')[0]), float(line.split(',')[1].strip())) for line in f.readlines()]
        return SubSignature(intervals=intervals)

    def fit(self, other, attempts=100, search_radius=10):
        """
        :return: (a, b, dist) such that a * self + b = other  
        """
        best = (1, 0, 1)  # a=1, b=0, dist=1
        for attempt in tqdm(range(attempts), desc='fitting'):
            random_window = int(.25 * len(self))
            idx1_self = random.randrange(0, random_window)
            idx1_other_expected = int(idx1_self * len(other) / len(self))

            idx2_self = random.randrange(len(self) - random_window, len(self))
            idx2_other_expected = int(idx2_self * len(other) / len(self))

            for idx1_other in range(max(0, idx1_other_expected - search_radius),
                                    min(idx1_other_expected + search_radius, len(other))):
                for idx2_other in range(max(0, idx2_other_expected - search_radius),
                                        min(idx2_other_expected + search_radius, len(other))):
                    # print('TYPE', type(self[idx1_self]), type(self[idx2_self]))
                    a, b = fit_linear(self[idx1_self][0], other[idx1_other][0],
                                      self[idx2_self][0], other[idx2_other][0])
                    dist = (a * self + b).dist(other)
                    if dist is not None and dist < best[2]:  # found better candidate
                        logger.debug('improved to dist=%f: a=%f, b=%f, ', dist, a, b)
                        # print('improved to dist=%f: a=%f, b=%f, ', dist, a, b)
                        best = (a, b, dist)
        return best


def fit_linear(x1, y1, x2, y2):
    """ fits a, b s.t.: y1 = a*x1+b, y2 = a*x2+b. """
    a = (y2 - y1) / (x2 - x1)
    b = (x2 * y1 - x1 * y2) / (x2 - x1)
    return a, b
