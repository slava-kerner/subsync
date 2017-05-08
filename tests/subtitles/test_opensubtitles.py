import unittest
from tests.test_utils import run_integration_tests

from subsync.subtitles.opensubtitles import OSCrawler, SubsOrganizer


imdb_id = '0060827'  # persona
os_id = '5577772'  # persona in french


@unittest.skipUnless(run_integration_tests(), '')
class TestOSCrawler(unittest.TestCase):
    @unittest.skip('')
    def test_imdb_to_os(self):
        crawler = OSCrawler()
        crawler.imdb_id_to_os_id(imdb_id)
        subs = crawler.imdb_id_to_subs(imdb_id)
        print(subs)

    def test_download(self):
        crawler = OSCrawler(download_folder='/home/slava/data/subs')
        subs = crawler.imdb_id_to_subs(imdb_id)
        crawler.download(subs)


@unittest.skipUnless(run_integration_tests(), '')
class TestSubsOrganizer(unittest.TestCase):
    def test_organize(self):
        organizer = SubsOrganizer()
        organizer.process_folder('/home/slava/Downloads', '/home/slava/data/subs')
