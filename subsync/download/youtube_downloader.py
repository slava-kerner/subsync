import youtube_dl
import logging
import copy


logger = logging.getLogger(__name__)


class Downloader:
    """ abstract class for downloading video/audio. """
    def __init__(self, settings):
        self.settings = settings

    def download(self, video_id, path):
        logger.info('%s starts downloading %s to %s', self.__class__.__name__, video_id, path)
        self._download(video_id, path)

    def _download(self, video_id, path):
        raise NotImplementedError


class YoutubeDownloader(Downloader):
    def _download(self, video_id, path):
        settings = copy.deepcopy(self.settings)
        settings.update({'outtmpl': path})
        with youtube_dl.YoutubeDL(settings) as ydl:
            ydl.download([self._video_path(video_id)])

    @classmethod
    def _video_path(cls, video_id):
        return 'http://www.youtube.com/watch?v=%s' % video_id
