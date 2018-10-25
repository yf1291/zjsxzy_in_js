# encoding: utf-8
import pandas as pd
import numpy as np

import const
import database

def holding_qeury(stock):
    query = 'SELECT t.SecuCode, t.SecuAbbr, s.SecuCode, s.SecuAbbr, fund.ReportDate, fund.SharesHolding, fund.MarketValue \
            FROM MF_KeyStockPortfolio as fund, SecuMain as t, SecuMain as s \
            WHERE s.SecuCode = \'%s\' \
                AND fund.InnerCode = t.InnerCode \
                AND fund.StockInnerCode = s.InnerCode \
                ORDER BY fund.ReportDate DESC, fund.SharesHolding DESC'%(stock)
    df = database.DataFrame_JY(query)
    df.columns = ['FundCode', 'FundAbbr', 'SecuCode', 'SecuAbbr', 'ReportDate', 'SharesHolding', 'MarketValue']
    return df

def quarter_sum_holding(stock):
    df = holding_qeury(stock)
    holding = df.groupby('ReportDate').sum()
    holding['Month'] = holding.index.map(lambda x: x.month)
    holding = holding[holding['Month'].isin([3,6,9,12])].resample('Q').last()
    return holding

def quarter_stock_holding(stock):
    df = holding_qeury(stock)
    df['Month'] = df['ReportDate'].map(lambda x: x.month)
    df['Day'] = df['ReportDate'].map(lambda x: x.day) 
    df = df[(df['Month'].isin([3,6,9,12])) & (df['Day'].isin([30,31]))]
    dates = df['ReportDate'].drop_duplicates().sort_values(ascending=False).values
    for next_date, prev_date in zip(dates, dates[1:]):
    #     print next_date.strftime('%Y-%m-%d'), prev_date_funds.strftime('%Y-%m-%d')
        next_date_funds = df[df['ReportDate'] == next_date]['FundCode']
        prev_date_funds = df[df['ReportDate'] == prev_date]['FundCode']
        codes = prev_date_funds.loc[~prev_date_funds.isin(next_date_funds)].values
        add_df = df[df['FundCode'].isin(codes)].copy()
        add_df = add_df[add_df['ReportDate'] == prev_date]
        add_df['MarketValue'] = 0
        add_df['SharesHolding'] = 0
        add_df['ReportDate'] = next_date
        df = df.append(add_df)
    df = df.sort_values('ReportDate', ascending=False)
    df['Diff'] = df['MarketValue'] - df.groupby('FundCode')['MarketValue'].shift(-1)
    df['Diff'] = df['Diff'].fillna(df['MarketValue'])
    df['SDiff'] = df['SharesHolding'] - df.groupby('FundCode')['SharesHolding'].shift(-1)
    df['SDiff'] = df['SDiff'].fillna(df['SharesHolding'])
    df = df.sort_values(['ReportDate', 'SDiff'], ascending=False)
    df = df.set_index('ReportDate')
    return df

if __name__ == '__main__':
    df = quarter_stock_holding('600519')
    print df
    df.to_excel('%s/stock_holding.xlsx'%(const.WEBSITE_DIR))
    