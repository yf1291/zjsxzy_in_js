# encoding: utf-8
import pandas as pd
import numpy as np
import os

import const

def wind2df(raw_data):
    """
    把wind数据转换成dataframe
    """
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def get_filename(code):
    """
    得到对应代码的本地文件地址
    """
    fname = "%s/%s.xlsx"%(const.STOCK_DIR, code)
    return fname

def get_factor_filename(code):
    """
    得到对应代码的因子本地文件地址
    """
    fname = '%s/%s.xlsx'%(const.FACTOR_DIR, code)
    return fname

def get_fundamental_filename(code):
    """
    得到对应代码的基本面因子本地文件
    """
    fname = '%s/%s.xlsx'%(const.FUNDAMENTAL_DIR, code)
    return fname

def read_data(fname):
    """
    读取excel表，输出dataframe
    """
    if not os.path.exists(fname):
        print('%s file not exists'%(fname))
    else:
        df = pd.read_excel(fname, index_col=0)
        return df

def save_factor(code, factor_name, series):
    """
    把factor计算结果保存到文件
    """
    fname = get_factor_filename(code)
    factor_df = read_data(fname)
    series = series[(series.index >= factor_df.index[0]) & (series.index <= factor_df.index[-1])]
    # assert(factor_df.shape[0] == series.shape[0])
    if factor_name in factor_df.columns:
        print('factor already exists')
    else:
        factor_df[factor_name] = series
        factor_df.to_excel(fname)
