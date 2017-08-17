# encoding: utf-8

import pandas as pd
import numpy as np
from WindPy import w
import datetime
import calendar
import os

import utils
import const

def download_fundamental_data():
    codes = utils.get_index_component('881001.WI')
    years = range(2008, 2018)
    months = [3, 6, 9, 12]
    dates = ['%s-%s-%s'%(y, m, calendar.monthrange(y, m)[1]) for y in years for m in months]
    fields = 'roic,roe,roa'
    for code in codes:
        fname = '%s/%s.xlsx'%(const.FUNDAMENTAL_DIR, code)
        if os.path.exists(fname):
            continue
        print('downloading %s...'%(code))
        df = pd.DataFrame(columns=fields.split(','), index=pd.to_datetime(dates, format='%Y-%m-%d'))
        for date in df.index:
            wdata = w.wss(code, fields, 'rptDate=%s'%(date.strftime('%Y-%m-%d')))
            df.loc[date, :] = [x[0] for x in wdata.Data]
        df.to_excel(fname)
