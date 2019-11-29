import time
from multiprocessing import Process, Queue

from HtmlDownloader import HtmlDownloader
from HtmlParser import HtmlParser
from DataOutput import DataOutput


class SpiderMan:

    def download_proc(self, root_url, store_q):
        if root_url is None:
            return
        downloader = HtmlDownloader()
        parser = HtmlParser()
        root_content = downloader.download(root_url)
        book_name, author, intor, urls = parser.parser_url(root_url, root_content)
        # output = DataOutput(book_name, author, intor)
        store_q.put((book_name, author, intor))
        for url in urls:
            print('正在爬取：%s  %s' % url)
            page_url = url[0]
            section_title = url[1]
            page_content = downloader.download(page_url)
            section_content = parser.parser_content(url, page_content)
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
                if data == 'end':
                    print('保存: %s 完毕!' % name)
                    return
                if output is None:
                    output = DataOutput(*data)
                    name = data[0]
                else:
                    output.store_data(*data)
            else:
                time.sleep(0.1)


if __name__ == '__main__':
    root_url = 'https://m.uctxt.com/book/25/25324/'
    store_q = Queue()
    spider = SpiderMan()
    download_proc = Process(target=spider.download_proc, args=(root_url, store_q))
    store_proc = Process(target=spider.store_proc, args=(store_q,))
    download_proc.start()
    store_proc.start()
    download_proc.join()
    store_proc.join()
