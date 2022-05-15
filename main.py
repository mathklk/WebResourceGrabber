#!/usr/bin/python3
import argparse
import requests
from typing import *
from urllib.parse import urlparse
import re
import os
import base64
import hashlib


def getCssPaths(url: str) -> List[str]:
    """
    Get a list of all could-be css urls from a web page

    :param url: the url to a web page
    :return:
    """
    r = requests.get(url).text

    # extract all lines from the html that contain ".css"
    stylesheet_lines = []
    for head_line in r.split('\n'):
        if '.css' in head_line:
            stylesheet_lines.append(head_line.strip())

    # extract all paths from the lines (e.g. "/_css/2022/iana_website.css")
    css_paths = []
    for stylesheet_line in stylesheet_lines:
        for word in stylesheet_line.split('\"'):
            if '.css' in word:
                css_paths.append(word)

    return css_paths


def getBulkPaths(url: str, paths: Iterable[str]) -> List[str]:
    """
    Tries to get the contents of multiple paths of a respective url

    :param url: ROOT-URL WITHOUT FOLLOWING SLASH
    :param paths: any amount of sub-paths
    :return:
    """

    content_list = []
    for path in paths:
        try:
            if path.startswith('http'):
                could_be_url = path
            else:
                if not path.startswith('/'):
                    path = '/' + path
                could_be_url = url_root + path
            r = requests.get(could_be_url)
            if r.status_code == 200:
                print('\t', could_be_url, 'returned with status code <200> - seems to be a legit file')
                content_list.append(r.text)
            else:
                print('\t', could_be_url, 'returned with status code', r.status_code)

        except ...:
            pass

    return content_list


def getUrlsFromCss(css: str) -> List[str]:
    pattern = 'url\\(\S*\\)'
    raws = re.findall(pattern, css)
    return [u[4:-1].strip('\"\'') for u in raws]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", nargs=1)
    args = parser.parse_args()
    url = args.url[0]
    url_components = urlparse(url)
    assert url_components.scheme
    assert url_components.hostname
    url_root: str = url_components.scheme + '://' + url_components.hostname
    if url_components.port is not None:
        url_root += ':' + str(url_components.port)

    css_paths = getCssPaths(url)
    css_paths = set(css_paths)  # filter duplicates
    css_contents = getBulkPaths(url_root, css_paths)
    css_mess = ''.join(css_contents)
    urls_or_paths = getUrlsFromCss(css_mess)

    b64_datas = []
    absolute_res_urls = []
    for url_or_path in urls_or_paths:
        isData = url_or_path.startswith('data:')
        if isData:  # Content is b64 (probably) data
            b64_datas.append(url_or_path)
        elif 'http' in url_or_path:  # Resource is an absolute path
            absolute_res_urls.append(url_or_path)
        else:  # Resource is a relative path
            absolute_res_urls.append(url_root + url_or_path)

    if not os.path.exists('./out'):
        os.mkdir('./out')

    foldername = url_components.hostname + url_components.path.replace('/', '_')
    subdir = './out/' + foldername
    if not os.path.exists(subdir):
        os.mkdir(subdir)

    print('Processing web resources..')
    if not absolute_res_urls:
        print('\tNo resources referenced via urls, skipping.')
    for url in absolute_res_urls:
        assert url.startswith('http')
        filename = url.split('/')[-1]
        print('Getting', filename, '..')
        r = requests.get(url)
        data = r.content
        dest = subdir + '/' + filename
        with open(dest, 'wb+') as f:
            f.write(data)
        print('\tExported', dest)

    print('Processing data resources..')
    if not b64_datas:
        print('\tNo embedded b64 data, skipping.')
    for d in b64_datas:
        if 'base64' not in d or 'image/png' not in d:
            continue
        filetype = d.split(';')[0].split('/')[-1]  # syntax assumed from image/png file
        b64str = d.split(',')[-1]
        print('\td  :: ' + d)
        print('\tb64:: ' + b64str)
        bytedata = base64.b64decode(b64str)
        filename = hashlib.sha1(bytedata).hexdigest()  # use sha sum of content as filename because why not
        file = subdir + '/' + filename + '.' + filetype
        with open(file, 'wb+') as f:
            f.write(bytedata)
        print('\tExported', file)
