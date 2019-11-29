import time

import pymysql


class DataOutput:

    def __init__(self):
        self.datas = []
        self._init_db()
        self.create_table('Qunar_hotel')
        self.date = time.strftime('%Y-%m-%d %X', time.localtime())

    def _init_db(self):
        '''
        初始化数据库连接
        '''
        self.con = pymysql.connect(host='localhost', user='root',
                                   password='111111', db='test', port=3306)
        self.cur = self.con.cursor()

    def _close(self):
        self.cur.close()
        self.con.close()

    def _re_init(self):
        try:
            self.cur.ping()
        except:
            self._init_db()

    def create_table(self, table_name):
        '''
        创建存储数据的表
        :params table_name: 创建的表名
        :return:
        '''
        values = '''
            date datetime comment "爬取时间",
            city varchar(255) comment "城市",
            hotel_name varchar(255) comment "酒店名称",
            hotel_score varchar(255) comment "酒店评分",
            hotel_address varchar(255) comment "酒店地址"
        '''

        self._re_init()

        try:
            r = self.cur.execute(
                'create table if not exists %s( %s )' % (table_name, values))
            self.table_name = table_name
            print('创建表: %s 成功！' % table_name)
        except Exception as e:
            print(e)
            print('创建表: %s 失败！' % table_name)
            self._close()
            raise

    def store_data(self, data):
        '''
        缓存数据，大于10条时存储到数据库中

        '''
        if data is None:
            return
        self.datas.append(data)
        if len(self.datas) >= 10:
            self.output_db(self.table_name)

    def store_datas(self, datas):
        '''
        缓存数据列表

        '''
        if datas is None or len(datas) == 0:
            return
        for data in datas:
            self.store_data(data)

    def output_db(self, table_name):
        '''
        保存数据到数据库
        '''
        sql = '''insert into %s
            (date, city, hotel_name, hotel_score, hotel_address)
            values(?, ?, ?, ?, ?)
        ''' % table_name

        self._re_init()

        try:

            for data in self.datas:
                # print(data)
                self.cur.execute(sql.replace('?', '%s'), (self.date,) + data)
            self.con.commit()
            self.datas.clear()
            print('成功插入10条记录!')
        except Exception as e:
            print(e)
            print('插入记录出现异常!')
            self.con.rollback()
            self._close()

    def output_end(self):
        if len(self.datas) > 0:
            self.output_db(self.table_name)
        self._close()


if __name__ == '__main__':
    output = DataOutput()
    data = (None, None, None, None)
    for i in range(10):
        output.store_data(data)
    del output
