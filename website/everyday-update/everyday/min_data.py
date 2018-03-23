# encoding: utf-8
import pandas as pd
import numpy as np
from WindPy import w
import os

import const
import utils

def download_data(codes, date):
    w.start()
    for code in codes:
        fname = '%s/%s.xlsx'%(const.MIN_STOCK_DIR, code)
        if os.path.exists(fname):
            old_df = pd.read_excel(fname)
            if (old_df.index[0].day == pd.to_datetime(date).day):
                if old_df.index[0] >= pd.to_datetime(date) and pd.to_datetime(date) <= old_df.index[-1]:
                    print('skipping %s'%(code))
                    continue
            print('downloading %s'%(code))
            data = w.wsi(code, 'close,amt', '%s 09:00:00'%(date), '%s 15:00:00'%(date))
            df = pd.DataFrame(np.array(data.Data).T, index=data.Times, columns=['close', 'amt'])
            if df.shape[0] == 0:
                print('shape error')
                continue
            if pd.to_datetime(date) < old_df.index[0]:
                df = df.append(old_df)
            elif pd.to_datetime(date) > old_df.index[-1]:
                df = old_df.append(df)
            # df = pd.read_excel(fname)
            # df = df.loc[df.index.drop_duplicates(keep='first')]
            df.to_excel(fname)

if __name__ == '__main__':
    codes = utils.get_index_component('000300.SH')
    # codes = ['000001.SZ']
    # print codes
    download_data(codes, '2018-01-24')
