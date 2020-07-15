# encoding: utf-8

import pandas as pd
import numpy as np
import os
from WindPy import w

import data
import const
import utils

def get_pe_ratio(code,
                 start_date,
                 end_date):
    """
    获得PE
    """
    w.start()
    raw_data = w.wsd(code, 'pe_ttm', start_date, end_date)
    df = data.wind2df(raw_data)
    return df["pe_ttm"]

def get_pe_ratio_percentile(code,
                            days,
                            start_date,
                            end_date):
    """
    获得PE历史百分比
    """
    pe = get_pe_raio(code, start_date, end_date)
    pe_percent = pe.rolling(window=days).apply(utils.rank_percentile)
    return pe_percent
