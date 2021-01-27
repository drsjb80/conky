#! /usr/bin/env bash

curl -s -o $$ https://www.moongiant.com/phase/today/

image=$(grep 'div id="todayMoonContainer"' < $$ | \
    sed -e 's/.*src="//' -e 's/".*//' -e 's,^,https://www.moongiant.com,')

curl -s -o /tmp/moon.jpg ${image}
echo '${image /tmp/moon.jpg -f}'

age=$(grep "Moon Age" < $$  | 
    sed -e 's/^  *//' -e 's,<span>,,g' -e 's,</span>,,g' -e 's,<br>,,')
echo '${alignc}'${age}

