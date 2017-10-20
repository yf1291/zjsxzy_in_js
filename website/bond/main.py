# encoding: utf-8

from os.path import dirname, join
import os
import pandas as pd
import numpy as np
import datetime

import bond.const as const

from bokeh.io import curdoc
from bokeh.charts import Bar, Area
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure
from bokeh.palettes import Spectral9

# 中美10年期国债利率与利差
source_chusa = ColumnDataSource(data=dict(date=[], ch10y=[], usa10y=[], spread=[]))
def update_chusa():
    print('update chusa')
    ch_df = pd.read_excel(const.treasury_file, index_col=0, sheetname='china')
    usa_df = pd.read_excel(const.treasury_file, index_col=0, sheetname='usa')
    df = ch_df.merge(usa_df, how='inner', left_index=True, right_index=True)
    source_chusa.data = {'date': df.index,
                         'ch10y': df['CGB10Y'] / 100,
                         'usa10y': df['UST10Y'] / 100,
                         'spread': (df['CGB10Y'] - df['UST10Y']) / 100}

# 美国短、长期国债收益率
source_usa_treasury = ColumnDataSource(data=dict(date=[], usa10y=[], usa2y=[]))
def update_usa_treasury():
    print('update usa treasury')
    df = pd.read_excel(const.usa_treasury_file, index_col=0, sheetname='bond')
    source_usa_treasury.data = {'date': df.index,
                                'usa10y': df[u'美国国债到期收益率 10年'] / 100,
                                'usa2y': df[u'美国国债到期收益率 2年'] / 100}

# TED spread
source_ted = ColumnDataSource(data=dict(date=[], shibor3m=[], cgb3m=[], spread=[]))
def update_ted():
    print('update ted')
    bdf = pd.read_excel(const.treasury_file, index_col=0, sheetname='china')
    shdf = pd.read_excel(const.libor_file, index_col=0, sheetname='shibor')
    df = bdf.merge(shdf, how='inner', left_index=True, right_index=True)
    df = df.rolling(window=5).mean()
    source_ted.data = {'date': df.index,
                       'shibor3m': df['SHIBOR3M'] / 100,
                       'cgb3m': df['CGB3M'] / 100,
                       'spread': (df['SHIBOR3M'] - df['CGB3M']) / 100}

# 10年期国债收益率-1年期国债收益率
source_cgb10y_1y = ColumnDataSource(data=dict(date=[], cgb10y=[], cgb1y=[], spread=[]))
def update_cgb10y_1y():
    print('update cgb10y 1y')
    df = pd.read_excel(const.treasury_file, index_col=0, sheetname='china')
    # df = df.rolling(window=20).mean()
    df = df[df.index >= '2006-01-01']
    source_cgb10y_1y.data = {'date': df.index,
                             'cgb10y': df['CGB10Y'] / 100,
                             'cgb1y': df['CGB1Y'] / 100,
                             'spread': (df['CGB10Y'] - df['CGB1Y']) / 100}

# 10年期国开债收益率-1年期国开债收益率
source_cdb10y_1y = ColumnDataSource(data=dict(date=[], cdb10y=[], cdb1y=[], spread=[]))
def update_cdb10y_1y():
    print('update cdb10y 1y')
    df = pd.read_excel(const.bank_file, index_col=0, sheetname='cdb')
    df = df[df.index >= '2006-01-01']
    source_cdb10y_1y.data = {'date': df.index,
                             'cdb10y': df[u'中债国开债到期收益率 10年'] / 100,
                             'cdb1y': df[u'中债国开债到期收益率 1年'] / 100,
                             'spread': (df[u'中债国开债到期收益率 10年'] - df[u'中债国开债到期收益率 1年']) / 100}

# 信用利差
source_coporate = ColumnDataSource(data=dict(date=[], spr1y=[], spr5y=[]))
def update_coporate():
    print('update corporate')
    df = pd.read_excel(const.corporate_file, index_col=0, sheetname='corporate')
    source_coporate.data = {'date': df.index,
                           'spr1y': (df['CB(AA)1Y'] - df['CB(AAA)1Y']) / 100,
                           'spr5y': (df['CB(AA)5Y'] - df['CB(AAA)5Y']) / 100}

source_credit = ColumnDataSource(data=dict(date=[], cbaa5y=[], prod6m=[], spread=[]))
def update_credict():
    print('update credit')
    cor_df = pd.read_excel(const.corporate_file, index_col=0, sheetname='corporate')
    pro_df = pd.read_excel(const.product_file, index_col=0, sheetname='financial product')
    df = cor_df.merge(pro_df, left_index=True, right_index=True, how='outer').fillna(method='ffill').dropna()
    df = df[df.index >= '2012-01-01']
    source_credit.data = {'date': df.index,
                         'cbaa5y': df['CB(AA)5Y'] / 100,
                         'prod6m': df[u'理财产品预期年收益率 6个月'] / 100,
                         'spread': (df['CB(AA)5Y'] - df[u'理财产品预期年收益率 6个月']) / 100}

