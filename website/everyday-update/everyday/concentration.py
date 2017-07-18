# encoding: utf-8

import pandas as pd
import datetime
from sklearn import preprocessing

import const

def get_concentration(k=25):
    pnl = pd.read_pickle('%s/price.pkl'%(const.DATA_DIR))
    pnl.ix[:, :, 'return'] = pnl.minor_xs('close').pct_change(k)
    pnl.ix[:, :, 'return sqr'] = pnl.minor_xs('return') ** 2
    # pnl.ix[:, :, 'weight'] = pnl.minor_xs('mkt_freeshares') / pnl.minor_xs('close')
    # n, m = pnl.shape[0], pnl.shape[1]

    wdf = pd.read_excel('%s/881001_weight.xlsx'%(const.DATA_DIR), index_col=0)
    wdf = wdf[wdf.index.map(lambda x: x in pnl.items)]
    wdf = wdf.sort_index()

    df = pd.read_csv('%s/881001.WI.csv'%(const.DATA_DIR), index_col=1)
    df.index = df.index.map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d') + datetime.timedelta(seconds=0.005))
    df = df[(df.index >= pnl.major_axis[0]) & (df.index <= pnl.major_axis[-1])]
    assert(df.shape[0] == pnl.major_axis.shape[0])
    df.index = pnl.major_axis
    df['return'] = df['close'].pct_change(k)
    # concentration = (df['return']**2) * (pnl.minor_xs('weight')**2).sum(axis=1) /\
                    # (pnl.minor_xs('return sqr') * (pnl.minor_xs('weight')**2)).sum(axis=1)
    concentration = (df['return']**2) * (wdf[u'权重']**2).sum() /\
                    pnl.minor_xs('return sqr').multiply(wdf[u'权重']**2, axis=1).sum(axis=1)
    scaler = preprocessing.MinMaxScaler()

    df = pd.DataFrame({'concentration': concentration, 'price': scaler.fit_transform(df['close'])}, index=df.index)
    df.to_excel('%s/concentration.xlsx'%(const.DATA_DIR))

def get_dataframe():
    df = pd.read_excel('%s/concentration.xlsx'%(const.DATA_DIR), index_col=0)
    return df

if __name__ == '__main__':
    get_concentration()
