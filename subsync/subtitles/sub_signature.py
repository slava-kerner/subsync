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