# 回购利率
source_repo = ColumnDataSource(data=dict(date=[], r001=[], r007=[], dr001=[], dr007=[]))
def update_repo():
    print('update repo')
    df = pd.read_excel(const.repo_file, index_col=0, sheetname='repo')
    source_repo.data = {'date': df.index,
                        'r001': df['R001'] / 100,
                        'r007': df['R007'] / 100,
                        'dr001': df['DR001'] / 100,
                        'dr007': df['DR007'] / 100}

# 人民币即期汇率与远期汇率
source_cny = ColumnDataSource(data=dict(date=[], spot=[], ndf=[]))
def update_currency():
    print('update currency')
    df = pd.read_excel(const.currency_file, index_col=0, sheetname='usdcny')
    df = df[df != 0]
    df = df.dropna()
    source_cny.data = {'date': df.index,
                       'spot': df['USDCNY spot'],
                       'ndf': df['USDCNY NDF 1Y']}

# 10年国开债收益率-贷款基础利率
source_cdb = ColumnDataSource(data=dict(date=[], cdb=[], base=[], spread=[]))
def update_bank():
    print('update bank')
    bank_df = pd.read_excel(const.bank_file, index_col=0, sheetname='cdb')
    base_df = pd.read_excel(const.base_file, index_col=0, sheetname='base')
    df = bank_df.merge(base_df, left_index=True, right_index=True, how='outer')
    df = df.fillna(method='ffill').dropna()
    df = df[df.index >= '2006-01-01']
    df['spread'] = df[u'1年期贷款基准利率'] - df[u'中债国开债到期收益率 10年']
    source_cdb.data = {'date': df.index,
                        'cdb': df[u'中债国开债到期收益率 10年'] / 100,
                        'base': df[u'1年期贷款基准利率'] / 100,
                        'spread': df['spread'] / 100}

# 金融产品收益率
source_product = ColumnDataSource(data=dict(date=[], fin_3m=[], fin_1y=[]))
def update_product():
    print('update financial product')
    df = pd.read_excel(const.product_file, index_col=0, sheetname='financial product')
    source_product.data = {'date': df.index,
                           'fin_3m': df[u'理财产品预期年收益率 3个月'] / 100,
                           'fin_1y': df[u'理财产品预期年收益率 1年'] / 100}

def update_all():
    update_chusa()
    update_usa_treasury()
    update_ted()
    update_cgb10y_1y()
    update_cdb10y_1y()
    update_coporate()
    update_repo()
    update_currency()
    update_bank()
    update_product()
    update_credict()

tools = "pan,wheel_zoom,box_select,reset"
plot_chusa = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_chusa.line('date', 'ch10y', source=source_chusa, color='red', legend=u'中国10年期国债收益率')
plot_chusa.line('date', 'usa10y', source=source_chusa, legend=u'美国10年期国债收益率')
plot_chusa.line('date', 'spread', source=source_chusa, color='green', legend=u'中美10年期国债利差')
plot_chusa.title.text_font_size = "15pt"
plot_chusa.title.text = u'中美10年期国债收益率与利差'
plot_chusa.title.text_font = "Microsoft YaHei"
plot_chusa.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_chusa.yaxis.minor_tick_line_color = None

plot_usa_treasury = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_usa_treasury.line('date', 'usa10y', source=source_usa_treasury, color='red', legend=u'美国10年期国债收益率')
plot_usa_treasury.line('date', 'usa2y', source=source_usa_treasury, legend=u'美国2年期国债收益率')
plot_usa_treasury.title.text_font_size = "15pt"
plot_usa_treasury.title.text = u'美国2年、10年期国债收益率'
plot_usa_treasury.title.text_font = "Microsoft YaHei"
plot_usa_treasury.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_usa_treasury.yaxis.minor_tick_line_color = None

plot_ted = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_ted.line('date', 'shibor3m', source=source_ted, color='#FF9999', line_width=2, legend='SHIBOR：3个月')
plot_ted.line('date', 'cgb3m', source=source_ted, line_width=2, legend=u'3个月国债收益率')
plot_ted.line('date', 'spread', source=source_ted, color='green', line_width=2, legend=u'利差')
plot_ted.title.text_font_size = "15pt"
plot_ted.title.text = u'TED Spread'
plot_ted.title.text_font = "Microsoft YaHei"
plot_ted.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_ted.yaxis.minor_tick_line_color = None

plot_cgb10y_1y = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_cgb10y_1y.line('date', 'cgb10y', source=source_cgb10y_1y, color='#990000', line_width=2, legend=u'10年期国债收益率')
plot_cgb10y_1y.line('date', 'cgb1y', source=source_cgb10y_1y, color='#FF9999', line_width=2, legend=u'1年期国债收益率')
plot_cgb10y_1y.line('date', 'spread', source=source_cgb10y_1y, color='green', line_width=2, legend=u'利差')
plot_cgb10y_1y.title.text_font_size = "15pt"
plot_cgb10y_1y.title.text = u'10年期国债收益率-1年期国债收益率（GDP领先指标）'
plot_cgb10y_1y.title.text_font = "Microsoft YaHei"
plot_cgb10y_1y.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cgb10y_1y.yaxis.minor_tick_line_color = None

