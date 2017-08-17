# encoding: utf-8
import pandas as pd
import numpy as np
import pyfolio as pf
import os

import const

def rank_percentile(array):
    """
    返回s的最后一个元素在s中的分位值
    """
    s = pd.Series(array)
    s = s.rank(pct=True)
    return s.iloc[-1]

def get_all_codes():
    '''
    返回所有股票代码
    '''
    codes = [code.rstrip('.xlsx') for code in os.listdir(const.STOCK_DIR)]
    return codes

def get_index_component(index_code):
    '''
    获取指数的成分股
    '''
    index_file = "%s/%s.xlsx"%(const.INDEX_COMP_DIR, index_code)
    df = pd.read_excel(index_file)
    return df['wind_code'].tolist()

def get_all_panel(DATA_DIR, files):
    """
    给定一堆资产目录和文件名，返回Panel
    """
    dic = {}
    for f in files:
        df = pd.read_excel('%s/%s'%(DATA_DIR, f), index_col=0)
        dic[f.rstrip('.xlsx')] = df
    pnl = pd.Panel(dic)
    return pnl

def get_factor_panel(codes, columns):
    """
    给定一堆wind代码和要获取的因子名称，返回Panel
    """
    dic = {}
    for code in codes:
        fname = '%s/%s.xlsx'%(const.FACTOR_DIR, code)
        df = pd.read_excel(fname, index_col=0, parse_cols=columns)
        dic[code] = df
    pnl = pd.Panel(dic)
    return pnl

def get_accumulated_return(daily_return):
    """
    得到累计收益率
    """
    return (1 + daily_return).cumprod()

def get_metrics(daily_return):
    """
    得到评价
    """
    an_ret = pf.empyrical.annual_return(daily_return)
    sharpe = pf.empyrical.sharpe_ratio(daily_return)
    vol = pf.empyrical.annual_volatility(daily_return)
    maxdraw = pf.empyrical.max_drawdown(daily_return)
    print 'Annual return: %.2f%%'%(an_ret*100)
    print 'Sharpe ratio: %.2f'%(sharpe)
    print 'Annual volatility: %.2f%%'%(vol*100)
    print 'Max drawdown: %.2f%%'%(maxdraw*100)
