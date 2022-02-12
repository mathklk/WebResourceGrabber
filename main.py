import requests
from typing import *
from urllib.parse import urlparse
import re
import os

tprint = lambda x: print(f"[{type(x)}] {x}")


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


def getBulkPaths(url: str, paths: List[str]) -> List[str]:
    """
    Tries to get the contents of multiple paths ofa respective url

    :param url: ROOT-URL WITHOUT FOLLOWING SLASH
    :param cssPaths: any amount of sub-paths
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
                print(could_be_url, 'returned with status code <200> - seems to be a legit file')
                content_list.append(r.text)
            else:
                print(could_be_url, 'returned with status code', r.status_code)

        except ...:
            pass

    return content_list


def getUrlsFromCss(css: str) -> List[str]:
    pattern = 'url\\(\S*\\)'
    raws = re.findall(pattern, css)
    return [u[4:-1].strip('\"\'') for u in raws]


url = "https://www.iana.org/domains/reserved"

url_components = urlparse(url)
url_root: str = url_components.scheme + '://' + url_components.hostname
if url_components.port is not None:
    url_root += ':' + str(url_components.port)

css_paths = getCssPaths(url)
css_contents = getBulkPaths(url_root, css_paths)
css_mess = ''.join(css_contents)
urls_or_paths = getUrlsFromCss(css_mess)
absolute_res_urls = []
for url_or_path in urls_or_paths:
    isData = url_or_path.startswith('data:')
    if isData:
        continue
    elif 'http' in url_or_path:
        absolute_res_urls.append(url_or_path)
    else:
        absolute_res_urls.append(url_root + url_or_path)



if not os.path.exists('./out'):
    os.mkdir('./out')

for url in absolute_res_urls:
    assert 'http' in url
    foldername = url_components.hostname + url_components.path.replace('/', '_')
    if not os.path.exists('./out/' + foldername):
        os.mkdir('./out/' + foldername)

    filename = url.split('/')[-1]
    print('Getting', filename, '...')
    r = requests.get(url)
    data = r.content
    with open('./out/' + foldername + '/' + filename, 'wb+') as f:
        f.write(data)