plot_cdb10y_1y = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_cdb10y_1y.line('date', 'cdb10y', source=source_cdb10y_1y, color='#990000', line_width=2, legend=u'10年期国开债收益率')
plot_cdb10y_1y.line('date', 'cdb1y', source=source_cdb10y_1y, color='#FF9999', line_width=2, legend=u'1年期国开债收益率')
plot_cdb10y_1y.line('date', 'spread', source=source_cdb10y_1y, color='green', line_width=2, legend=u'利差')
plot_cdb10y_1y.title.text_font_size = "15pt"
plot_cdb10y_1y.title.text = u'10年期国开债收益率-1年期国开债收益率'
plot_cdb10y_1y.title.text_font = "Microsoft YaHei"
plot_cdb10y_1y.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cdb10y_1y.yaxis.minor_tick_line_color = None

plot_corporate = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_corporate.line('date', 'spr1y', source=source_coporate, line_width=2, color='red', legend=u'AA-AAA，1年')
plot_corporate.line('date', 'spr5y', source=source_coporate, line_width=2, legend=u'AA-AAA，5年')
plot_corporate.title.text_font_size = "15pt"
plot_corporate.title.text = u'信用利差'
plot_corporate.title.text_font = "Microsoft YaHei"
plot_corporate.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_corporate.yaxis.minor_tick_line_color = None

plot_credit = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_credit.line('date', 'cbaa5y', source=source_credit, color='red', line_width=2, legend=u'企业债（AA）：5年')
plot_credit.line('date', 'prod6m', source=source_credit, color='#000099', line_width=2, legend=u'理财产品预期年化收益率：6个月')
plot_credit.line('date', 'spread', source=source_credit, color='green', line_width=2, legend=u'利差')
plot_credit.title.text_font_size = "15pt"
plot_credit.title.text = u'企业债与银行理财利差（信用利差）'
plot_credit.title.text_font = "Microsoft YaHei"
plot_credit.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_credit.yaxis.minor_tick_line_color = None

plot_repo = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_repo.line('date', 'r001', source=source_repo, line_width=2, color='#990000', legend=u'R001')
plot_repo.line('date', 'r007', source=source_repo, line_width=2, color='#FF9999', legend=u'R007')
plot_repo.line('date', 'dr001', source=source_repo, line_width=2, color='#000099', legend=u'DR001')
plot_repo.line('date', 'dr007', source=source_repo, line_width=2, color='#99CCFF', legend=u'DR007')
plot_repo.title.text_font_size = "15pt"
plot_repo.title.text = u'回购利率'
plot_repo.title.text_font = "Microsoft YaHei"
plot_repo.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_repo.yaxis.minor_tick_line_color = None

plot_cny = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_cny.line('date', 'spot', source=source_cny, line_width=2, color='#FF9999', legend=u'美元兑人民币即期汇率')
plot_cny.line('date', 'ndf', source=source_cny, line_width=2, color='#990000', legend=u'美元兑人民币远期汇率：12个月')
plot_cny.title.text_font_size = "15pt"
plot_cny.title.text = u'人民币即期与远期汇率'
plot_cny.title.text_font = "Microsoft YaHei"
plot_cny.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cny.yaxis.minor_tick_line_color = None

plot_cdb = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_cdb.line('date', 'cdb', source=source_cdb, color='#990000', line_width=2, legend=u'10年期国开债收益率')
plot_cdb.line('date', 'base', source=source_cdb, color='#99CCFF', line_width=2, legend=u'1年期贷款基准利率')
plot_cdb.line('date', 'spread', source=source_cdb, color='green', line_width=2, legend=u'利差')
plot_cdb.title.text_font_size = "15pt"
plot_cdb.title.text = u'10年期国开债收益率-1年期贷款基准利率'
plot_cdb.title.text_font = "Microsoft YaHei"
plot_cdb.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_cdb.yaxis.minor_tick_line_color = None

plot_product = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_product.line('date', 'fin_1y', source=source_product, color='#990000', line_width=2, legend=u'理财产品预期年收益率：1年')
plot_product.line('date', 'fin_3m', source=source_product, color='#FF9999', line_width=2, legend=u'理财产品预期年收益率：3个月')
plot_product.title.text_font_size = "15pt"
plot_product.title.text = u'金融产品收益率'
plot_product.title.text_font = "Microsoft YaHei"
plot_product.yaxis.formatter = NumeralTickFormatter(format="0.00%")
plot_product.yaxis.minor_tick_line_color = None

update_all()

curdoc().add_root(column(plot_chusa, plot_usa_treasury, plot_ted, plot_cgb10y_1y,
                         plot_cdb10y_1y, plot_corporate, plot_credit,
                         plot_repo, plot_cny, plot_cdb, plot_product))
curdoc().title = u"债券指标"
