# encoding: utf-8
import requests
from bs4 import BeautifulSoup
import os
import time
import pickle
import jieba

import const

BASE_URL = 'http://jhsjk.people.cn/article'
START_ID = 29615361
DATA_DIR = 'D:/Data/xjp'

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
        if os.path.exists(fname):
            print fname
            continue
        if responce.status_code == 200:
            print(url)
            text = responce.text
            soup = BeautifulSoup(text, 'html.parser')
            # print soup.title.string
            content = soup.find(class_='d2txt clearfix').text.strip()
            with open(fname, 'w') as f:
                f.write(content.encode('utf-8'))

def word_count():
    with open('../ipynb/stop_words_zh.txt', 'r') as f:
        stop_words = set([line.strip() for line in f.readlines()])
    files = [f for f in os.listdir(DATA_DIR)]
    word_count = {}
    for f in files:
        fname = '%s/%s'%(DATA_DIR, f)
        with open(fname, 'r') as f:
            text = f.readlines()
        content = ''.join(text).replace('\n', 'r').replace('\t', '').decode('utf-8')
        date = content[content.find(u'发布时间')+5:content.find(u'发布时间')+15]
        print f, date
        seg_list = jieba.cut(content)
        seg_list = [w for w in seg_list if w.encode('utf-8') not in stop_words]
        for word in seg_list:
            if not word_count.has_key(word):
                word_count[word] = {}
            if not word_count[word].has_key(date):
                word_count[word][date] = 0
            word_count[word][date] += 1
    with open('%s/xjp_count.pkl'%(const.WORK_DIR), 'wb') as f:
        pickle.dump(word_count, f)

if __name__ == '__main__':
    crawl(START_ID)
