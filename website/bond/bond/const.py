# encoding: utf-8

BOND_DIR = 'D:/Data/bonds'
treasury_file = '%s/treasury.xlsx'%(BOND_DIR)
usa_treasury_file = '%s/usa_treasury.xlsx'%(BOND_DIR)
libor_file = '%s/libor.xlsx'%(BOND_DIR)
corporate_file = '%s/corporate.xlsx'%(BOND_DIR)
repo_file = '%s/repo.xlsx'%(BOND_DIR)
currency_file = '%s/currency.xlsx'%(BOND_DIR)
bank_file = '%s/bank.xlsx'%(BOND_DIR)
base_file = '%s/base.xlsx'%(BOND_DIR)
product_file = '%s/product.xlsx'%(BOND_DIR)

edb2col = {'M1001099': 'CGB3M',
             'M1001102': 'CGB1Y',
             'M1001110': 'CGB10Y',
             'G0000891': 'UST10Y',
             'M1001858': 'SHIBOR3M',
             'M1000368': 'CB(AAA)1Y',
             'M1000372': 'CB(AAA)5Y',
             'M1000420': 'CB(AA)1Y',
             'M1000424': 'CB(AA)5Y',
             'M1001794': 'R001',
             'M1001795': 'R007',
             'M1006336': 'DR001',
             'M1006337': 'DR007',
             'M0290205': 'USDCNY spot',
             'M0068014': 'USDCNY NDF 1Y',
             'M1004271': u'中债国开债到期收益率 10年',
             'M1004263': u'中债国开债到期收益率 1年',
             'M0074413': u'理财产品预期年收益率 3个月',
             'M0074415': u'理财产品预期年收益率 6个月',
             'M0074417': u'理财产品预期年收益率 1年',
             'M1001791': u'美国国债到期收益率 10年',
             'M1001787': u'美国国债到期收益率 2年'}
col2edb = {v: k for k, v in edb2col.iteritems()}
