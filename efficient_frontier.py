# Multi-Asset Portfolio Optimization
# Ramy Alsammarae

import numpy as np
import pandas as pd
from pandas_datareader import data as pdr
import datetime as dt
import matplotlib.pyplot as plt
import yfinance as yf
yf.pdr_override()

# pulls data from Yahoo Finance and sets a default trailing 10 year data range
tickers = ['ITOT','IXUS','AGG','IAGG','REET','GSG','BTC-USD']
end_date = dt.datetime.now()
start_date = end_date - dt.timedelta(days=365*10)
ticker_data = pdr.get_data_yahoo(tickers, start=start_date, end=end_date)['Close']

# pulls the U.S. 10 Year Treasury Yield
risk_free_rate = (yf.Ticker('^TNX').info['regularMarketPreviousClose'] / 100)

# calculates the daily and annual returns 
daily_returns = ticker_data.pct_change()
annual_returns = daily_returns.mean() * 252

# calculates the daily and annual covariance of returns
daily_covariance = daily_returns.cov()
annual_covariance = daily_covariance * 252

# sets the number of iterations for the Monte Carlo simulation
num_tickers = len(tickers)
num_iterations = 20000

# creates empty lists to store portfolio data
portfolio_returns = []
portfolio_volatility = []
asset_weights = []
sharpe_ratio = []

# generates portfolio data using Monte Carlo and populates the empty lists above
for sample_portfolio in range(num_iterations):
    sample_weights = np.random.random(num_tickers)
    weights = sample_weights / np.sum(sample_weights)
    returns = np.dot(weights, annual_returns)
    volatility = np.sqrt(np.dot(weights.T, np.dot(annual_covariance, weights)))
    sharpe = (returns - risk_free_rate) / volatility
    portfolio_returns.append(returns)
    portfolio_volatility.append(volatility)
    asset_weights.append(weights)
    sharpe_ratio.append(sharpe)

# creates a dictionary to store corresponding portfolio data
portfolio = {'Returns': portfolio_returns,
             'Volatility': portfolio_volatility,
             'Sharpe Ratio' : sharpe_ratio}

# updates the dictionary to include portfolio tickers and weights
for index, ticker in enumerate(tickers):
    portfolio[ticker + ' Weight'] = [weight[index] for weight in asset_weights]

# creates a dataframe using the portfolio dictionary and then rearranges the column order
portfolio_df = pd.DataFrame(portfolio)
column_order = ['Returns', 'Volatility','Sharpe Ratio'] + [asset+' Weight' for asset in tickers]
portfolio_df = portfolio_df[column_order]

# locates and prints the max Sharpe Ratio portfolio and min volatility portfolio
min_volatility = portfolio_df['Volatility'].min()
max_sharpe = portfolio_df['Sharpe Ratio'].max()
max_sharpe_portfolio = portfolio_df.loc[portfolio_df['Sharpe Ratio'] == max_sharpe]
min_volatility_portfolio = portfolio_df.loc[portfolio_df['Volatility'] == min_volatility]
print(max_sharpe_portfolio.T)
print(min_volatility_portfolio.T)

# plots the efficient frontier, max Sharpe Ratio portfolio (blue star), and min volatility portfolio (red star)
plt.style.use('ggplot')
portfolio_df.plot.scatter(x='Volatility', y='Returns', c='Sharpe Ratio',
                cmap='viridis', edgecolors='black', figsize=(8, 6), grid=True)
plt.scatter(x=max_sharpe_portfolio['Volatility'], y=max_sharpe_portfolio['Returns'], c='blue', marker='*', s=400)
plt.scatter(x=min_volatility_portfolio['Volatility'], y=min_volatility_portfolio['Returns'], c='red', marker='*', s=400 )
plt.xlabel('Volatility')
plt.ylabel('Expected Returns')
plt.title('Efficient Frontier')
plt.show()