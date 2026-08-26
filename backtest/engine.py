from events import EventData
from data import config, MarketData

data = MarketData(config)

prices, earnings = data.load()

event_data = EventData(prices, earnings)

events = event_data.build()

print(events)