# encoding: utf-8
# 计算创新高的股票
import pandas as pd
import os
import datetime
from WindPy import w

import const
import utils

def record_high(year=2, recents=[20, 60, 121, 243]):
    '''
    计算recents范围内当前所有股票创新高的次数
    '''
    df = utils.get_stock_history_price_from_wind()
    max_df = df.rolling(243*year, min_periods=1).max()
    dic = {}
    for recent in recents:
        high_df = (df == max_df).rolling(window=recent).sum()
        dic[recent] = high_df.iloc[-1]
        high_df.sum(axis=1).to_csv('%s/record_high_%d.csv'%(const.DATA_DIR, recent))
    df = pd.DataFrame(dic)
    return df

def main():
    fname = '%s/record_high.xlsx'%(const.DATA_DIR)
    df = record_high()
    df.to_excel(fname)

    df = pd.read_excel(fname)
    w.start()
    df = df.set_index('S_INFO_WINDCODE')
    today = datetime.datetime.today()
    data = w.wss(df.index.tolist(), 'industry_citic', 
                 'tradeDate=%s;industryType=4'%(today.strftime('%Y%m%d')))
    df['industry'] = data.Data[0]
    data = w.wss(df.index.tolist(), 'sec_name')
    df['sec_name'] = data.Data[0]
    data = w.wss(df.index.tolist(), 'ipo_date')
    df['ipo_date'] = pd.to_datetime(data.Data[0])
    filter_date = datetime.datetime.today() - datetime.timedelta(365)
    df = df[df['ipo_date'] < filter_date]
    df.to_excel(fname)

if __name__ == '__main__':
    main()
    