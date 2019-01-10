# encoding: utf-8

from WindPy import w
import datetime
import pandas as pd
import numpy as np
import os

import const
import utils

ASSETS_NAME = {"881001.WI": u"万得全A指数",
                "HSI.HI": u"恒生指数",
                "SPX.GI": u"标普500",
                "SX5P.GI": u"欧洲50",
                "CBA00101.CS": u"中债新综合财富指数",
                "SPGSCITR.SPI": u"商品总指数",
                "USDX.FX": u"美元指数",
                "USDCNY.FX": u"美元兑人民币",
                "AU9999.SGE": u"黄金9999（民生银行）",
                "B.IPE": u"WTI原油",
                "CA.LME": u"LME铜",
                "VIX.GI": u"隐含波动率指数",
                "HSCAIT.HI": u'行业龙头指数'}


def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[str(field.lower())] = data
    df = pd.DataFrame(dic, index=raw_data.Times)
    return df

def download_wind_data(symbol, start_date, end_date):
    print start_date, end_date
    w.start()
    data = w.wsd(symbol, 'close', start_date, end_date)
    df = pd.DataFrame({'date': data.Times, 'close': np.array(data.Data[0])})
    df['date'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    return df

def download_data(symbol,
            start_date="2000-01-01",
            end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    if os.path.exists(fname):
        df = pd.read_csv(fname)
        start_date = utils.next_date(df['date'].iloc[-1])
        app_df = download_wind_data(symbol, start_date, end_date)
        df = df.append(app_df)
        df.to_csv(fname, index=False)
    else:
        df = download_wind_data(symbol, start_date, end_date)
        df.to_csv(fname, index=False)

    # w.start()
    # raw_data = w.wsd(symbol, "close", beginTime=start_date, endTime=end_date)
    # dic = {'date': raw_data.Times}
    # for data, field in zip(raw_data.Data, raw_data.Fields):
        # dic[str(field.lower())] = data
    # df = pd.DataFrame(dic)
    # df['date'] = df['date'].map(lambda x: x.strftime("%Y-%m-%d"))
    # df.to_csv(fname, index=False)

def download_all(symbols,
                start_date="2000-01-01",
                end_date=datetime.datetime.today().strftime("%Y-%m-%d")):
    # df = pd.read_excel('D:/wind_data.xlsx')
    for symbol in symbols:
        print symbol
        # out = df[[symbol]].copy()
        # out.columns = ['close']
        # out['date'] = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
        # out = out.replace([0.0], np.NAN)
        # fname = '%s/%s.csv'%(const.DATA_DIR, symbol)
        # out.to_csv(fname, index=False)
        download_data(symbol, start_date=start_date, end_date=end_date)

def get_component(symbols,
                  date=datetime.datetime.today().strftime("%Y-%m-%d")):
    w.start()
    data = w.wset("sectorconstituent","date=%s;windcode=%s"%(date, symbols))
    df = pd.DataFrame(np.array(data.Data).T, columns=data.Fields)
    df = df[["sec_name", "wind_code"]]
    df.to_excel("%s/%s.xlsx"%(const.INDEX_DIR, symbols), index=False)

def column_append(ticker,
                  fields,
                  start_date='2015-01-01',
                  end_date='2017-03-28'):
    fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
    old_df = pd.read_excel(fname, index_col=0)
    for col in fields.split(','):
        if col in old_df.columns:
            return

    print ticker
    data = w.wsd(ticker, fields, start_date, end_date, "traderType=1")
    df = wind2df(data)
    assert(df.shape[0] == old_df.shape[0])
    df = old_df.join(df)
    df.to_excel(fname)

def get_stock_information():
    w.start()
    df = pd.read_excel('%s/volume_top50.xlsx'%(const.DATA_DIR))
    if 'turnover' not in df.columns:
        df['turnover'] = df['amt'] / df['mkt_freeshares']
    today = datetime.datetime.today().strftime('%Y%m%d')
    if 'industry' not in df.columns:
        data = w.wss(df.index.tolist(), "industry_citic","tradeDate=%s;industryType=4"%(today))
        df['industry'] = data.Data[0]
    if 'sec_name' not in df.columns:
        data = w.wss(df.index.tolist(), 'sec_name')
        df['sec_name'] = data.Data[0]
    df.to_excel('%s/volume_top50.xlsx'%(const.DATA_DIR))

def get_stock_price_panel():
    # files = [f for f in os.listdir(const.STOCK_DIR)]
    files = [f.rstrip('.xlsx') for f in os.listdir(const.STOCK_DIR)]
    columns = ['amt', 'volume', 'mkt_freeshares']
    dic = {}
    vdf = pd.DataFrame({}, columns=columns, index=files)
    for f in files:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, f)
        df = pd.read_excel(fname, index_col=0)
        dic[f] = df[['close', 'mkt_freeshares', 'volume']]
        vdf.loc[f, :] = df[columns].iloc[-1]
    pnl = pd.Panel(dic)
    print pnl.major_axis.shape
    pnl.to_pickle('D:/Data/price.pkl')
    vdf = vdf.sort_values('amt', ascending=False).head(n=50)
    vdf.to_excel('%s/volume_top50.xlsx'%(const.DATA_DIR))

def main():
    # get_stock_price_panel()
    index = ['000016.SH', '000300.SH', '000905.SH', '000906.SH', '399005.SZ', '399006.SZ', '881001.WI', 'HSCAIT.HI', '000903.SH', '399673.SZ']
    for i in index:
        get_component(i)
    # get_stock_information()
    download_all(ASSETS_NAME.keys())

if __name__ == "__main__":
    main()
