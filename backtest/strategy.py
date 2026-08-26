# only a decision maker, doesn't handle execution
# use volatility based trade sizing somewhere else
from dataclasses import dataclass
from datetime import date 
import pandas as pd 

HOLDING_PERIOD = 60 # temporary

@dataclass
class Signal: # signal structure for execution handling 
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
        ticker_prices = self.prices[self.prices["ticker"].str.startswith(ticker)].copy()
        ticker_prices = ticker_prices.sort_values("date")

        trading_dates = ticker_prices["date"].drop_duplicates().reset_index(drop=True)

        confirmation_date = confirmation_date.tz_localize(None) if confirmation_date.tzinfo else confirmation_date
        confirmation_position = trading_dates.searchsorted(confirmation_date)

        entry_position = confirmation_position + 1 # day after movement
        exit_position = entry_position + HOLDING_PERIOD - 1

        if exit_position >= len(trading_dates):
            return None

        entry_date = trading_dates.iloc[entry_position]
        exit_date = trading_dates.iloc[exit_position]

        return entry_date, exit_date

    def _eval_event(self, event: pd.Series) -> Signal | None:
        eps_surprise = event["surprise_percent"]
        previous_close = event["previous_close"]
        next_close = event["next_close"]

        # This is the actual super simple strategy. 

        if eps_surprise > 0 and next_close > previous_close: # If EPS is positive and if the day after earnings call is bullish
            direction = "LONG"
        elif eps_surprise < 0 and next_close < previous_close: # vice versa
            direction = "SHORT"
        else: # No signal 
            return None 

        dates = self._get_entry_exit(event["ticker"], event["next_date"])
        if dates is None: 
            return None
        entry_date, exit_date = dates 

        return Signal(
            ticker=event["ticker"],
            event_date=event["earnings_date"],
            market_timing = event["market_timing"],
            eps_surprise=eps_surprise, 
            entry_date=entry_date,
            exit_date=exit_date,
            )
    def build(self) -> list[Signal]:
        signals = []

        for _, event in self.events.iterrows():
            signal = self._eval_event(event)

            if signal is not None: 
                signals.append(signal)

        return signals 
