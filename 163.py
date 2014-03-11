#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import glob
import sys


class find_163_img:

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url).content)

        self.article_name = self.__soup.find_all('meta')[2]['content'].replace(' ', '_')
        self.img_addr = [x['data-lazyload-src'] \
                    for x in \
                    self.__soup.find_all('img', \
                                         src = 'http://r.ph.126.net/image/sniff.png')]
        self.label = [x.get_text() \
                      for x in \
                      self.__soup.find_all('p', 'pic-index')]
        self.images = dict(zip(self.label, self.img_addr))

# TODO 增加下载cl的类
def download_imgs(download_dir,img_addr,img_label,classified):
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

    for image_index in range(len(img_addr)):
        PATH = ''.join((classified_PATH, \
                        img_label[image_index], '_', \
                        os.path.basename(img_addr[image_index])))
        r=requests.get(img_addr[image_index], stream=True)
        if r.status_code==200:
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
img_163 = find_163_img(url)
download_dir='d:/163/'
download_imgs(download_dir,img_163.img_addr,img_163.label,img_163.article_name)
