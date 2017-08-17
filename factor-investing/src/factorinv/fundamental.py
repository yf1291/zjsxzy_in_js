# encoding: utf-8
import pandas as pd

import const
import data

def merge_fundamental(code):
    '''
    因为基本面数据是季度更新，时间轴上跟stock数据不同，故先需要做merge操作
    '''
    fname = data.get_fundamental_filename(code)
    fdf = data.read_data(fname)
    fname = data.get_filename(code)
    df = data.read_data(fname)
    dates = df.index
    df = df.merge(fdf, left_index=True, right_index=True, how='outer')
    df = df.fillna(method='ffill')
    df = df.loc[dates]
    return df

def get_roic(code):
    '''
    获得ROIC，日期要重新生成以跟stock原数据对应
    '''
    df = merge_fundamental(code)
    return df['roic']

def get_roe(code):
    '''
    获得ROE，日期要重新生成以跟stock原数据对应
    '''
    df = merge_fundamental(code)
    return df['roe']

def get_roa(code):
    '''
    获得ROA，日期要重新生成以跟stock原数据对应
    '''
    df = merge_fundamental(code)
    return df['roa']
