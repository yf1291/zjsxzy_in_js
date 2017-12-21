# encoding: utf-8

import update_data
import momentum
import fundamental
import utils

def main():
    # 测试创建一个factor文件
    # update_data.create_factor_file('600835.SH')
    # 测试momentum因子计算
    # mom = momentum.get_k_day_return('600835.SH', 120)
    # 测试加入momentum因子
    # update_data.add_factors_to_factor_file('600835.SH')
    # 测试更新所有因子
    # update_data.update_factors('600835.SH')
    # 测试创建所有factor文件
    # update_data.create_all_factor_files()
    # 测试添加因子到所有factor文件
    # update_data.add_factors_to_all_factor_file()
    # 测试添加所有因子到所有factor文件
    # update_data.add_factors_to_all_factor_file()
    # 测试更新factor文件
    # update_data.update_all_factors()
    # 测试生成报告期
    # dates = utils.generate_rptdates('1990-01-01', '2017-12-20')
    # print dates
    # 测试生成基本面数据
    # fundamental.create_fundamental_file('603055.SH')
    # 测试添加基本面行情数据
    # fundamental.add_fundamental_indicator_to_file('603055.SH', 'eps_ttm')
    # 测试更新基本面行情数据
    # fundamental.update_fundamental_file('600835.SH')
    # 测试创建所有股票基本面数据
    # fundamental.create_all_factor_files()
    # 测试给所有股票基本面数据加入eps_ttm
    fundamental.add_factor_all_fundamental_files('eps_ttm')

if __name__ == '__main__':
    main()
