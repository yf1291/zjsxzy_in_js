# encoding: utf-8
import numpy as np
import pandas as pd
import datetime
import os
import sys
from os.path import dirname, join

from sector import sector_return

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, CustomJS, NumberFormatter
from bokeh.models.widgets import Slider, TextInput, TableColumn, DataTable, Select, Button
from bokeh.plotting import figure

source_table = ColumnDataSource(data=dict())

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

update_data()

curdoc().add_root(row(box, tables))
curdoc().title = u"A股行业轮动"
