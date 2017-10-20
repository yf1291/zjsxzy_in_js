# encoding: utf-8

import pandas as pd
import datetime
import os
from WindPy import w

import const
import utils

w.start()

def get_option_list():
    fname = '%s/option list.xlsx'%(const.DATA_DIR)
    df = pd.read_excel(fname, skiprows=6)
    return df

def download_option_information(option_code, start_date, end_date):
    fname = '%s/%s.xlsx'%(const.OPTION_DIR, option_code)
    '''
    if os.path.exists(fname):
        return
    '''
    data = w.wsd(option_code, "oi", start_date, end_date)
    df = utils.wind2df(data)
    df.to_excel(fname)

def download_options_history(df):
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    for option_code, start_date in zip(df[u'期权代码'], df[u'起始交易日期']):
        print option_code, start_date, today
        download_option_information(option_code, start_date, today)
