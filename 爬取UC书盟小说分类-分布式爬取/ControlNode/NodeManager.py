import time
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Queue

from DataOutput import DataOutput, ZipFiles
from UrlManager import UrlManager
from sendMail import send


class QueueManager(BaseManager):
    pass


class NodeManager:

    def start_manager(self, url_q, page_q, result_q):
        '''
        创建一个分布式管理器
        :param url_q: 小说URL队列
        :param page_q: 页面URL队列
        :param result_q: 结果队列
        :return:
        '''

        def get_url_q():
            return url_q

        def get_page_q():
            return page_q

        def get_result_q():
            return result_q

        # 把创建的两个队列注册在网络中，利用register方法，callable参数关联了Queue对象，
        # 将Queue对象在网络中暴露
        QueueManager.register('get_url_queue', callable=get_url_q)
        QueueManager.register('get_page_queue', callable=get_page_q)
        QueueManager.register('get_result_queue', callable=get_result_q)
        # 绑定端口8001，设置验证口令“ling”。这个相当对象的初始化
        manager = QueueManager(
            address=('172.30.196.104', 8001), authkey=b'ling')
        # 返回manager对象
        return manager

    def url_manager_proc(self, url_q, page_q, conn_q, root_url):
        url_manager = UrlManager()
        print('控制节点开始运行...')
        page_q.put(root_url)
        page_count = 1
        while True:
            # 将从result_solve_proc获取的URL添加到URL管理器
            try:
                if not conn_q.empty():
                    data = conn_q.get()
                    news, next_page = data
                    url_manager.add_news(news)
                    if next_page is None or page_count >= 2:
                        # 通知爬取页面进程结束
                        page_q.put('end')
                    else:
                        # 将新的页面任务发送给爬虫节点
                        page_q.put(next_page)
                        page_count += 1
            except Exception as e:
                time.sleep(0.1)  # 延时休息

            while url_manager.has_new():
                if url_manager.old_size() >= 10:
                    print('控制节点发起结束通知！')
                    url_q.put(('end', 'end'))
                    # 关闭管理节点，同时存储set状态
                    url_manager.save_progress(
                        'new_urls_names.txt', url_manager.new_urls_names)
                    url_manager.save_progress(
                        'old_urls.txt', url_manager.old_urls)
                    url_manager.save_progress(
                        'old_names.txt', url_manager.old_names)
                    return
                # 从URL管理器获取一个新的任务
                new_url, new_name = url_manager.get_new()
                # 将新的任务发送给爬虫节点
                url_q.put((new_url, new_name))
                print('正在添加爬取第 %s 本小说的任务！' % url_manager.old_size())
                

    def result_solve_proc(self, conn_q, store_q, result_q):
        print('结果分析进程开始运行...')
        spider_count = 0
        end_count = 0
        while True:
            try:
                if not result_q.empty():
                    content = result_q.get()  # 结果为字典类型
                    if content['status'] == 'end':
                        # 结果分析进程接收结束通知
                        end_count += 1
                        if end_count == spider_count:
                            print('结果分析进程接收通知然后结束！')
                            store_q.put(('end', 'end'))
                            return
                        continue
                    if content['status'] == 'join':
                        spider_count += 1
                        continue
                    if content['status'] == 'url':
                        conn_q.put(content['data'])  # data为元组类型 (urls, page)
                    if content['status'] == 'data':
                        store_q.put(content['data'])  # data为元组类型 (data, book_name)
                else:
                    time.sleep(0.1)  # 延时休息
            except BaseException as e:
                time.sleep(0.1)  # 延时休息

    def store_proc(self, store_q):
        print('数据存储进程开始运行...')
        output = {}
        z = ZipFiles('./txt', './zip', 'txt.zip')
        while True:
            if not store_q.empty():
                data, book_name = store_q.get()
                if data == 'end':
                    print('存储进程接收通知然后将文件打包压缩，通过邮件发送出去，最后结束!')
                    z.files_to_zip()
                    send('410982322@qq.com', '小说合集', None, filelist=[z.output_path])
                    return
                out = output.get(book_name)
                if out is None:
                    out = DataOutput(*data)
                    output[book_name] = out
                    continue
                out.store_data(book_name, *data)
            else:
                time.sleep(0.1)


if __name__ == '__main__':
    # 初始化5个队列
    url_q = Queue()
    page_q = Queue()
    result_q = Queue()
    store_q = Queue()
    conn_q = Queue()

    # 创建分布式管理器
    node = NodeManager()
    manager = node.start_manager(url_q, page_q, result_q)

    # 创建URL管理器进程、数据提取进程和数据存储进程
    root_url = 'https://m.uctxt.com/index/type-7-1'
    url_manager_proc = Process(target=node.url_manager_proc, args=(url_q, page_q, conn_q, root_url))
    result_solve_proc = Process(target=node.result_solve_proc, args=(conn_q, store_q, result_q))
    store_proc = Process(target=node.store_proc, args=(store_q,))

    # 启动3个进程和分布式管理器
    url_manager_proc.start()
    result_solve_proc.start()
    store_proc.start()
    manager.get_server().serve_forever()
