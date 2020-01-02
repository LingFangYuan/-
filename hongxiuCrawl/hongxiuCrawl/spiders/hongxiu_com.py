# -*- coding: utf-8 -*-
import re

import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Spider
from scrapy_redis.spiders import RedisSpider
from hongxiuCrawl.items import HongxiuBookListItem, HongxiuBookDetailItem


class HongxiuComSpider(RedisSpider):
    name = 'hongxiu.com'
    allowed_domains = ['www.hongxiu.com']
    #start_urls = [
    #    'https://www.hongxiu.com/all']
    redis_key = 'hongxiu.com:start_urls'

    def parse(self, response):
        return self.parse_book_list(response)

    def parse_book_list(self, response):
        if response.status == 500:
            return

        books = response.xpath('.//div[@class="right-book-list"]/ul/li')
        for book in books:
            novelLink = book.xpath(
                './/div[@class="book-info"]/h3/a/@href').extract_first()
            novelLink = response.urljoin(novelLink)
            novelId = novelLink.split('/')[-1]
            novelName = book.xpath(
                './/div[@class="book-info"]/h3/a/@title').extract_first()
            novelAuthor = book.xpath(
                './/div[@class="book-info"]/h4/a/text()').extract_first()
            novelType = book.xpath(
                './/div[@class="book-info"]/p[@class="tag"]/span[@class="org"]/text()').extract_first()
            novelStatus = book.xpath(
                './/div[@class="book-info"]/p[@class="tag"]/span[@class="pink"]/text()').extract_first()
            novelWorlds = book.xpath(
                './/div[@class="book-info"]/p[@class="tag"]/span[@class="blue"]/text()').extract_first()
            novelSections = None
            novelIntro = book.xpath(
                './/div[@class="book-info"]/p[@class="intro"]/text()').extract_first()
            novelImageUrl = book.xpath(
                './/div[@class="book-img"]/a/img/@src').extract_first()
            novelImageUrl = response.urljoin(novelImageUrl)

            book_list_item = HongxiuBookListItem(
                novelId=novelId, novelName=novelName, novelLink=novelLink,
                novelAuthor=novelAuthor, novelType=novelType, novelStatus=novelStatus,
                novelWorlds=novelWorlds, novelIntro=novelIntro, novelImageUrl=novelImageUrl)

            request = scrapy.Request(
                url=novelLink, callback=self.parse_book_detail)
            request.meta['book_list_item'] = book_list_item

            yield request

        # 爬取下一页链接
        page_container = response.xpath('.//*[@id="page-container"]')
        data_url = page_container.xpath('@data-url').extract_first()
        data_url = response.urljoin(data_url)
        data_total = page_container.xpath('@data-total').extract_first()
        data_size = page_container.xpath('@data-size').extract_first()
        data_page = page_container.xpath('@data-page').extract_first()
        if data_page and data_total and int(data_size) * int(data_page) < int(data_total):
            next_page = str(int(data_page) + 1)
            next_url = data_url.replace('pageNum=1', 'pageNum=' + next_page)

            next_request = scrapy.Request(
                url=next_url, callback=self.parse_book_list)

            yield next_request

    def parse_book_detail(self, response):
        book_list_item = response.meta['book_list_item']
        novelId = book_list_item['novelId']

        p_total = response.xpath(
            './/div[@class="book-info"]/p[@class="total"]').xpath('string()').extract_first()
        click_m = re.search(r'(\d+\.?(?:\d+)?.{2})总点击', p_total)
        collect_m = re.search(r'(\d+\.?(?:\d+)?.{2})总收藏', p_total)

        novelAllClick = click_m.group(1) if click_m else ''
        novelAllCollect = collect_m.group(1) if collect_m else ''
        novelDays = response.xpath('.//li[h4="创作天数"]/p/text()').extract_first()
        novelWeekPoll = response.xpath(
            './/*[@id="recCount"]/text()').extract_first()
        novelMonthPoll = response.xpath(
            './/*[@id="monthCount"]/text()').extract_first()

        book_detail_item = HongxiuBookDetailItem(novelId=novelId, novelAllClick=novelAllClick,
                                                 novelAllCollect=novelAllCollect, novelDays=novelDays,
                                                 novelWeekPoll=novelWeekPoll, novelMonthPoll=novelMonthPoll)

        sections = response.xpath(
            './/*[@id="J-catalogCount"]/text()').extract_first()
        sections = sections if sections is None else sections.lstrip(
            '(').rstrip('章)')
        book_list_item['novelSections'] = sections

        yield book_list_item
        yield book_detail_item
