import requests
from pymongo import MongoClient, errors
from bs4 import BeautifulSoup
import time
import random

#  constants

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'

MONGO_URL = 'mongodb://localhost:27017'
client = MongoClient('localhost', 27017)
database = client.lesson2
collection = database.avito_flats


MAIN_URL = 'https://www.avito.ru'
ENTRY_URL = f'{MAIN_URL}/moskva/kvartiry'


class AvitoParser:

    def __init__(self):
        self.entry_url = None
        self.next = None
        self.result = []

    def get_page_list(self, entry_url):
        """ Returns list of flat urls for single page"""

        # self.entry_url = entry_url

        response = requests.get(entry_url, headers={'User-Agent': USER_AGENT})
        soup = BeautifulSoup(response.text, 'lxml')
        body = soup.html.body

        flat_list = body.findAll('h3', attrs={'class': 'title item-description-title', 'data-marker': "item-title"})
        urls_list = [f"{MAIN_URL}{item.find('a').attrs['href']}" for item in flat_list]
        try:
            next_url = f"{MAIN_URL}{body.find('a', attrs={'class': 'pagination-page js-pagination-next'}).attrs['href']}"
        except AttributeError:  # last page case
            next_url = None

        return (urls_list, next_url)

    def get_flat_urls(self, entry_url, sleep=True):
        """Performs pagination from entry_url to last
        Returns all flat urls which can be riched from entry_url by pagination"""

        self.entry_url = entry_url
        self.next = entry_url

        results = []

        while True:
            if self.next == self.entry_url:
                page_flats, self.next = self.get_page_list(self.entry_url)

            elif self.next:
                page_flats, self.next = self.get_page_list(self.next)
            else:  # next == None
                break

            if sleep:
                time.sleep(random.randint(1, 3))

            results.extend(page_flats)
            print(self.entry_url, len(results))

        return results


    def get_flat(self, url):
        response = requests.get(url, headers={'User-Agent': USER_AGENT})
        soup = BeautifulSoup(response.text, 'lxml')

        try:
            price = soup.body.findAll('span', attrs={'class': 'js-item-price', 'itemprop': 'price'})[0].attrs.get(
                'content')
        except IndexError:
            price = None

        result = {'title': soup.body.find('span', attrs={'class': 'title-info-title-text'}).text,
                  'price': int(price) if price and price.isdigit else None,
                  'url': response.url,
                  'params': [tuple(itm.text.split(': ')) for itm in
                             soup.body.findAll('li', attrs={'class': 'item-params-list-item'})]
                  }

        return result

    def flats_to_mongo(self, collection, flat_urls=None):
        try:
            if flat_urls:
                for itm in flat_urls:
                    time.sleep(random.randint(1, 4))
                    flat = self.get_flat(itm)
                    # print(flat)
                    collection.insert_one(flat)
                print(f'{len(flat_urls)} flats written to {collection}')
            else:
                print('Empty set')

        except errors.ServerSelectionTimeoutError as err:
            # check that mongo alive
            print(f'DB IMPORT ERROR occurred: {err}')


    def parse_flats(self, entry_url, collection):
        flat_url_list = self.get_flat_urls(entry_url)
        self.flats_to_mongo(collection, flat_url_list)





if __name__ == '__main__':
    parser = AvitoParser()

    parser.parse_flats(f'{ENTRY_URL}', collection)
    # flat = parser.get_flat('https://www.avito.ru/moskva/kvartiry/3-k_kvartira_78.1_m_1617_et._1542337330')
    # parser.parse_flats(f'{ENTRY_URL}?p=98', collection)  # to specify start page


print(1)