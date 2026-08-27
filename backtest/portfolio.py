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
    percent_return: float
    dollar_return: float

# Better to return a full dataframe with ticker and daily prices until the exit date
class Portfolio: 
    def __init__(self, prices: pd.DataFrame, trades: list[Trade], starting_capital: float = STARTING_CAPITAL):
        self.starting_capital = starting_capital
        self.cash = starting_capital

        self.trades = trades
        self.prices = prices

        self.positions = []
        self.history = []

    def _get_trade_size(self, equity: float) -> float:
        return min(equity * POSITION_SIZE, self.cash) # never allocate more than available cash

    def _open_position(self, trade: Trade, equity: float): 
        capital_allocated = self._get_trade_size(equity)
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
            percent_return=trade.percent_return,
            dollar_return=dollar_return
            )
        self.positions.append(position) # don't return since we write directly to self.positions

        def _get_price(self, ticker: str, date: pd.Timestamp) -> float | None:
            ticker_prices = self.prices[self.prices["ticker"].str.startswith(ticker)]
            price = ticker_prices[ticker_prices["date"] == date]

            if price.empty: 
                return None

            return float(price.iloc[0]["close"])

        def _position_value(self, position: Position, current_price: float) -> float:
            stock_return = (current_price-position.entry_price)/position.entry_price

            if position.direction == "SHORT":
                stock_return *= -1 # just make the return positive

            return position.capital_allocated * (1 + stock_return) 

        def build(self) -> pd.DataFrame: 
            history = [] # historical daily returns/movement for graphing later on 

            trading_dates = (self.prices["date"].dropna().sort_values().reset_index(drop=True))

            trades_by_date = {}

            for trades in self.trades:
                trades_by_date.setdefault(trade.entry_price, []).append(trade)

            for current_date in trading_dates:
                invested = 0.0 

                for position in self.positions: 
                    if current_date < position.entry_date: 
                        continue

                    price = self._get_price(position.ticker, current_date)

                    if price is not None: 
                        invested += self._position_value(position, price)

                    equity = self.cash + invested

                    