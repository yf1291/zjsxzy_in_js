# encoding: utf-8
# 计算个股真实换手率，用以计算其平均持有成本

import pandas as pd
import numpy as np
from scipy.stats import stats
from WindPy import w
import datetime
import os

import const
import utils

def get_codes(index_code):
    df = pd.read_excel("%s/%s.xlsx"%(const.INDEX_DIR, index_code))
    return df["wind_code"].tolist()

def add_row(date):
    '''
    quote不够的时候
    '''
    codes = get_codes('881001.WI')
    everyday = pd.read_excel('D:/everyday.xlsx', index_col=0)
    for code in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, code)
        df = pd.read_excel(fname, index_col=0)
        add_df = everyday.loc[code].to_frame().transpose()
        add_df['date'] = pd.to_datetime([date])
        add_df.set_index('date', inplace=True)
        # print add_df
        if add_df.index[0] > df.index[-1]:
            print('updating %s...'%(code))
            df = df.append(add_df)
            df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
            df.index = pd.to_datetime(df.index)
            # print df.tail()
            df.to_excel(fname)
            # break

def add_column(field):
    # w.start()
    codes = get_codes('881001.WI')
    for code in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, code)
        df = pd.read_excel(fname, index_col=0)
        if field in df.columns:
            continue
        print('add %s...'%(code))
        # start_date, end_date = df.index[0].strftime('%Y-%m-%d'), df.index[-1].strftime('%Y-%m-%d')
        # print start_date, end_date
        # data = w.wsd(code, field, start_date, end_date, "traderType=1;PriceAdj=F")
        # cols = utils.wind2df(data)[field]
        # assert(cols.shape[0] == df.shape[0])
        # df[field] = cols
        # df.to_excel(fname)
        # break

def get_wind_data(code, start_date, end_date):
    w.start()
    fields = "mkt_freeshares,vwap,amt,close,dealnum,volume,mfd_buyamt_a,mfd_sellamt_a,high,low,pe_ttm"
    data = w.wsd(code, fields, start_date, end_date, "traderType=1;PriceAdj=F")
    return utils.wind2df(data)

def append_to_old_excel(code):
    """
    把最新的到今天/昨天的数据加入到旧的表格中
    """
    print('updating %s...'%(code))
    fname = "%s/%s.xlsx"%(const.STOCK_DIR, code)
    # print fname
    df = pd.read_excel(fname, index_col=0)
    # df = df.drop(df.index[-1])
    # df.to_excel(fname)
    # df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    # df.index = pd.to_datetime(df.index)
    # df.to_excel(fname)

    start_date = (df.index[-1] + datetime.timedelta(1)).strftime("%Y-%m-%d")
    if datetime.datetime.now().hour < 15:
        end_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    else:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    if datetime.datetime.strptime(start_date, "%Y-%m-%d") > datetime.datetime.strptime(end_date, "%Y-%m-%d"):
        return

    add_df = get_wind_data(code, start_date, end_date)
    if 'outmessage' in add_df.columns:
        return
    # print add_df
    add_df["turnover"] = add_df["amt"] / add_df["mkt_freeshares"]

    df = df.append(add_df)
    df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    df.index = pd.to_datetime(df.index)
    df.to_excel(fname)

def update_all(index_code=None, start_date="2010-04-01",
                     end_date=(datetime.datetime.today()-datetime.timedelta(1)).strftime("%Y-%m-%d")):
    if index_code == None:
        # 更新文件夹中所有
        codes = [f[:-5] for f in os.listdir(const.STOCK_DIR)]
    else:
        codes = get_codes(index_code)
    for code in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, code)
        if os.path.exists(fname):
            append_to_old_excel(code)
        else:
            print("downloding %s..."%(code))
            df = get_wind_data(code, start_date, end_date)
            df["turnover"] = df["amt"] / df["mkt_freeshares"] # 计算换手率
            df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
            df.index = pd.to_datetime(df.index)
            df.to_excel(fname)

