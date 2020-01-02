from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from deskzolSpider.spiders.fengjing_spider import FengjingSpider


if __name__ == '__main__':
    process = CrawlerProcess(get_project_settings())
    process.crawl('fengjing')
    process.start()
