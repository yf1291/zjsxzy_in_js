import pandas as pd
import numpy as np
import datetime
from WindPy import w

import const

w.start()
date = datetime.date.today() - datetime.timedelta(1)

def stock_list(index='881001.WI'):
    data = w.wset("sectorconstituent","date=%s;windcode=%s;field=wind_code,sec_name"%(date.strftime('%Y-%m-%d'), index))
    df = pd.DataFrame(np.array(data.Data).T, columns=['wind_code', 'sec_name'])
    return df

def main():
    fname = '%s/volume.xlsx'%(const.DATA_DIR)
    df = stock_list()
    df = df.set_index('wind_code')
    data = w.wss(df.index.tolist(), 'industry_citic', 
                'tradeDate=%s;industryType=4'%(date.strftime('%Y%m%d')))
    df['industry'] = data.Data[0]
    data = w.wss(df.index.tolist(), "free_turn,volume,amt,pct_chg", "tradeDate=%s;cycle=D"%(date.strftime('%Y%m%d')))
    df['turnover'], df['volume'], df['amt'], df['pct_chg'] = data.Data
    df = df.sort_values('amt', ascending=False)
    df.to_excel(fname)

if __name__ == '__main__':
    main()
    