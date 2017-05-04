import youtube_dl
import logging
import copy
import os


logger = logging.getLogger(__name__)


class Downloader:
    """ abstract class for downloading video/audio. """
    def __init__(self, settings):
        self.settings = settings

    def download(self, id, path):
        logger.info('%s starts downloading %s to %s', self.__class__.__name__, id, path)
        self._download(id, path)

    def _download(self, id, path):
        raise NotImplementedError


class YoutubeDownloader(Downloader):
    def _download(self, id, path):
        settings = copy.deepcopy(self.settings)
        # path = '/tmp/foo_%(title)s-%(id)s.%(ext)s'  #os.path.join()
        settings.update({'outtmpl': path})
        with youtube_dl.YoutubeDL(settings) as ydl:
            ydl.download([self._video_path(id)])

    def _video_path(self, id):
        return 'http://www.youtube.com/watch?v=%s' % id
