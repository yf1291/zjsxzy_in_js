# encoding: utf-8
import pandas as pd

import risk.const as const

from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, NumeralTickFormatter, Range1d, LinearAxis, HoverTool
from bokeh.plotting import figure

source_concentration = ColumnDataSource(data=dict(date=[], cap=[], p=[]))
def update_concentration():
    df = pd.read_excel(const.CAPITAL_CONCENTRATION, index_col=0)
    df = df.fillna(method='ffill')
    df = df[df.index >= '2000-01-01']
    source_concentration.data = {'date': df.index, 
                                 'cap': df['cap'], 
                                 'p': df['close']}

source_skew = ColumnDataSource(data=dict(date=[], skew=[], p=[]))
def update_skew():
    df = pd.read_excel(const.SKEWNESS, index_col=0)
    df = df[df.index >= '2000-01-01']
    source_skew.data = {'date': df.index, 
                        'skew': df['skew'], 
                        'p': df['close']}

source_corr = ColumnDataSource(data=dict(date=[], corr=[], p=[]))
def update_corr():
    df = pd.read_excel(const.CORRELATION, index_col=0)
    df = df[df.index >= '2000-01-01']
    source_corr.data = {'date': df.index, 
                        'corr': df['correlation'], 
                        'p': df['close']}

source_disp = ColumnDataSource(data=dict(date=[], disp=[], p=[]))
def update_disp():
    df = pd.read_excel(const.DISPERSION, index_col=0)
    df = df[df.index >= '2000-01-01']
    source_disp.data = {'date': df.index, 
                        'disp': df['dispersion'], 
                        'p': df['close']}

def update_all():
    update_concentration()
    update_skew()
    update_corr()
    update_disp()

def get_plot(title, pct=False):
    tools = "pan,wheel_zoom,box_select,reset,hover"
    plot = figure(plot_height=500, plot_width=1200, tools=tools, x_axis_type='datetime', toolbar_location='above')
    plot.title.text_font_size = "15pt"
    plot.title.text_font = "Microsoft YaHei"
    plot.extra_y_ranges = {'close': Range1d(start=0, end=7000)}
    plot.add_layout(LinearAxis(y_range_name='close'), 'right')
    plot.yaxis.minor_tick_line_color = None
    plot.title.text = title
    if pct:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00%')
    else:
        plot.yaxis.formatter = NumeralTickFormatter(format='0.00')
    return plot

plot_concentration = get_plot(u'资金集中度')
plot_concentration.line('date', 'cap', source=source_concentration, line_width=2, legend=u'资金集中度')
plot_concentration.y_range = Range1d(0.2, 0.9)
plot_concentration.line('date', 'p', source=source_concentration, y_range_name='close', line_width=1, color='red', legend=u'上证综指')
hover_concentration = plot_concentration.select(dict(type=HoverTool))
hover_concentration.tooltips = [(u'日期', '@date{%F}'), (u'集中度', '@cap{0.00}'), (u'上证综指', '@p{0000.00}')]
hover_concentration.formatters = {'date': 'datetime'}
hover_concentration.mode = 'mouse'

plot_skew = get_plot('收益率偏度')
plot_skew.line('date', 'skew', source=source_skew, line_width=2, legend=u'收益率偏度')
plot_skew.y_range = Range1d(-2, 2)
plot_skew.line('date', 'p', source=source_skew, y_range_name='close', line_width=1, color='red', legend=u'上证综指')
hover_skew = plot_skew.select(dict(type=HoverTool))
hover_skew.tooltips = [(u'日期', '@date{%F}'), (u'偏度', '@skew{0.00}'), (u'上证综指', '@p{0000.00}')]
hover_skew.formatters = {'date': 'datetime'}
hover_skew.mode = 'mouse'

plot_corr = get_plot('收益率相关性')
plot_corr.line('date', 'corr', source=source_corr, line_width=2, legend=u'收益率相关性')
plot_corr.y_range = Range1d(0, 1)
plot_corr.line('date', 'p', source=source_corr, y_range_name='close', line_width=1, color='red', legend=u'上证综指')
hover_corr = plot_corr.select(dict(type=HoverTool))
hover_corr.tooltips = [(u'日期', '@date{%F}'), (u'相关性', '@corr{0.00}'), (u'上证综指', '@p{0000.00}')]
hover_corr.formatters = {'date': 'datetime'}
hover_corr.mode = 'mouse'

plot_disp = get_plot(u'收益率离差')
plot_disp.vbar(x='date', top='disp', bottom=0, width=1, source=source_disp, legend=u'离差')
plot_disp.y_range = Range1d(-1, 6)
plot_disp.line('date', 'p', source=source_disp, y_range_name='close', line_width=1, color='red', legend=u'上证综指')
hover_disp = plot_disp.select(dict(type=HoverTool))
hover_disp.tooltips = [(u'日期', '@date{%F}'), (u'离差', '@disp{0.000000}'), (u'上证综指', '@p{0000.00}')]
hover_disp.formatters = {'date': 'datetime'}
hover_disp.mode = 'vline'

update_all()

curdoc().add_root(column(plot_concentration, plot_skew, plot_corr, plot_disp))
curdoc().title = u'风险指标'
