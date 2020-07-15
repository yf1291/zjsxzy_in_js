# encoding: utf-8
import os
import datetime
import calendar
import pandas as pd

import const

def get_all_stocks_codes():
    '''
    得到所有股票代码
    '''
    stocks = [f.rstrip('.xlsx') for f in os.listdir(const.STOCK_DIR)]
    return stocks

def get_stock_file_name(stock):
    '''
    得到某股票的行情文件地址
    '''
    fname = '%s/%s.xlsx'%(const.STOCK_DIR, stock)
    return fname

def get_factor_file_name(stock):
    '''
    得到某股票的factor文件地址
    '''
    fname = '%s/%s.xlsx'%(const.FACTOR_DIR, stock)
    return fname

def get_fundamental_file_name(stock):
    '''
    得到某股票的基本面行情文件地址
    '''
    fname = '%s/%s.xlsx'%(const.FUNDAMENTAL_DIR, stock)
    return fname

def generate_rptdates(start_date, end_date):
    '''
    生成区间内报告期
    '''
    # start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    # end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    start_date, end_date = pd.to_datetime(start_date), pd.to_datetime(end_date)
    years = range(start_date.year, end_date.year + 1)
    months = [3, 6, 9, 12]
    dates = ['%s-%s-%s'%(y, m, calendar.monthrange(y, m)[1]) for y in years for m in months]
    dates = pd.to_datetime(dates)
    dates = dates[(dates > start_date) & (dates < end_date)]
    # dates = dates.map(lambda x: x if x > start_date and x < end_date)
    # dates = [d for d in dates if d > start_date and d < end_date]
    return dates
