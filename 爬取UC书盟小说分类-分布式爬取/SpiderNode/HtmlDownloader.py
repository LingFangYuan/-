import requests
import chardet


class HtmlDownloader:

    def download(self, url):
        if url is None:
            return None
        user_agent = 'NOKIA5700/UCWEB7.0.2.37/28/999'
        # user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = {'User-Agent': user_agent}
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            r.encoding = chardet.detect(r.content)['encoding']
            return r.text
        return None
