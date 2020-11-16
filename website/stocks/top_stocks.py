import pandas as pd
import numpy as np
import os

import const

# 合并公司盈利预测表
def stocks_earning_prediction():
    print('合并盈利预测表')
    filenames = [f for f in os.listdir(const.DATA_DIR) if f.startswith('盈利预测')]
    filename = filenames[0]
    df = pd.read_excel('%s/%s'%(const.DATA_DIR, filename), sheet_name=const.SHEET_NAMES[0], skiprows=2, converters={'股票代码': str})
    for s in const.SHEET_NAMES[1:]:
        temp = pd.read_excel('%s/%s'%(const.DATA_DIR, filename), sheet_name=s, skiprows=2, converters={'股票代码': str})
        df = df.append(temp)
    df = df[['股票代码', '上次预测时间', '最新短评', '最新长评', '2020.4', '2021.4', '2022.4', '2020.11', '2021.11', '2022.11', '2020.2', '2021.2']]
    df.columns = ['股票代码', '上次预测时间', '短评', '长评', '增速(2020)', '增速(2021)', '增速(2022)', 'eps(2020)', 'eps(2021)', 'eps(2022)', 'pe(2020)', 'pe(2021)']

    stocks = pd.read_excel(const.TOP_STOCKS_LIST_FILE, converters={'股票代码': str})
    results = stocks.merge(df, how='left', on=['股票代码'])
    # new_columns = stocks.columns[:2].tolist() + df.columns[1:].tolist() + stocks.columns[2:].tolist()
    # results = results[new_columns]
    results.to_excel(const.TOP_STOCKS_LIST_FILE, index=False)

def main():
    df = pd.read_excel(const.TOP_STOCKS_FILE, converters={'股票代码': str}, sheet_name='A股')
    df['市值（亿元）'] = df['市值（亿元）'].astype(int)
    df['主题行业'] = df['主题行业'].fillna(method='ffill')
    df['大类行业'] = df['大类行业'].fillna(method='ffill')
    df['细分行业'] = df['细分行业'].fillna(method='ffill')

    df = df[['主题行业', '大类行业', '细分行业', '一线龙头', 
             '二线公司', '股票代码', '市值（亿元）', '行业打分', 
             '公司产品/服务']]
    
    df.to_excel(const.TOP_STOCKS_LIST_FILE, index=False)

if __name__ == '__main__':
    main()
    stocks_earning_prediction()
    
