import pandas as pd
import numpy as np
import datetime as dt
import os
from WindPy import w

pd.options.display.float_format = "{:.2f}".format

import const
import utils

w.start()
end_date = dt.datetime.today() - dt.timedelta(3)
start_date = end_date - dt.timedelta(31)
today = end_date.strftime('%Y%m%d')
industry = pd.read_excel(const.INDUSTRY_FILE, sheet_name='申万二级行业')
industry2theme = {}
for col in industry.columns:
    for i in industry[col]:
        if type(i) == str:
            industry2theme[i.rstrip('(申万)')] = col
            industry2theme[i.rstrip('Ⅱ(申万)')] = col
industry2theme['证券Ⅱ'] = '金融地产'
stock2theme = {}
stock_cate = {'内部股票池':set(), 
              '外部股票池': set(), 
              '基金重仓股票池': set(), 
              '北向资金重仓股票池': set()}

# 内部、外部股票池
def inside_outside_stocks():
    strategy = pd.read_excel(const.INSIDE_OUTSIDE_STOCKS_FILE)

    for c, s in zip(strategy['一级行业'], strategy['内部股票池']):
        if not pd.isna(s):
            stock_cate['内部股票池'].add(s)
            if not s in stock2theme:
                stock2theme[s] = c
    for c, s in zip(strategy['一级行业'], strategy['外部股票池']):
        if not pd.isna(s):
            stock_cate['外部股票池'].add(s)
            if not s in stock2theme:
                stock2theme[s] = c

# 基金重仓股
def fund_stocks():
    fund = pd.read_excel(const.FUND_STOCKS_FILE, skiprows=1)

    for c, s in zip(fund['主题行业分类'], fund['股票名称']):
        if not pd.isna(s):
            s = s.replace(' ', '').replace('Ａ', 'A')
            stock_cate['基金重仓股票池'].add(s)
            if not s in stock2theme:
                stock2theme[s] = c

def calculate_connect_stocks():
    print('提取北向资金重仓股')
    data = w.wset("shstockholdings",
                  "date=%s;field=wind_code,sec_name,hold_stocks,holding_marketvalue,calculate_ratio"%(today))
    sh = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes)
    sh = sh.T
    data = w.wset("szstockholdings",
                  "date=%s;field=wind_code,sec_name,hold_stocks,holding_marketvalue,calculate_ratio"%(today))
    sz = pd.DataFrame(data.Data, index=data.Fields, columns=data.Codes)
    sz = sz.T
    df = sh.append(sz)
    df = df.sort_values('calculate_ratio', ascending=False)
    df.index = np.arange(df.shape[0])
    df = df.drop(df.index[200:])
    data = w.wss(df['wind_code'].tolist(), 'industry_sw', 'industryType=2')
    df['industry_sw'] = data.Data[0]
    df['industry_theme'] = [industry2theme[x] for x in df['industry_sw']]
    df.columns = ['股票代码', '股票名称', '持仓股数', '持仓市值', '占流通市值比例', '申万二级行业', '主题行业分类']
    df.to_excel(const.CONNECT_STOCKS_FILE, index=False)

# 北向资金重仓股
def connect_stocks():
    connect = pd.read_excel(const.CONNECT_STOCKS_FILE)

    for c, s in zip(connect['主题行业分类'], connect['股票名称']):
        if not pd.isna(s):
            stock_cate['北向资金重仓股票池'].add(s)
            if not s in stock2theme:
                stock2theme[s] = c

# 合并股票池
def stocks_list():
    df = pd.DataFrame(index=list(stock2theme.values()))
    df.index.name = '主题行业'
    df['股票名称'] = list(stock2theme.keys())
    df['内部(40%)'] = [1 if s in stock_cate['内部股票池'] else np.NaN for s in df['股票名称']]
    df['外部(20%)'] = [1 if s in stock_cate['外部股票池'] else np.NaN for s in df['股票名称']]
    df['基金重仓(30%)'] = [1 if s in stock_cate['基金重仓股票池'] else np.NaN for s in df['股票名称']]
    df['外资重仓(10%)'] = [1 if s in stock_cate['北向资金重仓股票池'] else np.NaN for s in df['股票名称']]
    df['总分'] = df[df.columns[1:]].mul([0.4, 0.2, 0.3, 0.1], axis=1).sum(axis=1)
    industry = ['金融地产', '可选消费', '必选医药', '信息科技', '其他经济敏感', '其他经济不敏感']
    category_industry = pd.api.types.CategoricalDtype(categories=industry, ordered=True)
    df.index = df.index.astype(category_industry)
    df.sort_index().to_excel(const.STOCKS_LIST_FILE)

