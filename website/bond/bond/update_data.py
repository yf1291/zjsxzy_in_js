# encoding: utf-8

import pandas as pd
from WindPy import w
import datetime

import const
import utils

w.start()

def new_df(df):
    start_date = pd.to_datetime(df.index[-1]) + datetime.timedelta(1)
    end_date = datetime.datetime.today() - datetime.timedelta(1)
    if start_date > end_date:
        return df
    codes = [const.col2edb[col] for col in df.columns]
    # print df.tail()
    # print '\n'
    data = w.edb(codes, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "Fill=Previous")
    app_df = utils.wind2df(data)
    # print app_df
    app_df.columns = [const.edb2col[x] for x in app_df.columns]
    app_df = app_df[df.columns]
    app_df.index = app_df.index.map(lambda x: x - datetime.timedelta(seconds=0.005))
    # print app_df
    df = df.append(app_df)
    return df

def update_treasury():
    writer = pd.ExcelWriter(const.treasury_file, engine='xlsxwriter')

    # 中国国债数据
    df = pd.read_excel(const.treasury_file, index_col=0, sheetname='china')
    df = new_df(df)
    df.to_excel(writer, sheet_name='china')

    # 美国国债数据
    df = pd.read_excel(const.treasury_file, index_col=0, sheetname='usa')
    df = new_df(df)
    df.to_excel(writer, sheet_name='usa')
    writer.save()

def update_usa_treasury():
    # 美国长短债收益率数据
    df = pd.read_excel(const.usa_treasury_file, index_col=0, sheetname='bond')
    df = new_df(df)
    df.to_excel(const.usa_treasury_file, sheet_name='bond')

def update_libor():
    # SHIBOR数据
    df = pd.read_excel(const.libor_file, index_col=0, sheetname='shibor')
    df = new_df(df)
    df.to_excel(const.libor_file, sheet_name='shibor')

def update_corporate():
    # 企业债数据
    df = pd.read_excel(const.corporate_file, index_col=0, sheetname='corporate')
    df = new_df(df)
    df.to_excel(const.corporate_file, sheet_name='corporate')

def update_repo():
    # 回购利率数据
    df = pd.read_excel(const.repo_file, index_col=0, sheetname='repo')
    df = new_df(df)
    df.to_excel(const.repo_file, sheet_name='repo')

def update_cny():
    df = pd.read_excel(const.currency_file, index_col=0, sheetname='usdcny')
    df = new_df(df)
    df.to_excel(const.currency_file, sheet_name='usdcny')

def update_cdb():
    df = pd.read_excel(const.bank_file, index_col=0, sheetname='cdb')
    df = new_df(df)
    df.to_excel(const.bank_file, sheet_name='cdb')

def update_product():
    df = pd.read_excel(const.product_file, index_col=0, sheetname='financial product')
    df = new_df(df)
    df.to_excel(const.product_file, sheet_name='financial product')

def update():
    update_treasury()
    update_usa_treasury()
    update_libor()
    update_corporate()
    update_repo()
    update_cny()
    update_cdb()
    update_product()

if __name__ == '__main__':
    update()
