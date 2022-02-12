# WebResourceGrabber

A crude python script to grab resources (fonts, images) from web pages.


For a given URL, this script scans the html for any referenced css files.
Any fonts and images that the css file mentions, are downloaded and placed in a folder named `out`.

## Fonts

Fonts are often times in the [WOFF](https://en.wikipedia.org/wiki/Web_Open_Font_Format) format.
There a numerous online converters to convert them to otf or ttf, or use [this](https://github.com/hanikesn/woff2otf) tool.