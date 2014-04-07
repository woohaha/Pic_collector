#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from lxml import etree
from bs4 import BeautifulSoup
import os
import glob
import sys
import concurrent.futures
import re


global header
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'}


class find_cl_img:

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(
            requests.get(url, headers=header
                         ).content.decode('gbk', 'ignore'))

        self.article_name = self.__soup.h4.string

        self.img_addr = [x['src']
                         for x in
                         self.__soup.find_all('input', type="image")]


class find_163_img:

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.find_all('meta')[2]['content'] \
            .replace(' ', '_').replace('<', '[').replace('>', ']')
        self.img_addr = [x['data-lazyload-src']
                         for x in
                         self.__soup.find_all('img',
                                              src='http://r.ph.126.net/image/sniff.png')]
        # self.images = dict(zip(self.label, self.img_addr))

class find_poco_img:

    def __init__(self, url):
        self.url=url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.find('h1','mt10').text.strip(' ').replace(' ','_')
        patten=re.compile(r"photoImgArr\[\d+\]\.orgimg = \'(.*?)\';")
        script=self.__soup.find_all('script')

        self.img_addr=re.findall(patten,script[15].text)


def MT_download(download_dir, img_addrs, classified):
    def download(img_addr, img_index):

        PATH = ''.join((classified_PATH,
                        str(img_index + 1).zfill(2), '_',
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
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:'
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futureIteams = {executor.submit(
            download, item, img_addrs.index(item)): item for item in img_addrs}
        for future in concurrent.futures.as_completed(futureIteams):
            url = futureIteams[future]
            try:
                data = future.result()
            except Exception as exc:
                print('{} generated an exception: {}'.format(url, exc))

    print('All images are downloaded at {}'.format(classified_PATH))


def download_queue(download_dir, img_addrs, classified):
    classified_PATH = ''.join((download_dir, classified, '/'))
    To_be_down = len(img_addrs)
    downloading = To_be_down
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:'
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    for image in img_addrs:
        PATH = ''.join((classified_PATH,
                        str(img_addrs.index(image) + 1).zfill(2), '_',
                        os.path.basename(image)))
        try:
            r = requests.get(image, headers=header, stream=True)
        except:
            raise Exception('Image is unreachable')
        if r.ok:
            with open(PATH, 'wb') as f:
                for chunk in r.iter_content():
                    f.write(chunk)
            print('Remain {}/{}'.format(downloading, To_be_down), end='\r')
            downloading -= 1
    print('Complete. {} Pics downloaded at {}'.format(
        To_be_down, classified_PATH))


def mkindex(download_dir, classifed=''):
    head = '''<html xmlns="http://www.w3.org/1999/xhtml" lang="cn" xml:lang="cn">
    <head><title>Thumb</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    </head><body>'''
    tail = '''</body></html>'''
    with open(download_dir + classifed + '/index.html', 'w')as htm:
        htm.write(head)
        imgs = glob.glob(download_dir + classifed + '/*.jpg')
        for img in imgs:
            htm.write('''<a href={0}>
                      <img src={0} width=100/></a>'''.format(img.split('/')[-1]))
        htm.write(tail)

# TODO 自动生成gallery

try:
    url = sys.argv[1]
except:
    url = input('Album Address: ')

if 'cl' in url.split('/')[2]:
    img = find_cl_img(url)
    download_dir = os.path.expanduser('~') + '/lll/'
elif '163' in url.split('/')[2]:
    img = find_163_img(url)
    download_dir = os.path.expanduser('~') + '/163/'
elif 'poco' in url.split('/')[2]:
    img = find_poco_img(url)
    download_dir = os.path.expanduser('~') + '/poco/'

# print(img.img_addr)
# download_queue(download_dir, img.img_addr, img.article_name)
MT_download(download_dir, img.img_addr, img.article_name)
mkindex(download_dir, img.article_name)