def convert_cost(df, stock=None):
    """
    计算历史的成本和100%换手天数
    """
    if stock == None:
        # 产生一个新的文件
        df.loc[:, "turnover days"] = np.nan # 换手天数
        df.loc[:, "avg cost"] = np.nan # 平均持有成本
        df.loc[:, "profit percentage"] = np.nan # 盈利持仓占比
        k = 0
        dates = df.index
        last_shape = 0
    else:
        # 在原有文件上增加新数据
        fname = "%s/%s"%(const.BY_STOCK_DIR, stock)
        old_df = pd.read_excel(fname, index_col=0)
        '''
        if df.shape[0] != old_df.shape[0]:
            print stock
            return old_df
        else:
            old_df.index = old_df.index.map(lambda x: x.strftime('%Y-%m-%d'))
            old_df.index = pd.to_datetime(old_df.index)
            old_df.to_excel(fname)
            return old_df
        '''
        if old_df.index[-1] == df.index[-1]:
            return old_df
        df.loc[:, "turnover days"] = old_df["turnover days"]
        df.loc[:, "avg cost"] = old_df["avg cost"]
        df.loc[:, "profit percentage"] = old_df["profit percentage"]
        if pd.isnull(old_df["turnover days"][-1]):
            k = 0
        else:
            k = int(old_df.shape[0] - old_df["turnover days"][-1])
        dates = df[df.index > old_df.index[-1]].index
        last_shape = old_df.shape[0]

    for i, index in enumerate(dates):
        if df[df.index <= index]["turnover"].sum() < 1:
            continue
        # 双指针维护一段区间使得该区间内的换手率总和正好大于等于1
        prev_index = df.index[k]
        while df[(df.index >= prev_index) & (df.index <= index)]["turnover"].sum() > 1 and k < df.shape[0] - 1:
            k += 1
            prev_index = df.index[k]
        k -=1
        prev_index = df.index[k]

        # (prev_index, index)这段区间里的换手率总和正好大于等于1
        temp_df = df[(df.index >= prev_index) & (df.index <= index)]
        cost = (temp_df["vwap"] * temp_df["amt"]).sum() / temp_df["amt"].sum()
        current_price = df.loc[index, 'close']
        profit_volume = temp_df[temp_df['vwap'] < current_price]['volume'].sum()
        profit_percentage = profit_volume / temp_df['volume'].sum()
        df.loc[index, "avg cost"] = cost
        # df.loc[index, "turnover days"] = (index - prev_index).days
        df.loc[index, "turnover days"] = i - k + last_shape
        df.loc[index, "profit percentage"] = profit_percentage
    df.loc[:, "current return"] = (df["close"] - df["avg cost"]) / df["avg cost"]
    return df[["turnover days", "avg cost", "close", "profit percentage", "current return"]]

def filter_files(files, index_code):
    index_file = "%s/%s.xlsx"%(const.INDEX_DIR, index_code)
    df = pd.read_excel(index_file)
    codes = set(df["wind_code"].tolist())
    files = [f for f in files if f[:-5] in codes]
    return files

def get_history_turnover(index_code=None):
    """
    计算所有股票的
    1. 历史平均持有成本、
    2. 100%换手天数
    3. 收盘价
    并保存到D:/Data/avg_cost/by stock
    """
    files = [f for f in os.listdir(const.STOCK_DIR) if f.endswith("xlsx")]
    if index_code != None:
        files = filter_files(files, index_code)

    for stock in files:
        fname = "%s/%s"%(const.STOCK_DIR, stock)
        df = pd.read_excel(fname, index_col=0)
        if os.path.exists("%s/%s"%(const.BY_STOCK_DIR, stock)):
            print("processing %s..."%(stock))
            df = convert_cost(df, stock)
        else:
            print("processing %s..."%(stock))
            df = convert_cost(df)
        df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
        df.index = pd.to_datetime(df.index)
        df.to_excel("%s/%s"%(const.BY_STOCK_DIR, stock))

def get_all_by_stock_panel(files):
    """
    给定files中的by_stock的股票历史成本与换手，得到一个综合的panel类型数据
    """
    dic = {}
    for stock in files:
        # print("processing %s..."%(stock))
        fname = '%s/%s'%(const.BY_STOCK_DIR, stock)
        df = pd.read_excel(fname, index_col=0)
        if 'current return' not in df.columns:
            df['current return'] = (df['close'] - df['avg cost']) / df['avg cost']
            df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
            df.index = pd.to_datetime(df.index)
            df.to_excel(fname)
        df.index = pd.to_datetime(df.index)
        dic[stock[:-5]] = df[['current return', 'turnover days', 'profit percentage']]
    pnl = pd.Panel(dic)
    return pnl

"""
def save_by_date(index_code=None):
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    pnl = get_all_by_stock_panel(files)
    pnl.ix[:, :, "current return"] = (pnl.minor_xs("close") - pnl.minor_xs("avg cost")) / pnl.minor_xs("avg cost")
    pnl.ix[:, :, "rolling current return"] = pnl.minor_xs("current return").rolling(window=7).mean()

    for date in pnl.major_axis:
        df = pnl.major_xs(date).T
        df.to_excel("%s/%s.xlsx"%(const.BY_DATE_DIR, date.strftime("%Y-%m-%d")))
"""

