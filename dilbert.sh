#! /usr/bin/env bash

date=$(date +"%Y-%m-%d")
image=$(curl -s https://dilbert.com/strip/"${date}" | \
	 grep og:image | \
	 sed -e 's/^.*content="//' -e 's/".*//')
curl -s -o /tmp/tmp.gif "${image}"
convert /tmp/tmp.gif -resize "${1}"x"${2}" /tmp/dilbert.gif
echo '${image /tmp/dilbert.gif -n}'
