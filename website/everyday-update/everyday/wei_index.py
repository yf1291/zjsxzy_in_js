# encoding: utf-8

import pandas as pd
import numpy as np
import os

import const

def get_stock_wei_index():
    names, codes, pct = [], [], []
    files = [f for f in os.listdir(const.SEARCH_DIR)]
    for f in files:
        fname = '%s/%s'%(const.SEARCH_DIR, f)
        name = f.split('-')[1].rstrip('.xlsx').decode('gbk')
        code = f.split('-')[0]
        df = pd.read_excel(fname)
        names.append(name)
        codes.append(code)
        pct.append(df['value'].rank(pct=True).iloc[-1])
    df = pd.DataFrame({u'代码': codes, u'名称': names, u'百分位': pct})
    df = df.sort_values(u'百分位', ascending=False)
    df.to_excel('%s/wei_index_rank.xlsx'%(const.DATA_DIR), encoding='utf-8', index=False)

if __name__ == '__main__':
    get_stock_wei_index()
    