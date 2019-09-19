import requests
from pymongo import MongoClient, errors
from bs4 import BeautifulSoup


# constants

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.1.1 Safari/605.1.15'

MONGO_URL = 'mongodb://localhost:27017'
client = MongoClient('localhost', 27017)
database = client.lesson2
collection = database.jobs


HH_MAIN_URL = 'https://hh.ru'
SJ_MAIN_URL = 'https://www.superjob.ru'

query_str = input('query:')
hh_entry_url = f'{HH_MAIN_URL}/search/vacancy?area=1&st=searchVacancy&text={query_str}'
sj_entry_url = f'{SJ_MAIN_URL}/vacancy/search/?keywords={query_str}'


class JobParser:

    def __init__(self):
        self.entry_url = None
        self.next = None

    def get_body(self, entry_url):
        response = requests.get(entry_url, headers={'User-Agent': USER_AGENT})
        soup = BeautifulSoup(response.text, 'lxml')
        return soup.html.body

    def get_hh_job(self, job_tag):

        min_comp = max_comp = None
        url = job_tag.find('a').attrs['href']
        title = job_tag.find('a').text

        try:
            comp_str = job_tag.find('div', attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text


            if len(comp_str.replace('\xa0', '').strip(' руб.').split('-')) > 1:
                min_comp, max_comp = comp_str.replace('\xa0', '').strip(' руб.').split('-')
            else:
                rel, val = comp_str.replace('\xa0', '').strip(' руб.').split(' ')

                if rel == 'от':
                    min_comp = val
                elif rel == 'до':
                    max_comp = val
                else:
                    min_comp = max_comp = val

        except:
            pass

        job = {'title': title,
               'url': url,
               'min_comp': min_comp,
               'max_comp': max_comp,
               'source': HH_MAIN_URL
               }

        return job

    def get_sj_job(self, job_tag):

        min_comp = max_comp = None

        url = f"{SJ_MAIN_URL}{job_tag.find('a', attrs={'class': ['_1QIBo']}).attrs['href']}"
        title = job_tag.find('div', attrs={'class': '_3mfro CuJz5 PlM3e _2JVkc _3LJqf'}).text

        try:
            comp_tag = job_tag.find('span', attrs={'class': 'f-test-text-company-item-salary'})
            comp_str = ''.join([_.text.replace('\xa0', '') for _ in comp_tag.findAll('span')]).strip('₽')

            if len(comp_str.split('—')) > 1:
                min_comp, max_comp = comp_str.split('—')
            else:
                min_comp = max_comp = comp_str
        except:
            pass

        job = {'title': title,
               'url': url,
               'min_comp': min_comp,
               'max_comp': max_comp,
               'source': SJ_MAIN_URL
               }

        return job


    def get_page_list(self, source, entry_url):
        """ Returns list of entities urls for single page"""
        if source == 'hh':
            item_qtag = 'div'
            item_qattrs_list = ({'data-qa': 'vacancy-serp__vacancy vacancy-serp__vacancy_premium'},
                           {'data-qa': 'vacancy-serp__vacancy'},
                           )
            main_url = HH_MAIN_URL

        elif source == 'sj':
            item_qtag = 'div'
            # item_qtag = 'script'
            item_qattrs_list = ({'class': 'f-test-vacancy-item'},
                                )
            # item_qattrs_list = ({'type': 'application/ld+json'},
            #                    )
            main_url = SJ_MAIN_URL

        else:
            print('Invalid source name: please, specify the "source" as "hh" or "sj"')
            return

        body = self.get_body(entry_url)

        job_list = []

        for attrs in item_qattrs_list:
            # print(attrs)
            job_list.extend(body.findAll(item_qtag, attrs=attrs))
            # print(len(job_list))

        if source == 'hh':
            jobs = [self.get_hh_job(_) for _ in job_list]

        elif source == 'sj':
            jobs = [self.get_sj_job(_) for _ in job_list]

        try:
            if source == 'hh':
                next_url = f"{main_url}{body.find('a', attrs={'data-qa': 'pager-next'}).attrs['href']}"
            elif source == 'sj':
                next_url = f"{main_url}{body.find('a', attrs={'class': 'f-test-link-dalshe'}).attrs['href']}"
        except AttributeError:  # last page case
            next_url = None

        return jobs, next_url

    def paginate(self, page_lim, source, entry_url):
        """ Returns searching entities result list for several pages"""
        jobs = []
        i = 0

        self.next = entry_url
        while True:
            if self.next and (i < page_lim):
                new_jobs, self.next = self.get_page_list(source, self.next)
                jobs.extend(new_jobs)
                i += 1
            else:
                break
        return jobs

    def parse_jobs(self, hh_pages=1000, sj_pages=1000):

        jobs = []
        jobs.extend(self.paginate(sj_pages, 'sj', sj_entry_url))
        print('sj parsing completed')
        jobs.extend(self.paginate(hh_pages, 'hh', hh_entry_url))
        print('hh parsing completed')

        return jobs


def dict_to_mongo(res_list, collection):
    try:
        if res_list:
            collection.insert_many(res_list)
        else:
            print('Empty set')

    except errors.ServerSelectionTimeoutError as err:
        # check that mongo is alive
        print(f'DB IMPORT ERROR occurred: {err}')


parser = JobParser()
jobs = parser.parse_jobs()

print(f'Jobs extracted: {len(jobs)}')
dict_to_mongo(jobs, collection)

print(1)