# encoding: utf-8

import pandas as pd

def wind2df(raw_data):
    dic = {}
    if len(raw_data.Times) == 1:
        Data = raw_data.Data[0]
    else:
        Data = raw_data.Data
    for data, code in zip(Data, raw_data.Codes):
        dic[str(code)] = data
    return pd.DataFrame(dic, index=raw_data.Times)
