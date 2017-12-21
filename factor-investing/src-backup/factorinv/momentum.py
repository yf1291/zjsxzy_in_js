# encoding: utf-8

import pandas as pd
import numpy as np
import os

import data

def get_k_day_return(code,
                     days):
    """
    获得k日收益率，计算公式：(当日收盘价-k日前收盘价)/当日收盘价
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    return df['close'].pct_change(periods=days)

def get_k_day_average_return(code,
                             days):
    """
    获得k日平均收益率
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    df["return"] = df['close'].pct_change()
    return df["return"].rolling(window=days).mean()
