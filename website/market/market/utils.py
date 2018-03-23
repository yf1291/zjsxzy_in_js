# encoding: utf-8
import pandas as pd
import numpy as np
import datetime


def wind2df(data):
    columns = [c.lower() for c in data.Fields]
    return pd.DataFrame(np.array(data.Data).T, index=data.Times, columns=columns)

def get_end_date():
    if datetime.datetime.now().hour < 16:
        end_date = datetime.datetime.today() - datetime.timedelta(1)
    else:
        end_date = datetime.datetime.today()
    return end_date

def wind2df_economy(raw_data):
    dic = {}
    if len(raw_data.Times) == 1:
        Data = raw_data.Data[0]
    else:
        Data = raw_data.Data
    for data, code in zip(Data, raw_data.Codes):
        dic[str(code)] = data
    return pd.DataFrame(dic, index=raw_data.Times)

def next_date(date):
    return pd.to_datetime(date) + datetime.timedelta(1)
