import data
import const

if __name__ == '__main__':
    # df = data.get_option_list()
    # data.download_options_history(df)
    # data.append_options_history(df)
    df = data.get_futures_list(const.BOND_10Y_FUT_LIST)
    data.download_futures_history(df)
