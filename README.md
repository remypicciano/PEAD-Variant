# PEAD

A Python-based backtesting framework for studying **Post-Earnings Announcement Drift (PEAD)**. This project stems from deep interest in all things economics, bridging that with my deep passion of creating things through programming. 

**Disclaimer**: I am not a skilled programmer by any means. You will find that a lot of code is in a less-than-ideal state. I am always trying to improve and get better, but a project like this stems from such a deep place of interest that I tend to power through and find ways to make it happen. Most importantly, for my own learning, I am trying to keep my use of AI extremely limited. That being said, it can still be useful for debugging and cleaning up VERY bad code (yes – unfortunately the bar is very low for me), but I take immense pride in being able to say that I understand what each line of code does in this program. 

The project currently implements a deliberately simple PEAD strategy:

- Collect historical price data from Stooq and earnings data from yfinance
- Identify earnings events and EPS surprises
- Generate trading signals from earnings surprises and movement one day after announcement

The current release is a **BETA**. This project is far from a finished trading strategy/backtest, if anything, it is simply just a proof of concept. 

## Documentation

- [`STRATEGY.md`](STRATEGY.md) — Strategy design; signals; future development
- [`METHODOLOGY.md`](METHODOLOGY.md) — Backtesting methodology
- [`RESULTS.md`](RESULTS.md) — Results among versions and testing
- [`LIMITATIONS.md`](LIMITATIONS.md) — Brief limitations

## Current Status

**Version:** Beta

The current implementation intentionally uses simple position sizing and risk management. In the future I hope to include:

- Rank-based trade selection
- Volatility-adjusted position sizing
- EPS-surprise-weighted sizing
- Trailing stops
- Improved risk management
- Larger and more diverse universes
- More rigorous benchmarking

In short, I plan to actually make this a fully fledged trading backtest/strategy (even if it is not profitable!). 

## Usage
First clone the repo.  

`git clone https://github.com/remypicciano/PEAD-Variant`

Then setup the python environment from within the repo: 

`cd PEAD-Variant`

`source .venv/bin/activate`

Then, all primary logic should be run via `engine.py`. As of now, `engine.py` outputs portfolio performance for a certain set of tickers. It can be run via:  

`python backtest/engine.py`
