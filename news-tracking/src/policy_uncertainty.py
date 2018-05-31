# encoding: utf-8
import jieba
import os
import pandas as pd

DATA_DIR = 'D:/workspace/data/wallstreetcn'
WORD_DIR = u'D:/Data/词库'
CAIJING_WORD_FILE = u'%s/THUOCL_caijing.txt'%(WORD_DIR)

jieba.load_userdict(CAIJING_WORD_FILE)

def uncertainty(word_set):
    words1 = [u'政策', u'支出', u'预算', u'政治', u'利率', u'改革']
    flag1 = False
    for w in words1:
        if w in word_set:
            flag1 = True
            break
    if not flag1:
        return False
    words2 = [u'政府', u'背景', u'权威', u'官方']
    flag2 = False
    for w in words2:
        if w in word_set:
            flag2 = True
            break
    if not flag2:
        return False
    words3 = [u'央行', u'税收', u'监管', u'规定', u'中央银行', u'中国人民银行', u'赤字', u'TWO']
    for w in words3:
        if w in word_set:
            return True
    return False

def main(years):
    dic_tot, dic_pol = {}, {}
    for year in years:
        print(year)
        files = ['%s/%d/%s'%(DATA_DIR, year, f) for f in os.listdir('%s/%d'%(DATA_DIR, year))]
        for f in files:
            with open(f, 'r') as fp:
                text = fp.readlines()
            time = text[0].decode('utf-8').split('_')[0]
            time = time.strip()
            if time.find('-') == -1:
                time = time.replace(u'年', '-').replace(u'月', '-').replace(u'日', '')
            date = time.split(' ')[0]
            if not dic_tot.has_key(date):
                dic_tot[date] = 0
            if not dic_pol.has_key(date):
                dic_pol[date] = 0
            content = " ".join(text[1:])
            content = jieba.cut(content)
            doc = set([word for word in content])
            dic_tot[date] += 1
            if uncertainty(doc):
                dic_pol[date] += 1
    df = pd.DataFrame({'tot': pd.Series(dic_tot), 'pol': pd.Series(dic_pol)})
    df = df.sort_index()
    df.to_excel('D:/Data/risk/policy_uncertainty.xlsx')

if __name__ == '__main__':
    years = range(2010, 2019)
    main(years)
    