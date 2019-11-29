import time

from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from DataOutput import DataOutput
from HtmlParser import HtmlParser


class QunaSpider:

    def __init__(self):
        self.parser = HtmlParser()
        self.output = DataOutput()

    def crawl(self, root_url, city, from_date, to_date):
        '''
        爬虫入口
        :param root_url: 基础URL
        :param city: 城市
        :param from_date: 入住日期
        :param to_date: 离开日期
        :return:
        '''
        try:
            # 初始化浏览器 - 无头模式
            options = webdriver.FirefoxOptions()
            options.add_argument('-headless')
            driver = webdriver.Firefox(options=options)

            # 打开网页
            driver.get(root_url)
            self.get_hotel(driver, city, from_date, to_date)
        finally:
            driver.close()
            self.output.output_end()

    def get_hotel(self, driver, city, from_date, to_date):
        '''
        开始爬取酒店信息
        :param driver: 浏览器驱动程序
        :param city: 城市
        :param from_date: 入住日期
        :param to_date: 离开日期
        :return:
        '''
        # 获取元素
        ele_toCity = driver.find_element_by_id('toCity')
        ele_fromDate = driver.find_element_by_id('fromDate')
        ele_toDate = driver.find_element_by_id('toDate')
        ele_search_btn = driver.find_element_by_class_name('search-btn')

        # 填入搜索信息
        # 填入城市
        ele_toCity.clear()
        ele_toCity.send_keys(city)
        ele_toCity.click()

        # 填入入住日期
        ele_fromDate.clear()
        ele_fromDate.send_keys(from_date)

        # 填入离开日期
        ele_toDate.clear()
        ele_toDate.send_keys(to_date)

        # 点击搜索按钮
        ele_search_btn.click()
        num = 0
        while True:
            try:
                WebDriverWait(driver, 10).until(EC.title_contains(city))
            except Exception as e:
                print(e)
                break

            # 滚动窗口到底部
            js = "window.scrollTo(0, document.body.scrollHeight);"
            driver.execute_script(js)
            time.sleep(4)

            # 获取网页内容
            try:
                # 跳过不能获取内容的异常页面
                html_cont = driver.page_source
                datas = self.parser.parser(city, html_cont)
                self.output.store_datas(datas)
                num += 1
                print('第 %s 页完成' % num)
            except Exception as e:
                print(e)
                continue

            try:
                next_page = WebDriverWait(driver, 10).until(
                    EC.visibility_of(driver.find_element_by_css_selector('.item.next'))
                )
                next_page.click()
                time.sleep(4)
            except Exception as e:
                print(e)
                break


if __name__ == '__main__':
    spider = QunaSpider()
    spider.crawl('http://hotel.qunar.com/', '广州', '2019-11-23', '2019-11-25')
