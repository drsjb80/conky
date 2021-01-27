#! /usr/bin/env bash

rm -f /tmp/tmp.png /tmp/xkcd.png
image=$(curl -s https://xkcd.com/ | \
		grep og:image | \
		sed -e 's/^.*content="//' -e 's/".*//')
curl -s -o /tmp/tmp.png "${image}"
convert /tmp/tmp.png -resize "${1}"x"${2}" /tmp/xkcd.png
echo '${image /tmp/xkcd.png -n}'
