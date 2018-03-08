# encoding: utf-8

def change(x):
    if x > 0:
        return u'上涨%.2f%%'%(x)
    else:
        return u'下跌%.2f%%'%(-x)

def up_down(x):
    if x > -0.00001:
        return u'增加%.2f%%'%(x)
    else:
        return u'减少%.2f%%'%(-x)

def hk_fund_name(name):
    return name.find(u'港') != -1 or name.find(u'H股') != -1 or name.find(u'恒生') != -1

def gold_fund_name(name):
    return name.find(u'黄金') != -1

def oil_fund_name(name):
    return name.find(u'原油') != -1

def bond_fund_type(ftype):
    if ftype == None:
        return False
    return ftype.strip() == u'债券型基金'

def money_fund_type(ftype):
    if ftype == None:
        return False
    return ftype.strip() == u'货币市场型基金'

def oversea_fund_type(ftype):
    if ftype == None:
        return False
    return ftype.strip() == u'国际(QDII)基金'

def fixed_fund_type(type):
    if ftype == None:
        return False
    return ftype.strip() == u'混合型基金'
