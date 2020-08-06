import json
import re
from urllib.request import urljoin

from bs4 import BeautifulSoup
from lxml import etree
from Tools import *
from HtmlDownloader import HtmlDownloader

class HtmlParser:
    '''解析器基类'''
    
    def parser_url(self, page_url, page_content):
        '''
        解析网页中待爬取章节的URL
        :params page_url: 爬取小说网页的URL
        :params page_content: 爬取小说网页的内容
        :return: 返回小说名称，作者，内容简介，和各章节的名称及URL
        '''
    
    def parser_content(self, page_url, page_content):
        '''
        提取网页中的小说章节的内容
        :params page_url: 爬取小说章节的URL
        :params page_content: 爬取小说章节网页
        :return: 返回格式化后的章节内容
        '''
    
    def parser_search(self, page_url, page_content, parser_key):
        '''
        解析网页中搜索结果页面
        :params page_url: 爬取小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者，小说来源，解析器键及URL的元组列表
        '''

class HtmlParserUC(HtmlParser):
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

    def parser_search(self, page_url, page_content, parser_key):
        '''
        解析网页中搜索结果页面
        :params page_url: 爬取小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者，小说来源，解析器键及URL的元组列表
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
                book_info.append('uctxt.com')
                book_info.append(parser_key)
                book_info.append(book_url)
                result.append(tuple(book_info))
            return result
        except Exception as e:
            print(e, page_url)


class HtmlParserSM(HtmlParser):
    '''神马小说搜索'''

    def __init__(self):
        self.downloader = HtmlDownloader()

    def parser_search(self, page_url, page_content, parser_key):
        '''
        解析网页中搜索结果页面
        :params page_url: 搜索小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者，小说来源，解析器键及URL的元组列表
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
            result.append((lv['类型'], book_name, lv['作者'], lv['来源'], parser_key, book_url))

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
                json_url, json_str = self.downloader.download(url)
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
            content = soup.find(name=['div', 'p'], id=['content', 'nr1', 'TXT', 'htmlContent', 'BookTextt'])
            temp = content.get_text()
            if temp is None:
                return
            section_content = ' ' * 4 + re.sub(r'\s+', '\n\n' + ' ' * 4, temp)
            return section_content
        except Exception as e:
            print(e, page_url)

class HtmlParser51(HtmlParser):
    '''无忧书网'''
    
    def __init__(self):
        self.downloader = HtmlDownloader()
        
    def parser_search(self, page_url, page_content, parser_key):
        '''
        解析网页中搜索结果页面
        :params page_url: 搜索小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者，小说来源，解析器键及URL的元组列表
        '''
        if page_url is None or page_content is None:
            return
        try:
            result = []
            soup = BeautifulSoup(page_content, 'lxml')

            book_list = soup.find(
                'div', class_='list-lastupdate')
            if book_list is None:
                book_url = page_url
                book_name = soup.find(name='div', class_='book-info clrfix').div.h1.get_text()
                book_cate = soup.find(name='span', class_='c2').get_text().strip('小说 >')
                book_author = soup.find(name='div', class_='book-info clrfix').div.em.get_text().strip('作者: ')
                book_info = [book_cate, book_name, book_author]
                book_info.append('51shu.net')
                book_info.append(parser_key)
                book_info.append(book_url)
                result.append(tuple(book_info))
                if not book_name:
                    return
            else:
                book_list = book_list.find_all('li')
                for book in book_list:
                    book_url = urljoin(page_url, book.find('span', class_='name').find('a').get('href'))
                    book_name = book.find('span', class_='name').find('a').get_text()
                    book_cate = book.find('span', class_='class').get_text().strip('[]')
                    book_author = book.find('span', class_='other')
                    [x.extract() for x in book_author.find_all(name = ['small', 'i'])]
                    book_author = book_author.get_text()
                    book_info = [book_cate, book_name, book_author]
                    book_info.append('51shu.net')
                    book_info.append(parser_key)
                    book_info.append(book_url)
                    result.append(tuple(book_info))
                
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
            soup = BeautifulSoup(page_content, 'lxml')

            book_info = soup.find(class_='chapter-list clrfix')
            h1 = soup.find(name='div', class_='book-info clrfix').div.h1  # 小说名称
            em = soup.find(name='div', class_='book-info clrfix').div.em  # 作者
            intro = soup.find('p', class_='intro')  # 简介

            book_name = h1.get_text() if h1 is not None else ''
            author = em.get_text().strip('作者: ') if em is not None else ''
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
            content = content.get_text().replace('℡无忧书网-(http://m.51shu.net)℡gg4();', '').replace('天才壹秒記住', '').replace('\n', '')
            content = re.sub(r'https?://.*gg5\(\);', '', content)
            
            section_content = ' ' * 4 + content.strip().replace('    ',
                                                                           '\n\n' + ' ' * 4)
            
            # 判断本章是否有下一页
            book_title = soup.find('h1', id='BookTitle').get_text()
            pattern = re.search(r'\((\d+)/(\d+)\)', book_title)
            
            next_url = soup.find(name='a', text='下一页').get('href')
            next_url = urljoin(page_url, next_url)
            
            if pattern and pattern.group(1) != pattern.group(2):
                next_page_url, next_page_content = self.downloader.download(next_url)
                return section_content + self.parser_content(next_page_url, next_page_content)
            else:
                return section_content
        except Exception as e:
            print(e, page_url)


class HtmlParserBAOSHU(HtmlParser):
    '''宝书网'''
    
    def __init__(self):
        self.downloader = HtmlDownloader()
        
    def parser_search(self, page_url, page_content, parser_key):
        '''
        解析网页中搜索结果页面
        :params page_url: 搜索小说网页的URL
        :params page_content: 搜索结果网页的内容
        :return: 返回小说类别，小说名称，小说作者，小说来源，解析器键及URL的元组列表
        '''
        if page_url is None or page_content is None:
            return
        try:
            result = []
            soup = BeautifulSoup(page_content, 'lxml')

            book_list = soup.find(
                'div', class_='sslist')
            if book_list:
                book_list = book_list.find_all('li')
                for book in book_list:
                    h1_a = book.find_all('a')
                    book_url = urljoin(page_url, h1_a[1].get('href')) if len(h1_a) >= 2 else ''
                    book_name = h1_a[1].get_text() if len(h1_a) >= 2 else ''
                    book_cate = h1_a[0].get_text() if len(h1_a) >= 2 else ''
                    book_author = ''
                    
                    book_info = [book_cate, book_name, book_author]
                    book_info.append('baoshuu.com')
                    book_info.append(parser_key)
                    book_info.append(book_url)
                    result.append(tuple(book_info))
                
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
            soup = BeautifulSoup(page_content, 'lxml')

            book_info = soup.find(class_='mlist')
            h1 = book_info.find(name='h1')  # 小说名称
            a = book_info.find('li').find('a') # 作者
            
            intro = soup.find('p', class_='intro')  # 简介

            book_name = h1.get_text() if h1 is not None else ''
            author = a.get_text() if a is not None else ''
            intro = soup.find('div', class_='conten')
            intro = intro.get_text()if intro is not None else ''
            
            a_list = soup.find('div', class_='qd').find_all('a', class_='right')
            urls = []
            for a in a_list:
                section_url = urljoin(page_url, a.get('href'))
                section_name = a.get_text()
                urls.append((section_url, section_name))
            
            return book_name, author, intro, urls
        except Exception as e:
            print(e, page_url)
    
