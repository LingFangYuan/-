import re


def translation(url):
    transtable = {'http://www.paoshuba.cc/Partlist/': [('source', 'http://m.xpaoshuba.cc/wapbook/'),
                                                       (r'(\d+)/(\d+)\.shtml', r'\1_\2.html')]}

    for key, value in transtable.items():
        if url.startswith(key):
            for p, r in value:
                if p == 'source':
                    p = key
                url = re.sub(p, r, url)
    return url


def take_first(l):
    if len(l) >= 1:
        return l[0]
    else:
        return None


def my_strip(l):
    if l:
        return [s.strip('：') for s in l]


def deutf8Str(t):
    if t:
        r = []
        for i in t:
            r.append(chr(1 ^ ord(i)))
        return ''.join(r)
