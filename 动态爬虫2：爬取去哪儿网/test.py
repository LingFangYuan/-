import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# 初始化浏览器
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)
driver.get('http://hotel.qunar.com/')

# 获取元素
ele_toCity = driver.find_element_by_id('toCity')
ele_fromDate = driver.find_element_by_id('fromDate')
ele_toDate = driver.find_element_by_id('toDate')
ele_search_btn = driver.find_element_by_class_name('search-btn')

# 填入信息
ele_toCity.clear()
ele_toCity.send_keys('上海')
ele_toCity.click()
ele_fromDate.clear()
ele_fromDate.send_keys('2019-11-22')
ele_toDate.clear()
ele_toDate.send_keys('2019-11-25')

# 点击搜索按钮
ele_search_btn.click()

try:
    WebDriverWait(driver, 10).until(EC.title_contains('上海'))
except Exception as e:
    print(e)
time.sleep(5)

js = "window.scrollTo(0, document.body.scrollHeight);"
driver.execute_script(js)
time.sleep(5)

html_cont = driver.page_source
driver.close()
with open('test.html', 'w', encoding='utf-8') as f:
    f.write(html_cont)
