import logging
import copy

from pysrt import SubRipFile


logger = logging.getLogger(__name__)


class Subtitles(SubRipFile):
    """
    represents subtitles, as 1 file, for 1 movie.
    """
    def __init__(self, items=None, eol=None, path=None, encoding='utf-8', language=None, fps=None):
        super(Subtitles, self).__init__(items=items, eol=eol, path=path, encoding=encoding)
        self.lang = language
        self.fps = fps

    @classmethod
    def open(cls, path='', encoding=None, error_handling=SubRipFile.ERROR_RAISE, language=None, fps=None):
        srt = super(Subtitles, cls).open(path=path, encoding=encoding, error_handling=error_handling)
        sub = Subtitles(srt)
        sub.lang = language
        sub.fps = fps
        return sub

    def __add__(self, shift_ms):
        """ applies shift on signature. """
        clone = copy.deepcopy(self)
        clone.shift(milliseconds=shift_ms)
        return clone

    def __radd__(self, shift_ms):
        return self.__add__(shift_ms)

    def __mul__(self, ratio):
        """ applies gain on signature. """
        clone = copy.deepcopy(self)
        clone.shift(ratio=ratio)
        return clone

    def __rmul__(self, ratio):
        return self.__mul__(ratio)
