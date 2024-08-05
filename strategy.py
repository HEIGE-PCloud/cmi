from exchange import Exchange
from model import OrderRequest, Side
from trade_config import TradeConfig
from util import round_down_to_tick, round_up_to_tick


class Strategy:
    def __init__(self, config: TradeConfig, exchange: Exchange, symbol: str) -> None:
        self.config = config
        self.exchange = exchange
        self.symbol = symbol
        self.bid_price = None
        self.ask_price = None
        self.tick_size = exchange.products[symbol].tickSize  # TODO: read this from product info
        self.credit = 1  # TODO: set up this properly
        print(self.tick_size)

class Future(Strategy):
    def __init__(self, config: TradeConfig, exchange: Exchange, symbol: str) -> None:
        super().__init__(config, exchange, symbol)

    def make_market(self):
        # self.exchange.delete_all_orders_for_symbol(self.symbol)
        self.price = self.config.future_theo
        if self.price == None:
            return

        self.bid_price = round_down_to_tick(self.price - self.credit, self.tick_size)
        self.ask_price = round_up_to_tick(self.price + self.credit, self.tick_size)
        self.exchange.insert_order(
            OrderRequest(
                side=Side.BUY, price=self.bid_price, volume=1, product=self.symbol
            )
        )
        self.exchange.insert_order(
            OrderRequest(
                side=Side.SELL, price=self.ask_price, volume=1, product=self.symbol
            )
        )
