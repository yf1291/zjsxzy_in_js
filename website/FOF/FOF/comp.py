# encoding: utf-8

import pandas as pd
import empyrical

import os
import const
import utils

def save_comp_dataframe():
    '''
    保存基金公司旗下所有基金净值
    '''
    all_df = utils.get_all_funds()
    comps = all_df['mgrcomp'].unique()
    for c in comps:
        print c
        df = all_df[all_df['mgrcomp'] == c]
        dic = {}
        for code in df['wind_code']:
            fname = '%s/history/%s.xlsx'%(const.DATA_DIR, code)
            temp = pd.read_excel(fname, index_col=0)
            temp = temp.loc[~temp.index.duplicated(keep='first')]
            temp = temp['nav_adj']
            dic[code] = temp
        fdf = pd.DataFrame(dic)
        fdf.to_excel(u'%s/%s.xlsx'%(const.COMP_DIR, c))

def save_comp_rpt():
    '''
    保存基金公司季报数据
    '''
    files = [f.rstrip('.xlsx') for f in os.listdir(const.COMP_DIR)]
    for c in files:
        print c
        fname = '%s/%s.xlsx'%(const.COMP_DIR, c)
        df = pd.read_excel(fname, index_col=0)
        funds = df.columns.tolist()
        dic = {}
        for f in funds:
            fname = '%s/%s.xlsx'%(const.RPT_DIR, f)
            if os.path.exists(fname):
                temp = pd.read_excel(fname, index_col=0)
                dic[f] = temp
        pnl = pd.Panel(dic)
        pnl.to_pickle('%s/%s.pkl'%(const.COMP_RPT_DIR, c))

def get_comp_daily_return(comp_name):
    '''
    得到基金公司日收益率曲线
    '''
    fname = '%s/%s.xlsx'%(const.COMP_DIR, comp_name)
    df = pd.read_excel(fname, encoding='utf-8')
    df = df.pct_change()
    fname = '%s/%s.pkl'%(const.COMP_RPT_DIR, comp_name)
    pnl = pd.read_pickle(fname)
    if pnl.shape[2] == 0:
        return None
    st2nav = pnl.minor_xs('prt_stocktonav')
    weight_df = pnl.minor_xs('prt_netasset')
    weight_df = weight_df[st2nav > 60] # 股票仓位大于60%
    weight_df = weight_df.fillna(0)
    weight_zero_df = pd.DataFrame(index=df.index, columns=df.columns)
    weight_df = weight_zero_df.append(weight_df).sort_index()
    weight_df = weight_df.fillna(method='ffill').loc[df.index]
    weight_df = weight_df[~weight_df.index.duplicated(keep='first')]
    # print df.shape, weight_df.shape
    # print (1 + df).tail()
    # print weight_df.tail()
    # weight_df = weight_df * (1 + df) # 基金规模自然增长
    sum_weight = weight_df.sum(axis=1)
    select_index = sum_weight[sum_weight > 0].index
    weight_df = weight_df.loc[select_index]
    weight_df.to_excel('D:/Data/temp.xlsx')
    # print weight_df.shape
    # print weight_df.sum(axis=1)
    # print weight_df.div(weight_df.sum(axis=1), axis='index')
    # weight_df = weight_df.loc[sum_weight[sum_weight > 0].index]
    # print select_index
    # print weight_df.loc[select_index].div(sum_weight.loc[select_index].values(), axis='index')
    # weight_df = weight_df.iloc[-100:]
    weight_df = weight_df.div(weight_df.sum(axis=1), axis='index') # 按基金规模加权
    ret = (weight_df * df).sum(axis=1)
    return ret

def get_all_comp_daily_return():
    '''
    得到所有基金公司日收益率
    '''
    all_df = utils.get_all_funds()
    comps = all_df['mgrcomp'].unique()
    dic = {}
    for c in comps:
        print c
        daily_return = get_comp_daily_return(c)
        if daily_return is None:
            continue
        dic[c] = daily_return
    df = pd.DataFrame(dic)
    df.to_excel('%s/comp_ret.xlsx'%(const.FOF_DIR), encoding='utf-8')

def get_comp_position(comp_name):
    '''
    得到基金公司仓位
    '''
    fname = '%s/%s.pkl'%(const.COMP_RPT_DIR, comp_name)
    pnl = pd.read_pickle(fname)
    if pnl.shape[2] == 0:
        return None
    st2nav = pnl.minor_xs('prt_stocktonav')
    position_df = pnl.minor_xs('prt_netasset')
    position_df = position_df[st2nav > 60] # 股票仓位大于60%
    position = (position_df * st2nav).sum(axis=1)
    return position

def get_all_comp_position():
    '''
    得到所有基金公司仓位
    '''
    all_df = utils.get_all_funds()
    comps = all_df['mgrcomp'].unique()
    dic = {}
    for c in comps:
        print c
        position = get_comp_position(c)
        if position is None:
            continue
        dic[c] = position
    df = pd.DataFrame(dic)
    df.to_excel('%s/comp_position.xlsx'%(const.FOF_DIR), encoding='utf-8')

def comp_analysis(start_date='2017-07-01'):
    '''
    分析区间内基金公司收益率、波动率、beta与仓位变化
    '''
    comp_ret = pd.read_excel('%s/comp_ret.xlsx'%(const.FOF_DIR), index_col=0)
    comp_pos = pd.read_excel('%s/comp_position.xlsx'%(const.FOF_DIR), index_col=0)
    wdf = pd.read_csv('%s/881001.WI.csv'%(const.INDEX_DIR), index_col=1)
    wseries = wdf.pct_change()[wdf.index >= start_date]['close']
    wseries.index = pd.to_datetime(wseries.index)
    df = pd.DataFrame(index=comp_ret.columns, columns=['ret', 'vol', 'beta', 'pos'])
    for c in df.index:
        series = comp_ret[c]
        series = series[series.index >= start_date]
        df.loc[c, 'ret'] = (1 + series).cumprod()[-1] - 1
        df.loc[c, 'vol'] = empyrical.annual_volatility(series)
        wseries = wseries[(wseries.index >= series.index[0]) & (wseries.index <= series.index[-1])]
        df.loc[c, 'beta'] = empyrical.beta(series, wseries)
        if comp_pos[c].shape[0] > 1 and comp_pos[c][-2] != 0:
            df.loc[c, 'pos'] = (comp_pos[c][-1] - comp_pos[c][-2]) / comp_pos[c][-2]
    df = df.sort_values('ret', ascending=False)
    df = df.dropna()
    df.to_excel('%s/comp_analysis.xlsx'%(const.FOF_DIR))
