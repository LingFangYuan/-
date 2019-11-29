import os


class DataOutput:

    def __init__(self, name, author, intor):
        dir = './txt'
        self.path = os.path.join(dir, name + '.txt')
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.store_head((name, author, intor))

    def output_data(self, data, flag='a'):
        if data is not None:
            with open(self.path, flag, encoding='utf-8') as f:
                f.write(data)
                f.write('\n' * 2)

    def store_head(self, headers):
        self.output_data('', 'w')
        for data in headers:
            self.output_data(data)
        self.output_data('')

    def store_data(self, title, data):
        print('正在保存 %s' % title)
        self.output_data(title)
        self.output_data(data)
        self.output_data('')

    def zip_files(self):
        pass
