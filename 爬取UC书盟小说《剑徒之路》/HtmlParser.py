import json
import re
from urllib.request import urljoin

from bs4 import BeautifulSoup
from lxml import etree
from Tools import *
from HtmlDownloader import HtmlDownloader


class HtmlParserUC:
    '''UC书盟网 解析器'''

    def parser_url(self, page_url, page_content):
        '''
        解析网页中待爬取章节的URL
        :params page_url: 爬取小说网页的URL
        :params page_content: 爬取小说网页的内容
        :return: 返回小说名称，作者，内容简介，和各章节的名称及URL
        '''
        if page_url is None or page_content is None:
            return
        try:
            soup = BeautifulSoup(page_content, 'lxml')

            book_info = soup.find(class_='book-info clrfix')
            h1 = book_info.find('h1')  # 小说名称
            em = book_info.find('em')  # 作者
            intro = soup.find('p', class_='intro')  # 简介

            book_name = h1.get_text() if h1 is not None else ''
            author = em.get_text() if em is not None else ''
            intro = intro.get_text().replace('    ', '\n\n' + '' *
                                             4) if intro is not None else ''
            a_list = soup.find(
                'dl', class_='chapter-list clrfix').find_all('a', href=True)
            urls = []
            for a in a_list:
                section_url = urljoin(page_url, a.get('href'))
                section_name = a.get_text()
                urls.append((section_url, section_name))
            return book_name, author, intro, urls
        except Exception as e:
            print(e, page_url)

    def parser_content(self, page_url, page_content):
        '''
        提取网页中的小说章节的内容
        :params page_url: 爬取小说章节的URL
        :params page_content: 爬取小说章节网页
        :return: 返回格式化后的章节内容
        '''
        if page_url is None or page_content is None:
            return
        try:
            soup = BeautifulSoup(page_content, 'lxml')
            content = soup.find('div', id='content')
            temp = content.get_text()
            if temp is None:
                return
            section_content = ' ' * 4 + content.get_text().strip().replace('    ',
                                                                           '\n\n' + ' ' * 4)
            return section_content
        except Exception as e:
            print(e, page_url)

    def parser_search(self, page_url, page_content):
        '''
        解析网页中搜索结果页面
        :params page_url: 爬取小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者及URL的元组列表
        '''
        if page_url is None or page_content is None:
            return
        try:
            result = []
            soup = BeautifulSoup(page_content, 'lxml')

            book_list = soup.find(
                'ul', class_='item-list clrfix')
            if book_list is None:
                return
            book_list = book_list.find_all('li')
            for book in book_list:
                book_info = book.get_text().split()
                book_info[0] = book_info[0].strip('[]')
                book_url = urljoin(page_url, book.find('a').get('href'))
                book_info.append(book_url)
                result.append(tuple(book_info))
            return result
        except Exception as e:
            print(e, page_url)


class HtmlParserSM:
    '''神马小说搜索'''

    def __init__(self):
        self.downloader = HtmlDownloader()

    def parser_search(self, page_url, page_content):
        '''
        解析网页中搜索结果页面
        :params page_url: 搜索小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者及URL的元组列表
        '''
        if page_url is None or page_content is None:
            return
        try:
            result = []
            html = etree.HTML(page_content)

            book_name = take_first(html.xpath(
                './/div/a[@id and @class="c-header-inner c-flex-1"]//span[@c-bind="data.text"]/em/text()'))
            # url地址解码
            url_code = take_first(html.xpath(
                './/div/a[@id and @class="c-header-inner c-flex-1"]//span[@c-bind="data.text"]/em/ancestor::a[@class="c-header-inner c-flex-1"]/script/text()'))
            book_url = deutf8Str(url_code)
            if book_url is None:
                return

            label = my_strip(html.xpath(
                './/div/a[@id and @class="c-header-inner c-flex-1"]/following::*//p[@class="js-c-property-content c-property-content c-line-clamp-1"]/span[@class="c-property-label c-font-dark"]/text()'))
            value = html.xpath(
                './/div/a[@id and @class="c-header-inner c-flex-1"]/following::*//p[@class="js-c-property-content c-property-content c-line-clamp-1"]/span[@class="js-c-property-text"]/a/text() | .//div/a[@id and @class="c-header-inner c-flex-1"]/following::*//p[@class="js-c-property-content c-property-content c-line-clamp-1"]/span[@class="js-c-property-text"]/text()')

            lv = dict(zip(label, value))
            result.append((lv['类型'], book_name, lv['作者'], book_url))

            return result
        except Exception as e:
            print(e, page_url)

    def parser_url(self, page_url, page_content):
        '''
        解析网页中待爬取章节的URL
        :params page_url: 爬取小说网页的URL
        :params page_content: 爬取小说网页的内容
        :return: 返回小说名称，作者，内容简介，和各章节的名称及URL
        '''
        if page_url is None or page_content is None:
            return
        try:
            urls = []

            pattern = re.search(
                r'sm.runsc\("novel_intro_page", "#sc_novel_intro_page", (.*), 1\);', page_content)
            if pattern is None:
                return

            data = json.loads(pattern.group(1))
            author = data['author']
            book_name = data['title']
            intro = data['data']['novelInfo']['introduction']

            base_url = page_url.replace('&from=smor&safe=1', '&page={}&order=1').replace(
                '&format=html', '&format=json').replace('&title=', '&q=').replace('?method=novelintro.index&',
                                                                                  '?method=novelintro.menu&')
            page = 0

            while True:
                url = base_url.format(page)
                json_str = self.downloader.download(url)
                data = json.loads(json_str)
                pages = data['data']['pages']
                chapters = data['data']['chapters']
                for item in chapters:
                    section_url = item['url']
                    section_name = item['name']
                    urls.append((section_url, section_name))

                page += 1
                if page >= pages:
                    break

            return book_name, author, intro, urls
        except Exception as e:
            print(e, page_url)

    def parser_content(self, page_url, page_content):
        '''
        提取网页中的小说章节的内容
        :params page_url: 爬取小说章节的URL
        :params page_content: 爬取小说章节网页
        :return: 返回格式化后的章节内容
        '''
        if page_url is None or page_content is None:
            return
        try:
            soup = BeautifulSoup(page_content, 'lxml')
            content = soup.find('div', id=['content', 'nr1', 'TXT'])
            temp = content.get_text()
            if temp is None:
                return
            section_content = ' ' * 4 + re.sub(r'\s+', '\n\n' + ' ' * 4, temp)
            return section_content
        except Exception as e:
            print(e, page_url)
