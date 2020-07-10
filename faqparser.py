#!/usr/bin/env python3
from html.parser import HTMLParser
from urllib.request import urlopen

url = 'https://www.wpi.edu/we-are-wpi/frequently-asked-questions'


class FAQParser(HTMLParser):
    def error(self, message):
        pass

    def __init__(self):
        super().__init__()
        self.flag = 0
        self.data = []

    def handle_starttag(self, tag, attrs):
        # print("Encountered a start tag:", tag, attrs)
        if tag == "div":
            # print(tag,attrs)
            if len(attrs) and "pane-content" in attrs[0] and self.flag >= 0:
                self.flag += 1
                # print("flipped")
            if len(attrs) and "l-footer row" in attrs[0]:
                self.flag = -1
                # print("flipped")

    def handle_data(self, data):
        if self.flag > 0:
            if not all([i.isspace() for i in data]):
                tmp = ""
                for i in data:
                    if i.isalnum() or i == " ":
                        tmp += i
                tmp += '\n'
                self.data.append(tmp)
                # print("Encountered some data  :", tmp)


if __name__ == "__main__":
    response = urlopen(url)
    if response.getheader('Content-Type').split(";")[0] == 'text/html':
        html_bytes = response.read()
        html_string = html_bytes.decode("utf-8")
        parser = FAQParser()
        parser.feed(html_string)
        with open("current.html", "w+") as f:
            f.writelines(parser.data)
