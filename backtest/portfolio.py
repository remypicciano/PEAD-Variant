from dataclasses import dataclass
from execution import Trade
import pandas as pd 

STARTING_CAPITAL = 100_000 
POSITION_SIZE = 0.02 # in Percent: so 2% here

@dataclass 
class Position: 
    ticker: str
    direction: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float 
    exit_price: float
    capital_allocated: float

# Better to return a full dataframe with ticker and daily prices until the exit date
class Portfolio: 
    def __init__(self, trades: list[Trade], starting_capital: float = STARTING_CAPITAL):
        self.starting_capital = starting_capital
        self.cash = starting_capital
        self.trades = trades

        self.positions = []
        self.history = []

    def _get_trade_size(self) -> float:
        return self.cash * POSITION_SIZE

    def _open_positions(self, trade): 
        capital_allocated = self._get_trade_size()
        self.cash -= capital_allocated # subtract to get actual cash on hand afer trade 

        dollar_return = capital_allocated * (trade.percent_return / 100)

        position = Position(
            ticker=trade.ticker,
            direction=trade.direction,
            entry_date=trade.entry_date,
            exit_date=trade.exit_date,
            entry_price=trade.entry_price,
            exit_price=trade.exit_price,
            capital_allocated=capital_allocated,
            dollar_return=dollar_return
        )
        self.positions.append(position) # don't return since we pend to self.positions

        def _get_price(self, ticker: str, date: pd.Timestamp) -> float | None:
            ticker_prices = self.prices[self.prices["ticker"].str.startswith(ticker)]
            price = ticker_prices[ticker_prices["date"] == date]

            if price.empty: 
                return None

            return float(price.iloc[0]["close"])

        def _position_value(self, position: Position, current_price: float) -> float:
            stock_return = (current_price-position.entry_price)/position.entry_price

            if position.direction == "SHORT":
                stock_return *= -1

            return position.capital_allocated * (1 + stock_return) 
