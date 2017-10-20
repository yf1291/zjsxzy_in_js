import utils
import data
import pandas as pd
import datetime
import comp
from WindPy import w

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
    comp.save_comp_dataframe()
    comp.save_comp_rpt()
    comp.get_all_comp_daily_return()
    comp.get_all_comp_position()
    comp.comp_analysis()
    # print data.download_index_close('884224.WI', '2017-09-01', '2017-10-10')
    # data.update_theme_data()
    # data.update_concept_data()
