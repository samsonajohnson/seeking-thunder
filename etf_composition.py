import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import datetime as dt
import requests
import yfinance as yf
from time import sleep
import json
import difflib
import re
import bisect
import glob

import bs4
from bs4 import BeautifulSoup
#import ipdb
sns.set_style('darkgrid')

from api_keys import sec_email

headers = {"User-Agent": sec_email} # Your email goes here


def NPORT_Filings_from_CIK(cik, headers=headers):
    headers = headers
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    sleep(2)
    filings = requests.get(url, headers=headers).json()
    filings_df = pd.DataFrame(filings["filings"]["recent"])
    nport_filings_df = filings_df[filings_df["form"] == "NPORT-P"]
    nport_filings_df.loc[:,'filingDate'] = pd.to_datetime(nport_filings_df['filingDate'])
    nport_filings_df.loc[:,'reportDate'] = pd.to_datetime(nport_filings_df['reportDate'])
    return nport_filings_df


def gen_company_name_and_cik_list(headers=headers):
    headers = headers
    url = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"
    sleep(2)
    response = requests.get(url, headers=headers)
    # filings_df = pd.DataFrame(filings)
    return response.text.split('\n')


# cik_list = gen_company_name_and_cik_list()


def holdings_from_NPORT(accessionNumber, primaryDocument, reportDate, cik_list, headers=headers):
  
    sleep(2)

    url = f"https://www.sec.gov/Archives/edgar/data/1064641/{accessionNumber}/{primaryDocument}"
    
    response = requests.get(url, headers=headers)

    assert response.status_code == 200

    soup = BeautifulSoup(response.text, 'html.parser')

    stocks_source = soup.findAll("td",string='a. Name of issuer (if any). \n\t\t\t\t')
    CUSIPs_source = soup.findAll("td",string='d. CUSIP (if any).\n\t\t\t\t')
    weights_source = soup.findAll('td',string='Percentage value compared to net assets of the Fund.\n\t\t\t')

    stocks = [str(stock.parent.find('div').contents[0]) for stock in stocks_source]
    CUSIPs = [str(CUSIP.parent.find('div').contents[0]) for CUSIP in CUSIPs_source]
    weights = [float(weight.parent.find('div').contents[0]) for weight in weights_source]
    CIKs = []

    for stock in stocks:
        index = bisect.bisect_left(cik_list, stock.upper())
        CIKs.append(cik_list[index].split(":")[1])

    date_str = reportDate.strftime('%Y%m%d')
    
    holdings = pd.DataFrame({'Stock': stocks, 'CIK': CIKs, date_str: weights})

    # there are some duplicate CIKs within the holdings dataframe. This comes from the fact that
    # some shares for the same company are different. E.g., GOOG carries voting rights while
    # GOOGL does not, but they have the same CIK.
    # I am treating all dupplicate CIKs as the same for now, which is not the correct way to go
    # about this. Different share classes can have significantly different prices, but there I could not
    # find a robust mapping to identify the different share classes.
    # Look into PERMNO, ISIN
    
    aggregate_functions = {'Stock':'first',date_str:'sum'}
    holdings = holdings.groupby(holdings['CIK'],as_index=False).aggregate(aggregate_functions)
    #tickers = find_ticker(holdings,load_ticker_cik(path="../data/"))

    #holdings.insert(1,"Tickers",tickers)
    elem = soup.findAll('td',string="Series ID")[0]
    
    seriesID = str(elem.parent.parent.div.contents[0])

    return seriesID, holdings


def load_ticker_cik(path='./data/'):
    """
    A function to read in the CIK lookup json from SEC website ADD URL
    """  
    # file should be stored in ./data/, but could possibly change
    with open(path+'company_ticker.json', 'r') as fh:
        new_json = json.load(fh)
    # need to transpose, just formatting I think
    tbl = pd.DataFrame.from_dict(new_json).T
    
    return tbl


def find_ticker(holding_dict, lookup_tbl):
    # empty list to store tickers
    tickers = []
    # loop over every row in the dataframe
    for index, row in holding_dict.iterrows():
        # first try and find CIK
        # print("STOCK  ", row['CIK'])
        if int(row['CIK']) in lookup_tbl['cik_str'].values:
            ticker = lookup_tbl[lookup_tbl['cik_str'] == int(row['CIK'])]['ticker'].values[0]
        else:
            # this is a quick sequence matcher. It finds the closest match and uses that as the ticker. 
            # PROBABLY A BETTER WAY TO LOOK THIS UP
            max_row = lookup_tbl.iloc[lookup_tbl.apply(lambda x: difflib.SequenceMatcher(None, row['Stock'].lower(), x['title'].lower()).ratio(),axis=1).argmax()]
            ticker = max_row['ticker']
        if ticker == 'MAAI':
            ticker == 'MAA' # This is a messy quick fix for a bug in our code that affects one particular stock ticker
        tickers.append(ticker)
    return tickers


def load_etf_comps():
    """
    Method to read in ALL the nport files from the data directory
    """
    file_list = glob.glob('data/S*')
    master_dict = {}
    for file_name in file_list:
        accession_key = file_name.split('/')[-1].split('_')[0]
        if accession_key not in master_dict.keys():
            master_dict[accession_key] = {}
        date = file_name.split('/')[-1].split('_')[1].split('.')[0]
        df_temp = pd.read_pickle(file_name)
        master_dict[accession_key][date] = df_temp
    return master_dict


if __name__ == '__main__':
    #ipdb.set_trace()
    #run to generate new save files
    filings = NPORT_Filings_from_CIK('0001064641')
    
    seriesID_to_ticker_dict = {
    'S000006408': 'XLY',
    'S000006409': 'XLP',
    'S000006410': 'XLE',
    'S000006411': 'XLF',
    'S000006412': 'XLV',
    'S000006413': 'XLI',
    'S000006414': 'XLB',
    'S000006415': 'XLK',
    'S000006416': 'XLU',
    'S000051152': 'XLRE',
    'S000062095': 'XLC'
}
    
    cik_list = gen_company_name_and_cik_list()
    SPDR_holdings = {}

    for i in range(len(filings)):
        accessionNumber = filings["accessionNumber"].iloc[i].replace("-","")
        primaryDocument = filings["primaryDocument"].iloc[i]
        reportDate = filings["reportDate"].iloc[i]

        seriesID, holdings = holdings_from_NPORT(accessionNumber,primaryDocument,reportDate,cik_list,headers=headers)
        
        if seriesID in SPDR_holdings:
            SPDR_holdings[seriesID] = SPDR_holdings[seriesID].merge(holdings,how='outer').fillna(0)
            
        else:
            SPDR_holdings[seriesID] = holdings

    lookup_tbl = load_ticker_cik(path='../data/')
    
    for i,seriesID in enumerate(SPDR_holdings.keys()):
        # for each seriesID, find the ticker values
        tickers = find_ticker(SPDR_holdings[seriesID], lookup_tbl)
        SPDR_holdings[seriesID].insert(1,"Tickers",tickers)
        SPDR_holdings[seriesID].to_csv(f"../data/{seriesID_to_ticker_dict[seriesID]}_holdings.csv")
