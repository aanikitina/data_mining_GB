from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from scrapy_parser import settings
from scrapy_parser.spiders.hhru import HhruSpider
from scrapy_parser.spiders.sjru import SuperjobSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HhruSpider)
    process.crawl(SuperjobSpider)
    process.start()
