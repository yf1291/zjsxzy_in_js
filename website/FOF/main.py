# encoding: utf-8
import numpy as np
import pandas as pd
import pyfolio as pf
import datetime
import os
import sys
from os.path import dirname, join
sys.path.append('C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/FOF/src')

import FOF.bond_fund as bond_fund
import FOF.stock_fund as stock_fund
import FOF.mixed_fund as mixed_fund
import FOF.const as const
import FOF.data as data
import FOF.correlation as correlation
import FOF.comp as comp

from bokeh.io import curdoc
from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, CustomJS, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, NumberFormatter
from bokeh.plotting import figure

# DATA_DIR = 'C:/Users/jgtzsx01/Documents/workspace/zjsxzy_in_js/website/FOF/data'
DATA_DIR = 'D:/workspace/data/FOF/'
COMP_RET_FILE = '%s/comp_ret.xlsx'%(const.FOF_DIR)
COMP_POS_FILE = '%s/comp_position.xlsx'%(const.FOF_DIR)
ret_df = pd.read_excel(COMP_RET_FILE)
pos_df = pd.read_excel(COMP_POS_FILE)
comps = ret_df.columns.tolist()

invest_type_selections = [u'股票型基金', u'债券型基金', u'混合型基金']
bond_type_selections = [u'全部',
                        u'中长期纯债型基金',
                        u'混合债券型一级基金',
                        u'混合债券型二级基金',
                        u'被动指数型债券基金',
                        u'短期纯债型基金',
                        u'增强指数型债券基金',
]
stock_type_selections = [u'全部',
                         u'被动指数型基金',
                         u'增强指数型基金',
                         u'普通股票型基金',
]
mixed_type_selections = [u'全部',
                         u'偏股混合型基金',
                         u'偏债混合型基金',
                         u'灵活配置型基金',
                         u'平衡混合型基金',
]
scale_selections = [u'全部', u'2亿以下', u'2亿-10亿', u'10亿以上']
time_selections = [u'3年', u'2年', u'1年', u'6个月', u'3个月', u'1个月']
time_days = {u'3年': 729, u'2年': 486, u'1年': 243, u'6个月': 121, u'3个月': 60, u'1个月': 20}
time_dict = {u'3年': '3-year return', u'2年': '2-year return', u'1年': '1-year return',
             u'6个月': '6-month return', u'3个月': '3-month return', u'1个月': '1-month return'}

source_nav = ColumnDataSource(data=dict(date=[], nav=[]))
source_return = ColumnDataSource(data=dict(date=[], ret=[]))
source_table = ColumnDataSource(data=dict())
source_cor = ColumnDataSource(data=dict(days=[], cor=[], max=[], min=[], median=[], percent_75=[], percent_25=[]))
source_comp_nav = ColumnDataSource(data=dict(date=[], nav=[]))
source_comp_position = ColumnDataSource(data=dict(date=[], pos=[]))
source_comp_table = ColumnDataSource(data=dict())

def scale_filter(df):
    if scale_select.value == u'全部':
        return df
    if scale_select.value == u'2亿以下':
        return df[df['netasset'] < 200000000]
    if scale_select.value == u'2亿-10亿':
        return df[(df['netasset'] >= 200000000) & (df['netasset'] < 1000000000)]
    if scale_select.value == u'10亿以上':
        return df[df['netasset'] >= 1000000000]

def type_filter(df):
    if invtype2_select.value == u'全部':
        return df
    return df[df['investtype'] == invtype2_select.value]

def update_inputs():
    if invtype1_select.value == u'债券型基金':
        invtype2_select.options = bond_type_selections
    elif invtype1_select.value == u'股票型基金':
        invtype2_select.options = stock_type_selections
    elif invtype1_select.value == u'混合型基金':
        invtype2_select.options = mixed_type_selections

def update_new_data():
    nav_title = plot_nav.title.text
    ret_title = plot_return.title.text
    plot_nav.title.text = u'更新中...'
    plot_return.title.text = u'更新中...'
    data.update_bond_data()
    data.update_stock_data()
    data.update_mixed_data()
    plot_nav.title.text = nav_title
    plot_return.title.text = ret_title

