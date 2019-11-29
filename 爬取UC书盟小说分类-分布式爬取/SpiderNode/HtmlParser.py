import re
from urllib.request import urljoin

from bs4 import BeautifulSoup


class HtmlParser:

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
            # h1 = book_info.find('h1')  # 小说名称
            em = book_info.find('em')  # 作者
            intro = soup.find('p', class_='intro')  # 简介

            # book_name = h1.get_text() if h1 is not None else ''
            author = em.get_text() if em is not None else ''
            intro = intro.get_text().replace('    ', '\n\n' + '' * 4) if intro is not None else ''
            a_list = soup.find('dl', class_='chapter-list clrfix').find_all('a', href=True)
            urls = []
            for a in a_list:
                section_url = urljoin(page_url, a.get('href'))
                section_name = a.get_text()
                urls.append((section_url, section_name))
            return author, intro, urls
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
            section_content = ' ' * 4 + content.get_text().strip().replace('    ', '\n\n' + ' ' * 4)
            return section_content
        except Exception as e:
            print(e, page_url)

    def parser_page(self, page_url, page_content):
        '''
        爬取页面
        :param page_url: 页面的URL
        :param page_content: 页面的内容
        :return: 返回([(url, book_name)...], next_page)
        '''
        try:
            soup = BeautifulSoup(page_content, 'lxml')
            news = []
            details = soup.find('div', class_='details clrfix')
            if details is not None:
                item_list = details.find('ul', class_='item-list clrfix').find_all('a', href=re.compile(r'/book/.*'))
                next_page = details.find('div', class_='pages').find('a', class_='next').get('href')
                next_page = None if next_page is None else urljoin(page_url, next_page)
            for item in item_list:
                url = item.get('href')
                full_url = urljoin(page_url, url)
                book_name = item.get_text()
                if full_url is not None and book_name is not None:
                    news.append((full_url, book_name))
            return news, next_page
        except Exception as e:
            print(e, page_url)
