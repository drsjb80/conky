#! /usr/bin/env bash

curl -s -o /tmp/$$ https://www.moongiant.com/phase/today/

image=$(grep 'div id="todayMoonContainer"' < /tmp/$$ | \
    sed -e 's/.*src="//' -e 's/".*//' -e 's,^,https://www.moongiant.com,')

curl -s -o "/tmp/$$.jpg" "${image}"
convert "/tmp/$$.jpg" -modulate 120 /tmp/moon.jpg
echo '${image /tmp/moon.jpg -n}'

age=$(grep "Moon Age" < /tmp/$$  | 
    sed -e 's/^  *//' -e 's,<span>,,g' -e 's,</span>,,g' -e 's,<br>,,')
echo '${alignc}${color1}'"${age}"

rm /tmp/$$ /tmp/$$.jpg