def update_data():
    ticker = fund_text.value
    bond_df = bond_fund.get_bond_fund()
    bond_df.index = bond_df['wind_code']
    stock_df = stock_fund.get_stock_fund()
    stock_df.index = stock_df['wind_code']
    mixed_df = mixed_fund.get_mixed_fund()
    mixed_df.index = mixed_df['wind_code']
    if ticker in bond_df.index:
        fund_name = bond_df.loc[ticker, 'sec_name']
    elif ticker in stock_df.index:
        fund_name = stock_df.loc[ticker, 'sec_name']
    elif ticker in mixed_df.index:
        fund_name = mixed_df.loc[ticker, 'sec_name']
    else:
        plot_nav.title.text = u'基金不存在'
        plot_return.title.text = u'基金不存在'
        return
    fname = '%s/history/%s.xlsx'%(const.DATA_DIR, ticker)
    df = pd.read_excel(fname, index_col=0)
    temp = df['nav_adj'].dropna()
    temp = temp[temp.index >= temp.index[-min(time_days[time_select.value], temp.shape[0]-1)]]
    source_nav.data['date'] = temp.index.values
    source_nav.data['nav'] = temp.values
    temp = df[time_dict[time_select.value]].dropna()
    temp = temp[temp.index >= temp.index[-min(time_days[time_select.value], temp.shape[0]-1)]]
    source_return.data['date'] = temp.index.values
    source_return.data['ret'] = temp.values
    plot_nav.title.text = fund_name + u'净值'
    plot_return.title.text = fund_name + time_select.value + u'收益率'

def get_rank(df, ret_df, empyrical_df):
    percent = 1 - 0.1
    ret_df = ret_df[df['wind_code']]
    df.loc[:, 'current return'] = ret_df.values[-1]
    # df.loc[:, 'volatility'] = ret_df.ix[-min(ret_df.shape[0], time_days[time_select.value]):].std().values
    omega_ratio = empyrical_df.loc[df['wind_code'], 'omega'].values
    df['omega'] = omega_ratio
    ret_df = ret_df.rank(axis=1, pct=True)
    df.loc[:, 'max percentage'] = ret_df.max().values
    df.loc[:, 'max percentage date'] = ret_df.idxmax().values
    df = df[df['max percentage'] > percent]
    df = df.dropna()
    df.loc[:, 'max percentage'] = 1 - df.loc[:, 'max percentage']
    df = df.sort_values('current return', ascending=False)
    # df.to_excel('%s/result.xlsx'%(DATA_DIR), index=False)
    return df

def update_table_data(df):
    # df = pd.read_excel('%s/result.xlsx'%(DATA_DIR))
    source_table.data = {
        'sec_name': df['sec_name'].values,
        'wind_code': df['wind_code'].values,
        'fundmanager': df['fundmanager'].values,
        'netasset': df['netasset'].values,
        'current return': df['current return'].values,
        # 'volatility': df['volatility'].values,
        'omega': df['omega'].values,
        'max percentage': df['max percentage'].values,
        'max percentage date': df['max percentage date'].map(lambda x: x.strftime('%Y-%m-%d')).values
    }

