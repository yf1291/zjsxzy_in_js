# encoding: utf-8
import pandas as pd
import numpy as np
from WindPy import w
import datetime
import calendar
import os

import utils
import const

w.start()

def create_fundamental_dataframe(stock, start_date, end_date):
    '''
    生成一个基本面数据Dataframe
    '''
    rpt_dates = utils.generate_rptdates(start_date, end_date)
    df = pd.DataFrame(columns=const.FUNDAMENTAL_FIELDS, index=rpt_dates)
    for date in df.index:
        wdata = w.wss(stock, const.FUNDAMENTAL_FIELDS, 'rptDate=%s'%(date))
        df.loc[date] = [x[0] for x in wdata.Data]
    return df

def create_fundamental_file(stock):
    '''
    创建一个基本面数据文件
    '''
    fname = utils.get_fundamental_file_name(stock)
    if os.path.exists(fname):
        print('file exists')
        return
    ipo_date = w.wss(stock, 'ipo_date').Data[0][0]
    ipo_date = pd.to_datetime(ipo_date)
    start_date = pd.to_datetime('2000-01-01')
    start_date = start_date if ipo_date < start_date else ipo_date
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    print('downloading fundamental data of %s'%(stock))
    df = create_fundamental_dataframe(stock, start_date, end_date)
    df.to_excel(fname)

def add_fundamental_indicator(df, stock, indicator):
    '''
    在基本面文件中添加indicator数据
    '''
    print('adding indicator %s to %s'%(indicator, stock))
    if indicator in df.columns:
        print('indicator exist')
        return df
    df[indicator] = 0.
    for date in df.index:
        if indicator == 'eps_ttm':
            wdata = w.wss(stock, indicator, 'tradeDate=%s'%(date.strftime('%Y-%m-%d')))
        df[indicator][date] = wdata.Data[0][0]
    return df

def add_fundamental_indicator_to_file(stock, indicator):
    fname = utils.get_fundamental_file_name(stock)
    df = pd.read_excel(fname)
    df = add_fundamental_indicator(df, stock, indicator)
    df.to_excel(fname)

def update_fundamental_file(stock):
    '''
    更新一个基本面数据文件
    '''
    print('updating fundamental data of %s'%(stock))
    fname = utils.get_fundamental_file_name(stock)
    df = pd.read_excel(fname)
    start_date = df.index[-1].strftime('%Y-%m-%d')
    end_date = datetime.datetime.today().strftime('%Y-%m-%d')
    add_df = create_fundamental_dataframe(stock, start_date, end_date)
    if add_df.shape[0] == 0:
        return
    for ind in df.columns:
        if ind not in add_df.columns:
            add_df = add_fundamental_indicator(add_df, stock, ind)
    # add_df = add_fundamental_indicator(add_df, stock, 'eps_ttm')
    df = df.append(add_df)
    df.to_excel(fname)

def create_all_factor_files():
    '''
    创建所有股票的基本面数据文件
    '''
    stocks = utils.get_all_stocks_codes()
    for stock in stocks:
        create_fundamental_file(stock)

def add_factor_all_fundamental_files(indicator):
    '''
    给所有股票基本面数据加入indicator数据
    '''
    stocks = utils.get_all_stocks_codes()
    for stock in stocks:
        add_fundamental_indicator_to_file(stock, indicator)
