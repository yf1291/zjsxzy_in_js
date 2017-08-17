# encoding: utf-8

import pandas as pd
import numpy as np
import os

import defensive
import momentum
import fundamental
import data
import const
import utils
import const

def create_new_file(code):
    """
    添加一个因子文件
    """
    print('creating factor %s...'%(code))
    fname = '%s/%s.xlsx'%(const.STOCK_DIR, code)
    temp = pd.read_excel(fname, index_col=0)
    df = temp[['mkt_freeshares', 'turnover', 'pe_ttm', 'volume']]
    # 市值因子、换手率、市盈率、成交量
    df.columns = ['caps', 'turnover', 'pe', 'volume']

    # 持仓成本、换手天数、价格、盈利占比
    fname = '%s/%s.xlsx'%(const.STOCK_COST_DIR, code)
    temp = pd.read_excel(fname, index_col=0)
    assert(temp.shape[0] == df.shape[0])
    df = df.merge(temp, left_index=True, right_index=True, how='inner')

    fname = '%s/%s.xlsx'%(const.FACTOR_DIR, code)
    df.to_excel(fname)

def create_factor():
    '''
    创建因子文件
    '''
    codes = utils.get_all_codes()
    for code in codes:
        fname = '%s/%s.xlsx'%(const.FACTOR_DIR, code)
        if not os.path.exists(fname):
            create_new_file(code)
        else:
            # 更新因子，待补充
            pass

def add_volatility():
    '''
    添加波动率因子
    '''
    codes = utils.get_all_codes()
    for code in codes:
        print('adding volatility factor for %s...'%(code))
        # 1 month volatility
        vol1M = defensive.get_k_day_volatility(code, 23)
        data.save_factor(code, 'volatility 1M', vol1M)

def add_momentum():
    '''
    添加动量因子
    '''
    codes = utils.get_all_codes()
    for code in codes:
        print('adding momentum factor for %s...'%(code))
        # 6 month momentum
        mom6M = momentum.get_k_day_return(code, 121)
        data.save_factor(code, 'momentum 6M', mom6M)
        # 12 month momentum
        mom12M = momentum.get_k_day_return(code, 243)
        data.save_factor(code, 'momentum 12M', mom12M)

def add_fundamental():
    '''
    添加基本面因子
    '''
    codes = utils.get_all_codes()
    for code in codes:
        print('adding roic factor for %s...'%(code))
        # ROIC
        roic = fundamental.get_roic(code)
        data.save_factor(code, 'roic', roic)
        print('adding roe factor for %s...'%(code))
        # ROE
        roe = fundamental.get_roe(code)
        data.save_factor(code, 'roe', roe)
        print('adding roa factor for %s...'%(code))
        # ROA
        roa = fundamental.get_roa(code)
        data.save_factor(code, 'roa', roa)

if __name__ == '__main__':
    # add_momentum()
    # create_factor()
    add_fundamental()
