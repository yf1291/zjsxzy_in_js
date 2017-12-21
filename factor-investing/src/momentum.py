# encoding: utf-8
import pandas as pd

import utils 

def get_k_day_return(stock,
                     days):
    """
    获得k日收益率，计算公式：(当日收盘价-k日前收盘价)/当日收盘价
    """
    fname = utils.get_stock_file_name(stock)
    df = pd.read_excel(fname)
    return df['close'].pct_change(periods=days)

def get_k_day_average_return(stock,
                             days):
    """
    获得k日平均收益率
    """
    fname = utils.get_stock_file_name(code)
    df = pd.read_excel(fname)
    df["return"] = df['close'].pct_change()
    return df["return"].rolling(window=days).mean()
