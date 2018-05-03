# encoding: utf-8
import pandas as pd
import numpy as np

import const
import database

def quarter_stock_holding(stock):
    query = 'SELECT t.SecuCode, t.SecuAbbr, s.SecuCode, s.SecuAbbr, fund.ReportDate, fund.SharesHolding \
            FROM MF_KeyStockPortfolio as fund, SecuMain as t, SecuMain as s \
            WHERE s.SecuCode = \'%s\' \
                AND fund.InnerCode = t.InnerCode \
                AND fund.StockInnerCode = s.InnerCode \
                ORDER BY fund.ReportDate DESC, fund.SharesHolding DESC'%(stock)
    df = database.DataFrame_JY(query)
    df = df.set_index('ReportDate')
    df.columns = ['FundCode', 'FundAbbr', 'SecuCode', 'SecuAbbr', 'SharesHolding']
    df['Diff'] = df['SharesHolding'] - df.groupby('FundCode')['SharesHolding'].shift(-1)
    df['Diff'] = df['Diff'].fillna(df['SharesHolding'])
    return df

if __name__ == '__main__':
    df = quarter_stock_holding('600519')
    print df
    df.to_excel('%s/stock_holding.xlsx'%(const.WEBSITE_DIR))
    