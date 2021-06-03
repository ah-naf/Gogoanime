import time
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import urllib.request
from tqdm import tqdm

class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)

class Gogoanime:

    def __init__(self, driver, name):
        self.driver = driver
        self.driver.get("https://www1.gogoanime.ai/")
        self.wait()
        self.anime_title = ""
        self.anime_info = {}
        self.episode_number = -1
        self.search_anime(name)

    def wait(self):
        time.sleep(4)

    def search_anime(self, name):
        name = self._format(name)
        self.search_box = self.driver.find_element_by_xpath('//*[@id="keyword"]')
        self.search_box.send_keys(name)
        self.search_box.send_keys(Keys.ENTER)
        self.wait()

        try:
            self.anime_info = self.driver.find_element_by_xpath(
                '//*[@id="wrapper_bg"]/section/section[1]/div/div[2]/ul/li[1]').click()
            self.title()
            self.anime_info = self.anime_data()

        except NoSuchElementException:
            raise Exception("AnimeNotFound")
            self.driver.quit()

    def title(self):
        self.anime_title = self.driver.find_element_by_css_selector('.anime_info_body h1').text

    def anime_data(self):
        data = self.driver.find_elements_by_css_selector('.anime_info_body p')
        data_dict = {}
        for ind in data:
            data_list = ind.text.split(':')
            if len(data_list) > 1:
                data_dict[(data_list[0].strip())] = (data_list[1].strip())

        return data_dict

    def get_anime_title(self):
        return self.anime_title

    def get_anime_data(self):
        return self.anime_info

    def _format(self, name):
        name = name.title().split(' ')
        if 'Season' in name and '1' in name:
            name.remove('Season')
            name.remove('1')
        return ' '.join(name)

    def get_download_link(self, episode_number):
        self.valid_ep = False
        self.episode_number = episode_number
        self.start = 0
        self.end = 0
        self.wait()

        for i in range(1, 10):
            try:
                self.link = f'//*[@id="episode_page"]/li[{i}]/a'
                self.ep = self.driver.find_element_by_xpath(self.link)
                self.ep_list = self.ep.text.split('-')
                if int(self.ep_list[0]) <= self.episode_number <= int(self.ep_list[1]):
                    self.valid_ep = True
                    self.start, self.end = int(self.ep_list[0]), int(self.ep_list[1])
                    #self.ep.click()
                    self.driver.execute_script('arguments[0].click();', self.ep)
                    break
            except NoSuchElementException:
                self.valid_ep = False
                break

        if not self.valid_ep:
            raise Exception("InvalidEpisode")
        else:
            self.num = (self.end - self.start + 1) - (self.episode_number - self.start)
            self.wait()

            self.episode_xpath = f'//*[@id="episode_related"]/li[{self.num}]/a'
            self.desired_episode = self.driver.find_element_by_xpath(self.episode_xpath)
            self.driver.execute_script('arguments[0].click();', self.desired_episode)

            self.wait()

            self.download_btn_response = requests.get(self.driver.current_url)

            self.soup = BeautifulSoup(self.download_btn_response.text, 'html.parser')
            self.download_btn_url = self.soup.find('li', class_='dowloads').find('a')['href']
            self.download_btn_response = requests.get(self.download_btn_url)

            self.soup = BeautifulSoup(self.download_btn_response.text, 'html.parser')
            self.temp = (self.soup.find_all('a'))
            self.download_link = {}
            for i in self.temp:
                try:
                    if i.string.count('\n') > 0:
                        self.download_link[i.string.split('\n')[1].strip()] = i['href']
                except AttributeError:
                    continue
            return self.download_link

    def download(self,url, output_path):
        with DownloadProgressBar(unit='B', unit_scale=True,
                                 miniters=1, desc=url.split('/')[-1]) as t:
            urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)
