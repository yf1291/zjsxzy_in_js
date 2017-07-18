# encoding: utf-8

import pandas as pd
import numpy as np
import os

import data

def get_k_day_volatility(code,
                         days):
    """
    获得k日波动率
    """
    fname = data.get_filename(code)
    df = data.read_data(fname)
    df["return"] = df["close"].pct_change()
    return df["return"].rolling(window=days).std() * np.sqrt(243)
