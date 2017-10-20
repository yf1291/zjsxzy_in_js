import data

if __name__ == '__main__':
    df = data.get_option_list()
    data.download_options_history(df)
