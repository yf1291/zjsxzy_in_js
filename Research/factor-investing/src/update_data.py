# encoding: utf-8
import pandas as pd
import os

import utils
import const
import momentum

def create_factor_file(stock):
    '''
    创建一个新的factor文件
    '''
    print('creating factor file of %s...'%(stock))
    fname = utils.get_stock_file_name(stock)
    df = pd.read_excel(fname)
    fname = utils.get_factor_file_name(stock)
    df[const.BASIC_FIELDS].to_excel(fname)

def create_all_factor_files():
    '''
    创建所有factor文件
    '''
    stocks = utils.get_all_stocks_codes()
    for stock in stocks:
        fname = utils.get_factor_file_name(stock)
        if not os.path.exists(fname):
            create_factor_file(stock)

def add_factor_to_dataframe(df, series, factor_name):
    '''
    把series加入到dataframe中，以factor_name为因子的名称
    '''
    if factor_name in df.columns:
        print('factor exists')
        return df
    start_date, end_date = df.index[0], df.index[-1]
    series = series[(series.index >= start_date) & (series.index <= end_date)]
    if series.shape[0] == df.shape[0]:
        df[factor_name] = series
        return df
    else:
        print('shape error')
        raise NotImplementedError

def add_momentum_factor(df, stock):
    '''
    加入momentum因子到dataframe中
    '''
    mom = momentum.get_k_day_return(stock, 20)
    df = add_factor_to_dataframe(df, mom, 'price return 1M')
    mom = momentum.get_k_day_return(stock, 60)
    df = add_factor_to_dataframe(df, mom, 'price return 3M')
    mom = momentum.get_k_day_return(stock, 121)
    df = add_factor_to_dataframe(df, mom, 'price return 6M')
    mom = momentum.get_k_day_return(stock, 242)
    df = add_factor_to_dataframe(df, mom, 'price return 12M')
    return df

def add_factors_to_dataframe(df, stock):
    '''
    把因子加入到dataframe中
    '''
    print('add factor to factor file of %s...'%(stock))
    df = add_momentum_factor(df, stock)
    return df

def add_factors_to_factor_file(stock):
    '''
    把因子加入到factor文件中
    '''
    fname = utils.get_factor_file_name(stock)
    df = pd.read_excel(fname)
    df = add_factors_to_dataframe(df, stock)
    df.to_excel(fname)

def update_factors(stock):
    '''
    更新factor文件
    '''
    fname = utils.get_stock_file_name(stock)
    df = pd.read_excel(fname)
    fname = utils.get_factor_file_name(stock)
    fdf = pd.read_excel(fname)
    df = df[df.index > fdf.index[-1]][const.BASIC_FIELDS]
    if df.shape[0] > 0:
        print('updating factor file of %s...'%(stock))
        df = add_factors_to_dataframe(df, stock)
        if fdf.columns.tolist() == df.columns.tolist():
            fdf = fdf.append(df)
            fname = utils.get_factor_file_name(stock)
            fdf.to_excel(fname)
        else:
            print('columns error')
            raise NotImplemented

def add_factors_to_all_factor_file():
    '''
    添加因子到所有factor文件中
    '''
    stocks = utils.get_all_stocks_codes()
    for stock in stocks:
        fname = utils.get_factor_file_name(stock)
        if os.path.exists(fname):
            add_factors_to_factor_file(stock)

def update_all_factors():
    '''
    更新所有factor文件
    '''
    stocks = utils.get_all_stocks_codes()
    for stock in stocks:
        fname = utils.get_factor_file_name(stock)
        if os.path.exists(fname):
            update_factors(stock)
