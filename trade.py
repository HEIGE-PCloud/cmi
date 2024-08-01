

from trade_config import TradeConfig


def trade(config: TradeConfig):
    while True:
        for strategy in config.strategies:
            strategy.make_market()
