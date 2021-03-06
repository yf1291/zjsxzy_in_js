# encoding: utf-8
import pandas as pd
import os

import wind_data
import const

def get_dataframe(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    if not os.path.exists(fname):
        return pd.DataFrame()
    dataframe = pd.read_csv(fname)
    dataframe.dropna(inplace=True)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe['return'] = dataframe['close'].pct_change()
    dataframe = dataframe.set_index('date')
    dataframe.index.name = "date"
    dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]

    # dataframe['mom5'] = dataframe['return'].pct_change(periods=5) # 过去5日收益率
    # dataframe['mom20'] = dataframe['return'].pct_change(periods=20) # 过去一个月收益率
    # dataframe['mom40'] = dataframe['close'].pct_change(periods=40) # 过去两个月收益率
    # dataframe['mom60'] = dataframe['close'].pct_change(periods=60) # 过去三个月收益率
    # dataframe["mom30"] = dataframe["return"].rolling(window=30).mean() # 过去30个交易日平均收益
    dataframe['mom20'] = dataframe['return'].rolling(window=20).mean() # 过去20天平均收益
    dataframe['mom60'] = dataframe['return'].rolling(window=60).mean() # 过去60天平均收益
    dataframe["mom121"] = dataframe["return"].rolling(window=121).mean() # 过去半年平均收益
    dataframe["mom242"] = dataframe["return"].rolling(window=242).mean() # 过去一年平均收益
    # dataframe = dataframe.resample('BM').last()
    return dataframe