# 合并公司盈利预测表
def stocks_earning_prediction():
    print('合并盈利预测表')
    filenames = [f for f in os.listdir(const.DATA_DIR) if f.startswith('盈利预测')]
    filename = filenames[0]
    df = pd.read_excel('%s/%s'%(const.DATA_DIR, filename), sheet_name=const.SHEET_NAMES[0], skiprows=2)
    for s in const.SHEET_NAMES[1:]:
        temp = pd.read_excel('%s/%s'%(const.DATA_DIR, filename), sheet_name=s, skiprows=2)
        df = df.append(temp)
    df = df[['公司名称', '上次预测时间', '最新短评', '最新长评', '2020.4', '2021.4', '2022.4', '2020.11', '2021.11', '2022.11']]
    df.columns = ['股票名称', '上次预测时间', '短评', '长评', '增速(2020)', '增速(2021)', '增速(2022)', 'eps(2020)', 'eps(2021)', 'eps(2022)']

    stocks = pd.read_excel(const.STOCKS_LIST_FILE)
    results = stocks.merge(df, how='left', on=['股票名称'])
    new_columns = stocks.columns[:2].tolist() + df.columns[1:].tolist() + stocks.columns[2:].tolist()
    results = results[new_columns]
    results.to_excel(const.STOCKS_LIST_FILE, index=False)

# 合并股票基础数据
def stocks_infomation():
    print('合并股票基础数据')
    codes = pd.read_excel(const.STOCKS_CODE_FILE, skiprows=4, index_col=0)
    codes.columns = ['股票代码', '股票名称']
    hkcodes = pd.read_excel(const.HKSTOCKS_CODE_FILE, skiprows=4, index_col=0)
    hkcodes.columns = ['股票代码', '股票名称']
    codes = codes.merge(hkcodes, on=['股票名称'], how='outer')
    codes['股票代码'] = [codes.loc[i, '股票代码_y'] if pd.isna(codes.loc[i, '股票代码_x']) else codes.loc[i, '股票代码_x'] for i in codes.index]
    codes = codes[['股票名称', '股票代码']]

    stocks = pd.read_excel(const.STOCKS_LIST_FILE, 
                           converters={'增速(2020)': utils.percent2float,
                                       '增速(2021)': utils.percent2float,
                                       '增速(2022)': utils.percent2float})
    results = stocks.merge(codes, how='left', on=['股票名称'])

    # 计算股票动量
    data = w.wsd(results['股票代码'].tolist(), 'close', start_date, end_date)
    # print(data.Data)
    prices = pd.DataFrame(data.Data, index=data.Codes, columns=data.Times)
    prices = prices.T
    returns = prices.pct_change().mean()
    returns.index = np.arange(results.shape[0])
    results['动量'] = returns

    data = w.wss(','.join(results['股票代码'].dropna().tolist()),
                 "industry_sw,close",
                 "industryType=3;tradeDate=%s;priceAdj=U;cycle=D"%(today))
    info = pd.DataFrame(data.Data, 
                        index=['细分行业', '收盘价'],
                        columns=data.Codes)
    info = info.T
    info['细分行业'] = info['细分行业'].astype(str).map(lambda x: x.rstrip('Ⅲ'))
    info['股票代码'] = info.index
    results = results.merge(info, how='left', on=['股票代码'])
    results['pe(2020)'] = results['收盘价'] / results['eps(2020)']
    results['pe(2021)'] = results['收盘价'] / results['eps(2021)']
    results['pe(2022)'] = results['收盘价'] / results['eps(2022)']

    results_columns = ['主题行业', '股票名称', '细分行业', '收盘价', '上次预测时间', '短评', '长评', '动量',
                       '增速(2020)', '增速(2021)', '增速(2022)', 'pe(2020)', 'pe(2021)', 'pe(2022)',
                       '内部(40%)', '外部(20%)', '基金重仓(30%)', '外资重仓(10%)', '总分']
    results = results[results_columns]
    results.to_excel(const.STOCKS_LIST_FILE, index=False)

def core_stocks_pool():
    print("提取核心股票池")
    df = pd.read_excel(const.STOCKS_LIST_FILE)
    df['核心(10)'] = np.NaN
    df['核心(20)'] = np.NaN
    industry = ['可选消费', '必选医药', '信息科技']
    for i in industry:
        for k in [10, 20]:
            temp = df[df['主题行业'] == i].sort_values('总分', ascending=False)[:k]
            df.loc[temp.index, '核心(%s)'%(k)] = 'o'
    df.to_excel(const.STOCKS_LIST_FILE, index=False)

if __name__ == '__main__':
    calculate_connect_stocks()
    inside_outside_stocks()
    fund_stocks()
    connect_stocks()
    stocks_list()
    stocks_earning_prediction()
    stocks_infomation()
    core_stocks_pool()