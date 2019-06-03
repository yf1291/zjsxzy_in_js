# encoding: utf-8

import pandas as pd
import datetime
from WindPy import w
import os

import utils
import const
import comp
import stock_fund
import bond_fund
import mixed_fund

fund_week = pd.read_excel('D:/Data/fund/fund_weekly.xlsx')
index_week = pd.read_excel('D:/Data/fund/index_weekly.xlsx')

def update_nav(ticker):
    fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
    old_df = pd.read_excel(fname, index_col=0)
    df = fund_week[[ticker]]
    df.columns = ['nav_adj']
    df = old_df.append(df)
    df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    df.index = pd.to_datetime(df.index)
    df = df.loc[~df.index.duplicated(keep='first')]
    df.to_excel(fname)

def update_bond_data():
    bond_df = bond_fund.get_bond_fund()
    for ticker in bond_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    bond_fund.save_bond_fund_panel()

def update_stock_data():
    stock_df = stock_fund.get_stock_fund()
    for ticker in stock_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    stock_fund.save_stock_fund_panel()

def update_mixed_data():
    mixe_df = mixed_fund.get_mixed_fund()
    for ticker in mixe_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
    mixed_fund.save_mixed_fund_panel()

def update_index_data(wind_code):
    fname = '%s/%s.xlsx'%(const.INDEX_HIS_DIR, wind_code)
    df = index_week[[wind_code]]
    df.columns = ['close']
    df.index = pd.to_datetime(df.index)
    df.to_excel(fname)

def update_theme_data():
    df = pd.read_excel(const.theme_file)
    for wind_code in df[u'代码']:
        print('updating %s...'%(wind_code))
        update_index_data(wind_code)

def update_concept_data():
    df = pd.read_excel(const.concept_file)
    for wind_code in df[u'代码']:
        print('updating %s...'%(wind_code))
        update_index_data(wind_code)

def update_sector_data():
    df = pd.read_excel(const.sector_file)
    for wind_code in df[u'代码']:
        print('updating %s...'%(wind_code))
        update_index_data(wind_code)

if __name__ == '__main__':
    # update_bond_data()
    # update_stock_data()
    # update_mixed_data()
    update_theme_data()
    update_concept_data()
    update_sector_data()