"""
def calculate_profit_percentage(index_code=None):
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    for stock in files:
        ticker = stock[:-5]
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
        df = pd.read_excel(fname, index_col=0)
        fname = '%s/%s.xlsx'%(const.BY_STOCK_DIR, ticker)
        cost_df = pd.read_excel(fname, index_col=0)
        df = pd.concat([df, cost_df[['turnover days', 'avg cost']]], axis=1)
        print('processing %s...'%(ticker))
        if 'profit percentage' in df.columns:
            return

        df.loc[:, 'profit percentage'] = np.nan
        df.loc[:, 'current return'] = np.nan
        for index in df.index:
            turnover_days = df.loc[index, 'turnover days']
            current_price = df.loc[index, 'close']
            if not np.isnan(turnover_days):
                start_day = index - datetime.timedelta(turnover_days)
                select_df = df[(df.index >= start_day) & (df.index <= index)]
                profit_volume = select_df[select_df['vwap'] < current_price]['volume'].sum()
                df.loc[index, 'profit percentage'] = profit_volume / select_df['volume'].sum()
                df.loc[index, 'current return'] = (df.loc[index, 'close'] - df.loc[index, 'avg cost']) / df.loc[index, 'avg cost']
        df[['turnover days', 'avg cost', 'close', 'profit percentage', 'current return']].to_excel(fname)
"""

def cal_market_cost(index_code=None):
    """
    计算市场当前的成本与盈亏情况、skewness分布
    保存结果到./data/market.xlsx
    """
    fname = "%s/%s.xlsx"%(const.DATA_DIR, index_code)
    if os.path.exists(fname):
        return
    # 读入全市场所有股票的历史换手天数、持有成本与收盘价
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    if index_code != None:
        files = filter_files(files, index_code)

    pnl = get_all_by_stock_panel(files)

    dates = pnl.major_axis
    market_df = pd.DataFrame(index=dates)
    # 市场平均的换手天数
    market_df.loc[:, "turnover days"] = pnl.minor_xs("turnover days").mean(axis=1)
    # 市场平均的成本
    # market_df.loc[:, "current return"] = ((pnl.minor_xs("close") - pnl.minor_xs("avg cost")) / pnl.minor_xs("avg cost")).mean(axis=1)
    market_df.loc[:, "current return"] = pnl.ix[:, :, "current return"].mean(axis=1)
    # 市场平均盈亏占比
    market_df.loc[:, 'profit percentage'] = pnl.ix[:, :, 'profit percentage'].mean(axis=1)
    # 市场kurtosis, kewness
    """
    market_df["skewness"] = np.nan
    market_df["kurtosis"] = np.nan
    for date in dates:
        d = pnl.major_xs(date).ix["turnover days"].dropna()
        if d.shape[0] >= 400:
            skewness = stats.skew(d)
            kurtosis = stats.kurtosis(d)
            market_df.loc[date, "skewness"] = skewness
            market_df.loc[date, "kurtosis"] = kurtosis
    """
    market_df.index = market_df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    market_df.index = pd.to_datetime(market_df.index)
    market_df.to_excel(fname)
    return market_df

def delete_old_files():
    files = [f for f in os.listdir(const.DATA_DIR) if f.endswith('.csv')]
    for f in files:
        fname = '%s/%s'%(const.DATA_DIR, f)
        os.remove(fname)

def main():
    update_all("881001.WI")
    # add_row('2018-03-22')
    # delete_old_files()
    get_history_turnover()
    files = ['881001.WI', '399006.SZ', '399005.SZ',
             '000016.SH', '000905.SH', '000906.SH',
             '000300.SH', '399550.SZ', 'HSCAIT.HI']
    for f in files:
        fname = '%s/%s.xlsx'%(const.DATA_DIR, f)
        if os.path.exists(fname):
            os.remove(fname)
    cal_market_cost('881001.WI')

def test():
    files = [f for f in os.listdir(const.BY_STOCK_DIR)]
    for f in files:
        print("processing %s..."%(f))
        fname = '%s/%s'%(const.BY_STOCK_DIR, f)
        df = pd.read_excel(fname, index_col=0)
        df["current return"] = (df["close"] - df["avg cost"]) / df["avg cost"]
        df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
        df.index = pd.to_datetime(df.index)
        df.to_excel(fname)

if __name__ == "__main__":
    # test()
    main()
