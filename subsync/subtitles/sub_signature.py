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
        return '\n'.join(['%s -> %s' % (interval[0], interval[1]) for interval in self.intervals])

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

        return intersection_time / union_time
