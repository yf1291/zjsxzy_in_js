# encoding: utf-8
import numpy as np
import pandas as pd
import datetime
import os
import sys
from os.path import dirname, join

from sector import sector_return
from sector import const

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, CustomJS, NumberFormatter, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure

sector_list = [u'申万二级行业', u'中信一级行业', u'万得主题行业']
swdf = pd.read_excel(const.SW_SECTOR_FILE)
swdf = swdf.set_index(u'名称')
sw_sector = swdf.index.tolist()
zxdf = pd.read_excel(const.ZX_SECTOR_FILE)
zxdf = zxdf.set_index(u'名称')
zx_sector = zxdf.index.tolist()
wddf = pd.read_excel(const.THEME_FILE)
wddf = wddf.set_index(u'名称')
wd_sector = wddf.index.tolist()
base_select = [u'881001.WI', '000001.SH', '000300.SH']

source_table = ColumnDataSource(data=dict())
source_acc_ret = ColumnDataSource(data=dict(date=[], ret=[], r20=[], r120=[], r243=[]))

def update_sector():
    if sector_select.value == u'申万二级行业':
        sector_select2.options = sw_sector
        sector_select2.value = sw_sector[0]
    elif sector_select.value == u'中信一级行业':
        sector_select2.options = zx_sector
        sector_select2.value = zx_sector[0]
    elif sector_select.value == u'万得主题行业':
        sector_select2.options = wd_sector
        sector_select2.value = wd_sector[0]
    update_acc_ret()

def update_acc_ret():
    if return_select.value == u'超额收益':
        base_index.options = base_select
        base_symbol = base_index.value
    elif return_select.value == u'绝对收益':
        base_index.options = ['']
        base_symbol = ''

    if sector_select.value == u'申万二级行业':
        symbol = swdf.loc[sector_select2.value].values[0]
    elif sector_select.value == u'中信一级行业':
        symbol = zxdf.loc[sector_select2.value].values[0]
    elif sector_select.value == u'万得主题行业':
        symbol = wddf.loc[sector_select2.value].values[0]

    print symbol
    fname = '%s/%s.xlsx'%(const.INDEX_DIR, symbol)
    df = pd.read_excel(fname)
    ret = df['close'].pct_change()
    # print ret.head()
    # print ret.tail()
    if base_symbol != '':
        fname = '%s/%s.xlsx'%(const.INDEX_DIR, base_symbol)
        df = pd.read_excel(fname)
        bret = df['close'].pct_change()
        # print bret.head()
        # print bret.tail()
        ret = ret - bret
    else:
        bret, acc_ret = [], []
    ret = (1 + ret).cumprod()
    plot_ret.title.text = sector_select2.value
    source_acc_ret.data = {'date': ret.index,
                           'ret': ret,
                           'r20': ret.rolling(window=20).mean(),
                           'r120': ret.rolling(window=120).mean(),
                           'r243': ret.rolling(window=243).mean()}

def update_data():
    start_date = '%s-%s-%s'%(start_year.value, start_month.value, start_day.value)
    end_date = '%s-%s-%s'%(end_year.value, end_month.value, end_day.value)
    print start_date, end_date
    update_button.label = u'计算中'
    df = sector_return.return_intersect(start_date, end_date)
    app = pd.DataFrame({'sector': [' '], 'return': [' ']})
    df = df.append(app)
    source_table.data = {'sector': df['sector'], 'return': df['return']}
    update_button.label = u'更新'

columns = [
    TableColumn(field='sector', title=u'行业'),
    TableColumn(field='return', title=u'收益率', formatter=NumberFormatter(format='0.00%')),
]
table = DataTable(source=source_table, columns=columns, width=600, height=400)
years_selections = [str(year) for year in range(2000, 2019)]
months_selections = [str(month) for month in range(1, 13)]
days_selections = [str(day) for day in range(1, 32)]
start_year = Select(value='2017', title='开始年', width=100, options=years_selections)
end_year = Select(value='2018', title='结束年', width=100, options=years_selections)
start_month = Select(value='1', title='开始月', width=70, options=months_selections)
end_month = Select(value='1', title='结束月', width=70, options=months_selections)
start_day = Select(value='1', title='开始日', width=70, options=days_selections)
end_day = Select(value='1', title='结束日', width=70, options=days_selections)
start_input = row(start_year, start_month, start_day)
end_input = row(end_year, end_month, end_day)
update_button = Button(label=u'更新', button_type='success', width=240)
update_button.on_click(update_data)
inputs = row(start_input, end_input)
box = widgetbox(start_year, start_month, start_day, end_year, end_month, end_day, update_button)
tables = widgetbox(table)

sector_select = Select(value=sector_list[0], title=u'行业分类', width=100, options=sector_list)
sector_select.on_change('value', lambda attr, old, new: update_sector())
sector_select2 = Select(value=sw_sector[0], title=u'行业选择', width=100, options=sw_sector)
sector_select2.on_change('value', lambda attr, old, new: update_acc_ret())
return_select = Select(value=u'超额收益', title=u'收益类别', width=100, options=[u'超额收益', u'绝对收益'])
return_select.on_change('value', lambda attr, old, new: update_acc_ret())
base_index = Select(value=u'881001.WI', title=u'基准', width=100, options=base_select)
base_index.on_change('value', lambda attr, old, new: update_acc_ret())
box2 = widgetbox(sector_select, sector_select2, return_select, base_index)

def get_plot(title, pct=False):
    tools = "pan,wheel_zoom,box_select,reset"
    plot = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
    plot.title.text_font_size = "15pt"
    plot.title.text_font = "Microsoft YaHei"
    plot.yaxis.minor_tick_line_color = None
    plot.title.text = title
    if pct:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00%')
    else:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00')
    return plot
plot_ret = get_plot(sector_select2.value)
plot_ret.line('date', 'ret', source=source_acc_ret, line_width=2, legend=u'行业超额（绝对）收益率')
plot_ret.line('date', 'r20', source=source_acc_ret, line_width=1, color='red', legend=u'一个月均线')
plot_ret.line('date', 'r120', source=source_acc_ret, line_width=1, color='orange', legend=u'半年均线')
plot_ret.line('date', 'r243', source=source_acc_ret, line_width=1, color='pink', legend=u'一年均线')

update_data()
update_acc_ret()

curdoc().add_root(column(row(box, tables), box2, plot_ret))
curdoc().title = u"A股行业轮动"
