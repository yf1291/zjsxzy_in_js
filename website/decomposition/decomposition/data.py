# encoding: utf-8
import numpy as np
import pandas as pd

import const
import decomp

def update_data(start_date, end_date):
    df = pd.read_excel(const.INDEX_FILE)
    res = {'code': [], 'valuation_ret': [], 'earning_ret': [], 'dividend_ret': [], 'total_ret': [], 'name': []}
    for i in df.index:
        code, tcode, name = df.loc[i]['code'], df.loc[i]['t_code'], df.loc[i]['name']
        # print name
        v_ret, e_ret, d_ret, t_ret = decomp.decompose_return(code, tcode, start_date, end_date)
        res['code'].append(code)
        res['valuation_ret'].append(v_ret)
        res['earning_ret'].append(e_ret)
        res['dividend_ret'].append(d_ret)
        res['total_ret'].append(t_ret)
        res['name'].append(name)
    rdf = pd.DataFrame(res)
    rdf.to_excel(const.DECOMP_FILE, index=False)

def update_data_from_excel(start_date, end_date):
    df = pd.read_excel(const.INDEX_FILE)
    res = {'code': [], 'valuation_ret': [], 'earning_ret': [], 'dividend_ret': [], 'total_ret': [], 'name': []}
    for i in df.index:
        code, tcode, name = df.loc[i]['code'], df.loc[i]['t_code'], df.loc[i]['name']
        # print name
        v_ret, e_ret, d_ret, t_ret = decomp.decompose_return_from_excel(code, tcode, start_date, end_date)
        res['code'].append(code)
        res['valuation_ret'].append(v_ret)
        res['earning_ret'].append(e_ret)
        res['dividend_ret'].append(d_ret)
        res['total_ret'].append(t_ret)
        res['name'].append(name)
    rdf = pd.DataFrame(res)
    # print(rdf)
    rdf.to_excel(const.DECOMP_FILE, index=False)

if __name__ == '__main__':
    update_data('2018-01-01', '2018-10-30')
    # update_data_from_excel("2018-01-01", "2018-10-30")