def select_fund():
    nav_title = plot_nav.title.text
    ret_title = plot_return.title.text
    plot_nav.title.text = u'查询中...'
    plot_return.title.text = u'查询中...'
    time_value = time_dict[time_select.value]
    if invtype1_select.value == u'债券型基金':
        bond_df = bond_fund.get_bond_fund()
        # pnl = pd.read_pickle('%s/bond.pkl'%(const.FOF_DIR))
        ret_df = pd.read_pickle('%s/bond_%s.pkl'%(const.FOF_DIR, time_value))
        empyrical_df = pd.read_excel('%s/bond_empyrical.xlsx'%(const.FOF_DIR))
        df = bond_fund.filter_bond(bond_df)
    if invtype1_select.value == u'股票型基金':
        stock_df = stock_fund.get_stock_fund()
        # pnl = pd.read_pickle('%s/stock.pkl'%(const.FOF_DIR))
        ret_df = pd.read_pickle('%s/stock_%s.pkl'%(const.FOF_DIR, time_value))
        empyrical_df = pd.read_excel('%s/stock_empyrical.xlsx'%(const.FOF_DIR))
        df = stock_fund.filter_stock(stock_df)
    if invtype1_select.value == u'混合型基金':
        mixed_df = mixed_fund.get_mixed_fund()
        # pnl = pd.read_pickle('%s/mixed.pkl'%(const.FOF_DIR))
        ret_df = pd.read_pickle('%s/mixed_%s.pkl'%(const.FOF_DIR, time_value))
        empyrical_df = pd.read_excel('%s/mixed_empyrical.xlsx'%(const.FOF_DIR))
        df = mixed_fund.filter_mixed(mixed_df)
    df = type_filter(df)
    df = scale_filter(df)
    # ret_df = pnl[df['wind_code']].minor_xs(time_dict[time_select.value])
    df = get_rank(df, ret_df, empyrical_df)
    update_table_data(df)
    plot_nav.title.text = nav_title
    plot_return.title.text = ret_title

def update_correlation():
    fund1, fund2 = fund1_text.value, fund2_text.value
    data_df = correlation.get_dataframe(fund1, fund2)
    plot_correlation.title.text = fund1 + u"与" + fund2 + u"相关性锥"
    source_cor.data = source_cor.from_df(data_df)

def update_comp_table():
    print('analysing...')
    comp.comp_analysis(comp_start_time_text.value)
    df = pd.read_excel('%s/comp_analysis.xlsx'%(const.FOF_DIR), index_col=0)
    df['name'] = df.index.map(lambda x: x.rstrip(u'管理有限公司'))
    df.index = range(df.shape[0])
    source_comp_table.data = source_comp_table.from_df(df)

def update_comp():
    plot_comp_nav.title.text = comp_select.value + u'基金净值'
    plot_comp_pos.title.text = comp_select.value + u'股票仓位'
    print comp_select.value
    ret = ret_df[comp_select.value]
    acc_ret = (1 + ret).cumprod()
    acc_ret = acc_ret[acc_ret != 1]
    pos = pos_df[comp_select.value]
    source_comp_nav.data = {'date': acc_ret.index, 'nav': acc_ret.values}
    source_comp_position.data = {'date': pos.index, 'pos': pos.values}

invtype1_select = Select(value=invest_type_selections[0], title=u'基金一级投资分类', width=200, options=invest_type_selections)
invtype1_select.on_change('value', lambda attr, old, new: update_inputs())
invtype2_select = Select(value=bond_type_selections[0], title=u'基金二级投资分类', width=200, options=bond_type_selections)
scale_select = Select(value=scale_selections[0], title=u'基金资产净值', width=200, options=scale_selections)
time_select = Select(value=u'1年', title=u'业绩时间窗口', width=200, options=time_selections)
time_select.on_change('value', lambda attr, old, new: update_data())
fund_button = Button(label=u"筛选基金", button_type="success", width=200)
fund_button.on_click(select_fund)
update_button = Button(label=u'更新数据', button_type='success', width=200)
update_button.on_click(update_new_data)
fund_text = TextInput(value='000088.OF', title=u'基金Wind代码', width=200)
fund_text.on_change('value', lambda attr, old, new: update_data())
comp_select = Select(value=u'嘉实基金管理有限公司', title=u'基金公司', width=200, options=comps)
comp_select.on_change('value', lambda attr, old, new: update_comp())

