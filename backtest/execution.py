# Receives signals and executes a simulated trade on a realistic price 
# Price will use likely day close not open. 
from dataclasses import dataclass
from datetime import date 
from strategy import Strategy
from strategy import Signal

import pandas as pd 

@dataclass
class Trade: 
    ticker: str
    direction: str

    event_date = pd.Timestamp

    entry_date = pd.Timestamp
    entry_price = float

    exit_date = pd.Timestamp
    exit_price = float

    percent_return: float

class Execute: 
    def __init__(self, prices: pd.DataFrame, signals: list[Signal]):
        self.prices = prices
        self.signals = signals

    def _get_exec_price(self, signal: Signal) -> tuple[float, float] | None:
        ticker_prices = self.prices[self.prices["ticker"].str.startswith(signal.ticker)].copy()

        entry = ticker_prices[ticker_prices["date"] == signal.entry_date]
        exit = ticker_prices[ticker_prices["date"] == signal.exit_date]

        if entry.empty or exit.empty: 
            return None

        entry_price = entry.iloc[0]["close"]
        exit_price = exit.iloc[0]["close"]

        return entry_price, exit_price

    def execute(self, signal: Signal) -> Trade | None: # only execute trade on ONE signal
        entry_price, exit_price = self._get_exec_price(signal)

        if entry_price is None or exit_price is None: 
            return None

        percent_return = ((exit_price - entry_price)/entry_price)*100
        return Trade(
            ticker=signal.ticker,
            direction=signal.direction, 
            entry_date=signal.entry_date,
            exit_date=signal.exit_date,
            entry_price=entry_price,
            exit_price=exit_price,
            percent_return=percent_return
        )
    def execute_all(self, signal: list[Signal]) -> list[Trade]: # list of signals
        trades = []

        for signal in Signal: 
            trade = self.execute(signal)

            if trade is not None: 
                trades.append(trade)

        return trades