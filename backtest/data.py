# Please note that there is one key metric missing from the STOOQ data,
# and that is the adjusted close. While this won't affect the actual trading/backtesting,
# it will affect the calculated portfolio return. Take it with a grain of salt.

# NO ADJUSTED CLOSE???

from dataclasses import dataclass
from datetime import date
from pathlib import Path

import pandas as pd
import yfinance as yf
import json


PROJECT_DIR = Path(__file__).resolve().parent.parent
STOOQ_DIR = Path(__file__).resolve().parent / "data" / "stooq"

STOCKS = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
START_DATE = date(1980, 1, 1)
END_DATE = date(2025, 12, 31)
LOOKBACK_DAYS = 10
LOOKFORWARD_DAYS = 20


## Data Handling of Stooq Files – Building Index for Reference ##
## Reason: searching for the ticker in the file name would take FOREVER.
## So instead, we take all paths, extract the ticker from the filename, save the ticker
## and the file path we extracted from to a dict, and now we can search for our key (the ticker)
## at rocket speed and only have to run this once. Eventually this will be saved to a json file.


def build_file_index(root: Path) -> dict[str, Path]:
    index: dict[str, Path] = {}

    for path in root.rglob("*.us.txt"):
        ticker = path.name.removesuffix(".us.txt").upper()  # Changes aapl to AAPL
        index[ticker] = path

    return index


@dataclass
class DataConfig:
    stocks: list[str]
    start_date: date
    end_date: date
    lookback_days: int
    lookforward_days: int


config = DataConfig(
    stocks=STOCKS,
    start_date=START_DATE,
    end_date=END_DATE,
    lookback_days=LOOKBACK_DAYS,
    lookforward_days=LOOKFORWARD_DAYS,
)


