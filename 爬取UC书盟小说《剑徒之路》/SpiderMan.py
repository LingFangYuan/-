import time
from multiprocessing import Process, Queue, freeze_support
from urllib.parse import quote

from HtmlDownloader import HtmlDownloader
from HtmlParser import HtmlParserUC, HtmlParserSM
from DataOutput import DataOutput


def str_to_url(str, encoding):
    return quote(str.encode(encoding))


class SpiderMan:

    def __init__(self):
        self.downloader = HtmlDownloader()
        self.parsers = {'UC': HtmlParserUC(), 'SM': HtmlParserSM()}
        self.current_parser = None
        self.search_urls = {'UC': 'https://m.uctxt.com/modules/article/search.php?searchkey={}',
                            'SM': 'https://so.m.sm.cn/s?q={}&from=smor&safe=1&by=submit&snum=6'}

    def crawl(self):
        freeze_support()
        store_q = Queue()
        store_proc = Process(target=self.store_proc, args=(store_q,))
        store_proc.start()

        while True:
            try:
                answer = int(input('1:继续查询小说。0:退出。：'))
            except ValueError:
                print('输入错误，请输入选项对应的数字！')
                continue
            if answer == 0:
                break
            elif answer != 1:
                print('输入错误，请输入选项对应的数字！')
                continue

            while True:
                book_name = input('请输入小说名称(0:退出搜索)：')
                try:
                    if int(book_name) == 0:
                        break
                except:
                    pass

                for parser_key, search_url in self.search_urls.items():
                    url = search_url.format(str_to_url(book_name, 'gbk'))
                    self.current_parser = self.parsers[parser_key]

                    page_content = self.downloader.download(url)
                    book_list = self.current_parser.parser_search(
                        url, page_content)
                    if book_list:
                        break

                if not book_list:
                    print('小说不存在！')
                    continue

                book_len = len(book_list)

                while True:
                    try:
                        self.print_books(book_list)
                        answer = int(input('请选择需要下载的小说：'))
                    except ValueError:
                        print('输入错误，请输入选项对应的数字！')
                        continue
                    if answer == 0:
                        break
                    if answer > book_len:
                        print('输入错误，请输入选项对应的数字！')
                        continue

                    url = book_list[answer - 1][-1]

                    page_content = self.downloader.download(url)
                    book_name, author, intor, urls = self.current_parser.parser_url(
                        url, page_content)
                    self.print_book(book_name, author, intor, urls)
                    answer = input('请确认是否下载(Y/N)?: ').upper()
                    if answer == 'Y':
                        download_proc = Process(
                            target=self.download_proc, args=(url, store_q, (book_name, author, intor, urls)))
                        download_proc.start()
                        download_proc.join()
                        break

        store_q.put('endall')
        store_proc.join()

    def download_proc(self, root_url, store_q, data):
        if root_url is None:
            return
        # root_content = self.downloader.download(root_url)
        book_name, author, intor, urls = data
        # output = DataOutput(book_name, author, intor)
        store_q.put((book_name, author, intor))
        for url in urls:
            print('正在爬取：%s  %s' % url)
            page_url = url[0]
            section_title = url[1]
            time.sleep(3)
            page_content = self.downloader.download(page_url)
            section_content = self.current_parser.parser_content(url, page_content)
            # output.store_data(section_title, section_content)
            store_q.put((section_title, section_content))
        store_q.put('end')  # 通知保存进程结束
        print('爬取完成！')

    def store_proc(self, store_q):
        output = None
        name = None
        while True:
            if not store_q.empty():
                data = store_q.get()
                if data == 'endall':
                    return
                if data == 'end':
                    print('保存: %s 完毕!' % name)
                    output = None
                    continue
                if output is None:
                    output = DataOutput(*data)
                    name = data[0]
                else:
                    output.store_data(*data)
            else:
                time.sleep(0.1)

    def print_books(self, book_list):
        def _print(index, cate, author, name):
            print('[{:>2}]{:{b}^4}[{:{b}^10}]《{:{b}<}》'.format(
                index, cate, author, name, b=chr(12288)))
        _print('*', '分类', '作者', '书名')
        for index, book in enumerate(book_list):
            _print(index + 1, book[0], book[2], book[1])
        _print('0', '', '取消本次搜索', '')

    def print_book(self, book_name, author, intor, urls):
        print('书名：{}'.format(book_name))
        print('作者：{}'.format(author))
        print('章节数：{}'.format(len(urls)))
        print('简介：{}'.format(intor))
if __name__ == '__main__':
    spider = SpiderMan()
    spider.crawl()
