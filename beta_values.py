import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import json
import difflib
import yfinance as yf
from sklearn.linear_model import LinearRegression

days_in_quarter = 63

# Function to compute returns of stock from ticker

def returns(ticker,start_date=None,end_date=None):
    data = yf.Ticker(ticker).history(period='max')
    data.index = data.index.tz_localize(None)
    returns = (data['Close'] - data['Close'].shift(1)) / data['Close'].shift(1)
    if start_date is not None and end_date is not None:
        return returns.loc[str(start_date):str(end_date)]
    else:
        return returns
    
# Function to compute log returns of stock from ticker

def log_returns(ticker,start_date=None,end_date=None):
    data = yf.Ticker(ticker).history(period='max')
    data.index = data.index.tz_localize(None)
    log_returns = np.log(data.Close / data.Close.shift(1))
    if start_date is not None and end_date is not None:
        return log_returns.loc[str(start_date):str(end_date)]
    else:
        return log_returns

# Function to compute ETF betas of a stock over a specified time period.  The ETF beta of a stock in an ETF is defined as the coefficient of an exponentially weighted linear regression of the stock's daily returns (up to but not including the given date) against the ETF's returns.  Intuitively, a smaller beta means the stock's returns respond less to the returns of the ETF.  (We call the stocks with betas in the bottom 10 percent "outsider stocks" of the ETF.) We use these beta values to determine which stocks to invest in following high ETF selloffs.
    
def betas(stock, etf, start_date, end_date, L_min=100, halflife=days_in_quarter):
    
    # L_min specifies how many days the stock must have been listed to calculate the beta coefficient.  
    # If the stock is quite newly listed, then the calculated beta value is unstable and not very meaningful 
    # (and so we will set beta = np.nan).  
    
    times = np.arange(start_date,end_date)#pd.date_range(start=start_date, end=end_date, freq='D')
    betas = []
    
    stock_returns = returns(stock)
    etf_returns = returns(etf)
    
    two_stocks = pd.DataFrame({stock: stock_returns, etf: etf_returns}).dropna()
    
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

# List of ETF tickers we considered

etf_tickers = {
    'XLY',
    'XLP',
    'XLE',
    'XLF',
    'XLV',
    'XLI',
    'XLB',
    'XLK',
    'XLU',
    'XLRE',
    'XLC'
}

# Loading and preprocessing ETF holdings data previously compiled in etf_composition.py
# For each ETF, holdings_per_day gives a datframe of True/nan entries: 
#      True means the stock was included in the ETF that day
#      nan means that stock was not included in the ETF that day
# Note that, by commenting out the last two lines of this code, we get the exact weighting of the stock in the ETF
# on each day.  (We do not actually need this information for our analysis, but it could be useful for further analysis.)

start_date = np.datetime64('2019-10-01')
end_date = np.datetime64('2024-04-01')

holdings_per_day = {}

for etf in etf_tickers:

    # Read the CSV
    df = pd.read_csv(f"data/{etf}_holdings.csv")
    df.index = df['Tickers']
    df = df.iloc[:,:3:-1]

    # This is a fix for the fact that some tickers are duplicated because the associated company name
    # label is not consistent (e.g. LOW in the ETF XLY)
    df = df.groupby(df.index).sum()

    df.columns = pd.to_datetime(df.columns)

    etf_holdings_per_day = {}

    date_range = np.arange(start_date,end_date)

    for date in date_range:
        etf_holdings_per_day[date] = df[df.columns[df.columns < date].max()]

    holdings_per_day[etf] = pd.DataFrame(etf_holdings_per_day).transpose() 
    holdings_per_day[etf].index.name = 'Date'
    
    # To get the exact weighting of each stock in the ETF (not just whether the stock is included in the ETF),
    # comment out the following two lines:
        
    holdings_per_day[etf] = holdings_per_day[etf] != 0
    holdings_per_day[etf] = holdings_per_day[etf].where(holdings_per_day[etf] != 0,np.nan)   
    

if __name__ == '__main__':
    
    # We now use the above functions to compute the ETF betas for each stock in the ETF each day.  Note that this code takes some time to compile, which we why we save the results in csv files.
        
    # Note that a beta value of np.nan can mean two different things: 
    # (1) The stock wasn't part of the ETF that quarter.
    # (2) The stock was too newly listed to get a robust beta value.

    betas_per_day = {}
    
    save = True

    for etf in holdings_per_day.keys():
        df = holdings_per_day[etf]
        betas_per_day[etf] = pd.DataFrame({stock: betas(stock,etf,start_date,end_date) * df[stock] for stock in df.columns})
        betas_per_day[etf].index.name = 'Date'
        if save:
            betas_per_day[etf].to_csv(f"data/{etf}_betas_per_day.csv")

