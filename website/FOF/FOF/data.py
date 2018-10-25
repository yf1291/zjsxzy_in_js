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

def download_index_close(wind_code, start_date, end_date):
    w.start()
    data = w.wsd(wind_code, 'close', start_date, end_date)
    return utils.wind2df(data)

def update_fund_list(df, fname):
    df[['sec_name', 'wind_code']].to_excel(fname, index=False)
    df = pd.read_excel(fname)
    # 基金二级分类
    data = w.wss(df['wind_code'].tolist(), "fund_investtype")
    temp = utils.wind2df(data)
    df['investtype'] = temp['fund_investtype']
    # 发行时间
    data = w.wss(df['wind_code'].tolist(), "issue_date")
    temp = utils.wind2df(data)
    df['issue_date'] = temp['issue_date']
    # 资产规模
    data = w.wss(df['wind_code'].tolist(), "prt_netasset","rptDate=%s"%(const.rptDate))
    temp = utils.wind2df(data)
    df['netasset'] = temp['prt_netasset']
    # 基金公司
    data = w.wss(df['wind_code'].tolist(), 'fund_mgrcomp')
    temp = utils.wind2df(data)
    df['mgrcomp'] = temp['fund_mgrcomp']
    # 基金经理
    data = w.wss(df['wind_code'].tolist(), "fund_fundmanager")
    temp = utils.wind2df(data)
    df['fundmanager'] = temp['fund_fundmanager']
    # 当前申购赎回状态
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wss(df['wind_code'].tolist(), "fund_dq_status","tradeDate=%s"%(today))
    temp = utils.wind2df(data)
    df['fund_status'] = temp['fund_dq_status']
    df.to_excel(fname, index=False)

def update_stock_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885012.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/股票型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def update_bond_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885005.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/债券型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def update_mixed_list():
    w.start()
    today = datetime.datetime.today().strftime('%Y-%m-%d')
    data = w.wset("sectorconstituent","date=%s;windcode=885013.WI"%(today))
    df = utils.wind2df(data)
    fname = u'%s/混合型基金列表.xlsx'%(const.DATA_DIR)
    update_fund_list(df, fname)

def add_old_data(ticker):
    w.start()
    fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
    if os.path.exists(fname):
        df = pd.read_excel(fname)
        if 'outmessage' in df.columns:
            del df['outmessage']
        df = df[['nav_adj']]
        end_date = pd.to_datetime(df.index[0]) - datetime.timedelta(1)
        data = w.wss(ticker, 'issue_date')
        start_date = data.Data[0][0]
        if start_date < end_date:
            # print start_date, end_date
            days = (pd.to_datetime(end_date, format='%Y-%m-%d') - start_date).days
            data = w.wsd(ticker, "NAV_adj", "ED-%dD"%(days), end_date, "")
            old_df = utils.wind2df(data)
            df = old_df.append(df)
            # df = utils.get_historical_return(df)
            df.index = pd.to_datetime(df.index)
            df = df.loc[~df.index.duplicated(keep='first')]
            df.to_excel(fname)
        else:
            df = df[['nav_adj']]
            df = df.loc[~df.index.duplicated(keep='first')]
            df.to_excel(fname)

def add_old_rpt(ticker):
    w.start()
    rptdates = utils.generate_rptdate('2000-01-01')
    rptdates = pd.to_datetime(rptdates)
    fname = '%s/%s.xlsx'%(const.RPT_DIR, ticker)
    if os.path.exists(fname):
        df = pd.read_excel(fname)
        data = w.wss(ticker, 'issue_date')
        start_date = data.Data[0][0]
        rptdates = [d for d in rptdates if (d > start_date) and (d < df.index[0])]
        # print rptdates
        if len(rptdates) > 0:
            old_df = utils.download_season_rpt(ticker, rptdates)
            df = old_df.append(df)
            df.to_excel(fname)
    # print rptdates

def update_nav(ticker):
    w.start()
    today = datetime.datetime.today() - datetime.timedelta(1)
    fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
    if not os.path.exists(fname):
        utils.down_historical_nav(ticker)
        df = pd.read_excel(fname, index_col=0)
        df = utils.get_historical_return(df)
        df.to_excel(fname)
        return
    old_df = pd.read_excel(fname, index_col=0)
    # old_df = old_df[['nav_adj']]
    # old_df.to_excel(fname)
    # old_df = old_df.drop(old_df.index[-4:])
    # old_df.index = old_df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    # old_df.index = pd.to_datetime(old_df.index)
    if 'outmessage' in old_df.columns:
        del old_df['outmessage']
    last_day = old_df.index[-1]
    days = (today - last_day).days - 1
    if days < 0:
        return
    data = w.wsd(ticker, "NAV_adj", "ED-%dD"%(days), today, "")
    df = utils.wind2df(data)
    if 'outmessage' in df.columns:
        old_df.to_excel(fname)
        return
    for col in old_df.columns:
        if col not in df.columns:
            df[col] = 0
    df = old_df.append(df)
    df.index = df.index.map(lambda x: x.strftime('%Y-%m-%d'))
    df.index = pd.to_datetime(df.index)
    # df = utils.get_historical_return(df)
    df = df.loc[~df.index.duplicated(keep='first')]
    df.to_excel(fname)

