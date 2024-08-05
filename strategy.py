import queue
import threading
from cards import Cards
from exchange import Exchange
from model import OrderRequest, Side
from option_pricing import compile_option_pricing_cpp, option_pricing_cpp
from util import round_down_to_tick, round_up_to_tick


class Pricer:

    def __init__(self, cards: Cards, threads: int, iterations: int) -> None:
        compile_option_pricing_cpp()
        self.reset()
        self.cards = cards
        self.threads = threads
        self.iterations = iterations
        self.queue: queue.Queue[int] = queue.Queue()
        self.pricer_thread = threading.Thread(
            target=self.option_pricing_cpp_thread, daemon=True
        )
        self.pricer_thread.start()

    def option_pricing_cpp_thread(self):
        while True:
            self.queue.get()
            self.call, self.put, self.call_delta, self.put_delta = option_pricing_cpp(
                self.cards, self.threads, self.iterations
            )
            self.queue.task_done()

    def pricing(self):
        if self.call is None:
            self.queue.put(1)

    def reset(self):
        self.call = None
        self.put = None
        self.call_delta = None
        self.put_delta = None


class Strategy:
    def __init__(self, exchange: Exchange, symbol: str) -> None:
        self.exchange = exchange
        self.symbol = symbol
        self.tick_size = exchange.products[symbol].tickSize
        self.credit = 1.0
        self.position_limit = 100
        self.reset_price()

    def make_market(self):
        theo = self.theo_price
        if theo is None:
            self.exchange.delete_orders(self.symbol)
            return

        bid_price = round_down_to_tick(
            theo - self.credit * self.tick_size, self.tick_size
        )
        ask_price = round_up_to_tick(
            theo + self.credit * self.tick_size, self.tick_size
        )
        bid_price = max(0, bid_price)
        ask_price = max(bid_price + self.tick_size, ask_price)
        self.exchange.insert_order(
            instrument_id=self.symbol,
            price=bid_price,
            volume=self.position_limit * 2,
            side=Side.BUY,
        )

        self.exchange.insert_order(
            instrument_id=self.symbol,
            price=ask_price,
            volume=self.position_limit * 2,
            side=Side.SELL,
        )

        self.bid_price = bid_price
        self.ask_price = ask_price

    def reset_price(self):
        self.theo_price = None
        self.bid_price = None
        self.ask_price = None
        self.exchange.delete_orders(self.symbol)


class Future(Strategy):
    def __init__(self, exchange: Exchange, symbol: str, cards: Cards) -> None:
        super().__init__(exchange, symbol)
        self.cards = cards
        self.position_limit = 100
        self.credit = 0.5

    def make_market(self):
        if self.theo_price is None:
            self.exchange.delete_orders(self.symbol)
            self.theo_price = self.cards.get_theoretical_price()

        super().make_market()


class Call(Strategy):
    def __init__(
        self, exchange: Exchange, symbol: str, cards: Cards, pricer: Pricer
    ) -> None:
        super().__init__(exchange, symbol)
        self.cards = cards
        self.position_limit = 250
        self.credit = 2
        self.pricer = pricer

    def make_market(self):
        self.theo_price = self.pricer.call
        if self.theo_price is None:
            self.exchange.delete_orders(self.symbol)
        super().make_market()


class Put(Strategy):
    def __init__(
        self, exchange: Exchange, symbol: str, cards: Cards, pricer: Pricer
    ) -> None:
        super().__init__(exchange, symbol)
        self.cards = cards
        self.position_limit = 250
        self.credit = 2
        self.pricer = pricer
        print(self.tick_size)

    def make_market(self):
        self.theo_price = self.pricer.put
        if self.theo_price is None:
            self.exchange.delete_orders(self.symbol)
        super().make_market()
