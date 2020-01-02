from urllib.parse import urljoin

import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from deskzolSpider.items import DeskzolspiderItem


class FengjingSpider(CrawlSpider):
    name = 'fengjing'
    start_urls = ['http://desk.zol.com.cn/fengjing/4096x2160/']
    allowed_domains = ['desk.zol.com.cn']

    rules = (
        Rule(LinkExtractor(
            restrict_xpaths=('.//a[@id="pageNext" and @class="next"]',)),
            follow=True,
            callback='parse_page')
        ,)

    def parse_start_url(self, response):
        yield from self.parse_page(response)

    def parse_page(self, response):
        lis = response.xpath('.//div[@class="main"]/ul[position()=1]/li')
        for li in lis:
            url = li.xpath('./a/@href').extract()[0]
            url = urljoin(response.url, url)
            title = li.xpath('./a/span/em/text()').extract()[0]
            image_urls = list()
            item = DeskzolspiderItem(url=url, title=title, image_urls=image_urls)

            request = scrapy.Request(url=url, callback=self.parse_bizhi)
            request.meta['item'] = item
            yield request

    def parse_bizhi(self, response):
        item = response.meta['item']
        button = response.xpath('.//dd[@id="tagfbl"]/a[position()=1]/@href').extract()[0]
        button = urljoin(response.url, button)
        page_next = response.xpath('.//a[@id="pageNext" and contains(@href, "/bizhi/")]/@href').extract()

        if page_next:
            next_url = urljoin(response.url, page_next[0])
            r1 = scrapy.Request(url=next_url, callback=self.parse_bizhi)
            r1.meta['item'] = item
            yield r1
        request = scrapy.Request(url=button, callback=self.parse_image)
        request.meta['item'] = item
        yield request

    def parse_image(self, response):
        item = response.meta['item']
        image_url = response.xpath('.//body/img[position()=1]/@src').extract()
        if image_url:
            item['image_urls'].append(image_url[0])
        yield item
