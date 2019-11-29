import pickle
import hashlib


class UrlManager:

    def __init__(self):
        self.new_urls_names = self.load_progress('new_urls_names.txt')  # 未爬取URL集合
        self.old_urls = self.load_progress('old_urls.txt')  # 已爬取URL集合
        self.old_names = self.load_progress('old_names.txt')  # 已爬取的小说名称集合

    def has_new(self):
        '''
        判断是否有未爬取的URL
        :return:
        '''
        return self.new_size() != 0

    def get_new(self):
        '''
        获取一个未爬取的URL和小说名称
        :return: URL和小说名称的集合
        '''
        if not self.has_new():
            return
        new_url, new_name = self.new_urls_names.pop()
        m_url = hashlib.md5()
        m_name = hashlib.md5()
        m_url.update(new_url.encode(encoding='utf-8'))
        m_name.update(new_name.encode(encoding='utf-8'))
        self.old_urls.add(m_url.hexdigest()[8:-8])
        self.old_names.add(m_name.hexdigest()[8:-8])

        return new_url, new_name

    def add_new(self, new):
        '''
        将新的URL和小说名称添加到未爬取的集合
        :param new: 单个URL与小说名称的集合
        :return:
        '''
        url, name = new
        if url is None or name is None:
            return
        m_url = hashlib.md5()
        m_name = hashlib.md5()
        m_url.update(url.encode(encoding='utf-8'))
        m_name.update(name.encode(encoding='utf-8'))
        url_md5 = m_url.hexdigest()[8:-8]
        name_md5 = m_name.hexdigest()[8:-8]
        if (url, name) not in self.new_urls_names and url_md5 not in self.old_urls and \
                                name_md5 not in self.old_names:
            self.new_urls_names.add((url, name))

    def add_news(self, news):
        '''
        将新的URL添加到未爬取的URL集合
        :param urls: URL集合
        :return:
        '''
        if news is None and len(news) == 0:
            return
        for new in news:
            self.add_new(new)

    def new_size(self):
        '''
        获取未爬取URL集合的大小
        :return:
        '''
        return len(self.new_urls_names)

    def old_size(self):
        '''
        获取已爬取URL集合的大小
        :return:
        '''
        return len(self.old_urls)

    def save_progress(self, path, data):
        '''
        保存进度
        :param path: 文件路径
        :param data: 数据
        :return:
        '''
        with open(path, 'wb') as f:
            pickle.dump(data, f)

    def load_progress(self, path):
        '''
        从本地文件加载进度
        :param path: 文件路径
        :return: 返回set集合
        '''
        print('[+] 从文件加载进度: %s' % path)
        try:
            with open(path, 'rb') as f:
                tmp = pickle.load(f)
                return tmp
        except:
            print('[!] 无进度文件， 创建: %s' % path)
        return set()
