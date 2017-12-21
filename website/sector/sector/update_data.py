import pandas as pd
from WindPy import w

import const

def download_index_close(wind_code, start_date, end_date):
    w.start()
    data = w.wsd(wind_code, 'close', '2017-11-01', end_date)
    return utils.wind2df(data)

def save_theme_from_excel():
    df = pd.read_excel('D:/Data/list/sw-sector.xlsx')
    for wind_code in df.columns:
        print wind_code
        temp = df[[wind_code]]
        temp.columns = ['close']
        temp.to_excel('%s/%s.xlsx'%(const.INDEX_DIR, wind_code))

if __name__ == '__main__':
    save_theme_from_excel()
