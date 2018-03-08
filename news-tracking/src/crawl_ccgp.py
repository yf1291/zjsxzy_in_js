# encoding: utf-8

import urllib2
from bs4 import BeautifulSoup
import httplib
import datetime
import os

import const

WEBSITE = 'http://www.ccgp.gov.cn'

def get_url(level1, level2, level3, date, article_id):
    url = '%s/%s/%s/%s/%s/t%s_%d.htm'%(WEBSITE, level1, level2, level3, date[:6], date, article_id)
    return url

def fname_strip(fname):
    return fname.replace('\n', '').replace('/', '').replace('\\', '')\
                .replace(u'“', '').replace(u'”', '').replace('"', '')\
                .replace(u'<', '').replace(u'>', '').replace('?', '')\
                .replace(u'*', '').replace('\t', '').replace(':', '')

def try_url(level1, level2, level3, date, article_id, data_dir):
    url = get_url(level1, level2, level3, date, article_id)
    conn = httplib.HTTPConnection("www.ccgp.gov.cn")
    conn.request('GET', url)
    response = conn.getresponse()
    text = response.read()
    soup = BeautifulSoup(text, "html.parser")
    title = soup.title.text
    if title.startswith(u'错误页面') or title.startswith('403') or title.startswith('500'):
        return False
    else:
        print url
        title = title.replace(u'\xa0', u' ').replace(u'\u2022', u' ')
        print date, article_id, title
        chdir = '%s/%s'%(data_dir, date)
        if not os.path.exists(chdir):
            os.mkdir(chdir)
        fname = '%d_%s.txt'%(article_id, title)
        fname = fname_strip(fname)
        fname = '%s/%s'%(chdir, fname)
        # print fname
        if not os.path.exists(fname):
            content = soup.find(class_='vF_detail_main')
            if content == None:
                content = soup.find(class_='vT_detail_main')
            content = content.text
            with open(fname, 'w') as f:
                f.write(content.encode('utf-8'))
        return True

def crawl_department(start_date, start_article, level1, level2, level3, data_dir):
    date, article_id = start_date, start_article
    while article_id > 0:
        feedback = try_url(level1, level2, level3, date, article_id, data_dir)
        if not feedback:
            prev_date = datetime.datetime.strptime(date, '%Y%m%d') - datetime.timedelta(1)
            prev_date = prev_date.strftime('%Y%m%d')
            flag = try_url(level1, level2, level3, prev_date, article_id, data_dir)
            if flag:
                date = prev_date
        article_id -= 1

if __name__ == '__main__':
    crawl_department('20171010', 8966652, 'cggg', 'dfgg', 'zbgg', const.CCGP_DATA_DIR_DFGG_ZBGG)
