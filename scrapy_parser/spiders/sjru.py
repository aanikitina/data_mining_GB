# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from scrapy_parser.items import ScrapyParserItem

class SuperjobSpider(scrapy.Spider):
    name = 'superjob'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://www.superjob.ru/vacancy/search/?keywords=python']

    def parse(self, response):
        next_page = response.css('a.f-test-link-dalshe::attr(href)').extract_first()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        else:
            pass

        vacancy_list = response.css('a._1QIBo ::attr(href)').extract()

        for link in vacancy_list:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.css('div._3MVeX h1 ::text').extract_first()
        # salary = response.css('div._3MVeX span._2Wp8I::text').extract_first()
        salary = ''.join(response.css('div._3MVeX span.ZON4b *::text').getall()).replace('\xa0', ' ')
        company = response.css('div._3RlfE h2._15msI::text').extract_first().strip()
        url = response.url

        yield ScrapyParserItem(name=name, salary=salary, company=company, url=url)