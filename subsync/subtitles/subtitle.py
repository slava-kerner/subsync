import logging

from pysrt import SubRipFile


logger = logging.getLogger(__name__)


class Subtitles(SubRipFile):
    """
    represents subtitles, as 1 file, for 1 movie.
    """
    def __init__(self, items=None, eol=None, path=None, encoding='utf-8', language=None):
        super(Subtitles, self).__init__(items=items, eol=eol, path=path, encoding=encoding)
        self.lang = language

    @classmethod
    def open(cls, path='', encoding=None, error_handling=SubRipFile.ERROR_RAISE, language=None):
        srt = super(Subtitles, cls).open(path=path, encoding=encoding, error_handling=error_handling)
        sub = Subtitles(srt)
        sub.lang = language
        return sub
