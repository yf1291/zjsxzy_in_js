# encoding: utf-8
import numpy as np
import pandas as pd
from WindPy import w

import const
import utils


def get_info_wind(code, fields, date):
    w.start()
    data = w.wss(code, fields, "tradeDate=%s"%(date))
    df = pd.DataFrame(np.array(data.Data).T, index=[date], columns=data.Fields)
    return df

def decompose_return(code, tcode, start_date, end_date):
    w.start()
    '''
    在时间区间[start_date, end_date]中分解收益率
    '''
    # 计算估值和价格变动
    # print(code)
    # print(tcode)
    sdf = get_info_wind(code, 'close,estpe_fy1,estpe_fy2', start_date)
    end_year = '%s-12-31'%(end_date.split('-')[0])
    days = utils.days_delta(end_year, start_date)
    start_valuation = sdf['ESTPE_FY1'][0] * days / 365 + sdf['ESTPE_FY2'][0] * (365 - days) / 365
    edf = get_info_wind(code, 'close,estpe_fy1,estpe_fy2', end_date)
    days = utils.days_delta(end_year, end_date)
    end_valuation = edf['ESTPE_FY1'][0] * days / 365 + edf['ESTPE_FY2'][0] * (365 - days) / 365
    valuation_ret = end_valuation / start_valuation - 1
    price_ret = edf['CLOSE'][0] / sdf['CLOSE'][0] - 1
    # print(start_valuation)
    # print(end_valuation)
    # print(sdf)
    # print(edf)
    # 计算盈利变动
    start_earning = sdf['CLOSE'][0] / start_valuation
    end_earning = edf['CLOSE'][0] / end_valuation
    earning_ret = end_earning / start_earning - 1
    # 计算全回报收益率
    data = w.wss(tcode, 'close', 'tradeDate=%s'%(start_date))
    start_close = data.Data[0][0]
    data = w.wss(tcode, 'close', 'tradeDate=%s'%(end_date))
    end_close = data.Data[0][0]
    total_ret = end_close / start_close - 1
    # 计算红利变动
    dividend_ret = total_ret - price_ret
    return valuation_ret, earning_ret, dividend_ret, total_ret

def decompose_return_from_excel(code, tcode, start_date, end_date):
    pe1 = pd.read_excel(const.DATA_FILE, sheet_name='estpe_fy1')
    pe2 = pd.read_excel(const.DATA_FILE, sheet_name='estpe_fy2')
    end_year = '%s-12-31'%(end_date.split('-')[0])
    days = utils.days_delta(end_year, start_date)
    start_valuation = pe1.loc[start_date, code] * days / 365 + pe2.loc[start_date, code] * (365 - days) / 365
    days = utils.days_delta(end_year, end_date)
    end_valuation = pe1.loc[end_date, code] * days / 365 + pe2.loc[end_date, code] * (365 - days) / 365
    valuation_ret = end_valuation / start_valuation - 1

    pdf = pd.read_excel(const.DATA_FILE, sheet_name='price')
    price_ret = pdf.loc[end_date, code] / pdf.loc[start_date, code] - 1
    start_earning = pdf.loc[start_date, code] / start_valuation
    end_earning = pdf.loc[end_date, code] / end_valuation
    earning_ret = end_earning / start_earning - 1

    tdf = pd.read_excel(const.DATA_FILE, sheet_name='total')
    total_ret = tdf.loc[end_date, tcode] / tdf.loc[start_date, tcode] - 1

    dividend_ret = total_ret - price_ret
    return valuation_ret, earning_ret, dividend_ret, total_ret