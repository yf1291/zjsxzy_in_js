# encoding: utf-8
import empyrical
from WindPy import w
import numpy as np
import pandas as pd
import os
import datetime

import const
import database

w.start()

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def get_money_fund_daily_return(start_date, end_date):
    code = "H11025.CSI"
    fname = '%s/%s.csv'%(const.DATA_DIR, code)
    if os.path.exists(fname):
        df = pd.read_csv(fname, index_col=0)
    else:
        data = w.wsd(code, 'close', start_date, end_date)
        df = wind2df(data)
        df['return'] = df['close'].pct_change()
        df.to_csv(fname)
    return df['return'].dropna()

def get_sharpe_ratio(daily_return):
    sharpe_ratio = empyrical.sharpe_ratio(daily_return)
    return sharpe_ratio
    start_date = daily_return.index[0]
    end_date = daily_return.index[-1]
    days = int((end_date - start_date).days)
    acc_return = (1 + daily_return).cumprod()[-1]

    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    money_daily_return = get_money_fund_daily_return(start_date, end_date)
    money_acc_return = (1 + money_daily_return).cumprod()[-1]

    volatility = daily_return.std() * np.sqrt(243)
    print acc_return
    print money_acc_return

    sharpe_ratio = (acc_return**(365./days) - money_acc_return**(365./days)) / volatility
    return sharpe_ratio

def roll(df, w):
    """
    This fucntion comes from:
    http://stackoverflow.com/questions/37486502/why-does-pandas-rolling-use-single-dimension-ndarray/37491779#37491779
    """
    df.fillna(df.mean(), inplace=True)
    roll_array = np.dstack([df.values[i:i+w, :] for i in range(len(df.index) - w + 1)]).T
    panel = pd.Panel(roll_array,
                     items=df.index[w-1:],
                     major_axis=df.columns,
                     minor_axis=pd.Index(range(w), name='roll'))
    return panel.to_frame().unstack().T.groupby(level=0)

def get_index_component(index_code):
    index_file = "%s/%s.xlsx"%(const.INDEX_DIR, index_code)
    df = pd.read_excel(index_file)
    return df['wind_code'].tolist()

def next_date(date):
    return pd.to_datetime(date) + datetime.timedelta(1)

def get_stock_history_price_from_wind():
    '''
    从万得RDF数据库获得所有股票历史复权价格
    '''
    query = 'select t.trade_dt, t.s_info_windcode, t.s_dq_adjclose \
             from wind.AShareEODPrices t'
    df = database.DataFrame_from_wind(query)
    df['TRADE_DT'] = pd.to_datetime(df['TRADE_DT'], format='%Y%m%d')
    df = df.pivot_table('S_DQ_ADJCLOSE', index=['TRADE_DT', 'S_INFO_WINDCODE']).unstack()
    return df

def get_index_price(index_code, start_date, end_date):
    '''
    得到指数的历史价格，返回DataFrame格式
    '''
    data = w.wsd(index_code, 'close', start_date, end_date)
    df = pd.DataFrame(np.array(data.Data[0]), index=data.Times, columns=['p'])
    df.index = pd.to_datetime(df.index)
    df['date'] = df.index
    return df