# only a decision maker, doesn't handle execution
# use volatility based trade sizing somewhere else
from dataclasses import dataclass
from datetime import date 
import pandas as pd 


@dataclass
class Signal: 
    ticker: str
    event_date: pd.Timestamp
    direction: str # maybe bool at some point?
    eps_surprise: float
    market_timing: str

    entry_date: pd.Timestamp
    exit_date: pd.Timestamp

class Strategy: 
    def __init__(self, prices: pd.DataFrame, events: pd.DataFrame):
        self.prices = prices 
        self.events = events

    def _get_entry_exit(self, ticker: str, confirmation_date: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp] | None:
        ticker_prices = [self.prices["ticker"].str.startswith(ticker)].copy()
        ticker_prices = ticker_prices.sort_values("date")

        trading_dates = ticker_prices["date"].drop_duplicates().reset_index(drop=True)

        confirmation_date = confirmation_date.tz_localize(None) if confirmation_date.tzinfo else confirmation_date
        confirmation_position = trading_dates.searcahsorted(confirmation_date)

        entry_position = confirmation_position + 1 # day after movement
        exit_position = entry_position + HOLDING_PERIOD - 1

        if exit_position >= len(trading_dates):
            return None

        entry_date = trading_dates.iloc[entry_position]
        exit_date = trading_dates.iloc[exit_position]

        return entry_date, exit_date