columns = [
    TableColumn(field='sec_name', title=u'基金简称'),
    TableColumn(field='wind_code', title=u'万得代码'),
    TableColumn(field='fundmanager', title=u'基金经理'),
    TableColumn(field='netasset', title=u'基金资产净值', formatter=NumberFormatter(format='$0,0.00')),
    TableColumn(field='current return', title=u'当前业绩', formatter=NumberFormatter(format='0.00%')),
    # TableColumn(field='volatility', title=u'波动率', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='omega', title=u'Omega', formatter=NumberFormatter(format='0.00')),
    TableColumn(field='max percentage', title=u'最好业绩排名', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='max percentage date', title=u'获得最好业绩日期')
]
data_table = DataTable(source=source_table, columns=columns, width=800)
comp_columns = [
    TableColumn(field='name', title=u'基金公司'),
    TableColumn(field='ret', title=u'区间回报', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='vol', title=u'波动率', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='beta', title='Beta', formatter=NumberFormatter(format='0.00')),
    TableColumn(field='pos', title=u'仓位变化', formatter=NumberFormatter(format='0.00%'))
]
comp_data_table = DataTable(source=source_comp_table, columns=comp_columns, width=900)

tools = "pan,wheel_zoom,box_select,reset"
plot_nav = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_nav.line('date', 'nav', source=source_nav, line_width=3, line_alpha=0.6)
plot_nav.title.text_font_size = "15pt"
plot_nav.yaxis.minor_tick_line_color = None
plot_nav.title.text_font = "Microsoft YaHei"

plot_return = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_return.line('date', 'ret', source=source_return, line_width=3, line_alpha=0.6)
plot_return.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_return.title.text_font_size = "15pt"
plot_return.yaxis.minor_tick_line_color = None
plot_return.title.text_font = "Microsoft YaHei"

fund1_text = TextInput(value='070099.OF', title=u'基金1Wind代码', width=200)
fund2_text = TextInput(value='070013.OF', title=u'基金2Wind代码', width=200)
corr_button = Button(label=u"计算相关性", width=200, button_type="success")
corr_button.on_click(update_correlation)
corr_col = column(fund1_text, fund2_text, corr_button)
comp_start_time_text = TextInput(value='2017-07-01', title=u'开始时间', width=200)
comp_start_time_text.on_change('value', lambda attr, old, new: update_comp_table())

plot_correlation = figure(plot_height=400, plot_width=1000, tools=tools)
plot_correlation.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_correlation.title.text_font_size = "15pt"
plot_correlation.yaxis.minor_tick_line_color = None
plot_correlation.title.text_font = "Microsoft YaHei"
plot_correlation.line('days', 'cor', source=source_cor, line_width=5, color='red', legend='Now')
plot_correlation.line('days', 'max', source=source_cor, line_width=2, color='#002EB8', legend='Max')
plot_correlation.line('days', 'percent_75', source=source_cor, line_width=2, color='#003DF5', legend='3/4')
plot_correlation.line('days', 'median', source=source_cor, line_width=2, color='#33CCFF', legend='Median')
plot_correlation.line('days', 'percent_25', source=source_cor, line_width=2, color='#33FFCC', legend='1/4')
plot_correlation.line('days', 'min', source=source_cor, line_width=2, color='#33FF66', legend='Min')

plot_comp_nav = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_comp_nav.line('date', 'nav', source=source_comp_nav, line_width=3, line_alpha=0.6)
plot_comp_nav.title.text_font_size = "15pt"
plot_comp_nav.yaxis.minor_tick_line_color = None
plot_comp_nav.title.text_font = "Microsoft YaHei"

plot_comp_pos = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_comp_pos.line('date', 'pos', source=source_comp_position, line_width=3, line_alpha=0.6)
plot_comp_pos.yaxis.minor_tick_line_color = None
plot_comp_pos.title.text_font_size = '15pt'
plot_comp_pos.title.text_font = 'Microsoft Yahei'

inputs = widgetbox(update_button, invtype1_select, invtype2_select, scale_select, time_select, fund_button, fund_text)
table = widgetbox(data_table)
update_inputs()
update_data()
update_correlation()
update_comp()
update_comp_table()
select_fund()

curdoc().add_root(column(row(inputs, table), plot_nav, plot_return, corr_col, plot_correlation,
                         widgetbox(comp_start_time_text, comp_select), comp_data_table, plot_comp_nav, plot_comp_pos))
curdoc().title = u'基金筛选'
