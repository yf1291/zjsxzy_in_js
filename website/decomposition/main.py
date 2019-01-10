# encoding: utf-8
import numpy as np
import pandas as pd
import datetime
import os
import sys

import decomposition.const as const
import decomposition.data as data

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, NumeralTickFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button, NumberFormatter
from bokeh.plotting import figure
from bokeh.palettes import Spectral9

COLORS = Spectral9 + ["#053061", "#2166ac", "#4393c3" "#92c5de", "#d1e5f0"]# "#f7f7f7", "#fddbc7", "#f4a582", "#d6604d", "#b2182b"]

source_decomp = ColumnDataSource(data=dict(left=[], right=[], bottom=[], top=[], color=[], text=[], text_x=[], ret=[], ret_y=[], ret_x=[]))

def get_data(df):
    left, right, bottom, top, color, text = [], [], [], [], [], []
    text_x, ret_y, ret_x, ret = [], [], [], []
    df = df.sort_values('total_ret', ascending=False)
    df.index = range(df.shape[0])
    for i in df.index:
        # total ret
        left.append(i + 0.35)
        right.append(i + 0.65)
        bottom.append(0)
        top.append(df.loc[i]['total_ret'])
        color.append(COLORS[1])
        text.append(df.loc[i]['name'])
        text_x.append(i + 0.2)
        ret.append(u'总收益: %.2f%%'%(df.loc[i]['total_ret']*100))
        ret_x.append(i + 0.35)
        ret_y.append(df.loc[i]['total_ret'] / 2)

        pos, neg = 0, 0
        # valuation ret
        left.append(i)
        right.append(i + 0.3)
        if df.loc[i]['valuation_ret'] > 0:
            bottom.append(0)
            top.append(df.loc[i]['valuation_ret'])
            pos += df.loc[i]['valuation_ret']
        else:
            bottom.append(df.loc[i]['valuation_ret'])
            top.append(0)
            neg += df.loc[i]['valuation_ret']
        color.append(COLORS[5])
        text.append(df.loc[i]['name'])
        text_x.append(i + 0.2)
        ret.append(u'估值收益: %.2f%%'%(df.loc[i]['valuation_ret']*100))
        ret_x.append(i)
        ret_y.append(df.loc[i]['valuation_ret'] / 2)

        # earning ret
        left.append(i)
        right.append(i + 0.3)
        if df.loc[i]['earning_ret'] > 0:
            bottom.append(pos)
            top.append(pos + df.loc[i]['earning_ret'])
            ret_y.append(pos + df.loc[i]['earning_ret'] / 2)
            pos += df.loc[i]['earning_ret']
        else:
            bottom.append(neg + df.loc[i]['earning_ret'])
            top.append(neg)
            ret_y.append(neg + df.loc[i]['earning_ret'] / 2)
            neg += df.loc[i]['earning_ret']
        color.append('#d53e4f')
        text.append(df.loc[i]['name'])
        text_x.append(i + 0.2)
        ret.append(u'盈利收益: %.2f%%'%(df.loc[i]['earning_ret']*100))
        ret_x.append(i)

        # dividend ret
        left.append(i)
        right.append(i + 0.3)
        if df.loc[i]['dividend_ret'] > 0:
            bottom.append(pos)
            top.append(pos + df.loc[i]['dividend_ret'])
            ret_y.append(pos + df.loc[i]['dividend_ret'] / 2)
            pos += df.loc[i]['dividend_ret']
        else:
            bottom.append(neg + df.loc[i]['dividend_ret'])
            top.append(neg)
            ret_y.append(neg + df.loc[i]['dividend_ret'] / 2)
            neg += df.loc[i]['dividend_ret']
        color.append(COLORS[0])
        text.append(df.loc[i]['name'])
        text_x.append(i + 0.2)
        ret.append(u'红利收益: %.2f%%'%(df.loc[i]['dividend_ret']*100))
        ret_x.append(i)

    df = pd.DataFrame({'top': top, 'bottom': bottom, 'left': left, 'right': right, 'color': color, 
                       'text': text, 'text_x': text_x, 'ret': ret, 'ret_y': ret_y, 'ret_x': ret_x})
    return df

def update_decomp():
    start_date, end_date = time_start_text.value, time_end_text.value
    plot_decomp.title.text = u'计算中...'
    print start_date, end_date
    data.update_data(start_date, end_date)
    plot_decomp.title.text = u'A股主要指数收益率分解'
    df = pd.read_excel(const.DECOMP_FILE)
    df = get_data(df)
    source_decomp.data = source_decomp.from_df(df)

def update_all():
    update_decomp()

def get_plot(title, pct=False):
    tools = "pan,wheel_zoom,box_select,reset"
    plot = figure(plot_height=500, plot_width=1200, tools=tools, x_axis_type='datetime', toolbar_location='above')
    plot.title.text_font_size = "15pt"
    plot.title.text_font = "Microsoft YaHei"
    # plot.yaxis.minor_tick_line_color = None
    plot.title.text = title
    if pct:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00%')
    else:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00')
    return plot

time_start_text = TextInput(value="2018-01-01", title=u"开始时间", width=200)
# time_start_text.on_change('value', lambda attr, old, new: update_all())
today = (datetime.datetime.today() - datetime.timedelta(1))
time_end_text = TextInput(value=today.strftime("%Y-%m-%d"), title=u"结束时间", width=200)
# time_end_text.on_change('value', lambda attr, old, new: update_all())
update_button = Button(label=u'计算', button_type='success', width=200)
update_button.on_click(update_decomp)

inputs = widgetbox(time_start_text, time_end_text, update_button)

plot_decomp = get_plot(u'A股主要指数收益率分解', pct=True)
plot_decomp.quad(left='left', right='right', bottom='bottom', top='top', source=source_decomp, color='color')
plot_decomp.text(x='text_x', y=0, text='text', source=source_decomp, text_font_size='15pt')
plot_decomp.text(x='ret_x', y='ret_y', text='ret', source=source_decomp, text_font_size='7pt')
plot_decomp.xaxis.visible = False

update_all()

curdoc().add_root(column(inputs, plot_decomp))
curdoc().title = u'收益率分解'