import main
import pandas as pd
import empyrical
import everyday.utils as utils
import everyday.const as const
import everyday.cost as cost

def test_sharpe(symbol, start_date, end_date):
    fname = "%s/%s.csv"%(const.DATA_DIR, symbol)
    dataframe = pd.read_csv(fname)
    dataframe['date'] = pd.to_datetime(dataframe['date'], format="%Y-%m-%d")
    dataframe = dataframe.set_index('date')
    dataframe['return'] = dataframe['close'].pct_change()
    dataframe = dataframe[(dataframe.index >= start_date) & (dataframe.index <= end_date)]
    dataframe.dropna(inplace=True)
    sharpe = utils.get_sharpe_ratio(dataframe['return'])
    print sharpe
    print empyrical.sharpe_ratio(dataframe['return'])

if __name__ == '__main__':
    # main.update_momentum_statistics()
    # test_sharpe('HSCAIT.HI', '2016-01-01', '2017-12-24')
    cost.cal_market_cost('HSCAIT.HI')
