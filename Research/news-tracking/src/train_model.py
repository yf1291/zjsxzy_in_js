# encoding: utf-8

import os
import jieba
from textrank4zh import TextRank4Keyword, TextRank4Sentence

import const
import utils

jieba.load_userdict(const.MYWORD_FILE)
jieba.load_userdict(const.CAIJING_WORD_FILE)
with open(const.STOP_WORD_FILE, 'r') as f:
    stop_words = set([line.strip().decode('utf-8') for line in f.readlines()])
text_file = u'D:/Data/词检索/text.txt'
model_file = u'D:/Data/词检索/model'


def filter_keyword():
    fname = u'D:/Data/词检索/国家战略.txt'
    with open(fname, 'r') as f:
        files = [line.strip() for line in f.readlines()]
    for f in files:
        with open(f, 'r') as fp:
            text = fp.readlines()
        if f.startswith('D:/Data/gov'):
            text = ' '.join(text).decode('utf-8')
            # f = f.lstrip('D:/Data/gov/')
            # dep, fname = f.split('/')[0], f.split('/')[1]
            # f = '%s_%s_%s'%(fname.split('_')[0], dep, fname.split('_')[1])
            # print f
        if text.find(u'国家战略') != -1 and f.decode('gbk').find(u'习近平') != -1:
            print f
            # fname = u'D:/Data/词检索/国家战略/%s'%(f.decode('gbk'))
            # with open(fname, 'w') as fp:
                # fp.write(text.encode('utf-8'))
            doc = jieba.cut(text)
            doc = [word for word in doc if (not word in stop_words) and (not utils.isNumber(word))]
            doc = ' '.join(doc)
            doc = doc.replace('\t', ' ').replace('\n', ' ')
            with open(text_file, 'a') as fp:
                fp.write(doc.encode('utf-8') + '\n')

def extract_text(path):
    files = [f for f in os.listdir(path)]
    content = []
    for f in files:
        # print f
        fname = u'%s/%s'%(path, f)
        with open(fname, 'r') as fp:
            text = fp.readlines()
        text = ' '.join(text).decode('utf-8')
        doc = jieba.cut(text)
        doc = [word for word in doc if (not word in stop_words) and (not utils.isNumber(word))]
        # print(len(doc))
        doc = ' '.join(doc)
        doc = doc.replace('\t', ' ').replace('\n', ' ')
        content.append(doc)
        # for word in doc:
            # print word
        # print ' '.join(doc).encode('gbk')
        # break
    with open(text_file, 'w') as f:
        f.write('\n'.join(content).encode('utf-8'))

def theme():
    with open(text_file, 'r') as f:
        content = f.readlines()
    for text in content:
        tr4w = TextRank4Keyword()
        tr4w.analyze(text=text, lower=True, window=2)
        print( u'关键词：' )
        for item in tr4w.get_keywords(20, word_min_len=1):
            print item.word, item.weight

        print()
        print( u'关键短语：' )
        for phrase in tr4w.get_keyphrases(keywords_num=20, min_occur_num= 2):
            print phrase

        tr4s = TextRank4Sentence()
        tr4s.analyze(text=text, lower=True, source = 'all_filters')

        print()
        print( u'摘要：' )
        for item in tr4s.get_key_sentences(num=3):
            print item.index, item.weight, item.sentence.encode('utf-8')  # index是语句在文本中位置，weight是权重
        break

if __name__ == '__main__':
    # path = u'D:/Data/词检索/国家战略'
    # extract_text(path)
    # theme()
    filter_keyword()
