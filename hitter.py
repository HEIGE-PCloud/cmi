import threading
from typing import List

from order import OrderRequest, Side
from order_book import OrderBook


class Hitter:
    def __init__(self, symbol: str, low_price: float, high_price: float) -> None:
        self._symbol = symbol
        self._low_price = low_price
        self._high_price = high_price

    def get_symbol(self) -> str:
        return self._symbol

    def init(
        self,
        lock: threading.Lock,
        tick_size: float,
        starting_price: float,
        contract_size: float,
    ) -> None:
        self._lock = lock
        self._tick_size = tick_size
        self._starting_price = starting_price
        self._contract_size = contract_size

    def set_low_price(self, new_price: float) -> None:
        if new_price < self._high_price:
            self._low_price = new_price

    def set_high_price(self, new_price: float) -> None:
        if new_price > self._low_price:
            self._high_price = new_price

    def trade(self, order_book: OrderBook) -> List[OrderRequest]:
        orders: List[OrderRequest] = []
        buy_volume = 0
        sell_volume = 0
        with self._lock:
            for buy_order in order_book.buy.root:
                if buy_order.price >= self._high_price:
                    buy_volume += buy_order.volume
            for sell_order in order_book.sell.root:
                if sell_order.price <= self._low_price:
                    sell_volume += sell_order.volume
        if buy_volume > 0:
            orders.append(
                OrderRequest(
                    side=Side.SELL,
                    price=self._high_price,
                    volume=buy_volume,
                    product=self._symbol,
                )
            )
        if sell_volume > 0:
            orders.append(
                OrderRequest(
                    side=Side.BUY,
                    price=self._low_price,
                    volume=sell_volume,
                    product=self._symbol,
                )
            )
        return orders
