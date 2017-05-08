import unittest
import os
from glob import glob
import json
import warnings


from tests.test_utils import run_integration_tests

from subsync.subtitles.opensubtitles import OSCrawler, SubsOrganizer
from subsync.subtitles.subtitle import Subtitles
from subsync.utils.languages import detect_subtitle_language


imdb_id = '0060827'  # persona
os_id = '5577772'  # persona in french
all_encodings = ['utf_32_le', 'utf_32_be', 'utf_16_le', 'utf_16_be', 'utf_8', 'utf-8']

subs_folder = '/home/slava/data/subs'


@unittest.skipUnless(run_integration_tests(), '')
class TestOSCrawler(unittest.TestCase):
    @unittest.skip('')
    def test_imdb_to_os(self):
        crawler = OSCrawler()
        crawler.imdb_id_to_os_id(imdb_id)
        subs = crawler.imdb_id_to_subs(imdb_id)
        print(subs)

    def test_download(self):
        crawler = OSCrawler(download_folder=subs_folder)
        subs = crawler.imdb_id_to_subs(imdb_id)
        crawler.download(subs)


@unittest.skipUnless(run_integration_tests(), '')
class TestSubsOrganizer(unittest.TestCase):
    def test_organize(self):
        organizer = SubsOrganizer()
        organizer.process_folder('/home/slava/Downloads', subs_folder)


@unittest.skipUnless(run_integration_tests(), '')
class Sandbox(unittest.TestCase):
    def setUp(self):
        warnings.simplefilter("ignore")

    def test_check_languages(self):
        """ compares declared languages with detected ones. """
        with open(glob(os.path.join(subs_folder, 'subs.json'))[0]) as meta_f:
            subs_meta = json.load(meta_f)
        print(subs_meta)

        for sub_path in glob(os.path.join(subs_folder, '*.srt')):
            for encoding in all_encodings:
                try:
                    sub = Subtitles.open(sub_path, encoding=encoding)
                    lng = detect_subtitle_language(sub)
                    print('declared: %s, detected: %s' % (subs_meta[sub_path]['lang'], lng))
                    continue
                except:
                    pass
