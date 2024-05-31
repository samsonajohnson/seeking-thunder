#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import json
import difflib
import yfinance as yf
from sklearn.linear_model import LinearRegression

days_in_quarter = 63


# In[ ]:


# This part of the code is very ad-hoc, someone should clean it up---may be necessary to tweek data files to make it cleaner.

file_list = ['data\\S000006408.csv', 'data\\S000006409.csv', 'data\\S000006410.csv', 'data\\S000006411.csv', 'data\\S000006412.csv', 'data\\S000006413.csv', 'data\\S000006414.csv', 'data\\S000006415.csv', 'data\\S000006416.csv', 'data\\S000051152.csv', 'data\\S000062095.csv']

series_to_ticker_mapping = {
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

start_date = np.datetime64('2019-10-01')
end_date = np.datetime64('2024-04-01')

holdings_per_day = {}

for file_name in file_list:
    file_name = file_name.split('\\')[-1]
    series = file_name.split('.')[0]
    ticker = series_to_ticker_mapping[series]
    
    # Read the CSV
    df = pd.read_csv(f'data/{file_name}')
    df.index = df['Tickers']
    df = df.iloc[:,:3:-1]
    
    # This is an ad-hoc fix for the fact that some tickers are duplicated because the associated company name
    # label is not consistent (e.g. LOW in the ETF XLY)
    df = df.groupby(df.index).sum()
    
    df.columns = pd.to_datetime(df.columns)
    
    series_holdings_per_day = {}

    date_range = np.arange(start_date,end_date)

    for date in date_range:
        series_holdings_per_day[date] = df[df.columns[df.columns < date].max()]

    holdings_per_day[ticker] = pd.DataFrame(series_holdings_per_day).transpose() != 0
    
    holdings_per_day[ticker] = holdings_per_day[ticker].where(holdings_per_day[ticker] != 0,np.nan)


# In[ ]:


def returns(ticker):
    data = yf.Ticker(ticker).history(period='max')
    returns = (data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1)
    return returns

def log_returns(ticker):
    data = yf.Ticker(ticker).history(period='max')
    log_returns = np.log(data.Close / data.Close.shift(1))
    return log_returns

def betas(stock, etf, start_date, end_date, L_min=100, halflife=days_in_quarter):
    
    # L_min specifies how many days the stock must have been listed to calculate the beta coefficient.  
    # If the stock is quite newly listed, then the calculated beta value is unstable and not very meaningful 
    # (and so we will set beta = np.nan).  
    
    times = np.arange(start_date,end_date)#pd.date_range(start=start_date, end=end_date, freq='D')
    betas = []
    
    stock_returns = returns(stock)
    etf_returns = returns(etf)
    
    two_stocks = pd.DataFrame({stock: stock_returns, etf: etf_returns}).dropna()
    two_stocks.index = two_stocks.index.tz_localize(None)
    
    for t in times:
         
        # Include only columns through t-1 so that the beta on day t depends only on returns from before day t:
        
        etf_t = two_stocks.loc[:(t-1),etf].values.reshape(-1, 1)
        stock_t = two_stocks.loc[:(t-1),stock].values

        L = len(stock_t)
        
        alpha = 0.5 ** (1 / halflife)
        
        # Calculate exponentially decaying weights for linear regression, so that we weight more 
        # recent returns more heavily.
        
        weights = alpha ** (L - 1 - np.arange(L))
        weights /= weights.sum()
        
        # Compute regression coefficient beta, which measures how much the stock returns 
        # are expected to move in response to ETF returns.  Stocks in an ETF with larger betas
        # contribute more to the volatility of the ETF.  Intuitively, stocks with smaller beta
        # values are likely less related to the themes surrounding most high-volume selloffs of the ETF.
              
        model = LinearRegression()
        
        if L > L_min:
            model.fit(etf_t, stock_t, sample_weight=weights)
            beta = model.coef_[0]
        else:
            beta = np.nan
        
        betas.append(beta)
    
    return pd.Series(data = betas, index = times)


# Note that a beta value of np.nan can mean two different things: 
# (1) The stock wasn't part of the ETF that quarter.
# (2) The stock was too newly listed to get a robust beta value.

# In[ ]:


betas_per_day = {}

for etf in holdings_per_day.keys():
    df = holdings_per_day[etf]
    betas_per_day[etf] = pd.DataFrame({stock: betas(stock,etf,start_date,end_date) * df[stock] for stock in df.columns})

