from bs4 import BeautifulSoup


soup = BeautifulSoup(open('test.html', encoding='utf-8'), 'lxml')
infos = soup.find_all(class_='item_hotel_info')
for info in infos:
    hotel_title = info.find('span', class_='hotel_item').find('a').get_text()
    address = info.find('span', class_='area_contair').get_text()
    score = info.find('p', class_='score').get_text()

next_page = soup.select_one('.item.next')
print(next_page)