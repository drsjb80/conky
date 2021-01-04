import sys
import os.path
import urllib.request
from html.parser import HTMLParser
from datetime import date

# call only once a day

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            for attr in attrs:
                if attr[0] == 'property' and attr[1] == 'og:image':
                    urllib.request.urlretrieve(attrs[1][1], '/tmp/dilbert.gif')
                    sys.exit()
                            
url = 'https://dilbert.com/strip/' + date.today().strftime("%Y-%m-%d")
with urllib.request.urlopen(url) as response:
    parser = MyHTMLParser()
    parser.feed(str(response.read()))
