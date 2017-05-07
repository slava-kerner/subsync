from bs4 import BeautifulSoup
import logging
import os
from selenium import webdriver
import requests


logger = logging.getLogger(__name__)


class OSCrawler:
    """ interacts with OpenSubtitles. """
    def __init__(self, download_folder=None, temp_folder=None):
        self.download_folder = download_folder or '~/Downloads'
        os.makedirs(self.download_folder, exist_ok=True)
        self.temp_folder = temp_folder or '~/tmp'
        os.makedirs(self.temp_folder, exist_ok=True)

    @classmethod
    def imdb_id_to_os_id(cls, imdb_id):
        url = 'https://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-%s' % imdb_id
        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html.parser")
        # TODO parse soup?

    def download(self, sub_ids):
        driver = self._driver(output_folder=self.download_folder)
        selector = 'body > div.content > div:nth-child(14) > div > div:nth-child(1) > h1 > a'
        for sub_id in sub_ids:
            url = 'https://www.opensubtitles.org/en/subtitles/%s' % sub_id
            try:
                driver.get(url)
                driver.find_element_by_css_selector(selector).click()
                logger.info('sucessfully downloading id=%s', sub_id)
            except:
                logger.info('failed downloading id=%s', sub_id)
        driver.quit()

    @classmethod
    def _driver(cls, output_folder=None):
        chrome_options = webdriver.ChromeOptions()
        if output_folder:
            chrome_options.add_experimental_option('prefs', {'download.default_directory': output_folder})
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        # chrome_options.add_argument("-disable-popup-blocking")
        # chrome_options.add_argument("-incognito")
        chrome_driver_path = os.path.join(os.getcwd(), 'chromedriver_2_27')
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
        return driver
