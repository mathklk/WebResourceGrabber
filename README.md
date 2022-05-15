# WebResourceGrabber

A crude python script to grab resources (fonts, images) from web pages.

For a given URL, this script scans the html for any referenced css files.
Any fonts and images that the css file mentions, are downloaded and placed in a folder named `out`.

## Usage

```shell script
./main.py https://www.example.com
```

You should verify that the exported files are correctly formatted.
The command line utility `file` is perfect for this.
cd into the generated subdirectory and type `file *`.
If it says "empty", "ascii text" or "html document" for any of the files, then there was likely an error for that particular file.

## Fonts

Fonts are often times in the [WOFF](https://en.wikipedia.org/wiki/Web_Open_Font_Format) format.
There a numerous online converters to convert them to otf or ttf, or use [this](https://github.com/hanikesn/woff2otf) tool.

## Images

Only works for PNG images at the moment.

## Does it actually work?

Meh.

It depends largely on which web page you scan.
This program does not have all the functionality that a web browser has (it does not have javascript).
On modern web pages it will probably miss a lot of resources.

This program is unbelievably sketchy and botched together. 
It's safe to say you should not use it for serious purposes or even look at the source code.
