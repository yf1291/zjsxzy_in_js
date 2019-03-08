# encoding: utf-8
import urllib2
from bs4 import BeautifulSoup
import httplib
import os
import requests

BASE_URL = 'http://ldzl.people.com.cn/dfzlk/front/personPage'
DATA_DIR = u'D:/Data/地方政府领导'

def main():
    conn = httplib.HTTPConnection("ldzl.people.com.cn")
    for person_id in range(20000, 30000):
        if person_id % 100 == 0:
            print 'current status:', person_id
        url = '%s%d.htm'%(BASE_URL, person_id)
        conn.request('GET', url)
        response = conn.getresponse()
        text = response.read()
        if response.status == 200:
            soup = BeautifulSoup(text, "html.parser")
            name = soup.find(class_='long_name')
            duty = soup.findAll(class_='red')[1]
            content = soup.find(class_='box01')
            if content == None:
                continue
            duty, name = duty.text, name.text
            duty = duty.replace('\t', '').replace('\n', '')
            name = name.replace('\t', '').replace('\n', '')
            print person_id, duty, name
            fname = '%s/%s_%s_%s.txt'%(DATA_DIR, person_id, duty, name)
            with open(fname, 'w') as f:
                f.write(content.text.encode('utf-8'))

if __name__ == '__main__':
    main()