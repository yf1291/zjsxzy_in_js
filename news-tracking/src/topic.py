# encoding: utf-8

import os
import jieba

import const
import utils

jieba.load_userdict(const.CAIJING_WORD_FILE)
with open(const.STOP_WORD_FILE, 'r') as f:
    stop_words = set([line.strip().decode('utf-8') for line in f.readlines()])

def save_wallst_text():
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']
    with open(const.WST_WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = ([line.strip() for line in fp.readlines()])

    for y in years:
        files = [f for f in os.listdir('%s/%s'%(const.WALLSTCN_DIR, y))]
        print y, len(files)
        for f in files:
            fname = '%s/%s/%s'%(const.WALLSTCN_DIR, y, f)
            if fname in checked_list:
                with open(fname, 'r') as fp:
                    content = ' '.join([line.strip() for line in fp.readlines()[1:]])
                content = jieba.cut(content)
                content = [w for w in content if (w not in stop_words) and (not utils.isNumber(w))]
                content = ' '.join(content).encode('utf-8')
                with open(const.WST_TOPIC_FILE, 'a') as fp:
                    fp.write(content + '\n')

if __name__ == '__main__':
    save_wallst_text()
