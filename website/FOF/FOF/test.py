# encoding: utf-8
import utils
import data
import pandas as pd
import datetime
import comp
import correlation
import stock_fund
from WindPy import w
import const

if __name__ == '__main__':
    '''
    rptdates = utils.generate_rptdate('2010-01-01')
    rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    w.start()
    data = w.wss('160133.OF', 'issue_date')
    issue_date = data.Data[0][0]
    rptdates = [rptdate for rptdate in rptdates if rptdate > issue_date]
    utils.download_season_rpt('160133.OF', rptdates)
    # data.update_stock_season_rpt()
    '''
    # comp.save_comp_dataframe()
    # comp.save_comp_rpt()
    # comp.get_all_comp_daily_return()
    # comp.get_all_comp_position()
    # comp.comp_analysis()
    # print data.download_index_close('884224.WI', '2017-09-01', '2017-10-10')
    # data.update_theme_data()
    # data.update_concept_data()
    # data.update_sector_data()
    # data.update_season_rpt('660002.OF', [pd.to_datetime('2017-09-30')])
    # ret = comp.get_comp_daily_return(u'华夏基金管理有限公司')
    # print ret[ret.index >= '2017-01-01']
    # df = correlation.get_dataframe('001542.OF', '886043.WI')
    # print df
    # comp.comp_analysis()
    '''
    stock_df = stock_fund.get_stock_fund()
    rptdates = utils.generate_rptdate('2010-01-01')
    rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    for ticker, issue_date in zip(stock_df['wind_code'], stock_df['issue_date']):
        print('updating %s season report...'%(ticker))
        fund_rptdates = [rptdate for rptdate in rptdates if rptdate > issue_date]
        print fund_rptdates
        data.update_season_rpt(ticker, fund_rptdates)
        break
    '''
    # comp.get_comp_daily_return(u'信达澳银基金管理有限公司')
    # rptdates = utils.generate_rptdate('2010-01-01')
    # rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    # df = utils.download_season_rpt('001410.OF', rptdates)
    # df.to_excel('%s/%s.xlsx'%(const.RPT_DIR, '001410.OF'))
    # data.add_old_data('000011.OF')
    # data.add_old_rpt('000011.OF')
    # data.update_stock_season_rpt()
    # data.update_bond_season_rpt()
    # data.update_mixed_season_rpt()
    # comp.save_comp_dataframe()
    # comp.save_comp_rpt()
    # comp.get_all_comp_daily_return()
    # rptdates = utils.generate_rptdate('2000-01-01')
    # rptdates = pd.to_datetime(rptdates, format='%Y-%m-%d')
    # data.update_season_rpt('040002.OF', rptdates)
    comp.save_comp_rpt()
    # comp.get_comp_daily_return(u'华安基金管理有限公司')
