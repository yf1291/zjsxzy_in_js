# encoding: utf-8
import requests
from bs4 import BeautifulSoup
import os
import time

BASE_URL = 'http://jhsjk.people.cn/article'
START_ID = 25344624
DATA_DIR = 'D:Data/xjp'

def crawl(start_id):
    for aid in range(start_id, 0, -1):
        if aid % 10000 == 0:
            print aid
        article_id = str(aid)
        url = '%s/%s'%(BASE_URL, aid)
        try:
            responce = requests.get(url)
        except:
            time.sleep(60)
            responce = requests.get(url)
        fname = '%s/%s.txt'%(DATA_DIR, article_id)
        # if os.path.exists(fname):
            # continue
        if responce.status_code == 200:
            print(url)
            text = responce.text
            soup = BeautifulSoup(text, 'html.parser')
            content = soup.find(class_='d2txt clearfix').text.strip()
            with open(fname, 'w') as f:
                f.write(content.encode('utf-8'))

if __name__ == '__main__':
    crawl(START_ID)
