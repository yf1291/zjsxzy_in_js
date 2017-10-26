import pandas as pd

def wind2df(raw_data):
    dic = {}
    for data, field in zip(raw_data.Data, raw_data.Fields):
        dic[field.lower()] = data
    return pd.DataFrame(dic, index=raw_data.Times)
