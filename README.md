Some conky scripts that I wrote. Requires [Imagemagick](https://imagemagick.org/)

* nws.{conf,py} displays a forecast that looks like ![Image of NWS](https://github.com/drsjb80/conky/blob/main/NWS.png)
* nwsmap.{conf,sh} displays the current NWS US map  a forecast that looks like ![Image of NWS](https://github.com/drsjb80/conky/blob/main/NWSMap.png)
* dilbert.{conf,sh} displays the most recent Dilbert comic
* xkcd.{conf,sh} displays the most recent XKCD comic
* moon.{conf,sh} displays the phase of the moon and the number of days old it is

To run:

    conky -dc dilbert.conf
    conky -dc xkcd.conf
    conky -dc nwsmap.conf
    conky -dc nws.conf

<!--
vim: wm=0
-->
