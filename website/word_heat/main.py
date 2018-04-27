# encoding: utf-8
import numpy as np
import pandas as pd
import datetime
import os
import sys
from os.path import dirname, join

import word.word_heat_level as word_heat_level
import word.const as const

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, CustomJS, NumberFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure

DATA_DIR = "D:/workspace/data/asset-class"

asset_files = [f for f in os.listdir(const.ASSET_DIR) if f.endswith('.csv')]
assets = ['word'] + [a[:-4] for a in asset_files if not a.startswith('H11025')]
with open(const.WORDS_FILES, 'r') as fp:
    words = [w.rstrip().decode('utf-8') for w in fp.readlines()]
words = words[1:]

source = ColumnDataSource(data=dict(date=[], ts=[]))
source_absolute = ColumnDataSource(data=dict(date=[], ts=[]))
source_weighted = ColumnDataSource(data=dict(date=[], ts=[]))
source_table = ColumnDataSource(data=dict())
source_download = ColumnDataSource(data=dict())
source_absolute_corr = ColumnDataSource(data=dict())
source_corr = ColumnDataSource(data=dict(date=[], corr=[]))
source_per = ColumnDataSource(data=dict())
source_topic_words = ColumnDataSource(data=dict())
source_topic_per = ColumnDataSource(data=dict())
source_topic_absolute = ColumnDataSource(data=dict(date=[], ts=[]))
source_topic_relative = ColumnDataSource(data=dict(date=[], ts=[]))
source_wei_index = ColumnDataSource(data=dict(date=[], pc=[], mobile=[]))

tools = "pan,wheel_zoom,box_select,reset"
plot = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_absolute = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_weighted = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_corr = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_topic_absolute = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_topic_relative = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')
plot_wei_index = figure(plot_height=400, plot_width=1000, tools=tools, x_axis_type='datetime')

plot.line('date', 'ts', source=source, line_width=3, line_alpha=0.6)
plot_absolute.line('date', 'ts', source=source_absolute, line_width=3, line_alpha=0.6)
plot_weighted.line('date', 'ts', source=source_weighted, line_width=3, line_alpha=0.6)
plot_corr.line('date', 'corr', source=source_corr, line_width=3, line_alpha=0.6)
plot_topic_absolute.line('date', 'ts', source=source_topic_absolute, line_width=3, line_alpha=0.6)
plot_topic_relative.line('date', 'ts', source=source_topic_relative, line_width=3, line_alpha=0.6)
plot_wei_index.line('date', 'pc', source=source_wei_index, line_width=3, line_alpha=0.6)
plot_wei_index.title.text = words[0] + u'微指数'
# plot_wei_index.line('date', 'mobile', source=source_wei_index, color='green', line_width=3, line_alpha=0.6, legend=u'移动端')

columns = [
    TableColumn(field="word", title="word"),
    TableColumn(field="distance", title="distance")
]
per_columns = [
    TableColumn(field='word', title=u'词'),
    TableColumn(field='percentile', title=u'历史分位', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='wei_percentile', title=u'微指数历史分位', formatter=NumberFormatter(format='0.00%')),
    TableColumn(field='diff', title=u'（华尔街见闻-微指数）历史分位', formatter=NumberFormatter(format='0.00%'))
]
topic_columns = [
    TableColumn(field='word', title=u'词'),
    TableColumn(field='value', title=u'概率', formatter=NumberFormatter(format='0.0000'))
]
topic_per_columns = [
    TableColumn(field='topic', title=u'主题'),
    TableColumn(field='word', title=u'代表词'),
    TableColumn(field='percentile', title=u'历史分位', formatter=NumberFormatter(format='0.00%'))
]
data_table = DataTable(source=source_table, columns=columns, width=400, height=300)
per_table = DataTable(source=source_per, columns=per_columns, width=800, height=300)
topic_table = DataTable(source=source_topic_words, columns=topic_columns, width=400, height=300)
topic_per_table = DataTable(source=source_topic_per, columns=topic_per_columns, width=800, height=300)

def update_title():
    plot_absolute.title.text = text.value + u"（绝对）= 周词频"
    plot.title.text = text.value + u"（相对）= 周词频 / 周所有词总词频"
    plot_weighted.title.text = text.value + u"（加权）= 周词频 * 词距离 / 周所有词总词频"

def update_data():
    word = text.value
    threshold = float(slider.value)
    start_date = datetime.datetime(int(year_select.value), 1, 1)

    fname = os.path.join(DATA_DIR, "%s_%.1f.csv"%(word, threshold))
    try:
        if not os.path.exists(fname):
            print("calculating...")
            plot.title.text = "calculating..."
            plot_absolute.title.text = "calculating..."
            plot_weighted.title.text = "calculating..."
            word_heat_level.get_word_heat(word, threshold=threshold)
    except KeyError:
        plot.title.text = u"没有该关键词"
        plot_absolute.title.text = u"没有该关键词"
        plot_weighted.title.text = u"没有该关键词"
        source_table.data = {}
        return

    update_title()

    dataframe = pd.read_csv(fname)
    # print dataframe.tail()
    # dataframe.to_excel("./%s.xlsx"%(text.value), index=False)
    # 可下载数据
    source_download.data = source_download.from_df(dataframe)

    dataframe["date"] = pd.to_datetime(dataframe["date"], format="%Y-%m-%d")
    dataframe = dataframe.set_index('date')
    dataframe = dataframe[dataframe.index >= start_date]
    dataframe = dataframe[dataframe.index <= (datetime.datetime.today() - datetime.timedelta(1))]
    dataframe = dataframe.replace([0], np.nan).dropna()

    # 加权值曲线
    df = pd.DataFrame({'ts': dataframe["weighted"]})
    source_weighted.data = source_weighted.from_df(df)

    # 相对值曲线
    source.data = source.from_df(pd.DataFrame({'ts': dataframe["relative"]}))

    # 绝对值曲线
    source_absolute.data = source_absolute.from_df(pd.DataFrame({'ts': dataframe['absolute']}))

    # 词表格
    data = pd.read_csv("%s/%s_%s_words.csv"%(DATA_DIR, word, threshold))
    source_table.data = {'word': data['word'], 'distance': data['distance']}

