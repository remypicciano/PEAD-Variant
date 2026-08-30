from dataclasses import dataclass
from execution import Trade
import pandas as pd

STARTING_CAPITAL = 100_000
POSITION_SIZE = 0.02 # in Percent: so 2% here

## ** ALERT ** ## HUGE ISSUE: RUNNING PORTFOLIO.BUILD() TWICE RETURNS TWO DIFFERENT RESULTS, WITH DIFFERENT AMOUNTS OF EVENTS, SIGNALS, TRADES, AND A DIFFERENT RETURN AMOUNT

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


# Better to return a full dataframe with ticker and daily prices until the exit date
class Portfolio:
    def __init__(self, prices: pd.DataFrame, trades: list[Trade], starting_capital: float = STARTING_CAPITAL):
        self.starting_capital = starting_capital
        self.cash = starting_capital
        self.trades = trades
        self.prices = prices
        self.positions = []
        self.history = []
        self.price_calls = 0
        self.price_lookup = prices.assign(ticker=prices["ticker"].str.removesuffix(".US")).set_index(["ticker", "date"])["close"]

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
            percent_return=trade.percent_return
        )

        self.positions.append(position) # don't return since we write directly to self.positions

    def _get_price(self, ticker: str, date: pd.Timestamp) -> float | None:
        self.price_calls += 1
        print(f"Number of price lookups: {self.price_calls}")

        try: 
            return float(self.price_lookup.loc[(ticker, date)])
        except KeyError:
            return None


    def _position_value(self, position: Position, current_price: float) -> float:
        stock_return = (current_price - position.entry_price) / position.entry_price

        if position.direction == "SHORT":
            stock_return *= -1 # just make the return positive

        return position.capital_allocated * (1 + stock_return)

    def build(self) -> pd.DataFrame:
        history = []
        trading_dates = self.prices["date"].drop_duplicates().sort_values().reset_index(drop=True)

        trades_by_date = {}
        for trade in self.trades:
            trades_by_date.setdefault(trade.entry_date, []).append(trade)

        for current_date in trading_dates:
            invested = 0.0

            for position in self.positions:
                if current_date < position.entry_date:
                    continue

                price = self._get_price(position.ticker, current_date)

                if price is not None:
                    invested += self._position_value(position, price)

            equity = self.cash + invested

            todays_trades = trades_by_date.get(current_date, [])

            for trade in todays_trades:
                self._open_position(trade, equity)

            invested = 0.0

            for position in self.positions:
                price = self._get_price(position.ticker, current_date)

                if price is not None:
                    invested += self._position_value(position, price)

            remaining_positions = []

            for position in self.positions:
                if position.exit_date == current_date:
                    price = self._get_price(position.ticker, current_date)

                    if price is not None:
                        final_value = self._position_value(position, price)
                        self.cash += final_value
                else:
                    remaining_positions.append(position)

            self.positions = remaining_positions

            invested = 0.0

            for position in self.positions:
                price = self._get_price(position.ticker, current_date)

                if price is not None:
                    invested += self._position_value(position, price)

            equity = self.cash + invested

            if history:
                previous_equity = history[-1]["equity"]

                if previous_equity != 0:
                    daily_return = (equity - previous_equity) / previous_equity
                else:
                    daily_return = 0.0
            else:
                daily_return = 0.0

            net_return = (equity - self.starting_capital)/self.starting_capital

            history.append({
                "date": current_date,
                "cash": self.cash,
                "invested": invested,
                "equity": equity,
                "daily_return": daily_return,
                "net_return": net_return,
                "open_positions": len(self.positions)
            })

        return pd.DataFrame(history)
