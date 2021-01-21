import sys
import os.path
import urllib.request
from html.parser import HTMLParser
from datetime import date
import imagesize

class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'meta':
            for attr in attrs:
                if attr[0] == 'property' and attr[1] == 'og:image':
                    urllib.request.urlretrieve(attrs[1][1], '/tmp/dilbert.gif')
                    width, height = imagesize.get("/tmp/dilbert.gif")
                    xscale = width / int(sys.argv[1])
                    yscale = height / int(sys.argv[2])
                    scale = xscale if xscale > yscale else yscale
                    # print('${{image /tmp/dilbert.gif -s {}x{}}}'.format(int(width/scale), int(height/scale)))

url = 'https://dilbert.com/strip/' + date.today().strftime("%Y-%m-%d")
with urllib.request.urlopen(url) as response:
    parser = MyHTMLParser()
    parser.feed(str(response.read()))
    print('fetched:', url, file=sys.stderr)
