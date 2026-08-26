from data import MarketData, config
from events import EventData
from strategy import Strategy

data = MarketData(config)

prices, earnings = data.load()

event_data = EventData(prices, earnings)
events = event_data.build()

strategy = Strategy(prices, events)
signals = strategy.build()

for signal in signals:
    print(signal)