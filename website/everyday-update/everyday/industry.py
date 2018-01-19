# encoding: utf-8
import pandas as pd
import numpy as np
import datetime
from WindPy import w
from sklearn.decomposition import PCA
import os

import wind_data
import utils
import const

codes = ['CI0050%02d.WI'%(i) for i in range(1, 30)]
fields = 'close,volume'
INDEX_DIR = 'D:/Data/index'

def download_data(codes,
                  fields,
                  start_date='2001-01-01',
                  end_date='2017-07-07'):
    for code in codes:
        print(code)
        data = w.wsd(code, fields, start_date, end_date)
        df = wind_data.wind2df(data)
        df.to_excel('%s/%s.xlsx'%(INDEX_DIR, code))

def append_data(codes,
                fileds):
    for code in codes:
        print(code)
        fname = '%s/%s.xlsx'%(INDEX_DIR, code)
        if datetime.datetime.now().hour < 15:
            end_date = datetime.datetime.today() - datetime.timedelta(1)
        else:
            end_date = datetime.datetime.today()
        if os.path.exists(fname):
            old_df = pd.read_excel(fname, index_col=0)
            start_date = old_df.index[-1] + datetime.timedelta(1)
            if start_date > end_date:
                continue
            else:
                data = w.wsd(code, fields, start_date, end_date)
                df = wind_data.wind2df(data)
                df = old_df.append(df)
                df.to_excel(fname)
        else:
            data = w.wsd(code, fields, '2001-01-01', end_date)
            df = wind_data.wind2df(data)
            df.to_excel(fname)

def get_panel():
    dic = {}
    for code in codes:
        temp = pd.read_excel('%s/%s.xlsx'%(INDEX_DIR, code), index_col=0)
        dic[code] = temp
    pnl = pd.Panel(dic)
    return pnl

def principal_ratio(df, k):
    pca = PCA()
    pca.fit(df)
    pricipal = pca.explained_variance_ratio_
    return pricipal[:k].sum()

def get_dataframe():
    pnl = get_panel()
    pnl.ix[:, :, 'return'] = pnl.minor_xs('close').pct_change()
    df = pnl.minor_xs('return')
    # print df.tail()

    rolled_df = utils.roll(df, 60)
    ratio = rolled_df.apply(lambda x: principal_ratio(x, 3))

    res = pd.DataFrame({'con60': ratio})
    res.index.name = 'date'

    return res

def correlation():
    df = pd.read_csv('%s/881001.WI.csv'%(const.DATA_DIR))
    df = df.set_index('date')
    df.index = pd.to_datetime(df.index)
    df = df[df.index >= '2005-01-01']
    dic = {}
    for code in codes:
        fname = '%s/%s.xlsx'%(INDEX_DIR, code)
        temp = pd.read_excel(fname)
        temp = temp[temp.index >= '2005-01-01']
        dic[code] = temp['close'].pct_change().rolling(window=243).corr(df['close'].pct_change())
    cor_df = pd.DataFrame(dic)
    cor_df = pd.DataFrame({'corr': cor_df.mean(axis=1), 'median': cor_df.median(axis=1)})
    cor_df = cor_df.dropna()
    cor_df.to_excel('%s/industry_corr.xlsx'%(const.DATA_DIR))

def main():
    append_data(codes, fields)

if __name__ == '__main__':
    # download_data(codes, fields)
    main()
    correlation()
    df = get_dataframe()
    # print df
    df.to_excel('%s/consistency.xlsx'%(const.DATA_DIR))
