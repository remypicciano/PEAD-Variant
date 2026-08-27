Since the APIs don't offer historical earnings data really past the last year, we're in a tough spot. 

We've already solved on part of the problem which is that we need hyper accurate, day by day price data. Unfortunately, we also need to then obtain the consensus EPS estimate. 

This is difficult, since already this metric is paywalled since it is usually determined by actual financial experts and market analyzers. Meaning, for years of historical data, it will almost always be paywalled. We can calculate the surprise ourselves without a problem, but obtaining the EPS estimate is the bottleneck. 

We can definitely obtain ACTUAL EPS data using EDGAR, but this also becomes a monstrous data project since EPS is in the actual filings, which are documents. Likely an LLM solution that I cannot do!

The yfinance package for python fully solves this problem (I thought it didn't) by giving the full calendar. Surprise EPS, consensus estimate, and actual, with corresponding dates. 

yFinance uses dates for the get_earnings_dates() in terms of quarters. Meaning, limit = 20 says to return the past 20 financial quarters of earnings data. Luckily, we also get specific dates for those earnings. My solution is going to be pretty simple: make a function that caches all the earnings data since 1980 for the stocks we want. The reason I mention that get_earnings_dates(limit=100) uses quarters ie bcause we will have to work backward and calculate how many financial quarters ago was 1980 from the present date. I'll make this an ongoing but one-time called function so that if this is to be used in the future, we have quality replicable code. 

There is no real need to create an event logic that handles earnings directly, sincce this would basically just be the earnings dataset itself. However, we do need to handle the price after and before the earnings call. 

events.py essentially handles the information should we be trading live: previous close, earnings call results/timing, next day open/close (since we will be trading right after that)

Now we need to actually simiulate an execution of those trades. Likely to be handled in execution.py, or engine.py. 

I've included the closing price in the events handling, which is no good. This creates look ahead bias, but then again we also need to see if the stock is moving that DAY to decide whether or not to enter. I don't think the open being greater than the previous close is a good enough indicator of actual market reaction. 

This is hard though since we don't have a smaller timeframe to see the stock moving. Maybe we just delay the entry by one day so that we can use the previous close. Then just say: (Close - Open) / Open = % change, then trade the next day. 

``Strategy logic, not execution/main function logic, to be held in strategy.py. Here are the rules (organized by ChatGPT):

slippage will ba bit greater, 0.20%
trade size, 2% per trade (for now)
commission, 0.05% of size
take profit, none, exit after 2 months
stop loss, none (for now)
long for positive surprise; short for negative
confirm trade/entry 2 days after earnings call, 1 day after price-direction confirmation``

volatility based trade sizing in the future to determine how large trade sizes should be among concurrent trade signals