class MarketData:  # What data do I want?
    def __init__(self, config: DataConfig):
        self.file_index = build_file_index(STOOQ_DIR)
        self.config = config
        self.stocks = config.stocks

    def _quarter_count(self) -> int:
        start = config.start_date
        end = config.end_date

        return ((end.year - start.year) * 4
                + (end.month - 1) // 3
                - (start.month - 1) // 3
                + 1)

    def _read_price_file(self, ticker: str) -> pd.DataFrame:
        path = self.file_index[ticker]
        df = pd.read_csv(path)
        return df

    def _clean_prices(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.rename(columns={
            "<TICKER>": "ticker",
            "<PER>": "period",
            "<DATE>": "date",
            "<TIME>": "time",
            "<OPEN>": "open",
            "<HIGH>": "high",
            "<LOW>": "low",
            "<CLOSE>": "close",
            "<VOL>": "volume",
            "<OPENINT>": "open_interest",
        })

        df = df[["ticker", "date", "open", "high", "low", "close", "volume"]]
        df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")

        numeric_columns = ["open", "high", "low", "close", "volume"]

        for column in numeric_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")

        df = df.dropna()
        df = df.sort_values("date")
        df = df.reset_index(drop=True)

        return df

    def prices(self) -> pd.DataFrame:
        frames = []

        for ticker in self.stocks:
            df = self._read_price_file(ticker)
            df = self._clean_prices(df)
            frames.append(df)

        return pd.concat(frames, ignore_index=True)

    def _clean_earnings(self, df: pd.DataFrame, ticker: str) -> pd.DataFrame:
        df.index.name = "earnings_date"
        df = df.reset_index()

        df = df.rename(columns={
            "EPS Estimate": "eps_estimate",
            "Reported EPS": "eps_actual",
            "Surprise(%)": "surprise_percent",
        })

        df["ticker"] = ticker
        df["earnings_date"] = (
            pd.to_datetime(df["earnings_date"], utc=True)
            .dt.tz_localize(None)
        )  # Note that time is still here

        df = df[[
            "ticker",
            "earnings_date",
            "eps_estimate",
            "eps_actual",
            "surprise_percent",
        ]]

        df = df.dropna(subset=[
            "eps_estimate",
            "eps_actual",
            "surprise_percent",
        ])

        df = df.sort_values("earnings_date")

        return df

    def _get_earnings(self, ticker: str) -> pd.DataFrame:
        yf_ticker = yf.Ticker(ticker)

        frames = []
        offset = 0
        previous_earliest = None

        while True:
            print(f"Requesting {ticker}, offset={offset}...")

            df = yf_ticker.get_earnings_dates(
                limit=100,
                offset=offset,
            )

            # Explicitly distinguish None from an empty DataFrame
            if df is None:
                print(f"WARNING: Yahoo returned None for {ticker}, offset={offset}.")
                break

            if df.empty:
                print(f"WARNING: Yahoo returned an empty DataFrame for {ticker}, offset={offset}.")
                break

            earliest_date = df.index.min().date()

            if previous_earliest is not None and earliest_date >= previous_earliest:
                break

            frames.append(df)

            if earliest_date <= self.config.start_date:
                break

            if len(df) < 100:
                break

            previous_earliest = earliest_date
            offset += 100

        if not frames:
            print(f"WARNING: {ticker} returned NO earnings data.")
            return pd.DataFrame()

        result = pd.concat(frames).drop_duplicates()
        earliest = result.index.min().date()

        if earliest > self.config.start_date:
            print(
                f"WARNING: {ticker} has no earnings data back to "
                f"{self.config.start_date}. Earliest available: {earliest}."
            )

        return result

    def earnings(self) -> pd.DataFrame:
        frames = []

        for ticker in self.stocks:
            df = self._get_earnings(ticker)

            if df.empty:
                print(f"WARNING: {ticker} will be excluded from the earnings dataset.")
                continue

            df = self._clean_earnings(df, ticker)
            frames.append(df)

        earnings = pd.concat(frames, ignore_index=True)
        earnings = self._get_market_timing(earnings)

        return earnings

    def _get_market_timing(self, earnings: pd.DataFrame) -> pd.DataFrame:
        earnings = earnings.copy()

        # Convert the earnings timestamp from UTC to U.S. Eastern Time.
        earnings["earnings_date"] = (
            pd.to_datetime(earnings["earnings_date"], utc=True)
            .dt.tz_convert("America/New_York")
        )

        market_open = pd.Timestamp("09:30:00").time()
        market_close = pd.Timestamp("16:00:00").time()

        def classify_time(timestamp):
            time = timestamp.time()

            if time < market_open:
                return "before"
            elif time <= market_close:
                return "during"
            else:
                return "after"

        earnings["market_timing"] = earnings["earnings_date"].apply(classify_time)

        return earnings

    def _get_common_period(self, prices: pd.DataFrame, earnings: pd.DataFrame) -> tuple[pd.Timestamp, pd.Timestamp]:
        earnings_start_by_ticker = (
            earnings.groupby("ticker")["earnings_date"]
            .min()
        )

        common_start = max(
            earnings_start_by_ticker.max(),
            pd.Timestamp(self.config.start_date, tz="America/New_York"),
        )

        earnings_end_by_ticker = (
            earnings.groupby("ticker")["earnings_date"]
            .max()
        )

        common_end = min(
            earnings_end_by_ticker.min(),
            pd.Timestamp(self.config.end_date, tz="America/New_York"),
        )

        return common_start, common_end

    def _get_price_period(self, prices: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.Timestamp, pd.Timestamp]:
        # Stooq dates are timezone-naive.
        start = start.tz_localize(None)
        end = end.tz_localize(None)

        trading_dates = (
            prices["date"]
            .drop_duplicates()
            .sort_values()
            .reset_index(drop=True)
        )

        start_position = trading_dates.searchsorted(start)
        end_position = trading_dates.searchsorted(end, side="right") - 1

        padded_start_position = max(
            0,
            start_position - self.config.lookback_days,
        )

        padded_end_position = min(
            len(trading_dates) - 1,
            end_position + self.config.lookforward_days,
        )

        return (
            trading_dates.iloc[padded_start_position],
            trading_dates.iloc[padded_end_position],
        )

    def _align_data(self, prices: pd.DataFrame, earnings: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
        common_start, common_end = self._get_common_period(prices, earnings)
        price_start, price_end = self._get_price_period(prices, common_start, common_end)

        prices = prices[
            (prices["date"] >= price_start)
            & (prices["date"] <= price_end)
        ].copy()

        earnings = earnings[
            (earnings["earnings_date"] >= common_start)
            & (earnings["earnings_date"] <= common_end)
        ].copy()

        return prices, earnings

    def load(self) -> tuple[pd.DataFrame, pd.DataFrame]:
        prices = self.prices()
        earnings = self.earnings()

        prices, earnings = self._align_data(prices, earnings)

        return prices, earnings


data = MarketData(config)


# Temporary Testing
if __name__ == "__main__":
    prices, earnings = data.load()
    print(prices)
    print(earnings)