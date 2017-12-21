import pandas as pd
import datetime
import os
from WindPy import w

import const
import utils

w.start()

def get_option_list():
    df = pd.read_excel(const.OPT_LIST, index_col=0)
    return df

def download_option_information(option_code, start_date, end_date):
    fname = '%s/%s.xlsx'%(const.OPTION_DIR, option_code)
    '''
    if os.path.exists(fname):
        return
    '''
    data = w.wsd(option_code, "oi,close", start_date, end_date)
    df = utils.wind2df(data)
    df.to_excel(fname)

def append_option_column(option_code, col_name):
    fname = '%s/%s.xlsx'%(const.OPTION_DIR, option_code)
    if os.path.exists(fname):
        df = pd.read_excel(fname, index_col=0)
        if col_name.lower() in df.columns:
            return
        start_date, end_date = df.index[0].strftime('%Y-%m-%d'), df.index[-1].strftime('%Y-%m-%d')
        data = w.wsd(option_code, col_name, start_date, end_date)
        temp = utils.wind2df(data)
        df[col_name.lower()] = temp[col_name]
        df.to_excel(fname)

def download_options_history(df):
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for index in df.index:
        wind_code = str(index) + '.SH'
        start_date = df.loc[index, 'listed_date']
        end_date = df.loc[index, 'exercise_date']
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        if yesterday < end_date:
            end_date = yesterday
        print wind_code
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        download_option_information(wind_code, start_date, end_date)

def append_options_history(df):
    for index in df.index:
        wind_code = str(index) + '.SH'
        append_option_column(wind_code, 'us_impliedvol')

def get_futures_list(future_list):
    df = pd.read_excel(future_list, index_col=0)
    return df

def download_future_information(future_code, start_date, end_date):
    fname = '%s/%s.xlsx'%(const.FUTURE_DIR, future_code)
    '''
    if os.path.exists(fname):
        return
    '''
    data = w.wsd(future_code, "oi,close", start_date, end_date)
    df = utils.wind2df(data)
    df.to_excel(fname)

def download_futures_history(df):
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for wind_code in df.index:
        start_date = df.loc[wind_code, 'ftdate']
        end_date = df.loc[wind_code, 'ltdate']
        if start_date == 0:
            continue
        end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        if yesterday < end_date:
            end_date = yesterday
        print 'downloading %s...'%(wind_code)
        end_date = end_date.strftime('%Y-%m-%d')
        download_future_information(wind_code, start_date, end_date)
