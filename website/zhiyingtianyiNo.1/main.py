# encoding: utf-8
from os.path import dirname, join
import os
import pandas as pd
import numpy as np
import datetime

import zhiying.data_update as data_update
import zhiying.const as const

from bokeh.layouts import row, widgetbox, column
from bokeh.models import ColumnDataSource, CustomJS
from bokeh.models.widgets import Slider, Button, DataTable, TableColumn, Select, TextInput
from bokeh.plotting import figure
from bokeh.io import curdoc
from bokeh.palettes import Spectral8

# COLORS = Spectral8 + ["#053061", "#2166ac", "#4393c3", "#92c5de", "#d1e5f0", "#f7f7f7"]
# DATA_DIR = "D:/sheet/zhiyingtianyi portfolio"
# ZHIYING_FILE = "%s/zhiyingtianyi No.1.csv"%(DATA_DIR)
# ZHIYING_FILE2 = '%s/zhiyingtianyi No.1.xlsx'%(DATA_DIR)

portfolio_selection = [u"智盈添易一号第%d期"%(i) for i in range(const.first_num_of_portfolio, const.last_num_of_portfolio+1) if i not in const.exceptions]
portfolio_dict = {u"智盈添易一号第%d期"%(i): unicode(i) for i in range(const.first_num_of_portfolio, const.last_num_of_portfolio+1) if i not in const.exceptions}
# ASSETS_COLOR = {asset: COLORS[i] for i, asset in enumerate(portfolio_dict.values())}
source = ColumnDataSource(data=dict())
source_value = ColumnDataSource(data=dict(date=[], value=[]))

def update_excel():
    date = time_text.value
    fname = "%s/%s.xlsx"%(const.DATA_DIR, date)
    if not os.path.exists(fname):
        data_update.get_statistics(date)
    if not os.path.exists(fname):
        source.data = {}
        return
    df = pd.read_excel(fname)
    source.data = {
        'name': df[u"组合"],
        'net value': df[u"单位净值"],
        'year return': df[u"今年以来业绩"],
        'total return': df[u"成立以来业绩"],
        'annual return': df[u'年化收益率'],
        'max drawdown': df[u"最大回撤"],
        'sharpe': df[u"夏普率"],
        'volatility': df[u"波动率"]
    }

def update_plot():
    plot_value.title.text = portfolio_select.value
    asset = portfolio_dict[portfolio_select.value]
    print asset

    if int(asset) < 24:
        df = pd.read_csv(const.ZHIYING_FILE)
        df.index = pd.to_datetime(df['date'], format='%Y/%m/%d')
        df = df[[asset]]
        df = df.dropna()
        df.loc[:, 'return'] = df.pct_change()
        df.loc[:, 'net value'] = (1+df['return']).cumprod()
        df.loc[df.index[0], 'net value'] = 1
    else:
        df = pd.read_excel(const.ZHIYING_FILE2, index_col=0)
        df = df[[int(asset)]]
        df = df.dropna()
        df.loc[:, 'return'] = df[int(asset)] / 100.
        df.loc[:, 'net value'] = (1+df['return']).cumprod()
        df.loc[df.index[0], 'net value'] = 1

    source_value.data = {'date': df.index, 'value': df['net value']}

def update_data():
    for t in text:
        if t.value == '' or t.value == np.nan:
            print('null value')
            return
    values = [t.value for t in text]
    for t in text:
        t.value = ""
    df = pd.DataFrame(columns=[portfolio_dict[t] for t in portfolio_selection], index=[0])
    df.iloc[0] = values
    df.to_csv("%s/%s.csv"%(const.DATA_DIR, update_time_text.value), index=False)
    print df

    data_update.merge_to_sheet(update_time_text.value)
    time_text.value = update_time_text.value
    update_excel()
    update_plot()

tools = "pan,wheel_zoom,box_select,reset"
plot_value = figure(plot_height=400, plot_width=1200, tools=tools, x_axis_type='datetime')
plot_value.line('date', 'value', source=source_value, line_width=3, line_alpha=0.6)
plot_value.title.text_font_size = "15pt"
plot_value.yaxis.minor_tick_line_color = None

button = Button(label=u"下载", button_type="success", width=300)
button.callback = CustomJS(args=dict(source=source),
                           code=open(join(dirname(__file__), "download.js")).read())

columns = [
    TableColumn(field="name", title=u"组合"),
    TableColumn(field="net value", title=u"单位净值", width=150),
    TableColumn(field="year return", title=u"今年以来业绩", width=200),
    TableColumn(field="total return", title=u"成立以来业绩", width=200),
    TableColumn(field='annual return', title=u'年化收益率', width=200),
    TableColumn(field="max drawdown", title=u"最大回撤", width=200),
    TableColumn(field="sharpe", title=u"夏普率", width=200),
    TableColumn(field="volatility", title=u"波动率", width=200)
]

data_table = DataTable(source=source, columns=columns, width=900, height=500)

today = datetime.datetime.now()
yesterday = today - datetime.timedelta(1)
yesterday = yesterday.strftime("%Y-%m-%d")
time_text = TextInput(value=yesterday, title="提取时间", width=300)
time_text.on_change('value', lambda attr, old, new: update_excel())

portfolio_select = Select(value=portfolio_selection[0], title="组合", width=300, options=portfolio_selection)
portfolio_select.on_change('value', lambda attr, old, new: update_plot())

update_excel()
update_plot()

# update_time_text = TextInput(value=today.strftime("%Y-%m-%d"), title=u"更新日期", width=300)
# update_button = Button(label=u"更新数据", width=300, button_type="success")
# update_row = row(update_time_text, update_button)
# update_button.on_click(update_data)
# text = [TextInput(value="", title=name, width=165) for name in portfolio_selection]
# text_row_1 = row(text[0], text[1], text[2], text[3])

controls = widgetbox(time_text, portfolio_select, button)
table = widgetbox(data_table)

curdoc().add_root(column(row(controls, table), plot_value))
curdoc().title = u"智盈添易一号"
