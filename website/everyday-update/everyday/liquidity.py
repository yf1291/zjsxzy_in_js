# encoding: utf-8

import pandas as pd
import numpy as np
from sklearn import preprocessing

import utils
import const

def liquidity_value(X):
    m = 4
    centered_matrix = X - X.mean(axis=0)
    cov = np.dot(centered_matrix.T, centered_matrix)
    eigvals, eigvecs = np.linalg.eig(cov)
    F = np.dot(X, eigvecs[:, :m])
    lambdas = eigvals[:m]
    lambdas = lambdas / lambdas.sum()
    F_score = np.dot(F, lambdas.T)
    return F_score

def cal_index_liquidity(index_code):
    codes = utils.get_index_component(index_code)
    dic = {}
    indicators = [
              '20-day amt',
              '20-day turnover',
              '20-day close',
              '20-day ret',
              'volatility',
              '20-day mfd_buyamt_a',
              '20-day mfd_sellamt_a',
             ]
    for ticker in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
        df = pd.read_excel(fname, index_col=0)
        df['20-day turnover'] = df['turnover'].rolling(window=20).sum()
        df['20-day mfd_buyamt_a'] = df['mfd_buyamt_a'].rolling(window=20).sum()
        df['20-day mfd_sellamt_a'] = df['mfd_sellamt_a'].rolling(window=20).sum()
        df['20-day amt'] = df['amt'].rolling(window=20).sum()
        df['ret'] = df['close'].pct_change()
        df['20-day ret'] = df['ret'].rolling(window=20).mean()
        df['20-day close'] = df['close'].rolling(window=20).mean()
        df['volatility'] = df['ret'].rolling(window=20).std()
        X = df[indicators].fillna(df[indicators].mean())
        try:
            scaler = preprocessing.StandardScaler().fit(X)
            X_scaled = scaler.transform(X)
            F_score = liquidity_value(X_scaled)
            df['liquidity'] = F_score
            dic[ticker] = df[['amt', 'liquidity']]
        except Exception as e:
            print(e)
            print(ticker)
    pnl = pd.Panel(dic)
    avg_liquidity = pnl.minor_xs('liquidity').mean(axis=1)
    return avg_liquidity

def cal_market_liquidity():
    df = pd.DataFrame({'sz50': cal_index_liquidity('000016.SH')})
    df['wdqa'] = cal_index_liquidity('881001.WI')
    df['hs300'] = cal_index_liquidity('000300.SH')
    df['zz500'] = cal_index_liquidity('000905.SH')
    df['zz800'] = cal_index_liquidity('000906.SH')
    df['zxb'] = cal_index_liquidity('399006.SZ')
    df['cyb'] = cal_index_liquidity('399005.SZ')
    df.to_excel('%s/liquidity.xlsx'%(const.DATA_DIR))

