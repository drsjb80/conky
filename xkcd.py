import sys
import os.path
import urllib.request
from html.parser import HTMLParser
from datetime import date
import imagesize

filename = '/tmp/xkcd.png'
class MyHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        if tag == 'meta' and attrs[0][1] == 'og:image':
            urllib.request.urlretrieve(attrs[1][1], filename)
            width, height = imagesize.get(filename)
            xscale = width / int(sys.argv[1])
            # print('xscale:', xscale, file=sys.stderr)
            yscale = height / int(sys.argv[2])
            # print('yscale:', yscale, file=sys.stderr)
            scale = xscale if xscale > yscale else yscale
            # print('scale:', scale, file=sys.stderr)
            # print(int(width/scale), file=sys.stderr)
            # print(int(height/scale), file=sys.stderr)
            print('${{image {} -s {}x{}}}'.format(filename, 
                int(width/scale), int(height/scale)))
            sys.exit(0)

with urllib.request.urlopen('https://xkcd.com/') as response:
    # print('XKCDing', file=sys.stderr)
    parser = MyHTMLParser()
    parser.feed(str(response.read()))

