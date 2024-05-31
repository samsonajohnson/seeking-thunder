# Seeking Thunder
B.  Baharinezhad, S. Johnson, M. LaCroix, A. Patil, J. Pfeffer, 

## Introduction

Exchange Traded Funds ([ETFs](https://www.investopedia.com/terms/e/etf.asp)) are investment instruments that pool several securities into one. ETFs typically group stocks of a common theme and increase correlations between stock prices, even for "outsider" stocks contained in the ETF that have *little or negative exposure* to the theme. If outsider stocks exhibit unjustified, sympathic price movements due to this correlation with other stocks in the ETF, one would expect their precies to revert to nominal values. This produces a trading opportunity that can be capitalized upon. This behavior was pointed out by [Lynch et al. 2019](https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358), and here we investigate and extend their findings. In short, they found that a high sell-off day for and ETF (qualified by a high trading volume) lead to . They determined the outsider stocks by chosing those that were least correlated with the ETF prior to the sell-off day and constructed a portfolio using those stocks. They then measured the returns from holding these stocks for 40 trading days. 

To motivate this further, [Lynch et al. 2019](https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358) evoke an example from 2015 when the Health Care Select Sector SPDR ETF (XLV) saw significant selling action following a Tweet from Hillary Clinton announcing a crackdown on pharmaceutical price gouging. While this sensibly would have impact on companies producing pharmaceuticals for humans, it likely should not have had the same for those producing animal medicines of medical equipment. They find that a portfolio that picked these outsider stocks would have performed 4.2% better than XLV over the next 40 days. 

## Data

We examine ten(?) ETFs from the [Select Sector SPDR Trust](https://www.sectorspdrs.com/) which contain broad themes ranging from health care to entertainment. We gather data for each of these from their NPORT-P filings from the [SEC EDGARS](https://www.sec.gov/edgar/search-and-access) database. These NPORT-P filings contain the quartly reporting of the relative composition of the ETF, as the ETF can change its make-up by rebalancing the amount the fund holds of each individual consitituent stock on a quarterly basis. Each of these ETFs contain an average (median) of ~60 (~45) individual tickers. These composition and weights are stored in the data directory (e.g., [XLV](data/S000006408.csv)). These data were produced by running [etf_composition.py](data_collection/etf_composition.py), which took roughly 10 minutes. 

Once we have obtained the composition of the ETFs, we then retrieve the daily [open, high, low, close] prices of the stocks within the ETF. We obtain these using the Python API [yfinance](https://pypi.org/project/yfinance/) for querying [Yahoo! Finances](https://finance.yahoo.com/) stock price records. We measure the return $R$ of the stocks in an ETF and of the ETF itself through the relative change of the closing price from one day $K_t$ compared to the previous $K_{t-1}$
$$R = \frac{K_t - K_{t-1}}{K_{t-1}}.
$$

## Method

To quantify the correlation between the returns of the individual stocks and for their ETF, we compute the $\beta$ coefficients for the individual stock prices regressed on the ETF returns. We do so with an exponentially decaying weight, such that more recent returns are weighted more heavily in the regression. These $\beta$ coefficients are predictors of how much a stock's returns should change in response to a change in the ETF's returns. 



<!--# seeking-thunder
 

placeholder to stick some content in the readme

This currently leaves us with two ideas to explore:
  1) Samson's ETF idea described above.  He linked this full article  https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358 that describes the idea in greater detail.  We discussed looking at different types of ETFs (number of stocks, type of stocks, perhaps looking specifically at ETFs of penny stocks, etc.) and seeing whether the phenomenon is more pronounced with some than with others.

  2) Mike's original project proposal.  As I understand this idea, we'd be looking at daily stock data (open, close, high, low) and see if adding more features from these price trends yields better predictive models.  For example, if we create a feature that examines whether the stock has reached its maximum over the past x days, where x is a hyperparameter we can toy with.   We could theoretically also incorporate Samson's idea by using the stock trends of other stocks in the same ETF as a predictor, but perhaps our intuition is that the phenomenon Samson described would be significant only on small time scales.


A challenge that Mike pointed out is that it is paramount to have access to the right data (and enough of it) to do the data science we want. This might be particularly challenging with Samson's idea if we cannot access the per-minute stock trading data that we need.  So Mike suggested that we investigate what data we can actually access to explore problems (1) and (2) above before deciding which problem to tackle.  So our objective going forward is to look into what data we can get for these two problems in the next couple of days and go from there.
-->