def cal_index_liquidity_proxy(index_code='881001'):
    codes = utils.get_index_component(index_code)
    dic = {}
    for ticker in codes:
        fname = '%s/%s.xlsx'%(const.STOCK_DIR, ticker)
        df = pd.read_excel(fname, index_col=0)
        # Amihud
        df['ret'] = df['close'].pct_change()
        df['amihud'] = df['ret'].abs() * 10e6 / (df['volume'] * df['close'])
        # Wu
        df['turn'] = df['amt'] / df['mkt_freeshares']
        df['wu'] = df['ret'].abs() / df['turn']
        # Corwin and Schultz
        df['high t-1'] = df['high'].shift(1)
        df['low t-1'] = df['low'].shift(1)
        df['beta'] = np.log(df['high']/df['low'])**2 + np.log(df['high t-1']/df['low t-1'])**2
        df['gamma'] = np.log(df[['high', 'high t-1']].max(axis=1) / df[['low', 'low t-1']].min(axis=1))**2
        df['alpha'] = (np.sqrt(2*df['beta'])-np.sqrt(df['beta']))/(3-2*np.sqrt(2)) - np.sqrt((df['gamma'])/(3-2*np.sqrt(2)))
        df['CS'] = 2*(np.exp(df['alpha'])-1)/(1+np.exp(df['alpha']))
        # Roll
        df['ret_2'] = df['ret'].shift(1)
        df['roll'] = df['ret'].rolling(window=60).cov(df['ret_2'])
        df['roll'] = 2 * np.sqrt(df['roll'].abs())
        dic[ticker] = df[['amihud', 'wu', 'CS', 'roll']]
    pnl = pd.Panel(dic)
    # pnl.ix[:, :, 'amihud'] = pnl.minor_xs('ret').abs() * 10e6 / (pnl.minor_xs('volume') * pnl.minor_xs('close'))
    pnl.ix[:, :, 'amihud'] = pnl.minor_xs('amihud').replace(np.inf, np.nan)
    # pnl.ix[:, :, 'wu'] = pnl.minor_xs('ret').abs() / pnl.minor_xs('turn')
    pnl.ix[:, :, 'wu'] = pnl.minor_xs('wu').replace(np.inf, np.nan)
    # pnl.ix[:, :, 'high t-1'] = pnl.minor_xs('high').shift(1)
    # pnl.ix[:, :, 'low t-1'] = pnl.minor_xs('low').shift(1)
    # pnl.ix[:, :, 'beta'] = np.log(pnl.minor_xs('high') / pnl.minor_xs('low'))**2 + np.log(pnl.minor_xs('high t-1') / pnl.minor_xs('low t-1'))**2
    # pnl.ix[:, :, 'gamma'] = np.log(pnl.ix[:, :, ['high', 'high t-1']].max(axis=2) / pnl.ix[:, :, ['low', 'low t-1']].min(axis=2))**2
    # pnl.ix[:, :, 'alpha'] = (np.sqrt(2*pnl.minor_xs('beta'))-np.sqrt(pnl.minor_xs('beta')))/(3-2*np.sqrt(2)) - np.sqrt(pnl.minor_xs('gamma')/(3-2*np.sqrt(2)))
    # pnl.ix[:, :, 'CS'] = 2*(np.exp(pnl.minor_xs('alpha'))-1) / (1+np.exp(pnl.minor_xs('alpha')))
    return pnl

def get_index_liquidity_proxy(pnl, index_code):
    print(index_code)
    codes = utils.get_index_component(index_code)
    return pnl[codes].minor_xs('amihud').median(axis=1), \
           pnl[codes].minor_xs('wu').median(axis=1), \
           pnl[codes].minor_xs('CS').median(axis=1).abs(), \
           pnl[codes].minor_xs('roll').median(axis=1)

def cal_market_liquidity_proxy():
    code = '881001.WI'
    pnl = cal_index_liquidity_proxy(code)
    amihud, wu, cs, roll = get_index_liquidity_proxy(pnl, code)
    df = pd.DataFrame({'amihud': amihud, 'wu': wu, 'corwin and schultz': cs, 'roll': roll})
    df.to_excel('%s/amihud_liquidity.xlsx'%(const.DATA_DIR))

def min_liquidity():
    codes = utils.get_index_component('000300.SH')
    dic = {}
    for code in codes:
        fname = '%s/%s.xlsx'%(const.MIN_STOCK_DIR, code)
        temp = pd.read_excel(fname)
        liquidity = temp.resample('D').apply(lambda x: x['close'].pct_change().abs() / x['amt'])
        dic[code] = pd.Series(liquidity.values, index=temp.index)
    df = pd.DataFrame(dic)
    # df.to_excel('%s/temp.xlsx'%(const.DATA_DIR))
    df = df.replace([np.inf, -np.inf], np.NAN)
    df['liquidity'] = df.median(axis=1)
    df[['liquidity']].to_excel('%s/min_liquidity.xlsx'%(const.DATA_DIR))

if __name__ == '__main__':
    # cal_market_liquidity()
    cal_market_liquidity_proxy()
    # min_liquidity()
