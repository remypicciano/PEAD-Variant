from dataclasses import dataclass
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


class Portfolio: 
    def __init__(self, starting_capital: float = STARTING_CAPITAL):
        self.starting_capital = starting_capital
        self.cash = starting_capital
        self.positions = []

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
