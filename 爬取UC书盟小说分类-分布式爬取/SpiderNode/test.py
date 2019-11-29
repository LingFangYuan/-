import re
from urllib.request import urljoin

import chardet
import requests
from bs4 import BeautifulSoup

root_url = 'https://m.uctxt.com/index/type-7-1'
soup = BeautifulSoup(open('test.html', encoding='utf-8'), 'lxml')
urls = []
details = soup.find('div', class_='details clrfix')
if details is not None:
    item_list = details.find('ul', class_='item-list clrfix').find_all('a', href=re.compile(r'/book/.*'))
    next_page = details.find('div', class_='pages').find('a', class_='next').get('href')
    next_page = None if next_page is None else urljoin(root_url, next_page)
for item in item_list:
    url = item.get('href')
    full_url = urljoin(root_url, url)
    book_name = item.get_text()
    if full_url is not None and book_name is not None:
        urls.append((full_url, book_name))
print(urls, next_page)

# user_agent = 'NOKIA5700/UCWEB7.0.2.37/28/999'
# headers = {'User-Agent': user_agent}
# r = requests.get('https://m.uctxt.com/index/type-7-1', headers=headers)
# r.encoding = chardet.detect(r.content)['encoding']
# with open('test.html', 'w', encoding='utf-8') as f:
#     f.write(r.text)
