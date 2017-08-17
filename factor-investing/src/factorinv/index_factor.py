# encoding: utf-8

import pandas as pd
import numpy as np
import datetime

import utils
import const

def add_factor(index_code, col_name, series):
    fname = '%s/%s.xlsx'%(const.INDEX_FACTOR_DIR, index_code)
    df = pd.read_excel(fname, index_col=0)
    if col_name not in df.columns:
        df[col_name] = series
        df.to_excel(fname)

def pe(index_code):
    """
    得到指数的市值加权pe
    """
    codes = utils.get_index_component(index_code)
    pnl = utils.get_factor_panel(codes, columns='A,B,D')
    # 计算权重
    caps_sum = pnl.minor_xs('caps').sum(axis=1)
    pnl.ix[:, :, 'caps'] = pnl.minor_xs('caps').div(caps_sum, axis='index')
    # 加权pe
    # print pnl.minor_xs('caps').tail()
    # print pnl.minor_xs('pe').tail()
    pe = pnl.minor_xs('caps') * pnl.minor_xs('pe')
    pe = pe.sum(axis=1)
    pe.index = pe.index.map(lambda x: x - datetime.timedelta(seconds=0.005))
    add_factor(index_code, 'pe_weight', pe)
