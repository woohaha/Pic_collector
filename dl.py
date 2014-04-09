#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
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
    '''
    例：http://cl.man.lv/....
    '''

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(
            requests.get(url, headers=header
                         ).content.decode('gbk', 'ignore'))

        self.article_name = self.__soup.h4.string

        self.img_addr = [x['src']
                         for x in
                         self.__soup.find_all('input', type="image")]


class find_flickr_img:
    '''
    例：https://www.flickr.com/photos/astiya/sets/72157642803390374
    '''

    def __init__(self, url):
        self.url=url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name=self.__soup.h1.string

        self.img_addr=[]
        #self.img_addr=[re.sub(r'\.jpg','_b.jpg',x['data-defer-src']) for x in self.__soup.find_all('img','pc_img')]
        def get_img(url):
            soup=BeautifulSoup(requests.get(url, headers=header).content)
            for x in soup.find_all('img','pc_img'):
                self.img_addr.append(re.sub(r'\.jpg','_b.jpg',x['data-defer-src']))

            try:
                href_nextpage=soup.find('a','Next rapidnofollow')['href']
                nextpage='https://www.flickr.com'+href_nextpage
                get_img(nextpage)
            except:
                pass

        get_img(self.url)


class find_163_img:
    '''
    例：http://pp.163.com/superbunny/pp/12307173.html
    '''

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
    '''
    例：http://my.poco.cn/lastphoto_v2.htx&id=3654521&user_id=54967495&p=0&temp=1182
    '''

    def __init__(self, url):
        self.url = url
        page = requests.get(url, headers=header)
        self.__soup = BeautifulSoup(page.content)

        self.article_name = self.__soup.find(
            'h1', 'mt10').text.strip(' ').replace(' ', '_')
        pattern = re.compile(r"photoImgArr\[\d+\]\.orgimg = \'(.*?)\';")

        self.img_addr = re.findall(pattern, page.text)


class find_meizitu_img:
    '''
    例：http://www.meizitu.com/a/4154.html
    '''

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.find_all(
            'h2')[1].find('a').text.replace(' ', '_')
        self.img_addr = [x['src']
                         for x in self.__soup.find('div', id='picture').find_all('img')]


class find_curator_img:
    '''
    例：http://curator.im/girl_of_the_day/2014-04-08/
    '''

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.h1.text.strip(
            ' ').replace(' ', '_') + '_' + self.url.split('/')[-2]
        self.img_addr = [
            'http://' + x['src'].split('/', 11)[-1] for x in self.__soup.find_all('img', 'god')]
        self.img_addr.insert(
            0, 'http://' + self.__soup.find('img', 'profile_image')['src'].split('/', 5)[-1])


def MT_download(download_dir, img_addrs, classified, workers=10):
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
            print('{} Finished'.format(img_addr), end='\r')

    classified_PATH = ''.join((download_dir, classified, '/'))
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, Overwrite?[Y/n]:'
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0)

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futureIteams = {executor.submit(
            download, item, img_addrs.index(item)): item for item in img_addrs}
        for future in concurrent.futures.as_completed(futureIteams):
            url = futureIteams[future]
            try:
                data = future.result()
            except Exception as exc:
                print('{} generated an exception: {}'.format(url, exc))

    print('{} images downloaded at {}'.format(
        len(os.listdir(classified_PATH)), classified_PATH))


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
elif 'meizitu' in url.split('/')[2]:
    img = find_meizitu_img(url)
    download_dir = os.path.expanduser('~') + '/meizitu/'
elif 'curator' in url.split('/')[2]:
    img = find_curator_img(url)
    download_dir = os.path.expanduser('~') + '/curator/'
elif 'flickr' in url.split('/')[2]:
    img = find_flickr_img(url)
    download_dir = os.path.expanduser('~') + '/flickr/'
else:
    print('No pattern found.')
    sys.exit(1)

# download_queue(download_dir, img.img_addr, img.article_name)
#print(download_dir+'\n'+ str(len(img.img_addr))+'\n'+ img.article_name)
MT_download(download_dir, img.img_addr, img.article_name)
mkindex(download_dir, img.article_name)
