import pandas as pd


class EventData:

    def __init__(self, prices: pd.DataFrame, earnings: pd.DataFrame):
        self.prices = prices
        self.earnings = earnings

    def _get_surrounding_price(self, event: pd.Series) -> pd.Series:
        ticker = event["ticker"]
        earnings_timestamp = event["earnings_date"]

        # Stooq price dates are timezone-naive
        earnings_timestamp = earnings_timestamp.tz_localize(None)

        ticker_prices = self.prices[
            self.prices["ticker"].str.startswith(ticker)
        ].copy()

        ticker_prices = ticker_prices.sort_values("date")

        earnings_date = earnings_timestamp.normalize() # remove time, just calendar date

        # valid trading day before the earnings date
        previous_prices = ticker_prices[
            ticker_prices["date"] < earnings_date
        ]

        # valid trading days after the earnings dates
        next_prices = ticker_prices[
            ticker_prices["date"] > earnings_date
        ]

        if previous_prices.empty or next_prices.empty: # edge case basically, very rare though
            return pd.Series(dtype=object)

        previous_day = previous_prices.iloc[-1] # pos of previous day
        next_day = next_prices.iloc[0] # pos of next day

        return pd.Series({
            "previous_date": previous_day["date"],
            "previous_open": previous_day["open"],
            "previous_high": previous_day["high"],
            "previous_low": previous_day["low"],
            "previous_close": previous_day["close"],
            "previous_volume": previous_day["volume"],

            "next_date": next_day["date"],
            "next_open": next_day["open"],
            "next_high": next_day["high"],
            "next_low": next_day["low"],
            "next_close": next_day["close"],
            "next_volume": next_day["volume"],
        })

    def build(self) -> pd.DataFrame:
        events = self.earnings.copy()

        surrounding_prices = events.apply(
            self._get_surrounding_price,
            axis=1,
        ) # apply to each row, and concat (below) hence axis=1

        event_data = pd.concat([events.reset_index(drop=True),surrounding_prices.reset_index(drop=True),],axis=1,)

        return event_data
