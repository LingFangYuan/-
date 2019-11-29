from bs4 import BeautifulSoup


class HtmlParser:

    def parser(self, city, content):
        soup = BeautifulSoup(content, 'lxml')
        infos = soup.find_all(class_='item_hotel_info')
        datas = []
        for info in infos:
            hotel_title = info.find('span', class_='hotel_item').find('a').get_text()
            address = info.find('span', class_='area_contair').get_text().strip().lstrip('位于')
            score = info.find('p', class_='score')
            score = score.get_text() if score is not None else '暂无评分'
            datas.append((city, hotel_title, score, address))
        return datas


if __name__ == '__main__':
    parser = HtmlParser()
    datas = parser.parser(open('test.html', encoding='utf-8'))
    print(datas)
