#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dl import find_curator_img
import requests
from dl import MT_download

url_base='http://curator.im/girl_of_the_day/2014-04-'
for i in range(1,13):
    url=url_base+str(i).zfill(2)+'/'
    targe=find_curator_img(url)
    MT_download('capture/',targe.img_addr,targe.article_name)

print('all done')
