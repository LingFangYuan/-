import os
import zipfile


class DataOutput:

    def __init__(self, name, author, intor):
        txt_path = './txt'
        self.path = os.path.join(txt_path, name + '.txt')
        # 文件夹不存在则创建
        if not os.path.exists(txt_path):
            os.makedirs(txt_path)
        # 输出小说头部信息
        self.store_head((name, author, intor))

    def output_data(self, data, flag='a'):
        '''
        输出内容到txt文本
        :param data: 内容
        :param flag: 输出模式：a 追加到末尾，w： 覆盖
        :return:
        '''
        if data is not None:
            with open(self.path, flag, encoding='utf-8') as f:
                f.write(data)
                f.write('\n' * 2)

    def store_head(self, headers):
        '''
        输出小说名称、作者、简介等信息到txt文本
        :param headers: 小说名称、作者、简介等信息
        :return:
        '''
        self.output_data('', 'w')
        for data in headers:
            self.output_data(data)
        self.output_data('')

    def store_data(self, book_name, title, data):
        '''
        输出章节内容到txt文本
        :param title: 章节名称
        :param data: 章节内容
        :return:
        '''
        print('正在保存 %s' % title)
        self.output_data(title)  # 输出章节名称
        self.output_data(data)  # 输出章节内容
        self.output_data('')


class ZipFiles:

    def __init__(self, input_path, zip_path, zip_name):
        self.input_path = input_path  # 源文件夹路径
        self.zip_path = zip_path  # zip目标文件夹路径
        self.zip_name = zip_name  # zip文件名称

    def files_to_zip(self):
        '''
        将文件夹打包压缩成zip
        :return:
        '''
        # 如果文件夹不存在则创建
        for d in [self.input_path, self.zip_path, self.zip_name]:
            if not os.path.exists(d):
                os.makedirs(d)
        # 拼接输出路径
        self.output_path = os.path.join(self.zip_path, self.zip_name).replace('\\', '/')
        with zipfile.ZipFile(self.output_path, 'w', zipfile.ZIP_DEFLATED) as f:
            # 待压缩文件列表
            filelists = []
            # 遍历源文件夹
            files_tuple = os.walk(self.input_path)
            for files in files_tuple:
                path = files[0].replace('\\', '/')
                for file in files[1:]:
                    if len(file) != 0:
                        # 拼接文件夹路径和文件名
                        filelists.append(os.path.join(path, file[0]).replace('\\', '/'))
            # 逐个文件打包
            for file in filelists:
                f.write(file)
        print('打包完成: %s !' % self.output_path)


if __name__ == '__main__':
    z = ZipFiles('../txt', '../zip', 'txt.zip')
    z.files_to_zip()
