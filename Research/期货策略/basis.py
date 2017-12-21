import pandas as pd
from WindPy import w
import os

DATA_DIR = 'D:/Data/derivatives/futures/'
start_date, end_date = '2013-01-01', '2017-12-12'

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[field.lower()] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def short_long_period(df, short, longp):
    df['short basis diff'] = df['basis diff'].rolling(window=short).mean()
    df['long basis diff'] = df['basis diff'].rolling(window=longp).mean()
    strategy = df.dropna().copy()
    bought = False
    flag = 0
    strategy['signal'] = 0
    strategy['hold'] = 0
    prev_diff = 100.
    for date in strategy.index:
        strategy['signal'][date] = flag
        strategy['hold'][date] = 1 if bought else 0
        diff = df.loc[date]['short basis diff'] - df.loc[date]['long basis diff']
        if not bought and diff > 0 and prev_diff < 0:
            bought = True
            flag = 1
        elif bought and diff < 0 and prev_diff > 0:
            bought = False
            flag = -1
        else:
            flag = 0
        prev_diff = diff
    ret = strategy['close'].pct_change() * strategy['hold']
    print('saving %d-%d'%(short, longp))
    pd.DataFrame({'return': ret}).to_excel('./data/%d-%d.xlsx'%(short, longp))

def main():
    w.start()
    data = w.wsd('000300.SH', 'close', start_date, end_date)
    df = wind2df(data)
    fnames = [f for f in os.listdir(DATA_DIR) if f.startswith('IF')]
    oi_df = pd.DataFrame(index=df.index)
    p_df = pd.DataFrame(index=df.index)
    for f in fnames:
        fname = '%s/%s'%(DATA_DIR, f)
        wind_code = f.rstrip('.xlsx')
        temp = pd.read_excel(fname)
        oi_df[wind_code] = temp['oi']
        p_df[wind_code] = temp['close']
    idx_max = oi_df.idxmax(axis=1)
    future_close = pd.Series(index=idx_max.index)
    for index in idx_max.index:
        future_close.loc[index] = p_df.loc[index][idx_max.loc[index]]
    df['future'] = future_close
    df['basis'] = df['future'] - df['close']
    df['basis diff'] = df['basis'].diff()

    for s in range(5, 20):
        for l in range(s+15, 240, 5):
            short_long_period(df, s, l)

if __name__ == '__main__':
    main()
