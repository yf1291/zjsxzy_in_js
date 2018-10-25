# encoding: utf-8
import pandas as pd
import numpy as np
import datetime
from WindPy import w

import const
import database

w.start()

def holding_query():
    query = 'SELECT fdo.InvestAdvisorAbbrName, t.SecuAbbr, s.SecuCode, s.SecuAbbr, f.ReportDate, f.SharesHolding, f.MarketValue \
            FROM MF_KeyStockPortfolio as f, SecuMain as t, SecuMain as s, MF_FundArchives as fd, MF_InvestAdvisorOutline as fdo \
            WHERE f.InnerCode = t.InnerCode \
                AND f.StockInnerCode = s.InnerCode \
                AND fd.InnerCode = f.InnerCode \
                AND fd.InvestAdvisorCode = fdo.InvestAdvisorCode \
                ORDER BY f.ReportDate DESC, f.SharesHolding DESC'
    df = database.DataFrame_JY(query)
    df.columns = ['InvestAdvisorAbbrName', 'FundAbbr', 'SecuCode', 'SecuAbbr', 'ReportDate', 'SharesHolding', 'MarketValue']
    return df

def quarter_stock_holding(comp):
    comp_df = comp.groupby(['ReportDate', 'SecuAbbr', 'SecuCode']).sum()
    comp_df = comp_df.reset_index(level=[1]).reset_index(level=[1])
    comp_df['Month'] = comp_df.index.map(lambda x: x.month)
    comp_df['Day'] = comp_df.index.map(lambda x: x.day)
    comp_df = comp_df[(comp_df['Month'].isin([3,6,9,12])) & (comp_df['Day'].isin([30,31]))]
    comp_df['ReportDate'] = comp_df.index
    dates = comp_df.index.drop_duplicates().sort_values(ascending=False).values
    for next_date, prev_date in zip(dates, dates[1:]):
        next_date_hold = comp_df[comp_df.index == next_date]['SecuAbbr']
        prev_date_hold = comp_df[comp_df.index == prev_date]['SecuAbbr']
        codes = prev_date_hold.loc[~prev_date_hold.isin(next_date_hold)].values
        add_df = comp_df[comp_df['SecuAbbr'].isin(codes)].copy()
        add_df = add_df[add_df.index == prev_date]
        add_df['MarketValue'] = 0
        add_df['SharesHolding'] = 0
        add_df['ReportDate'] = next_date
        comp_df = comp_df.append(add_df)
    comp_df = comp_df.sort_values('ReportDate', ascending=False)
    comp_df['Diff'] = comp_df['MarketValue'] - comp_df.groupby('SecuAbbr')['MarketValue'].shift(-1)
    comp_df['Diff'] = comp_df['Diff'].fillna(comp_df['MarketValue'])
    comp_df['SDiff'] = comp_df['SharesHolding'] - comp_df.groupby('SecuAbbr')['SharesHolding'].shift(-1)
    comp_df['SDiff'] = comp_df['SDiff'].fillna(comp_df['SharesHolding'])
    comp_df = comp_df.sort_values(['ReportDate', 'SDiff'], ascending=False)
    comp_df = comp_df.set_index('ReportDate')
    comp_df = comp_df[comp_df.index == comp_df.index[0]]
    comp_df = comp_df[['SecuCode', 'SecuAbbr', 'SharesHolding', 'MarketValue', 'Diff', 'SDiff']]
    return comp_df

def wind_code(x):
    if x.startswith('60'):
        return x + '.SH'
    else:
        return x + '.SZ'

def update_data(df):
    today = datetime.datetime.today()
    tot = quarter_stock_holding(df)
    data = w.wss(tot['SecuCode'].apply(lambda x: wind_code(x)).tolist(), 'industry_citic',
                 'tradeDate=%s;industryType=4'%(today.strftime('%Y%m%d')))
    tot['industry'] = data.Data[0]
    tot.to_excel(u'%s/%s.xlsx'%(const.COMP_STOCK_HOLD_DIR, u'全部'))
    for name in df['InvestAdvisorAbbrName'].unique():
        print name
        comp = df[df['InvestAdvisorAbbrName'] == name]
        comp = quarter_stock_holding(comp)
        data = w.wss(comp['SecuCode'].apply(lambda x: wind_code(x)).tolist(), 'industry_citic',
                     'tradeDate=%s;industryType=4'%(today.strftime('%Y%m%d')))
        comp['industry'] = data.Data[0]
        comp.to_excel(u'%s/%s.xlsx'%(const.COMP_STOCK_HOLD_DIR, name))

if __name__ == '__main__':
    df = holding_query()
    update_data(df)