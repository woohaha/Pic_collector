#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
import glob
import sys
import concurrent.futures
import re
import json


# initial
failed = set() # 聲明下載下載失敗的圖片集合，用集合可以避免重複
global header # 聲明全局請求頭
header = {'User-Agent':
          'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:27.0) Gecko/20100101 Firefox/27.0'}

class find_example_img:
    """
    這是範例。
    """

    def __init__(self, url):
        self.url = url # 傳入的url
        self.article_name = '這個attr用於劃分子目錄'
        self.img_addr = ['這個attr是一個list','用於保存圖片地址']

class find_lofter_img:
    """
    http://wanimal.lofter.com/post/17d0d7_15aa344
    """

    def __init__(self, url):
        self.url = url # 傳入的url
        self.article_name = self.url.split('/')[4]
        soup=BeautifulSoup(requests.get(url,headers=header).content)
        self.img_addr = [x['bigimgsrc'] for x in soup.find_all('a','imgclasstag')]

class find_fotop_img:
    """
    例: http://www.fotop.net/joecww/joecww336
    """

    def __init__(self, url):
        self.url = url # 傳入的url
        self.article_name = self.url.split('/')[4]
        self.__soup = BeautifulSoup(
            requests.get(url, headers=header
                         ).content.decode('BIG5-HKSCS', 'ignore'))
        #self.img_addr=[x['src'] for x in self.__soup.find_all(istarget)]
        self.img_addr = []
        def get_more_img(url):
            soup = BeautifulSoup(
                requests.get(url, headers=header
                             ).content.decode('BIG5-HKSCS', 'ignore'))
            def istarget(tag):
                return tag.name=='img' and tag.has_attr('title') and tag.has_attr('border')
            for img in soup.find_all(istarget):
                self.img_addr.append(img['src'].replace('.thumb',''))

            try:
                next_page='http://www.fotop.net/'+soup.find_all('img',alt='Next Page')[-1].findParent('a')['href']
                get_more_img(next_page)
            except:
                pass

        get_more_img(self.url)


class find_cl_img:

    """
    例：http://cl.man.lv/....
    """

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

    """
    例：https://www.flickr.com/photos/astiya/sets/72157642803390374
    """

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.h1.string

        self.img_addr = []
        #self.img_addr=[re.sub(r'\.jpg','_b.jpg',x['data-defer-src']) for x in self.__soup.find_all('img','pc_img')]

        def get_img(url):
            soup = BeautifulSoup(requests.get(url, headers=header).content)
            for x in soup.find_all('img', 'pc_img'):
                self.img_addr.append(
                    re.sub(r'\.jpg', '_b.jpg', x['data-defer-src']))

            try:
                href_nextpage = soup.find('a', 'Next rapidnofollow')['href']
                nextpage = 'https://www.flickr.com' + href_nextpage
                get_img(nextpage)
            except:
                pass

        get_img(self.url)


class find_instagram_img:

    def __init__(self, url):
        self.url = url
        soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.url.split('/')[3]
        quary_json = json.loads(soup.find_all('script')[3].string[21:-1])
        self.img_addr = [x['images']['standard_resolution']['url']
                         for x in quary_json['entry_data']['UserProfile'][0]['userMedia']]
        json_url = 'http://instagram.com/chloefi/media?max_id='
        # moreAvailable: ['entry_data']['UserProfile'][0]['moreAvailable']

        def get_more_img(url):
            nextpage = requests.get(url).json()
            #img_buf=[x['images']['standard_resolution']['url'] for x in nextpage['items']]
            for item in nextpage['items']:
                self.img_addr.append(
                    item['images']['standard_resolution']['url'])

            max_id = nextpage['items'][-1]['id']
            if nextpage['more_available']:
                get_more_img(json_url + max_id)

        if quary_json['entry_data']['UserProfile'][0]['moreAvailable']:
            get_more_img(
                json_url + quary_json['entry_data']['UserProfile'][0]['userMedia'][-1]['id'])

        self.img_addr = self.img_addr[::-1]


class find_163_img:

    """
    例：http://pp.163.com/superbunny/pp/12307173.html
    """

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

    """
    例：http://my.poco.cn/lastphoto_v2.htx&id=3654521&user_id=54967495&p=0&temp=1182
    or: http://photo.poco.cn/lastphoto-htx-id-3883441-p-0.xhtml
    """

    def __init__(self, url):
        self.url = url
        page = requests.get(url, headers=header)
        self.__soup = BeautifulSoup(page.content)

        pattern = re.compile(r"photoImgArr\[\d+\]\.orgimg = \'(.*?)\';")
        try:
            self.article_name = self.__soup.find(
                'h1', 'mt10').text.strip(' ').replace(' ', '_')
            self.img_addr = re.findall(pattern, page.text)
        except AttributeError:
            self.article_name = self.__soup.h3.string.strip(
                ' ').replace(' ', '_')
            self.img_addr = [x['data_org_bimg']
                             for x in self.__soup.find_all('img', 'photo-item')]


class find_meizitu_img:

    """
    例：http://www.meizitu.com/a/4154.html
    """

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.find_all(
            'h2')[1].find('a').text.replace(' ', '_')
        self.img_addr = [x['src']
                         for x in self.__soup.find('div', id='picture').find_all('img')]


