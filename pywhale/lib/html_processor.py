import re
from bs4 import BeautifulSoup


class HTMLBody:
    body = None
    ctype = None
    parsed = None
    links = [

    ]

    images = [

    ]
    _seen_links = []

    def __init__(self, body, content_type="text/html"):
        self.body = body
        self.ctype = content_type
        if self.try_parse():
            self.extract()

    def try_parse(self):
        try:
            self.parsed = BeautifulSoup(self.body, features="lxml")
            return True
        except:
            return False

    def extract(self):
        if not self.parsed:
            return None
        self.links = []
        self.images = []
        for link_element in self.parsed.find_all('a', attrs={'href': True}):
            link_href = link_element.attrs['href'].strip()
            link_text = link_element.text.strip()
            if link_href not in self._seen_links:
                self.links.append({'href': link_href, 'text': link_text})
                self._seen_links.append(link_href)

        for img_element in self.parsed.find_all('img', attrs={'src': True}):
            img_href = img_element.attrs['src'].strip()
            self.images.append(img_href)
        return
