import pandas as pd
from WindPy import w
import datetime

import const
import utils

def download_index_close(wind_code, start_date, end_date):
    w.start()
    data = w.wsd(wind_code, 'close', start_date, end_date)
    return utils.wind2df(data)

def save_theme_from_excel():
    df = pd.read_excel('D:/Data/list/sw-sector.xlsx')
    for wind_code in df.columns:
        print wind_code
        temp = df[[wind_code]]
        temp.columns = ['close']
        temp.to_excel('%s/%s.xlsx'%(const.INDEX_DIR, wind_code))

def update_data():
    df = pd.read_excel(const.SW_SECTOR_FILE, index_col=0)
    yesterday = datetime.datetime.today() - datetime.timedelta(1)
    for wind_code in df.index:
        fname = '%s/%s.xlsx'%(const.INDEX_DIR, wind_code)
        df = pd.read_excel(fname)
        if df.index[-1] <= yesterday:
            print('updating %s...'%(wind_code))
            start_date = pd.to_datetime(df.index[-1]) + datetime.timedelta(1)
            end_date = yesterday
            add_df = download_index_close(wind_code, start_date, end_date)
            df = df.append(add_df)
            df.to_excel(fname)

def save_to_file():
    df = pd.read_excel(const.SW_SECTOR_FILE, index_col=0)
    dic = {}
    for wind_code in df.index:
        fname = '%s/%s.xlsx'%(const.INDEX_DIR, wind_code)
        temp = pd.read_excel(fname)
        dic[wind_code] = temp['close']
    his_df = pd.DataFrame(dic)
    his_df.to_excel(const.SW_SECTOR_HIS_FIKE)

if __name__ == '__main__':
    # save_theme_from_excel()
    update_data()
    save_to_file()
