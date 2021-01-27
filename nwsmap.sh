#! /usr/bin/env bash

rm -rf /tmp/noaa.gif /tmp/noaa.png
curl -s -o /tmp/noaa.gif https://www.wpc.ncep.noaa.gov/noaa/noaa.gif
convert /tmp/noaa.gif /tmp/noaa.png
echo '${image /tmp/noaa.png -n}'