def update_season_rpt(ticker, rptdates):
    fname = '%s/%s.xlsx'%(const.RPT_DIR, ticker)
    if not os.path.exists(fname):
        df = utils.download_season_rpt(ticker, rptdates)
        if df.shape[0] > 0:
            df.to_excel(fname)
    else:
        df = pd.read_excel(fname, index_col=0)
        if df.shape[0] == 0:
            os.remove(fname)
            return
        # df = df.dropna(how='all')
        # df.to_excel(fname)
        # if df.shape[0] == 1:
            # print 'deleting %s'%(fname)
            # os.remove(fname)
            # df = utils.download_season_rpt(ticker, rptdates)
            # df.to_excel(fname)
        last_date = df.index[-1]
        if isinstance(df.loc[last_date]['prt_stocktonav'], float):
            rptdates = [rptdate for rptdate in rptdates if rptdate > last_date]
            # print rptdates
            if len(rptdates) > 0:
                new_df = utils.download_season_rpt(ticker, rptdates)
                # print new_df
                if new_df.shape[0] > 0:
                    assert(new_df.shape[1] == df.shape[1])
                    df = df.append(new_df)
                    df.to_excel(fname)
            else:
                return
        else:
            df = utils.download_season_rpt(ticker, rptdates)
            if df.shape[0] > 0:
                df.to_excel(fname)

def update_stock_season_rpt():
    stock_df = stock_fund.get_stock_fund()
    rptdates = utils.generate_rptdate('2000-01-01')
    rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    for ticker, issue_date in zip(stock_df['wind_code'], stock_df['issue_date']):
        print('updating %s season report...'%(ticker))
        fund_rptdates = [rptdate for rptdate in rptdates if rptdate > issue_date]
        update_season_rpt(ticker, fund_rptdates)
        # add_old_rpt(ticker)

def update_mixed_season_rpt():
    mixed_df = mixed_fund.get_mixed_fund()
    rptdates = utils.generate_rptdate('2000-01-01')
    rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    for ticker, issue_date in zip(mixed_df['wind_code'], mixed_df['issue_date']):
        print('updating %s season report...'%(ticker))
        fund_rptdates = [rptdate for rptdate in rptdates if rptdate > issue_date]
        update_season_rpt(ticker, fund_rptdates)
        # add_old_rpt(ticker)

def update_bond_season_rpt():
    bond_df = bond_fund.get_bond_fund()
    rptdates = utils.generate_rptdate('2000-01-01')
    rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    for ticker, issue_date in zip(bond_df['wind_code'], bond_df['issue_date']):
        print('updating %s season report...'%(ticker))
        fund_rptdates = [rptdate for rptdate in rptdates if rptdate > issue_date]
        update_season_rpt(ticker, fund_rptdates)
        # add_old_rpt(ticker)

def update_bond_data():
    bond_df = bond_fund.get_bond_fund()
    for ticker in bond_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
        # add_old_data(ticker)
    bond_fund.save_bond_fund_panel()

def update_stock_data():
    stock_df = stock_fund.get_stock_fund()
    for ticker in stock_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
        # add_old_data(ticker)
    stock_fund.save_stock_fund_panel()

def update_mixed_data():
    mixe_df = mixed_fund.get_mixed_fund()
    for ticker in mixe_df['wind_code']:
        print('updating %s...'%(ticker))
        update_nav(ticker)
        # add_old_data(ticker)
    mixed_fund.save_mixed_fund_panel()

def update_index_data(wind_code):
    fname = '%s/%s.xlsx'%(const.INDEX_HIS_DIR, wind_code)
    if datetime.datetime.now().hour < 15:
        end_date = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y-%m-%d")
    else:
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    if os.path.exists(fname):
        df = pd.read_excel(fname, index_col=0)
        df = df[df.index < '2018-07-16']
        if 'outmessage' in df.columns:
            del df['outmessage']
            # df = df[df.index < '2017-10-30']
        start_date = df.index[-1] + datetime.timedelta(1)
        if start_date > datetime.datetime.strptime(end_date, "%Y-%m-%d"):
            return
        print('updating %s...'%(wind_code))
        add_df = download_index_close(wind_code, start_date, end_date)
        df = df.append(add_df)
        df.to_excel(fname)
    else:
        print('downloding %s...'%(wind_code))
        start_date = '2000-01-01'
        df = download_index_close(wind_code, start_date, end_date)
        df.to_excel(fname)

def update_theme_data():
    df = pd.read_excel(const.theme_file)
    for wind_code in df[u'代码']:
        update_index_data(wind_code)

def update_concept_data():
    df = pd.read_excel(const.concept_file)
    for wind_code in df[u'代码']:
        update_index_data(wind_code)

def update_sector_data():
    df = pd.read_excel(const.sector_file)
    for wind_code in df[u'代码']:
        update_index_data(wind_code)

if __name__ == '__main__':
    # update_stock_list()
    # update_bond_list()
    # update_mixed_list()
    # update_stock_season_rpt()
    # update_mixed_season_rpt()
    # update_bond_season_rpt()
    update_bond_data()
    update_stock_data()
    update_mixed_data()
    comp.save_comp_dataframe()
    comp.save_comp_rpt()
    comp.get_all_comp_daily_return()
    comp.get_all_comp_position()
    comp.comp_analysis()
    update_theme_data()
    update_concept_data()
    update_sector_data()
