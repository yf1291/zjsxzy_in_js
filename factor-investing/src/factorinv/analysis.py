# encoding: utf-8
import pandas as pd
import numpy as np

import utils

def factor_weight(df,
                  history_window=484,
                  ascending=False,
                  threshold=0.2,
                  frequency='D',
                  relative=False):
    """
    根据因子筛选资产

    df: 因子矩阵

    return: 根据因子选择出来的资产01矩阵
    """
    # 得到历史百分位
    if relative == True:
        df = df.rolling(window=history_window).apply(lambda x: utils.rank_percentile(x))
    # 排序
    if frequency == 'D':
        rank_df = df.rank(axis=1, pct=True, ascending=ascending)
    if frequency == 'M':
        months = pd.Series(df.index.map(lambda x: (x.year, x.month)), index=df.index)
        rebalance_dates = months.drop_duplicates(keep='last').index
        rank_df = df.loc[rebalance_dates].rank(axis=1, pct=True, ascending=ascending)
    # 得到资产配置
    rank_df = rank_df.fillna(0)
    rank_df[rank_df > threshold] = 0
    rank_df[rank_df != 0] = 1
    weight_df = pd.DataFrame(columns=df.columns, index=df.index)
    weight_df.loc[rank_df.index] = rank_df
    # weight_df.iloc[0] = 0
    weight_df = weight_df.fillna(method='ffill')
    return weight_df

def calculate_return(weight_df, return_df):
    """
    计算组合收益率

    weight_df: 资产配置权重矩阵
    return_df: 收益率矩阵

    return: 组合日收益率
    """
    # 当天的收益要乘以上一天的weight才是当天的portfolio的收益
    weight_df = weight_df.shift(1).dropna()
    return_df = return_df.loc[weight_df.index]
    assert(return_df.shape[0] != 0)
    daily_return = (weight_df * return_df).sum(axis=1)
    return daily_return

def factor_return(df,
                  return_df,
                  history_window=484,
                  ascending=False,
                  threshold=0.2,
                  frequency='D'):
    """
    计算因子收益率

    df: 因子矩阵
    return_df: 收益率矩阵

    return: 因子的日收益率
    """
    weight_df = factor_weight(df, history_window=history_window,
                              ascending=ascending, threshold=threshold, frequency=frequency)
    # 等权分配
    weight_df = weight_df.div(weight_df.sum(axis=1), axis='index')
    return calculate_return(weight_df, return_df)
