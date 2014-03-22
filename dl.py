#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from lxml import etree
from bs4 import BeautifulSoup
import os
import glob
import sys
import concurrent.futures


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

        self.article_name = self.__soup.find_all('meta')[2]['content'] \
            .replace(' ', '_').replace('<', '[').replace('>', ']')
        self.img_addr = [x['data-lazyload-src'] \
                    for x in \
                    self.__soup.find_all('img', \
                                         src = 'http://r.ph.126.net/image/sniff.png')]
        # self.images = dict(zip(self.label, self.img_addr))


def MT_download(download_dir, img_addrs, classified):
    def download(img_addr, img_index):

        PATH = ''.join((classified_PATH, \
                        str(img_index + 1).zfill(2), '_', \
                        os.path.basename(img_addr)))
        try:
            r = requests.get(img_addr, headers=header, stream=True)
        except:
            raise Exception('Image is unreachable')
        if r.ok:
            with open(PATH, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            print('{} Finished'.format(img_addr))

    classified_PATH = ''.join((download_dir, classified, '/'))
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:' \
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futureIteams = {executor.submit(download, item, img_addrs.index(item)): item for item in img_addrs}
        for future in concurrent.futures.as_completed(futureIteams):
            url = futureIteams[future]
            try:
                data = future.result()
            except Exception as exc:
                print('{} generated an exception: {}'.format(url, exc))

    print('All images are downloaded at {}'.format(classified_PATH))


def download_queue(download_dir, img_addrs, classified):
    classified_PATH=''.join((download_dir,classified,'/'))
    To_be_down = len(img_addrs)
    downloading=To_be_down
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:' \
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    for image in img_addrs:
        PATH = ''.join((classified_PATH, \
                        str(img_addrs.index(image) + 1).zfill(2), '_', \
                        os.path.basename(image)))
        try:
            r = requests.get(image, headers=header, stream=True)
        except:
            raise Exception('Image is unreachable')
        if r.ok:
            with open(PATH, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            print('Remain {}/{}'.format(downloading,To_be_down), end='\r')
            downloading-=1
    print('Complete. {} Pics downloaded at {}'.format(To_be_down,classified_PATH))

def mkindex(download_dir, classifed=''):
    imgs = glob.glob(download_dir + classifed + '/*')
    imgs.sort()
    page = etree.Element('html')
    doc = etree.ElementTree(page)
    headElt = etree.SubElement(page, 'head')
    bodyElt = etree.SubElement(page, 'body')
    titleElt = etree.SubElement(headElt, 'title')
    titleElt.text = classifed
    for img in imgs:
        imgElt = etree.SubElement(bodyElt, 'img', src=os.path.basename(img))
        brElt = etree.SubElement(bodyElt,'br')
        brElt = etree.SubElement(bodyElt,'br')
    with open(download_dir + classifed + '/index.html', 'wb')as f:
        doc.write(f)

# TODO 自动生成gallery

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
# download_queue(download_dir, img.img_addr, img.article_name)
MT_download(download_dir, img.img_addr, img.article_name)
mkindex(download_dir,img.article_name)