def update_correlation():
    absolute_df = pd.read_excel('%s/absolute_corr.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    for asset in assets:
        print asset
    absolute_df = absolute_df[assets]
    source_absolute_corr.data = source_absolute_corr.from_df(absolute_df)

def update_percentile():
    df = pd.read_excel('%s/percentile.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    # source_per.data = source_per.from_df(df)
    tdf = pd.read_excel('%s/wei_percentile.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    tdf.columns = ['wei_percentile', 'word']
    df = df.merge(tdf, on='word', how='outer')
    df['diff'] = df['percentile'] - df['wei_percentile']
    source_per.data = {'word': df['word'],
                       'percentile': df['percentile'],
                       'wei_percentile': df['wei_percentile'],
                       'diff': df['diff']}
    # source_per.data = {'word': df['word'], 'percentile': df['percentile'], 'wei_percentile': tdf['percentile']}
    df = pd.read_excel('%s/topic_percentile.xlsx'%(const.WORD_HEAT_DIR), index_col=None)
    source_topic_per.data = source_topic_per.from_df(df)

def update_corr():
    asset = asset_text.value
    word = word_text.value
    wfname = '%s/%s_0.5.csv'%(const.WORD_DIR, word)
    afname = '%s/%s.csv'%(const.ASSET_DIR, asset)
    if os.path.exists(wfname) and os.path.exists(afname):
        wdf = pd.read_csv(wfname)
        adf = pd.read_csv(afname)
        wdf.index = pd.to_datetime(wdf['date'], format='%Y-%m-%d')
        adf.index = pd.to_datetime(adf['date'], format='%Y-%m-%d')
        corr = word_heat_level.get_correlation(wdf['relative'], adf['close'])
        source_corr.data = {'date': corr.index, 'corr': corr.values}
        plot_corr.title.text = word + u'词频与' + asset + u'价格相关性'
    else:
        plot_corr.title.text = u'关键词或资产不存在'

def update_topic():
    fname = '%s/topic_words/topic_%s_twords.xlsx'%(const.TOPIC_DIR, topic_number.value)
    print fname
    df = pd.read_excel(fname)
    source_topic_words.data = source_topic_words.from_df(df)

    # word_heat_level.get_topic_heat(topic_number.value)
    fname = '%s/%s.xlsx'%(const.TOPIC_CLASS_DIR, topic_number.value)
    print fname
    df = pd.read_excel(fname)
    source_topic_absolute.data = {'date': pd.to_datetime(df['date']), 'ts': df['absolute']}
    source_topic_relative.data = {'date': pd.to_datetime(df['date']), 'ts': df['relative']}
    # source_topic_absolute.data = source_topic_absolute.from_df(df[['absolute']])
    # source_topic_relative.data = source_topic_relative.from_df(df[['relative']])

def update_wei_index():
    fname = '%s/%s_zt.xlsx'%(const.WEI_INDEX_DIR, word_select.value)
    df = pd.read_excel(fname, index_col=0)
    source_wei_index.data = {'date': df.index, 'pc': df['value']}
    plot_wei_index.title.text = word_select.value + u'微指数'

years_selections = [str(year) for year in range(2010, 2018)]
year_select = Select(value="2010", title="开始年份", width=200, options=years_selections)
year_select.on_change("value", lambda attr, old, new: update_data())
slider = TextInput(title="阈值", value="0.5")
# slider = Slider(title="阈值", start=0.0, end=1.0, value=0.3, step=0.1)
slider.on_change('value', lambda attr, old, new: update_data())
text = TextInput(title="关键词（例如：MPA、房地产、通胀）", value=u'楼市')
text.on_change('value', lambda attr, old, new: update_data())
button = Button(label=u"下载数据", button_type="success", width=300)
button.callback = CustomJS(args=dict(source=source_download),
                           code=open(join(dirname(__file__), "download.js")).read())
topic_number = Select(value='0', title=u'主题', width=200, options=[str(i) for i in range(100)])
topic_number.on_change('value', lambda attr, old, new: update_topic())
word_select = Select(value=words[0], title=u'选择关键词', width=200, options=words)
word_select.on_change('value', lambda attr, old, new: update_wei_index())

# absolute_corr_columns = [TableColumn(field=x, title=x) for x in assets]
# absolute_corr_data_table = DataTable(source=source_absolute_corr, columns=absolute_corr_columns, width=1000)
# asset_text = TextInput(title=u'资产', value='AU9999.SGE')
# asset_text.on_change('value', lambda attr, old, new: update_corr())
# word_text = TextInput(title=u'关键词', value=u'加息')
# word_text.on_change('value', lambda attr, old, new: update_corr())

update_data()
# update_correlation()
# update_corr()
update_percentile()
update_topic()
update_wei_index()

# Set up layouts and add to document
inputs = widgetbox(text, slider, year_select, button)
table = widgetbox(data_table)
# text_box = row(asset_text, word_text)
topic_inputs = widgetbox(topic_number)
topic_table_wid = widgetbox(topic_table)

curdoc().add_root(column(word_select, plot_wei_index, per_table, row(inputs, table), plot_absolute, plot, plot_weighted,
                         topic_per_table, row(topic_inputs, topic_table_wid), plot_topic_absolute, plot_topic_relative))
curdoc().title = u"关键词历史热度"
