from multiprocessing.managers import BaseManager
from multiprocessing import Process

from HtmlDownloader import HtmlDownloader
from HtmlParser import HtmlParser


class QueueManager(BaseManager):
    pass


class SpiderWork:

    def __init__(self):
        # 初始化分布式进程中工作节点的连接工作
        # 实现第一步：使用BaseManager注册用于获取Queue的方法名称
        QueueManager.register('get_url_queue')
        QueueManager.register('get_page_queue')
        QueueManager.register('get_result_queue')

        # 实现第二步：连接到服务器
        server_addr = '172.30.196.104'
        print('Connect to server %s ...' % server_addr)
        # 注意保持端口和验证口令与服务进程设置的完全一致
        self.m = QueueManager(address=(server_addr, 8001), authkey=b'ling')
        # 网络连接
        self.m.connect()
        # 实现第三步：获取Queue的对象
        self.url_q = self.m.get_url_queue()
        self.page_q = self.m.get_page_queue()
        self.result_q = self.m.get_result_queue()
        # 初始化网页下载和解析器
        self.downloader = HtmlDownloader()
        self.parser = HtmlParser()
        # 发送加入标志到控制节点
        self.result_q.put({'data': 'join', 'status': 'join'})
        print('init finish')

    def crawl_page_proc(self):
        while True:
            try:
                if not self.page_q.empty():
                    url = self.page_q.get()
                    print(url)
                    if url == 'end':
                        print('控制节点通知爬虫节点爬取页面进程停止工作...')
                        return
                    print('爬虫节点正在解析: %s' % url)
                    content = self.downloader.download(url)
                    news, next_page = self.parser.parser_page(url, content)
                    self.result_q.put({'data': (news, next_page), 'status': 'url'})
            except Exception as e:
                print(e)
                print('爬取页面进程错误！')

    def crawl_content_proc(self):
        while True:
            try:
                if not self.url_q.empty():
                    book_url, book_name = self.url_q.get()
                    if book_url == 'end':
                        print('控制节点通知爬虫节点爬取小说进程停止工作...')
                        self.result_q.put({'data': 'end', 'status': 'end'})
                        self.url_q.put(('end', 'end'))
                        return
                    print('爬虫节点正在爬取: %s %s' % (book_url, book_name))
                    content = self.downloader.download(book_url)
                    author, intor, urls = self.parser.parser_url(book_url, content)
                    self.result_q.put({'data': ((book_name, author, intor), book_name), 'status': 'data'})
                    # i = 0
                    for url in urls:
                        # if i >= 0:
                            # break
                        print('正在爬取：%s  %s' % url)
                        page_url = url[0]
                        section_title = url[1]
                        page_content = self.downloader.download(page_url)
                        section_content = self.parser.parser_content(page_url, page_content)
                        self.result_q.put({'data': ((section_title, section_content), book_name), 'status': 'data'})
                        # i += 1
                    print('爬取完成！%s %s' % (book_url, book_name))
            except Exception as e:
                print(e)
                print('爬取页面进程错误！')

    def crawl(self):
        crawl_page = Process(target=self.crawl_page_proc)
        crawl_content = Process(target=self.crawl_content_proc)
        crawl_page.start()
        crawl_content.start()
        crawl_page.join()
        crawl_content.join()


if __name__ == '__main__':
    spider = SpiderWork()
    spider.crawl()
