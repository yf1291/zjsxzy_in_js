# encoding: utf-8
import pandas as pd
import numpy as np
import empyrical

import const

'''
def return_intersect(start_date, end_date):
    # df = pd.read_excel(const.THEME_FILE, index_col=0)
    df = pd.read_excel(const.SW_SECTOR_FILE, index_col=0)
    df.columns = ['sector']
    df['return'] = 0.0
    df = df.copy()
    for wind_code in df.index:
        fname = '%s/%s.xlsx'%(const.INDEX_DIR, wind_code)
        temp = pd.read_excel(fname)
        close = temp[(temp.index >= start_date) & (temp.index <= end_date)]['close']
        ret = (close[-1] - close[0]) / close[0] if close[0] != 0 else 0.0
        # df['return'][wind_code] = ret
        df.loc[wind_code, 'return'] = ret

    df = df.sort_values('return')[::-1]
    return df
'''

def return_intersect(start_date, end_date):
    print start_date, end_date
    df = pd.read_excel(const.SW_SECTOR_HIS_FIKE)
    # df = df[(df.index >= start_date) & (df.index <= end_date)]
    # ret = (df.iloc[-1] - df.iloc[0]) / df.iloc[0]
    # ret = df.pct_change(df.shape[0] - 1).dropna().iloc[-1]
    ret = df.pct_change()
    ret = ret[(ret.index >= start_date) & (ret.index <= end_date)]
    ret = (1 + ret).cumprod().iloc[-1] - 1.
    # print ret.tail()

    df = pd.read_excel(const.SW_SECTOR_FILE, index_col=0)
    df.columns = ['sector']
    df['return'] = ret.T
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna().sort_values('return')[::-1]
    # print df
    return df

if __name__ == '__main__':
    df = return_intersect('2017-01-02', '2018-01-02')
    print df
