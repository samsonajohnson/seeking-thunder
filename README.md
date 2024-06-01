# Repo Guide
- This [beta values script](https://github.com/mjplacroix/seeking-thunder/blob/main/beta_values.py) walks through calculating the beta coefficients
- The [beta values notebook](https://github.com/mjplacroix/seeking-thunder/blob/main/beta_values_bupd.ipynb) contains similar content with additional visuals
- The [portfolio strategy notebook](https://github.com/mjplacroix/seeking-thunder/blob/main/portfolio-strategy.ipynb) walks through the performance of our strategy and contains visuals
- [Data folder](https://github.com/mjplacroix/seeking-thunder/tree/main/data) contains the raw data and beta coefficients

# Seeking Thunder - Overview
B.  Baharinezhad, S. Johnson, M. LaCroix, A. Patil, J. Pfeffer, 

## Introduction

Exchange Traded Funds ([ETFs](https://www.investopedia.com/terms/e/etf.asp)) are investment instruments that pool several securities into one. ETFs typically group stocks of a common theme and increase correlations between stock prices, even for "outsider" stocks contained in the ETF that have *little or negative exposure* to the theme. If outsider stocks exhibit unjustified, sympathic price movements due to this correlation with other stocks in the ETF, one would expect their precies to revert to nominal values. This produces a trading opportunity that can be capitalized upon. This behavior was pointed out by [Lynch et al. 2019](https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358), and here we investigate and extend their findings. In short, they found that a high sell-off day for an ETF (qualified by a high trading volume) leads to to predictable price movements in outsider stocks. They determined the outsider stocks by chosing those that were least correlated with the ETF prior to the sell-off day and constructed a portfolio using those stocks. They then measured the returns from holding these stocks for 40 trading days. 

To motivate this further, [Lynch et al. 2019](https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358) evoke an example from 2015 when the Health Care Select Sector SPDR ETF (XLV) saw significant selling action following a Tweet from Hillary Clinton announcing a crackdown on pharmaceutical price gouging. While this sensibly would have impact on companies producing pharmaceuticals for humans, it likely should not have had the same for those producing animal medicines or medical equipment. They find that a portfolio that picked these outsider stocks would have performed 4.2% better than XLV over the next 40 days. 

## Data

We examine eleven ETFs from the [Select Sector SPDR Trust](https://www.sectorspdrs.com/) which contain broad themes ranging from health care to entertainment. We gather data for each of these from their NPORT-P filings from the [SEC EDGARS](https://www.sec.gov/edgar/search-and-access) database. These NPORT-P filings contain the quartly reporting of the relative composition of the ETF, as the ETF can change its make-up by rebalancing the amount the fund holds of each individual consitituent stock on a quarterly basis. Each of these ETFs contain an average (median) of ~60 individual tickers. These composition and weights are stored in the data directory (e.g., [XLV](data/S000006408.csv)). These data were produced by running [etf_composition.py](data_collection/etf_composition.py), which took roughly 10 minutes. 

Once we have obtained the composition of the ETFs, we then retrieve the daily [open, high, low, close] prices of the stocks within the ETF. We obtain these using the Python API [yfinance](https://pypi.org/project/yfinance/) for querying [Yahoo! Finances](https://finance.yahoo.com/) stock price records. We measure the return $R$ of the stocks in an ETF and of the ETF itself through the relative change of the closing price from one day $K_t$ compared to the previous $K_{t-1}$
$$R = \frac{K_t - K_{t-1}}{K_{t-1}}.
$$

## Method

To quantify the correlation between the returns of the individual stocks and for their ETF, we compute the $\beta$ coefficients for the individual stock prices regressed on the ETF returns. We do so with an exponentially decaying weight, such that more recent returns are weighted more heavily in the regression. These $\beta$ coefficients are predictors of how much a stock's returns should change in response to a change in the ETF's returns.
We select the bottom 10% of these stocks, purchase them, and compare their returns with those of the ETF over the 40 days following the ETF trading volume spike. (The choice of 40 days was based on the empirical findings in Lynch, et al.)  

## Findings

Our analysis confirmed that average cross-correlations among constituent stocks in the ETF are abnormally high during ETF trading volume spikes. We identified the outsider stocks and implemented the strategy proposed in Lynch et al. (2019). Our results find that, from October 2019 to March 2024, this strategy does not generate returns that consistently outperform the corresponding ETFs. This difference may indicate that the strategy proposed by Lynch et al. (2019) may not have persisted since it was proposed. 

## Conclusion

Our analysis provides mixed results regarding the strategy proposed by Lynch et al. (2019). While we confirmed that high trading volume spikes in ETFs lead to increased correlations among constituent stocks, including those with little exposure to the ETF's theme, we did not consistently find significant returns from investing in these outsider stocks. It is possible that the strategy's effectiveness may have diminished over time. 

## Acknowledgement 

We would like to express our gratitude to the Erdos Institute for their support and resources. Special thanks to Steven Gubkin, the Lead Instructor, and to Professor Thomas Polstra from the Quantitative Research course for his insightful contributions, and our group mentor Rongqing Ye. 



