import sys
import os.path
import urllib.request
from html.parser import HTMLParser
from datetime import date
import imagesize

# call only once a day

filename = '/tmp/xkcd.png'
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and attrs[0][1] == 'og:image':
            urllib.request.urlretrieve(attrs[1][1], filename)
            width, height = imagesize.get(filename)
            xscale = width / 450
            yscale = height / 450
            scale = xscacle if xscale > yscale else yscale
            print('${{image {} -s {}x{}}}'.format(filename, 
                int(width/scale), int(height/scale)))
            sys.exit()

with urllib.request.urlopen('https://xkcd.com/') as response:
    print('XKCDing', file=sys.stderr)
    parser = MyHTMLParser()
    parser.feed(str(response.read()))

