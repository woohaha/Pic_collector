#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import glob
import sys


global header
header = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'}
class find_cl_img:
    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(
            requests.get(url, headers=header
                         ).content.decode('gbk', 'ignore'))

        self.article_name = self.__soup.h4.string

        self.img_addr = [x['src'] \
                         for x in \
                         self.__soup.find_all('input', type="image")]

class find_163_img:

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.find_all('meta')[2]['content'].replace(' ', '_')
        self.img_addr = [x['data-lazyload-src'] \
                    for x in \
                    self.__soup.find_all('img', \
                                         src = 'http://r.ph.126.net/image/sniff.png')]
        # self.images = dict(zip(self.label, self.img_addr))


def download_imgs(download_dir,img_addr,classified):
    # make_index=True
    classified_PATH=''.join((download_dir,classified,'/'))
    To_be_down=len(img_addr)
    downloading=To_be_down
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:' \
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    for image in img_addr:
        PATH = ''.join((classified_PATH, \
                        str(img_addr.index(image) + 1), '_', \
                        os.path.basename(image)))
        try:
            r = requests.get(image, headers=header, stream=True)
        except:
            raise Exception('Image is unreachable')
        if r.ok:
            with open(PATH, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            print('Downloading {}/{}'.format(downloading,To_be_down), end='\r')
            downloading-=1
    print('Complete. {} Pics downloaded at {}'.format(To_be_down,classified_PATH))

# TODO 自动生成gallery
# TODO 多线程下载

try:
    url = sys.argv[1]
except:
    url = input('Album Address: ')

if 'cl' in url.split('/')[2]:
    img = find_cl_img(url)
    download_dir = os.path.expanduser('~') + '/lll/'
else:
    img = find_163_img(url)
    download_dir = os.path.expanduser('~') + '/163/'

# print(img.img_addr)
download_imgs(download_dir, img.img_addr, img.article_name)
