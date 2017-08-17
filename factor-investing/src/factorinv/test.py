# encoding: utf-8
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

import const
import utils
import analysis
import index_factor

def test_index_factor_return():
    print("test index factor return")
    files = [f for f in os.listdir(const.INDEX_FACTOR_DIR)]
    pnl = utils.get_all_panel(const.INDEX_FACTOR_DIR, files)
    # 得到收益率
    pnl.ix[:, :, 'return'] = pnl.minor_xs('close').pct_change()
    # 计算Momentum因子收益率
    k = 60
    df = pnl.minor_xs('return').rolling(window=k).mean()
    return_df = pnl.minor_xs('return')
    daily_return = analysis.factor_return(df, return_df, threshold=0.2)
    daily_return = daily_return[daily_return != 0]
    # print daily_return
    utils.get_metrics(daily_return)
    acc_ret = utils.get_accumulated_return(daily_return)
    acc_ret.plot()
    plt.show()

if __name__ == '__main__':
    # test_index_factor_return()
    # pnl = utils.get_factor_panel(['000002.SZ'], 'A,B,D')
    index_factor.pe('000016.SH')
