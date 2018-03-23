# encoding: utf-8
import pandas as pd
from WindPy import w
import os
import datetime

import const
import utils

w.start()

def download_margin(wind_code, start_date, end_date):
    fields = "mrg_long_bal,mrg_long_amt,mrg_short_bal,margin_saletradingamount"
    data = w.wsd(wind_code, fields, start_date, end_date)
    df = utils.wind2df(data)
    return df

def download_economy_data(codes, start_date, end_date):
    data = w.edb(codes, start_date, end_date)
    df = utils.wind2df_economy(data)
    return df

def update_margin_all():
    ldf = pd.read_excel(const.MARGIN_FILE)
    ldf = ldf[ldf['bid_type'] == u'融资标的']
    for wind_code, date in zip(ldf['wind_code'], ldf['effective_date']):
        fname = '%s/%s.xlsx'%(const.MARGIN_DIR, wind_code)
        end_date = utils.get_end_date()
        if not os.path.exists(fname):
            print 'downloading %s...'%(wind_code)
            df = download_margin(wind_code, date, end_date)
            df.to_excel(fname)
        else:
            print 'updating %s...'%(wind_code)
            df = pd.read_excel(fname)
            start_date = utils.next_date(df.index[-1])
            add_df = download_margin(wind_code, start_date, end_date)
            df = df.append(add_df)
            df.to_excel(fname)
            break

def update_economy():
    df = pd.read_excel(const.LIST_FILE)
    df = df.dropna()
    for name, code in zip(df[u'名称'], df[u'代码']):
        print name, code
        fname = '%s/%s.xlsx'%(const.MARKET_DIR, name)
        end_date = datetime.date.today()
        if not os.path.exists(fname):
            start_date = '1990-01-01'
            df = download_economy_data(code, start_date, end_date)
        else:
            df = pd.read_excel(fname)
            start_date = df.index[-1] + datetime.timedelta(1)
            app_df = download_economy_data(code, start_date, end_date)
            if pd.to_datetime(app_df.index[0]) >= start_date:
                df = df.append(app_df)
        df.to_excel(fname)

if __name__ == '__main__':
    update_margin_all()
    # update_economy()
