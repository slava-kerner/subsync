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
        sorted = self.intervals.copy()
        sorted.sort(key=lambda interval: interval[0])
        return SubSignature(intervals=sorted)

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
        raise NotImplementedError  # TODO

    def intersect(self, other):
        raise NotImplementedError  # TODO

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
