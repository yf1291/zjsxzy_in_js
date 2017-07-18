# encoding: utf-8
import pandas as pd
import numpy as np

import utils

def factor_weight(df, history_window=484, ascending=False, threshold=0.2):
    """
    根据因子筛选资产

    df: 因子矩阵

    return: 根据因子选择出来的资产01矩阵
    """
    # 得到历史百分位
    df = df.rolling(window=history_window).apply(lambda x: utils.rank_percentile(x))
    df = df.dropna()
    # 排序
    rank_df = df.rank(axis=1, pct=True, ascending=ascending)
    # 得到资产配置
    weight_df = rank_df.copy()
    weight_df[weight_df > threshold] = 0
    weight_df[weight_df != 0] = 1
    return weight_df

def factor_return(df, return_df, history_window=484, ascending=False, threshold=0.2):
    """
    计算因子收益率

    df: 因子矩阵
    return_df: 收益率矩阵

    return: 因子的日收益率
    """
    weight_df = factor_weight(df, history_window=history_window, ascending=ascending, threshold=threshold)
    # 当天的收益要乘以上一天的weight才是当天的portfolio的收益
    weight_df = weight_df.shift(1).dropna()
    return_df = return_df.loc[weight_df.index]
    assert(return_df.shape[0])
    # 等权分配
    weight_df = weight_df.div(weight_df.sum(axis=1), axis='index')
    daily_return = (weight_df * return_df).sum(axis=1)
    return daily_return
