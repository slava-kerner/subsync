from bs4 import BeautifulSoup
import logging
import os
from selenium import webdriver
import requests
from tqdm import tqdm


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

    def imdb_id_to_subs(self, imdb_id):
        driver = self._driver(output_folder=self.download_folder)
        sub_ids = []
        offset = 0
        done = False
        while not done:
            url = 'https://www.opensubtitles.org/en/search/sublanguageid-all/imdbid-%s/offset-%s' % (imdb_id, offset)
            try:
                driver.get(url)
                form = driver.find_element_by_css_selector('#submultiedit')
                body = form.find_elements_by_xpath('.//*[@id="search_results"]/tbody')[0]
                records = body.find_elements_by_xpath('//*[contains(@id, "name")]')
                for control in records:
                    try:
                        sub_id = control.get_property('id')[4:]
                        logger.debug('adding sub_id %s', sub_id)
                        sub_ids += [sub_id]
                    except:
                        pass
            except Exception as e:
                logger.error('failed getting subs for imdb_id=%s: %s', imdb_id, e)
                done = True
            offset += 40
        return sub_ids

    def download(self, sub_ids):
        driver = self._driver(output_folder=self.download_folder)
        selector = 'body > div.content > div:nth-child(14) > div > div:nth-child(1) > h1 > a'
        for sub_id in tqdm(sub_ids, desc='downloading subs'):
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
        if output_folder:  # not sure this works
            chrome_options.add_experimental_option('prefs', {'download.default_directory': output_folder})
        chrome_options.add_experimental_option("prefs", {"profile.managed_default_content_settings.images": 2})
        chrome_options.add_argument("-disable-popup-blocking")
        chrome_options.add_argument("-incognito")
        chrome_driver_path = os.path.join(os.getcwd(), 'chromedriver_2_27')
        driver = webdriver.Chrome(chrome_options=chrome_options, executable_path=chrome_driver_path)
        return driver
