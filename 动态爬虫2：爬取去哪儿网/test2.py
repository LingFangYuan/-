import time

from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

# 初始化浏览器
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(options=options)
try:
    driver.get(
        'https://hotel.qunar.com/city/guangzhou/#fromDate=2019-11-21&bs=&bc=%E5%B9%BF%E5%B7%9E&QHFP=ZSL_A3AD1D22&cityurl=guangzhou&toDate=2019-11-22&from=hotellist')

    # driver.find_element_by_tag_name('body').send_keys(Keys.END)
    # time.sleep(1)

    # # js = "window.scrollTo(0, document.body.scrollHeight);"
    # # driver.execute_script(js)

    # time.sleep(5)
    print(driver.page_source)
finally:
    driver.close()