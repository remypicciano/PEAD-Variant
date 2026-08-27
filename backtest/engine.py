from data import MarketData, config
from events import EventData
from strategy import Strategy
from execution import Execute
from portfolio import Portfolio

data = MarketData(config)

prices, earnings = data.load()

print(f"Prices: {len(prices):,} rows")
print(f"Earnings: {len(earnings):,} rows")

event_data = EventData(prices, earnings)
events = event_data.build()

print(f"Events: {len(events):,}")

strategy = Strategy(prices, events)
signals = strategy.build()

print(f"Signals: {len(signals):,}")

execute = Execute(prices, signals)
trades = execute.execute_all(signals)

print(f"Trades: {len(trades):,}")

portfolio = Portfolio(prices=prices, trades=trades)
portfolio_history = portfolio.build()

print("\n--- Portfolio History ---")
print(portfolio_history)

print("\n--- Portfolio Statistics ---")

print(f"Starting capital: ${portfolio.starting_capital:,.2f}")

print(f"Ending equity: ${portfolio_history.iloc[-1]['equity']:,.2f}")

print(f"Final cash: ${portfolio_history.iloc[-1]['cash']:,.2f}")

print(f"Final invested: ${portfolio_history.iloc[-1]['invested']:,.2f}")

print(f"Maximum open positions: {portfolio_history['open_positions'].max()}")
