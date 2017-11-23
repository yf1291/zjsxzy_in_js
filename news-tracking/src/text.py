# encoding: utf-8

from os.path import join, dirname
import jieba
import datetime
import os
import json

import utils
import const

years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017']
# years = ['2010']
# with open(const.STOP_WORD_FILE, 'r') as f:
    # stop_words = set([line.strip() for line in f.readlines()])
# jieba.load_userdict(const.CAIJING_WORD_FILE)
# jieba.load_userdict(const.MYWORD_FILE)

def get_wallst_text():
    document = ''
    for y in years:
        files = ["%s/%s/%s"%(const.WALLSTCN_DIR, y, f) for f in os.listdir("%s/%s/"%(const.WALLSTCN_DIR, y))]
        print y, len(files)
        if len(files) > 0:
            for f in files:
                with open(f, 'r') as fp:
                    text = fp.readlines()
                text = ' '.join(text).decode('utf-8')
                if text.find(u'国家战略') != -1:
                    print u'国家战略', f
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(f + '\n')
                elif text.find(u'创新战略') != -1:
                    print u'创新战略', f
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(f + '\n')
                elif text.find(u'发展战略') != -1:
                    print u'发展战略', f
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(f + '\n')
                # time = text[0].split('_')[0]
                # time = time.strip()
                # if time.find('-') != -1:
                    # dt = datetime.datetime.strptime(time, "%Y-%m-%d %H:%M")
                # else:
                    # dt = datetime.datetime.strptime(time, '%Y年%m月%d日 %H:%M:%S')
                # date = dt.strftime("%Y-%m-%d")

                # content = " ".join(text[1:])
                # doc = [word for word in jieba.cut(content) if (not word in stop_words) and (not utils.isNumber(word))]
                # document += '\n' + ' '.join(doc)

    # with open(const.WALLSTCN_TEXT_FILE, 'w') as fp:
        # fp.write(document.encode('utf-8'))

def get_gov_text():
    deps = [d for d in os.listdir(const.GOV_DIR) if not d.endswith('.txt')]
    for d in deps:
        files = [f for f in os.listdir('%s/%s'%(const.GOV_DIR, d))]
        for f in files:
            fname = r'%s/%s/%s'%(const.GOV_DIR, d, f)
            try:
                with open(fname, 'r') as fp:
                    text = fp.readlines()
                text = ' '.join(text).decode('utf-8')
                if text.find(u'国家战略') != -1:
                    print u'国家战略', fname
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(fname + '\n')
                elif text.find(u'创新战略') != -1:
                    print u'创新战略', fname
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(fname + '\n')
                elif text.find(u'发展战略') != -1:
                    print u'发展战略', fname
                    with open(u'D:/Data/词检索/国家战略.txt', 'a') as fp:
                        fp.write(fname + '\n')
            except Exception as e:
                print(fname)
                print(e)

if __name__ == "__main__":
    # get_wallst_text()
    get_gov_text()
