import pandas as pd
import etf_composition
import glob


if __name__ == "__main__":
    # get all files
    file_list = glob.glob('../data/S*')
    lookup_tbl = etf_composition.load_ticker_cik(path='../data/')

    for file_name in file_list:
        # read in file
        df_temp = pd.read_pickle(file_name)
        # find tickers
        tickers = etf_composition.find_ticker(df_temp,lookup_tbl=lookup_tbl)
        # append
        df_temp['Ticker'] = tickers
        # save file
        df_temp.to_pickle(file_name)
    