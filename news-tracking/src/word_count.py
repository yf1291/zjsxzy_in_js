# encoding: utf-8
# 统计华尔街见闻新闻文本的词频

from os.path import join, dirname
import jieba
import datetime
import os
import json
import utils
import pickle

import total_word_count
import const
import utils

# DATA_DIR = "D:/workspace/data/"
# WALLSTCN_DIR = "%s/wallstreetcn"%(DATA_DIR)
# WORD_CNT_FILE = '%s/wallstreetcn_words/word_count.pkl'%(DATA_DIR)
# WORD_CNT_CHECKED_FILE = '%s/wallstreetcn_words/word_count_checked.txt'%(DATA_DIR)
# WORD_CNT_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count.json"%(DATA_DIR)
# WORD_CNT_CHECKED_FILE = "%s/wallstreetcn_words/wallstreetcn_word_count_checked.txt"%(DATA_DIR)
jieba.load_userdict(const.CAIJING_WORD_FILE)
with open(const.STOP_WORD_FILE, 'r') as f:
    stop_words = set([line.strip() for line in f.readlines()])

def update_wallst_word_count():
    years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018']
    # years = ['2010']
    with open(const.WST_WORD_CNT_FILE, 'rb') as fp:
        word_count = pickle.load(fp)
    with open(const.WST_WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = set([line.strip().decode('utf-8') for line in fp.readlines()])
    # f_check = open(const.WST_WORD_CNT_CHECKED_FILE, 'a')
    new_checked = []
    for y in years:
        files = ["%s/%s/%s"%(const.WALLSTCN_DIR, y, f) for f in os.listdir("%s/%s/"%(const.WALLSTCN_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                if f in checked_list:
                    continue
                # with open(WORD_CNT_CHECKED_FILE, 'a') as fp:
                    # fp.write(f + '\n')
                # f_check.write(f.encode('utf-8') + '\n')
                new_checked.append(f)
                with open(f, 'r') as fp:
                    text = fp.readlines()
                time = text[0].decode('utf-8').split('_')[0]
                time = time.strip()
                if time.find('-') == -1:
                    time = time.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
                '''
                if time.count(':') == 2:
                    dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
                else:
                    dt = datetime.datetime.strptime(time, '%Y-%m-%d %H:%M')
                date = dt.strftime("%Y-%m-%d")
                '''
                date = time.split(' ')[0]

                content = " ".join(text[1:])
                content = jieba.cut(content)
                doc = [word for word in content if (not word in stop_words) and (not utils.isNumber(word))]
                for word in doc:
                    if not word_count.has_key(word):
                        word_count[word] = {}
                    if not word_count[word].has_key(date):
                        word_count[word][date] = 0
                    word_count[word][date] += 1

    with open(const.WST_WORD_CNT_CHECKED_FILE, 'a') as fp:
        fp.write(('\n' + '\n'.join(new_checked)).encode('utf-8'))
    with open(const.WST_WORD_CNT_FILE, 'wb') as fp:
        pickle.dump(word_count, fp)

def update_files(prefix, files):
    with open(const.GOV_WORD_CNT_FILE, 'rb') as fp:
        word_count = pickle.load(fp)
    with open(const.GOV_WORD_CNT_CHECKED_FILE, 'r') as fp:
        checked_list = set([line.strip().decode('utf-8') for line in fp.readlines()])
    # print '\n'.join(checked_list)
    # f_check = open(const.GOV_WORD_CNT_CHECKED_FILE, 'a')
    new_checked = []
    for f in files:
        date = f.split('_')[0]
        # if not date.startswith('2016') and not date.startswith('2017'):
            # continue
        date = date.split(' ')[0]
        f = '%s/%s'%(prefix, f)
        # f = f.replace('？', '')
        f = f.decode('gbk')
        if f in checked_list or not f.endswith('.txt'):
            # print "exist: ", f
            continue
        new_checked.append(f)
        # print f
        # f_check.write(f.encode('utf-8') + '\n')
        try:
            with open(f, 'r') as fp:
                text = fp.readlines()
            content = ' '.join(text)
            doc = [word for word in jieba.cut(content) if (not word in stop_words) and (not utils.isNumber(word))]
            for word in doc:
                if not word_count.has_key(word):
                    word_count[word] = {}
                if not word_count[word].has_key(date):
                    word_count[word][date] = 0
                word_count[word][date] += 1
        except Exception as e:
            print(e)

    # print('\n'.join(new_checked))
    with open(const.GOV_WORD_CNT_CHECKED_FILE, 'a') as fp:
        fp.write(('\n' + '\n'.join(new_checked)).encode('utf-8'))
    with open(const.GOV_WORD_CNT_FILE, 'wb') as fp:
        pickle.dump(word_count, fp)

def update_gov_word_count():
    departments = [d for d in os.listdir(const.GOV_DIR) if not d.endswith('.txt')]
    for dep in departments:
        prefix = '%s/%s'%(const.GOV_DIR, dep)
        if prefix.endswith('txt'):
            continue
        files = [f for f in os.listdir(prefix)]
        print dep, len(files)
        if len(files) > 0:
            update_files(prefix, files)

def main():
    update_wallst_word_count()
    total_word_count.get_total_word_count(const.WST_WORD_CNT_FILE, const.WST_TOTAL_WORD_COUNT_FILE)
    # update_gov_word_count()
    # total_word_count.get_total_word_count(const.GOV_WORD_CNT_FILE, const.GOV_TOTAL_WORD_COUNT_FILE)

if __name__ == "__main__":
    main()