class find_curator_img:

    """
    例：http://curator.im/girl_of_the_day/2014-04-08/
    """

    def __init__(self, url):
        self.url = url
        self.__soup = BeautifulSoup(requests.get(url, headers=header).content)

        self.article_name = self.__soup.h1.text.strip(
            ' ').replace(' ', '_') + '_' + self.url.split('/')[-2]
        self.img_addr = [
            'http://' + x['src'].split('/', 5)[-1] for x in self.__soup.find_all('img', 'god')]
        if self.img_addr==[]:
            self.img_addr=[
                'http://' + x['src'].split('/', 5)[-1] for x in self.__soup.find_all('img',itemprop='contentURL')]
        self.img_addr.insert(
            0, 'http://' + self.__soup.find('img', 'profile_image')['src'].split('/', 5)[-1])


def MT_download(download_dir, img_addrs, classified, workers=10):
    def download(img_addr, img_index):# 真正工作的下載函數

        PATH = ''.join((classified_PATH,
                        str(img_index + 1).zfill(2), '_',
                        os.path.basename(img_addr))) # 構造保存地址
        try:
            img_status = os.stat(PATH).st_size
        except FileNotFoundError:
            img_status = 0 # 取得已下載文件的大小,大小與請求頭一致則不下載
        try:
            r = requests.get(img_addr, headers=header, stream=True)
            if r.ok and img_status != int(r.headers['content-length']):
                with open(PATH, 'wb') as f:
                    for chunk in r.iter_content():
                        f.write(chunk)
                print('{} Finished'.format(img_addr), end='\r')
        except Exception as Exc:
            print(Exc)

    classified_PATH = ''.join((download_dir, classified, '/'))
    if not os.path.exists(classified_PATH):
        os.makedirs(classified_PATH)
    else:
        go_on = input('Folder exist containing {} files, go ahead?[Y/n]:'
                      .format(len(os.listdir(classified_PATH))))
        if go_on.lower() == 'n':
            print('Downloading Abort.')
            exit(0) # 構建分類目錄

    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as executor:
        futureIteams = {executor.submit(
            download, item, img_addrs.index(item)): item for item in img_addrs}
        for future in concurrent.futures.as_completed(futureIteams):
            url = futureIteams[future]
            try:
                data = future.result()
                if url in failed:
                    failed.remove(url)
            except Exception as exc:
                print('{} generated an exception: {}'.format(url, exc))
                failed.add(url) # 多線程執行下載函數

    if failed:
        prompt = input(
            'There are {} images downloaded failed, retry?[Y/n]:', end='')
        if prompt.upper() == 'Y':
            MT_download(download_dir, list(failed), classified, workers=2)
        else:
            print('{} images downloaded at {}, while {} failed.'.format(
                len(os.listdir(classified_PATH)), classified_PATH, len(failed)))
    else:
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
    head = """<html xmlns="http://www.w3.org/1999/xhtml" lang="cn" xml:lang="cn">
    <head><title>Thumb</title>
    <meta http-equiv="content-type" content="text/html; charset=UTF-8" />
    </head><body>"""
    tail = """</body></html>"""
    with open(download_dir + classifed + '/index.html', 'w')as htm:
        htm.write(head)
        imgs = glob.glob(download_dir + classifed + '/*.jpg')
        for img in imgs:
            htm.write("""<a href={0}>
                      <img src={0} width=100/></a>""".format(img.split('/')[-1]))
        htm.write(tail)


if __name__ == '__main__':
    try:
        url = sys.argv[1]
    except:
        url = input('Album Address: ') # 若參數無地址傳入，則要求填寫

    MT = True # 默認開啓多線程下載
    workers = 10 # 線程數默認為10
    coll_dir = '/coll'
    if 'cl' in url.split('/')[2]:
        img = find_cl_img(url)
        download_dir = os.path.expanduser('~') + '/lll/'
    elif '163' in url.split('/')[2]:
        img = find_163_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/163/'
    elif 'lofter' in url.split('/')[2]:
        img = find_lofter_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/lofter/'
    elif 'meizitu' in url.split('/')[2]:
        img = find_meizitu_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/meizitu/'
    elif 'curator' in url.split('/')[2]:
        img = find_curator_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/curator/'
    elif 'fotop' in url.split('/')[2]:
        img = find_fotop_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/fotop/'
    elif 'flickr' in url.split('/')[2]:
        img = find_flickr_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/flickr/'
    elif 'poco' in url.split('/')[2]:
        img = find_poco_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/poco/'
        # MT=False
        workers = 2 # poco會限制同時下載數，所以減少下載線程
    elif 'instagram' in url.split('/')[2]:
# TODO instagram 有部分圖片使用fackbook的cdn，要考慮加入proxy功能
        img = find_instagram_img(url)
        download_dir = os.path.expanduser('~') + coll_dir + '/instagram/'
        with open(download_dir+img.article_name + '.dl', 'w')as f:
            f.write('\n'.join(img.img_addr))
        print('Total {}'.format(len(img.img_addr)))
        prompt = input('Continue Download?[y/N]:')
        if prompt.upper() != 'Y':
            sys.exit(0)

    MT_download(download_dir, img.img_addr, img.article_name, workers=workers) if MT else download_queue(
        download_dir, img.img_addr, img.article_name) #下載
    mkindex(download_dir, img.article_name) # 寫一個index.html

#print(download_dir+'\n'+ str(len(img.img_addr))+'\n'+ img.article_name)
