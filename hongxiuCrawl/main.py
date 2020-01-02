from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from hongxiuCrawl.spiders.hongxiu_com import HongxiuComSpider


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl('hongxiu.com')
    process.start()
