#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
from bs4 import BeautifulSoup
import requests


class getproxy(object):

    '''
    Get Proxy list from http://www.cnproxy.com
    '''

    def __init__(self):
        self.url = 'http://www.cnproxy.com/proxy1.html'
        self.port_dict = {
            'a': '2', 'c': '1', 'i': '7', 'm': '4', 'q': '0', 'r': '8', 'v': '3', 'l': '9', 'b': '5', 'w': '6'}
        soup = BeautifulSoup(requests.get(self.url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:28.0) Gecko/20100101 Firefox/28.0'
        }).content)

        self.servers = [(x.find('td').contents[0], ''.join(re.findall(r'(?<=\+)(.)', x.find('td').contents[1].text)).translate(
            str.maketrans(''.join(self.port_dict.keys()), ''.join(self.port_dict.values())))) for x in soup.find_all('tr')[2:]]
        self.proxy = 'http://' + self.servers[0][0] + ':' + self.servers[0][1]

if __name__ == '__main__':
    a = getproxy()
    print(a.proxy)
