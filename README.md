# seeking-thunder

placeholder to stick some content in the readme

This currently leaves us with two ideas to explore:
  1) Samson's ETF idea described above.  He linked this full article  https://www.tandfonline.com/doi/full/10.1080/0015198X.2019.1572358 that describes the idea in greater detail.  We discussed looking at different types of ETFs (number of stocks, type of stocks, perhaps looking specifically at ETFs of penny stocks, etc.) and seeing whether the phenomenon is more pronounced with some than with others.

  2) Mike's original project proposal.  As I understand this idea, we'd be looking at daily stock data (open, close, high, low) and see if adding more features from these price trends yields better predictive models.  For example, if we create a feature that examines whether the stock has reached its maximum over the past x days, where x is a hyperparameter we can toy with.   We could theoretically also incorporate Samson's idea by using the stock trends of other stocks in the same ETF as a predictor, but perhaps our intuition is that the phenomenon Samson described would be significant only on small time scales.


A challenge that Mike pointed out is that it is paramount to have access to the right data (and enough of it) to do the data science we want. This might be particularly challenging with Samson's idea if we cannot access the per-minute stock trading data that we need.  So Mike suggested that we investigate what data we can actually access to explore problems (1) and (2) above before deciding which problem to tackle.  So our objective going forward is to look into what data we can get for these two problems in the next couple of days and go from there.
